# Server 架构重构执行方案

**文档日期**: 2026-05-11
**状态**: ✅ 已完成
**完成日期**: 2026-05-11
**合并提交**: `6b8c696` (server), `a0e5aec` (parent)

---

## 执行结果

### 重构前 (master @ cffa0cc)
```
server/iina/
├── applescript.go    # 1710行，混合所有功能 ❌
├── ipc_test.go
└── applescript_test.go
```

### 重构后 (master @ 6b8c696)
```
server/iina/
├── applescript.go    # 494行，AppleScript 执行核心 ✅
├── ipc.go            # 347行，IPC 通信核心 ✅
├── playback.go       # 548行，播放控制函数 ✅
├── status.go         # 166行，状态查询函数 ✅
├── types.go          # 85行，类型定义 ✅
├── ipc_test.go
└── applescript_test.go
```

### 代码行数变化
| 文件 | 重构前 | 重构后 | 变化 |
|------|--------|--------|------|
| applescript.go | 1710 | 494 | -1216 行 |
| ipc.go | 0 | 347 | +347 行 |
| playback.go | 0 | 548 | +548 行 |
| status.go | 0 | 166 | +166 行 |
| types.go | 0 | 85 | +85 行 |
| **总计** | 1710 | 1640 | -70 行 |

---

## 附带修复

本次重构合并时同时修复了两个 bug：

1. **SeekTo()** - 使用 `seek` 命令替代 `set_property time-pos`（只读属性）
2. **Seek()** - 移除 300 秒跳转限制

---

## 一、当前问题分析

### 1.1 文件现状

```
server/iina/
├── applescript.go    # 1710行，混合所有功能 ❌
├── ipc_test.go
└── applescript_test.go
```

**应有但缺失的文件**:
- `ipc.go` - IPC 通信核心
- `playback.go` - 播放控制函数
- `status.go` - 状态查询函数
- `types.go` - 类型定义
- `constants.go` - Key code 常量

### 1.2 代码分布统计

| 类别 | 函数数量 | 当前位置 | 应在位置 |
|------|---------|---------|---------|
| IPC-only 函数 | 13 | applescript.go | ipc.go / playback.go |
| IPC+AppleScript fallback | 27 | applescript.go | playback.go |
| 纯 AppleScript 函数 | 3 | applescript.go | applescript.go (正确) |
| IPC 协议类型 | 2 | applescript.go | ipc.go |
| 业务类型定义 | 7 | applescript.go | types.go |
| Key code 常量 | 13 | applescript.go | constants.go |

---

## 二、重构目标文件结构

```
server/iina/
├── applescript.go      # AppleScript 执行 + 菜单操作 (~300行)
├── ipc.go              # IPC 通信核心 (~300行)
├── playback.go         # 播放控制函数 (~500行)
├── status.go           # 状态查询函数 (~300行)
├── types.go            # 所有类型定义 (~200行)
├── constants.go        # Key code 常量 (~50行)
├── volume.go           # 系统音量函数 (~50行)
├── browse.go           # 文件浏览类型和函数 (~100行)
├── util.go             # 共享工具函数 (~100行)
├── ipc_test.go
└── applescript_test.go
```

---

## 三、分阶段执行方案

### Phase 1: 创建新文件骨架 (基础文件)

**目标**: 创建空文件结构，定义类型和常量

#### Step 1.1: 创建 `constants.go`
```go
package iina

const (
    keySpace    = 49
    keyLeft     = 123
    keyRight    = 124
    keyDown     = 125
    keyUp       = 126
    keyDelete   = 51
    keyReturn   = 36
    keyM        = 46
    keyS        = 31
    keyF        = 3
    keyT        = 17
    keyPageUp   = 116
    keyPageDown = 121
)
```

#### Step 1.2: 创建 `types.go`
迁移以下类型：
- `Status`
- `Track`
- `Chapter`
- `FullStatus`
- `BrowseEntry`
- `BrowseResult`
- `PlaylistEntry`

#### Step 1.3: 创建 `ipc.go`
```go
package iina

// ipcCommand, ipcResponse 类型
// ipcSend() 函数
// IsIPCAvailable() 函数
// getStatusViaIPC()
// getTracksViaIPC()
// getChaptersViaIPC()
// getPlaylistViaIPC()
```

#### Step 1.4: 创建 `volume.go`
迁移系统音量函数：
- `SetSystemVolume()`
- `GetSystemVolume()`
- `getVolumeViaAppleScript()`

#### Step 1.5: 创建 `util.go`
迁移共享工具：
- `escapeAppleScriptString()`
- `toFloat64()`
- `getFileDuration()`

---

### Phase 2: 创建 `playback.go` (播放控制)

**目标**: 迁移所有播放控制函数到独立文件

#### Step 2.1: 迁移 IPC-only 函数
| 函数 | IPC 命令 |
|------|---------|
| `SeekTo()` | `seek <seconds> absolute` |
| `SetVolume()` | `set_property volume` |
| `SetSpeed()` | `set_property speed` |
| `JumpToPlaylistItem()` | `playlist-play-index` |
| `GetChapters()` | `get_property chapter-list` |
| `ChapterJump()` | `set_property chapter` |
| `SetABLoopA()` | `set_property ab-loop-a` |
| `SetABLoopB()` | `set_property ab-loop-b` |
| `ClearABLoop()` | `set_property ab-loop-a/b "no"` |
| `SetAspectRatio()` | `set_property video-aspect-override` |
| `GetAudioDelay()` | `get_property audio-delay` |
| `SetAudioDelay()` | `add audio-delay` |

#### Step 2.2: 迁移 IPC+fallback 函数
| 函数 | IPC 命令 | Fallback |
|------|---------|---------|
| `TogglePlay()` | `get/set pause` | keySpace |
| `Play()` | `set pause false` | keySpace |
| `Pause()` | `set pause true` | keySpace |
| `Seek()` | `add time-pos` | Left/Right keys |
| `PrevTrack()` | `playlist-prev` | Shift+comma |
| `NextTrack()` | `playlist-next` | Shift+period |
| `ToggleMute()` | `get/set mute` | keyM |
| `GetFullscreen()` | `get fullscreen` | - |
| `WindowFullscreen()` | `cycle fullscreen` | keyF |
| `ChapterNext()` | `add chapter 1` | keyPageUp |
| `ChapterPrev()` | `add chapter -1` | keyPageDown |
| `AspectRatio()` | `cycle video-aspect` | Shift+A |

#### Step 2.3: 迁移 track/schedule 相关
| 函数 | IPC 命令 |
|------|---------|
| `GetAudioTracks()` | `getTracksViaIPC` |
| `GetSubtitleTracks()` | `getTracksViaIPC` |
| `SwitchAudio()` | `set aid` |
| `SwitchSubtitle()` | `set sid` |
| `CycleAudio()` | `cycle audio` |
| `CycleSubtitle()` | `cycle sub` |

#### Step 2.4: 迁移字幕/音量控制
| 函数 | IPC 命令 |
|------|---------|
| `SubtitleZoomIn()` | `get/set sub-scale` |
| `SubtitleZoomOut()` | `get/set sub-scale` |
| `SubtitleSetScale()` | `set sub-scale` |
| `SubtitleZoomGet()` | `get sub-scale` |
| `GetSubtitleDelay()` | `get sub-delay` |
| `SetSubtitleDelay()` | `add sub-delay` |
| `GetStatus()` | 多 property 查询 |
| `GetFullStatus()` | `GetStatus` + tracks |
| `OpenFile()` | `loadfile` |

---

### Phase 3: 创建 `status.go` (状态查询)

**目标**: 迁移所有状态查询相关函数

迁移函数：
- `GetStatus()`
- `GetFullStatus()`
- `GetPlaylist()`
- `GetChapters()`
- `GetABLoop()`

---

### Phase 4: 创建 `browse.go` (文件浏览)

**目标**: 迁移文件浏览相关类型和函数

迁移类型：
- `BrowseEntry`
- `BrowseResult`

---

### Phase 5: 精简 `applescript.go`

**目标**: `applescript.go` 只保留 AppleScript 核心功能

**保留内容**:
1. `execAppleScript()`
2. `execAppleScriptMulti()`
3. `sendKey()`
4. `sendKeyWithModifier()`
5. `openFileScript()`
6. 菜单操作函数（`getMenuItems`, `clickMenuItem`, 等）
7. 菜单解析函数（`parseAudioMenuItems`, `parseSubtitleMenuItems`, 等）
8. AppleScript 列表解析（`parseAppleScriptList`, `reorderOffFirst`）
9. IINA 状态检查（`isIINARunning`, `isIINAPlayerWindowOpen`）
10. 初始化函数（`EnsureIINARunning`）

**目标行数**: ~400 行

---

### Phase 6: 修复 Handler 层问题

#### Step 6.1: 修复 `handler/iina.go`
问题：`RestartIINA` 直接调用 `exec.Command("osascript")`，绕过了 iina 包

修复：创建 `iina.RestartIINA()` 函数，在 handler 中调用

#### Step 6.2: 消除重复验证
问题：`handler/playback.go` 和 `iina/applescript.go` 都有 speed/volume 边界检查

修复：
- Handler 只做 HTTP 层验证（如 JSON schema）
- iina 包函数做业务逻辑验证
- 删除 handler 中的重复验证

#### Step 6.3: 迁移初始化逻辑
问题：`handler/browse.go` 中的 `LoadVisiblePathsFromSettings()` 是初始化逻辑

修复：迁移到 `main.go` 或新建 `config.go`

---

## 四、详细执行步骤

### Step 1: 创建 `constants.go`
```bash
# 创建文件
touch server/iina/constants.go
```
写入内容：
- 所有 key code 常量

### Step 2: 创建 `types.go`
```bash
touch server/iina/types.go
```
写入内容：
- `Status`, `Track`, `Chapter`, `FullStatus`
- `BrowseEntry`, `BrowseResult`, `PlaylistEntry`

### Step 3: 创建 `ipc.go`
```bash
touch server/iina/ipc.go
```
写入内容：
- `ipcCommand`, `ipcResponse` 结构体
- `ipcSend()` 函数
- `IsIPCAvailable()` 函数
- `getStatusViaIPC()`, `getTracksViaIPC()`, `getChaptersViaIPC()`, `getPlaylistViaIPC()`

### Step 4: 创建 `volume.go`
```bash
touch server/iina/volume.go
```
写入内容：
- `SetSystemVolume()`, `GetSystemVolume()`
- `getVolumeViaAppleScript()`

### Step 5: 创建 `util.go`
```bash
touch server/iina/util.go
```
写入内容：
- `escapeAppleScriptString()`
- `toFloat64()`
- `getFileDuration()`

### Step 6: 创建 `playback.go`
```bash
touch server/iina/playback.go
```
写入内容：
- 所有播放控制函数（参考 Phase 2 表格）

### Step 7: 创建 `status.go`
```bash
touch server/iina/status.go
```
写入内容：
- `GetStatus()`, `GetFullStatus()`, `GetPlaylist()`, `GetChapters()`, `GetABLoop()`

### Step 8: 创建 `browse.go`
```bash
touch server/iina/browse.go
```
写入内容：
- `BrowseEntry`, `BrowseResult` 类型
- 文件浏览相关函数

### Step 9: 精简 `applescript.go`
保留内容：
- AppleScript 执行：`execAppleScript()`, `execAppleScriptMulti()`
- Key 发送：`sendKey()`, `sendKeyWithModifier()`
- 菜单操作：所有 `getMenu*`, `clickMenu*`, `parse*` 函数
- 初始化：`EnsureIINARunning()`, `isIINARunning()`, `isIINAPlayerWindowOpen()`
- `openFileScript()`

删除内容：
- 所有已迁移的类型、函数、常量

### Step 10: 修复 Handler 层
修改文件：
- `handler/iina.go`: 添加 `iina.RestartIINA()` 并在 handler 中调用
- `handler/playback.go`: 删除重复的边界检查
- `handler/browse.go`: 迁移 `LoadVisiblePathsFromSettings()` 到 `main.go`

### Step 11: 构建验证
```bash
cd server && go build ./...
```

### Step 12: 测试验证
```bash
cd server && go test ./...
```

---

## 五、风险控制

### 5.1 回滚策略
每完成一个 Phase 创建 Git 提交，便于回滚：
```bash
git add -A && git commit -m "refactor: Phase X - <description>"
```

### 5.2 依赖检查
重构时确保：
1. 外部调用者（handler）不需要修改接口
2. 函数签名保持一致
3. 只移动代码，不改变逻辑

### 5.3 验证清单
- [ ] `go build ./...` 成功
- [ ] `go test ./...` 通过
- [ ] `applescript.go` < 500 行
- [ ] 新文件全部存在：`ipc.go`, `playback.go`, `status.go`, `types.go`, `constants.go`, `volume.go`, `util.go`, `browse.go`

---

## 六、预估工时

| Phase | 任务 | 复杂度 | 预估时间 |
|-------|------|--------|---------|
| Phase 1 | 创建骨架文件 | 低 | 30 分钟 |
| Phase 2 | 创建 playback.go | 高 | 2 小时 |
| Phase 3 | 创建 status.go | 中 | 1 小时 |
| Phase 4 | 创建 browse.go | 低 | 30 分钟 |
| Phase 5 | 精简 applescript.go | 高 | 2 小时 |
| Phase 6 | 修复 Handler 层 | 中 | 1 小时 |
| Phase 7 | 验证测试 | 中 | 30 分钟 |
| **总计** | | | **7.5 小时** |

---

## 七、注意事项

1. **保持函数签名不变**: 外部调用者（handler）依赖现有函数签名
2. **不改变业务逻辑**: 只移动代码，不修改实现
3. **注释保留**: 迁移时保留所有有价值的注释
4. **测试覆盖**: 确保重构后测试仍能通过
5. **分步提交**: 每完成一个 Phase 提交一次，便于审查和回滚

---

## 八、验证检查点

### 重构完成标准
- [ ] `go build ./...` 成功
- [ ] `go test ./...` 通过
- [ ] `iina/applescript.go` 行数 < 500
- [ ] 新文件结构符合目标

### 代码质量
- [ ] 无循环依赖
- [ ] 包内聚合度提高
- [ ] AppleScript 代码与 IPC 代码完全分离
- [ ] Handler 只做 HTTP 包装，不含业务逻辑
