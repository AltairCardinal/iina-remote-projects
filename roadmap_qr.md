# QR Code 配对功能 — 完善路线图

## 现状分析

| 层 | 状态 | 详情 |
|----|------|------|
| Android 扫码 | ✅ 完成 | ML Kit 扫描 + deep link 双通道，`iina-remote://pair?hosts=...&port=...&code=...` 格式 |
| Server localhost 端点 | ✅ 存在 | `GET /api/v1/pair/code`（port+1，仅 localhost）返回 `{code, expires_in, lan_ips}` |
| macOS QR 生成库 | ✅ 已写+已测 | `QRCodeGenerator`, `PairURLBuilder`, `PairCodeResponse`，19 个测试全通过 |
| macOS QR UI | ❌ 未接入 | 生成链路从未被 UI 调用 |
| macOS 配对浮窗 | ❌ 未使用 | `PairingOverlayWindow` 存在但被 `NSAlert` 代替 |
| macOS 数据源 | ❌ 用错端点 | `StatusBarController` 轮询公网 `/api/v1/pair/challenge`，返回 `{challenge, serverCode}` 而非 QR 所需的 `{code, expires_in, lan_ips}` |

## 需要修改的文件

### 1. `macos/IINARemote/App/StatusBarController.swift`
**目的**：将配对码数据源从公网 challenge 端点改为 localhost pair/code 端点

| 改动 | 详情 |
|------|------|
| 新增 `fetchPairCodeFromLocal()` | 调用 `http://127.0.0.1:{port+1}/api/v1/pair/code`，解析 `PairCodeResponse`（code + lanIPs） |
| 修改 `pollPairChallenge()` | 改为调用 localhost 端点；缓存 `code` + `lanIPs` 供 QR 生成 |
| 修改 `fetchPairCodeSync()` | 同上，返回完整的 `PairCodeResponse` 而非仅 code 字符串 |
| 修改 `showOverlay(code:)` | 改为显示 `PairingOverlayWindow`（含 QR 码），移除 `NSAlert` 用法 |
| 新增 QR 展示逻辑 | 调用 `PairURLBuilder.build()` → `QRCodeGenerator.generate()` → 在 `PairingOverlayWindow` 中展示图片 |

**TDD 测试计划**：
1. 测试 `PairCodeResponse` 能正确解析 localhost 端点的 JSON
2. 测试 `PairURLBuilder` 生成的 URL 与 Android 解析一致
3. 测试 `QRCodeGenerator` 生成的图片可被解码（像素校验）

### 2. `macos/IINARemote/UI/PairingOverlayWindow.swift`
**目的**：在浮窗中加入 QR 码图片展示区域

| 改动 | 详情 |
|------|------|
| 新增 `qrImageView: NSImageView` | 位于 code label 下方，约 200×200 pt |
| 新增 `update(code:lanIPs:port:)` | 同时更新文字码和 QR 图片 |
| 保留纯文字码展示 | 用户仍可手动输入 6 位码 |
| 布局调整 | 窗口高度增大（约 180→440 pt），容纳 QR 图 |

**TDD 测试计划**：
1. 测试 `show(code:lanIPs:port:)` 正确设置 `qrImageView.image`
2. 测试窗口尺寸足以容纳 QR 图片

### 3. `macos/IINARemote/App/StatusBarController.swift`（菜单栏）
**目的**：菜单项增加"显示 QR 码"选项

| 改动 | 详情 |
|------|------|
| 修改 `pairCodeMenuItem` | 显示 "配对码：XXXXXX（点击查看二维码）" |
| 菜单点击 → 浮窗 | 点击配对码项调用 `showPairingOverlay()` 并传入 lanIPs |
| 移除测试项 | 删除 "测试配对码浮窗" 或改为使用真实数据 |

### 4. `macos/IINARemote/Server/HTTPServerManager.swift`（小改）
**目的**：确保 port+1 信息可被 StatusBarController 访问

| 改动 | 详情 |
|------|------|
| 暴露 `localPort` | `port + 1` 属性供其他模块构建 localhost URL |

### 5. `macos/IINARemoteTests/`（新增测试）
**目的**：端到端 QR 生成链路测试

| 测试文件 | 内容 |
|----------|------|
| `PairCodeFlowTests.swift` | 模拟 localhost 响应 → `PairCodeResponse` 解析 → `PairURLBuilder` → `QRCodeGenerator` → 验证生成的 NSImage 非空且像素正确 |
| `PairingOverlayWindowTests.swift` | 测试窗口正确显示 code label + QR image |

---

## 实施顺序（严格 Red-Green TDD）

### Phase 1：修复数据源（最小改动，最大价值）
1. **Red** — 写测试：模拟 `GET /api/v1/pair/code` 响应，验证 `PairCodeResponse.fromJSON()` 解析成功
2. **Green** — `StatusBarController` 新增 `fetchPairCodeFromLocal()`，使用 localhost 端点
3. **验证** — 运行已有 `PairCodeResponseTests` 确保不破坏

### Phase 2：接入 PairingOverlayWindow
1. **Red** — 写测试：验证 `PairingOverlayWindow.show(code:lanIPs:port:)` 设置了 QR image
2. **Green** — 修改 `PairingOverlayWindow` 增加 QR 图片区域 + `update` 方法
3. **Green** — `StatusBarController.showOverlay()` 改为使用 `PairingOverlayWindow` 而非 `NSAlert`

### Phase 3：QR 码生成接入 UI
1. **Red** — 写测试：端到端验证 localhost response → URL → QR image 链路
2. **Green** — `StatusBarController` 中调用 `PairURLBuilder.build()` + `QRCodeGenerator.generate()`
3. **Green** — 将生成的 QR image 传入 `PairingOverlayWindow`
4. **Refactor** — 提取 QR 生成为独立方法，清理重复代码

### Phase 4：菜单栏和交互完善
1. **Red** — 写测试：验证菜单项点击触发浮窗显示
2. **Green** — 修改菜单项文案和行为
3. **Green** — 浮窗关闭时正确更新状态（`overlayDismissedByUser`）

### Phase 5：同步 Figma 原型
1. 更新 `figma/index.html`，在配对页面增加"扫码配对"说明/示意图（如适用）

---

## 验证标准

- [ ] macOS 菜单栏点击"配对码" → 浮窗同时显示 6 位文字码和 QR 码
- [ ] Android 扫描 QR 码 → 自动连接成功（跳过手动输入）
- [ ] QR 码中的 URL 格式为 `iina-remote://pair?hosts=IP1,IP2&port=8765&code=XXXXXX`
- [ ] 配对码过期后浮窗自动更新为新码和新 QR
- [ ] 所有新代码有对应测试，测试全部通过
- [ ] Figma 原型与实际 UI 同步

---

## macOS 配对成功后未自动关闭 QR 窗口 — 修复方案

### 问题结论

当前 macOS 端的自动关闭逻辑依赖以下条件同时成立：

1. 本次轮询拿到的 `code` 与浮窗展示时相同
2. `deviceCount > deviceCountAtOverlayShow`

但 server 在 Android 配对成功后会立即使当前配对码失效；随后 macOS 下一次轮询 `GET /api/v1/pair/code` 时，本地端点会立刻生成一个新 code。结果是：

1. Android 配对成功
2. server 清空旧 code
3. macOS 轮询时拿到新 code
4. `StatusBarController` 命中 `code != lastPolledCode` 分支，执行 `showOverlay(...)`
5. 自动关闭分支因为只存在于 `else if !overlayDismissedByUser` 中而完全跳过

因此 bug 不在窗口本身，而在 `StatusBarController.pollPairCode()` 的状态判断顺序。

### 修改目标

- 只要检测到“新增已配对设备”，就优先关闭当前 QR 窗口
- 不允许“新 code 出现”覆盖“刚刚配对成功”的关闭动作
- 区分“用户手动关闭”和“因配对成功自动关闭”，避免自动关闭后把新 code 永久屏蔽
- 保持现有 server 行为不变，只修 macOS

### 涉及文件

#### `macos/IINARemote/App/StatusBarController.swift`

这是唯一必须修改的生产代码入口，核心是重写 `pollPairCode()` 内的状态流转顺序。

建议增加或调整的状态：

| 状态/字段 | 方案 |
|------|------|
| `deviceCountAtOverlayShow` | 保留，表示当前浮窗对应的设备数基线 |
| `overlayDismissedByUser` | 保留，但语义严格限定为“用户手动关闭当前 code 对应浮窗” |
| `lastPolledCode` | 保留，用于识别 code 切换 |
| `lastObservedDeviceCount` | 新增，记录最近一次轮询得到的 `deviceCount`，便于调试和测试断言 |

建议把轮询后的主线程逻辑改成以下顺序：

1. 若 `code.isEmpty`：
   更新菜单文案，清空 `lastPolledCode` / `lastPolledLanIPs`
   不自动弹窗
2. 先计算 `didPairSucceed = pairingOverlayWindow != nil && deviceCount > deviceCountAtOverlayShow`
3. 若 `didPairSucceed`：
   调用 `pairingOverlayWindow?.dismiss()`
   将 `pairingOverlayWindow = nil`
   不把 `overlayDismissedByUser` 设为 `true`
   更新 `deviceCountAtOverlayShow = deviceCount`
   更新 `lastPolledCode = code` 和 `lastPolledLanIPs = lanIPs`
   直接 `return`
4. 若 `code != lastPolledCode`：
   说明 code 已轮换，但本轮没有新增设备
   重置 `overlayDismissedByUser = false`
   更新 `lastPolledCode` / `lastPolledLanIPs`
   显示新浮窗
5. 若 `code == lastPolledCode && !overlayDismissedByUser`：
   刷新当前浮窗内容，确保 QR 和局域网 IP 保持最新

关键点：

- “设备数增加”判断必须放在“code 是否变化”之前
- 自动关闭不能复用当前 `onDismiss` 的用户关闭副作用
- 自动关闭后应允许未来新 code 再次显示浮窗

### `PairingOverlayWindow` 协作修改

#### `macos/IINARemote/UI/PairingOverlayWindow.swift`

不需要改 UI 布局，但建议把关闭来源区分出来，避免 `dismiss()` 一律触发“用户手动关闭”语义。

建议改法二选一：

方案 A，最直接：
- 新增 `dismiss(notify: Bool)`，用户点关闭按钮时传 `true`
- 自动关闭时调用 `dismiss(notify: false)`

方案 B，语义更清晰：
- 保留 `dismiss()` 代表通用关闭
- 新增 `dismissByUser()`，只有这个方法才触发 `onDismiss`

推荐方案 A，改动更小。

同时在 `StatusBarController` 中将 `onDismiss` 回调只视为“手动关闭当前 code”，不要用于自动关闭路径。

### TDD 方案

#### 先补测试，再改生产代码

现有仓库没有覆盖这个状态机的测试，必须先补。

建议新增测试文件：
- `macos/IINARemoteTests/StatusBarControllerOverlayDismissTests.swift`

建议把轮询后的 UI 判定提取成一个可测试的方法，例如：
- `handlePolledPairCode(_ result: PairCodeResponse)`
- 或更细一点：`applyPairCodeState(code:lanIPs:deviceCount:)`

这样测试不需要真的发网络请求，也不依赖定时器。

#### Red 1

测试名建议：
- `testAutoDismissesOverlayWhenDeviceCountIncreasesEvenIfCodeChanges`

步骤：
1. 先构造一个已显示浮窗的状态：`lastPolledCode = "OLD111"`，`deviceCountAtOverlayShow = 0`
2. 模拟下一次轮询返回：`code = "NEW222"`，`deviceCount = 1`
3. 断言浮窗被关闭
4. 断言不会再次立即显示新浮窗
5. 断言 `overlayDismissedByUser == false`

这个测试在当前实现下应失败，因为现逻辑会命中 `code changed` 分支并继续显示浮窗。

#### Red 2

测试名建议：
- `testNewCodeShowsOverlayWhenDeviceCountDidNotIncrease`

步骤：
1. 初始状态为无新增配对设备
2. 模拟 `code` 从旧值切到新值，`deviceCount` 不变
3. 断言浮窗被重新显示/更新

用于保证修复不会误伤正常的 code 轮换展示。

#### Red 3

测试名建议：
- `testManualDismissSuppressesReshowForSameCode`

步骤：
1. 显示某个 code 的浮窗
2. 触发用户手动关闭
3. 再次轮询到同一个 code
4. 断言不重新显示

用于锁住现有“用户关闭后同 code 不再弹出”的行为。

#### Red 4

测试名建议：
- `testAutoDismissDoesNotBlockFutureOverlayForNextCode`

步骤：
1. 先触发一次自动关闭
2. 再模拟后续新一轮未配对请求带来另一个新 code，`deviceCount` 不变
3. 断言浮窗可以正常再次显示

这个测试用来防止把自动关闭错误地标成 `overlayDismissedByUser = true`。

### 具体实现建议

`StatusBarController` 内建议抽一个小状态机，避免继续把逻辑堆在 `URLSession` 回调里。

可接受结构：

```swift
private func applyPolledPairCode(code: String, lanIPs: [String], deviceCount: Int) {
    lastObservedDeviceCount = deviceCount

    if code.isEmpty {
        ...
        return
    }

    if shouldAutoDismissOverlay(for: deviceCount) {
        dismissOverlayAfterSuccessfulPair(code: code, lanIPs: lanIPs, deviceCount: deviceCount)
        return
    }

    if code != lastPolledCode {
        ...
        showOverlay(...)
        return
    }

    if !overlayDismissedByUser {
        showOverlay(...)
    }
}
```

辅助方法建议：
- `shouldAutoDismissOverlay(for deviceCount: Int) -> Bool`
- `dismissOverlayAfterSuccessfulPair(code:lanIPs:deviceCount:)`
- `handleNewPairCode(code:lanIPs:deviceCount:)`

这样别的 agent 改起来更安全，测试也能直接对方法打点。

### 验证步骤

实现完成后，至少做以下验证：

1. 运行新增的 macOS 单测，确认上述 4 个状态机测试通过
2. 运行现有 `StatusBarControllerPairCodeTests` 和 QR 相关测试，确认无回归
3. 真机联调：
   在 macOS 打开 QR 浮窗
   Android 完成一次成功配对
   确认当前浮窗立即关闭
   再触发下一次未配对请求，确认新 code 的浮窗还能再次出现

### 不建议的修法

- 不要依赖延迟几秒后再关闭窗口
- 不要把 server 改成“成功后暂不生成新 code”
- 不要把 `overlayDismissedByUser` 同时表示“用户关闭”和“自动关闭”
- 不要继续把“deviceCount 增长”判断放在 `code unchanged` 分支内
