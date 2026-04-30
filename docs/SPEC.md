# IINA Remote — 完整项目规范

## 1. 项目概述

**项目名称：** IINA Remote  
**目标：** 从 Android 手机远程控制 Mac 上的 IINA 播放器，实现完整的播放控制、字幕/音轨切换、文件浏览、局域网自动发现和配对验证。

**最终用户体验：**
- 手机和 Mac 在同一局域网下，手机自动发现 Mac 上的 IINA Remote 服务
- 首次连接需输入 Mac 端显示的配对码
- 配对后手机成为 IINA 的遥控器，支持所有核心播放功能

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    ANDROID APP                          │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  MainCtrl │  │  PlaylistView │  │  Sub/AudioView  │  │
│  └──────────┘  └──────────────┘  └─────────────────┘  │
│                         │                               │
│              ┌──────────┴──────────┐                    │
│              │   IinaApiClient    │                    │
│              └──────────┬──────────┘                    │
│                         │                               │
│              ┌──────────┴──────────┐                    │
│              │  NsdServiceManager │  ← Bonjour 发现     │
│              └───────────────────┘                    │
└─────────────────────────────┬───────────────────────────┘
                              │ HTTP + Bonjour/mDNS
┌─────────────────────────────┴───────────────────────────┐
│                   macOS MENU BAR APP                     │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────┐  │
│  │  IINAPairingApp │  │  HTTPServer    │  │  Tray   │  │
│  │  (配对验证)      │  │  (Python/Go)   │  │  Menu   │  │
│  └────────────────┘  └────────────────┘  └──────────┘  │
│         │                    │                   │      │
│         └────────────────────┴───────────────────┘      │
│                         │                               │
│                    NSWorkspace                          │
│                         │                               │
│                    IINA Player                         │
└─────────────────────────────────────────────────────────┘
```

**组件说明：**

| 组件 | 技术 | 职责 |
|------|------|------|
| macOS Menu Bar App | Swift + AppKit | 服务管理、配对验证、通知、托盘菜单 |
| HTTP Server | Go（嵌入式） | 接收控制命令、操作 IINA（AppleScript） |
| Android App | Kotlin + Jetpack Compose | 遥控器界面 |
| Bonjour/mDNS | macOS NSD + Android NsdManager | 局域网自动发现 |

---

## 3. macOS Menu Bar App 详细设计

### 3.1 技术方案

- **语言：** Swift 5.9+
- **框架：** AppKit（NSStatusBar、NSMenu、NSUserNotification）
- **HTTP Server：** Go 嵌入式服务器（gorilla/mux），编译进 bundle
- **IINA 启动：** 使用 `NSWorkspace.shared.openApplication(at:configuration:)`，不走路径直译，因此 IINA 升级后不受影响
- **通知气泡：** `NSUserNotificationCenter` 或 `UNUserNotificationCenter`，可在 IINA 全屏时弹出
- **打包：** XcodeGen 生成 `.xcodeproj`，构建为 `.app` 放在 `/Applications`

### 3.2 托盘菜单结构

```
┌─────────────────────────────┐
│ 🟢 IINA Remote  运行中      │
├─────────────────────────────┤
│ 服务器状态：已启动           │
│ 配对码：随机 2 位数字        │
├─────────────────────────────┤
│ 📁 可见目录...          →   │  → 子菜单列出配置的目录，可勾选
│ ⚙️ 设置...                  │  → 弹出设置窗口
│ 📊 状态详情                  │  → 弹出状态窗口（连接数、当前播放等）
├─────────────────────────────┤
│ ❌ 退出                      │
└─────────────────────────────┘
```

### 3.3 配对流程

1. Menu Bar App 启动时生成随机 2 位数字配对码（如 "47"）
2. Android App 通过 Bonjour 发现服务，尝试连接 HTTP 端口
3. HTTP Server 发现客户端未配对，返回 HTTP 401 + 配对挑战 `{challenge: "pair_required", server_code: "47"}`
4. Android App 弹出输入框让用户输入 "47"
5. Android App 用 `{challenge: "pair", code: "47", device_name: "Altair的Pixel"}` 再次请求
6. Server 验证配对码，验证通过后返回配对令牌（JWT），有效期 7 天
7. 后续请求携带 Bearer Token

### 3.4 通知气泡（配对码显示）

使用 `UNUserNotificationCenter`：
- 当 Android 首次连接时（即使未配对），macOS 弹出通知
- 标题：`IINA Remote 连接请求`
- 内容：`设备 "Altair的Pixel" 请求连接，配对码：XX`
- 声音：默认
- 即使 IINA 全屏，通知也能弹出（通过 Notification Center）

### 3.5 设置窗口

- **可见目录配置：** 添加/删除允许浏览的文件夹路径（`NSOpenPanel` 选择）
- **端口配置：** 默认 8765，可修改
- **配对码有效期：** 配对码刷新间隔（默认 60 秒）
- **开机启动：** 写入 `~/Library/LaunchAgents`
- **配对设备管理：** 列出已配对设备，可撤销

---

## 4. HTTP API 设计

### 4.1 Base URL
`http://<mac-ip>:<port>/api/v1/`

### 4.2 Authentication

**首次连接（未配对）：**
```
POST /api/v1/pair
Body: {"code": "47", "device_name": "Altair的Pixel"}
Response 200: {"token": "<jwt>", "expires_in": 604800}
Response 401: {"error": "invalid_code"}
```

**已配对设备：**
```
Header: Authorization: Bearer <token>
```

### 4.3 Endpoints

| 方法 | 路径 | 说明 | 需认证 |
|------|------|------|--------|
| GET | `/status` | 播放状态 + 轨道列表 + 播放列表 + 目录 | ✅ |
| GET | `/audio` | 音轨列表 | ✅ |
| GET | `/subtitle` | 字幕列表 | ✅ |
| POST | `/switch/audio/{id}` | 切换音轨 | ✅ |
| POST | `/switch/subtitle/{id}` | 切换字幕 | ✅ |
| POST | `/cycle/audio` | 循环切换音轨 | ✅ |
| POST | `/cycle/subtitle` | 循环切换字幕 | ✅ |
| POST | `/subtitle/zoom/in` | 字幕放大 | ✅ |
| POST | `/subtitle/zoom/out` | 字幕缩小 | ✅ |
| POST | `/playback/play` | 播放 | ✅ |
| POST | `/playback/pause` | 暂停 | ✅ |
| POST | `/playback/seek` | 跳转到指定时间（body: `{position: 125.5}`） | ✅ |
| POST | `/playback/skip` | 前进/后退秒数（body: `{seconds: 10}`，正数前进负数后退） | ✅ |
| POST | `/playback/speed` | 设置播放速度（body: `{speed: 1.5}`） | ✅ |
| POST | `/playback/volume` | 设置音量（body: `{volume: 0.8}`，0.0~1.0） | ✅ |
| POST | `/playback/prev` | 上一个视频 | ✅ |
| POST | `/playback/next` | 下一个视频 | ✅ |
| GET | `/playlist` | 当前播放列表 | ✅ |
| POST | `/playlist/jump/{index}` | 跳转到列表中第 N 个 | ✅ |
| GET | `/browse?path=/Volumes/Video` | 浏览目录，返回文件列表 | ✅ |
| POST | `/open?path=/Volumes/Video/Movie.mkv` | 在 IINA 中打开指定文件 | ✅ |
| GET | `/pair/challenge` | 获取当前配对挑战信息（返回 server_code） | ❌ |
| GET | `/health` | 服务健康检查 | ❌ |

### 4.4 Status Response

```json
{
  "playing": true,
  "position": 125.5,
  "duration": 3600.0,
  "speed": 1.0,
  "volume": 0.8,
  "subtitle_zoom": 100,
  "audio_tracks": [{"id": "1", "label": "English aac", "is_default": true}],
  "subtitle_tracks": [{"id": "2", "label": "Michiko and Hatchin - 14.ass", "is_default": false}],
  "current_file": "/Volumes/Video/Movie.mkv",
  "playlist": [
    {"index": 0, "name": "Movie.mkv", "path": "/Volumes/Video/Movie.mkv"},
    {"index": 1, "name": "S02E01.mkv", "path": "/Volumes/Video/S02E01.mkv"}
  ]
}
```

### 4.5 Browse Response

```json
{
  "path": "/Volumes/Video",
  "parent": "/Volumes",
  "entries": [
    {"name": "Movie.mkv", "type": "video", "size": 1500000000},
    {"name": "Subtitles", "type": "directory", "size": 0},
    {"name": "cover.jpg", "type": "image", "size": 300000}
  ]
}
```

---

## 5. Android App 完整 UI 设计

### 5.1 屏幕结构

```
App
├── 配对引导页     (/pair)
├── 主控界面       (/main)
│   ├── 主播放控制页  (PlaybackFragment)
│   ├── 播放列表页    (PlaylistFragment)
│   └── 副控制页      (SubAudioFragment) ← 字幕/音轨 Tab
└── 目录浏览页     (/browse)
```

### 5.2 主题与配色

- **主色：** `#1A73E8`（Google Blue）
- **深色主题：** 背景 `#121212`，表面 `#1E1E1E`
- **浅色主题：** 背景 `#FAFAFA`，表面 `#FFFFFF`
- **强调色：** `#34A853`（播放中）、`#EA4335`（暂停/错误）

### 5.3 主控界面（PlaybackFragment）

```
┌──────────────────────────────────────────────┐
│ ← 已连接 MacBook Pro           [≡] [⚙]       │  ← 顶栏：状态 + 菜单
├──────────────────────────────────────────────┤
│                                              │
│            Movie.mkv - 正在播放               │  ← 当前文件名
│            ████████░░░░░░  00:02:05 / 01:00:00 │  ← 进度条 + 时间
│                                              │
│  ┌────┐  ◀◀  ▶/⏸  ▶▶  ┌────┐  🔊━━━━  │
│  │ 1x │  -10s   ▶   +10s │2x  │  音量     │  ← 控制行
│  └────┘                └────┘             │
│                                              │
│  ┌──────────────────┐ ┌──────────────────┐  │
│  │     ⬆ 字幕放大     │ │     ⬇ 字幕缩小   │  │  ← 字幕缩放
│  └──────────────────┘ └──────────────────┘  │
│                                              │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐       │
│  │ ⏮  │ │ ⏭  │ │ 📋 │ │ 🎵 │ │ 🁢 │       │  ← 底部快捷
│  │上一 │ │下一 │ │列表 │ │字幕│ │音频│       │
│  └────┘ └────┘ └────┘ └────┘ └────┘       │
└──────────────────────────────────────────────┘
```

**布局说明：**
- **顶栏：** 设备名 + 连接状态指示点 + 菜单按钮（目录浏览、设置）
- **进度条：** 可拖动seek，拖动时显示目标时间 tooltip
- **播放按钮：** 中央大按钮（64dp），点击切换播放/暂停
- **▶▶ +10s / ◀◀ -10s：** 前进/后退按钮
- **速度按钮：** 显示当前速度，点击弹出速度选择器（0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x）
- **音量滑块：** 右侧垂直滑块或水平滑块
- **字幕缩放按钮：** 两个独立按钮，单次点击 ± 一个步进（默认 10%）
- **底部快捷栏：** 5 个图标按钮，切换不同 Fragment

### 5.4 副控制页（SubAudioFragment）

Tab 切换：**字幕** | **音轨**

```
┌──────────────────────────────────────────────┐
│  字幕  │  音轨                               │  ← TabRow
├──────────────────────────────────────────────┤
│ ┌────────────────────────────────────────┐  │
│ │  ●  [默认] hdmv_pgs_subtitle          │  │  ← 当前选中（高亮）
│ └────────────────────────────────────────┘  │
│ ┌────────────────────────────────────────┐  │
│ │     Michiko and Hatchin - 14.ass      │  │
│ └────────────────────────────────────────┘  │
│ ┌────────────────────────────────────────┐  │
│ │     <无> (关闭字幕)                     │  │
│ └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

- 当前选中项左侧有实心圆点 + 高亮背景
- 默认轨有 `[默认]` 标签
- 点击即切换，带 loading 状态

### 5.5 播放列表页（PlaylistFragment）

```
┌──────────────────────────────────────────────┐
│  播放列表                            [刷新]   │
├──────────────────────────────────────────────┤
│ ▶ 1. Movie.mkv          [正在播放]           │  ← 高亮行
├──────────────────────────────────────────────┤
│   2. S02E01.mkv                             │
├──────────────────────────────────────────────┤
│   3. S02E02.mkv                             │
└──────────────────────────────────────────────┘
```

- 当前播放项高亮显示
- 点击即跳转播放
- 支持下拉刷新

### 5.6 目录浏览页（BrowseActivity）

```
┌──────────────────────────────────────────────┐
│  ← /Volumes/Video                 [打开目录] │  ← 顶栏 + 路径面包屑
├──────────────────────────────────────────────┤
│  📁 Subtitles/                              │  ← 目录（蓝色）
├──────────────────────────────────────────────┤
│  📹 Movie.mkv           1.4 GB             │  ← 视频文件
├──────────────────────────────────────────────┤
│  🖼 cover.jpg              300 KB            │  ← 图片
└──────────────────────────────────────────────┘
```

- 点击目录进入
- 点击视频文件 → 发送到 IINA 播放
- 路径面包屑可点击跳转
- `打开目录` 按钮：调用系统文件选择器快速添加可见目录

### 5.7 配对引导页（PairActivity）

```
┌──────────────────────────────────────────────┐
│                                              │
│              🎬 IINA Remote                   │
│                                              │
│     在 Mac 上的 IINA Remote 菜单栏            │
│     应用中查看配对码，然后在下方输入：          │
│                                              │
│           ┌───┐ ┌───┐                       │
│           │ 4 │ │ 7 │   ← 大字输入框          │
│           └───┘ └───┘                       │
│                                              │
│           [ 连接 ]                           │
│                                              │
└──────────────────────────────────────────────┘
```

- 两个大方框输入两位数字
- 自动聚焦下一个
- 底部显示"在 Mac 上查看配对码"提示

### 5.8 导航结构

底部 TabBar + 每个 Tab 内 Fragment 切换：

```
BottomNavigationBar
├── 播放控制  (PlaybackFragment)     — 主界面
├── 播放列表  (PlaylistFragment)     — 当前队列
├── 字幕/音频  (SubAudioFragment)    — 轨道切换
└── 浏览     (BrowseActivity)       — 文件浏览
```

---

## 6. Bonjour/mDNS 自动发现设计

### 6.1 服务端广播（macOS App）

```swift
// Service type: _iinaremote._tcp
// TXT record: {"version": "1.0", "name": "MacBook Pro", "port": "8765"}
NSDictionary *txtRecord = @{
    @"version": @"1.0",
    @"name": [[NSHost currentHost] localizedName],
    @"port": @(port)
};
// 发布服务
```

### 6.2 客户端发现（Android）

```kotlin
val nsdManager = getSystemService(Context.NSD_SERVICE)
nsdManager.discoverServices("_iinaremote._tcp", NsdManager.PROTOCOL_DNS_SD, discoveryListener)
```

发现服务后提取 TXT record 中的 `name`（显示设备名）和 `port`。

---

## 7. 数据持久化

### 7.1 Android 端（DataStore）

```kotlin
// 配对令牌
pairedToken: String

// 已配对设备列表（serverId -> deviceName）
pairedDevices: Map<String, String>

// 最近连接的服务器信息
lastServer: {host: String, port: Int, name: String}

// 可视目录配置
visiblePaths: List<String>

// 音量默认值
defaultVolume: Float
```

### 7.2 macOS 端（UserDefaults）

```swift
// 可见目录列表
visiblePaths: [String]

// 端口
serverPort: Int

// 配对设备列表（deviceToken -> deviceInfo）
pairedDevices: [String: DeviceInfo]

// 配对码
currentPairCode: String

// 配对码生成时间
pairCodeGeneratedAt: Date

// 开机启动
launchAtLogin: Bool
```

---

## 8. 项目模块划分

```
iina-remote/                      ← 父目录（文档）
└── SPEC.md                      ← 完整项目规范文档

iina-remote-android/             ← Android App 独立仓库
├── app/src/main/java/com/iina/remote/
│   ├── data/
│   │   ├── api/                # Retrofit HTTP client
│   │   └── model/              # Track, StatusResponse, etc.
│   ├── domain/                 # IinaRepository (business logic)
│   ├── ui/
│   │   ├── components/         # TrackListItem, ConnectionBar
│   │   ├── screens/            # MainScreen, MainViewModel
│   │   └── theme/             # Compose theme
│   └── MainActivity.kt
└── build.gradle.kts

iina-remote-macos/               ← macOS App 独立仓库
├── IINARemote/
│   ├── App/
│   │   ├── main.swift          # 入口点
│   │   ├── AppDelegate.swift   # 应用生命周期
│   │   └── StatusBarController.swift  # 托盘菜单控制
│   ├── Server/
│   │   ├── HTTPServerManager.swift    # Go 服务进程管理
│   │   ├── PairingManager.swift       # 配对验证
│   │   └── SettingsManager.swift      # UserDefaults 持久化
│   ├── Resources/
│   │   └── Info.plist
│   └── Assets.xcassets/
├── project.yml                 # XcodeGen 配置
└── IINARemote.xcodeproj        # 生成的项目文件

iina-remote-server/              ← Go HTTP Server 独立仓库（待建）
├── main.go                     # HTTP 入口
├── handler/                    # 请求处理器
│   ├── playback.go             # 播放控制
│   ├── subtitle.go             # 字幕/音轨
│   ├── playlist.go             # 播放列表
│   └── browse.go               # 目录浏览
├── iina/                       # IINA AppleScript 封装
├── auth/                       # JWT 配对验证
└── bonjour/                    # mDNS 广播
```

---

## 9. 实现优先级

### Phase 1：核心通信（不依赖 UI）
1. macOS Menu Bar App 基础框架 + HTTP Server
2. 配对验证流程
3. 基础播放控制 API（播放/暂停/进度）
4. Android App 骨架 + 配对页面

### Phase 2：完整播放控制
5. 所有播放控制 API（seek/skip/speed/volume/prev/next）
6. Android 主控界面
7. 字幕/音轨 API + Android 副控制页

### Phase 3：文件与播放列表
8. 目录浏览 API + macOS 可见目录配置
9. 播放列表 API
10. Android 播放列表页
11. Android 目录浏览页

### Phase 4：发现与完善
12. Bonjour/mDNS 自动发现
13. 开机启动配置
14. 配对设备管理 UI
15. 设置页面

---

## 10. 技术风险与应对

| 风险 | 应对 |
|------|------|
| IINA AppleScript 不稳定 | AppleScript 失败时返回友好错误，菜单操作加超时保护 |
| IINA 全屏时通知被遮挡 | 使用 `UNUserNotificationCenter` 的 `alert` 类型，走系统 Notification Center |
| IINA 升级后路径失效 | 用 `NSWorkspace` 启动而非路径直译 |
| 局域网发现跨网段 | 要求手机和 Mac 在同一网段，startTLS 不支持则降级 |
| 配对码暴力破解 | 60 秒刷新 + 3 次错误锁定 30 秒 |
| Go HTTP Server 内存占用 | 嵌入式 Go 编译为单一二进制，内存 ~10MB |
