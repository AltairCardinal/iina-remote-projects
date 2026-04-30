# IINA Remote — Implementation Plan

## 当前状态 (2026-04-10)

### 已完成
- ✅ Go 服务端基础框架 (main.go, handler/)
- ✅ 播放控制 API (play/pause/seek/skip/speed/volume/prev/next)
- ✅ 字幕/音频轨道切换 API
- ✅ 字幕缩放 API
- ✅ 播放列表 API
- ✅ 文件浏览 API
- ✅ 配对认证系统
- ✅ Python 服务端播放控制增强 (iina_remote.py)
- ✅ P0 服务端全部 API (Mute/章节/AB循环/画面比例/截图/全屏置顶) - 2026-04-10
- ✅ Android 端缺失功能调研 (章节/AB循环/画面比例/延迟控制)

## 待完成任务

### P0 - 服务端缺失 API (必须实现)

#### 1. Mute API ✅ (2026-04-10)
- `POST /playback/mute` - 静音切换
- 实现：CGEvent 'm' 或 AppleScript 菜单

#### 2. 章节 API ✅ (2026-04-10)
- `GET /api/v1/chapters` - 获取章节列表
- `POST /api/v1/chapter/:index` - 跳转到指定章节
- `POST /api/v1/chapter/next` - 下一章
- `POST /api/v1/chapter/prev` - 上一章
- 注意：CONTROL_METHODS.md 显示 IINA 支持章节菜单但 IPC 无法获取章节列表

#### 3. AB 循环 API ⬜
- `GET /api/v1/playback/loop/ab` - 获取 A/B 循环状态
- `POST /api/v1/playback/loop/ab` - 设置/清除 A/B 点
- 注意：mpv IPC 无直接 A-B 循环命令，需通过 OSD 显示状态

#### 4. 画面比例 API ✅ (2026-04-10)
- `GET /api/v1/video/aspect` - 获取当前画面比例
- `POST /api/v1/video/aspect` - 设置画面比例
- 实现：CGEvent 'A' 循环切换

#### 5. 截图 API ✅ (2026-04-10)
- `POST /api/v1/screenshot` - 截图
- 实现：CGEvent 's'

#### 6. 全屏/置顶 API ✅ (2026-04-10)
- `POST /api/v1/window/fullscreen` - 全屏切换
- `POST /api/v1/window/ontop` - 窗口置顶

### P1 - Android 端实现

#### 1. 章节面板 ⬜
- 新增 ChaptersSheet BottomSheet
- 对接 GET /api/v1/chapters
- 显示当前章节和章节列表

#### 2. AB 循环 UI ⬜
- ControlRow 新增 A/B 按钮
- 新增 ABLoopSheet
- 对接 /playback/loop/ab API

#### 3. 画面比例选择 ⬜
- 新增 AspectSheet
- 对接 /video/aspect API

#### 4. 音频/字幕延迟 ⬜
- SubAudioScreen 新增延迟控制行
- 对接 /audio/delay 和 /subtitle/delay API

#### 5. Mute 按钮 ⬜
- ControlRow 新增静音按钮

### P2 - 完善功能

#### 1. 增强状态 API ⬜
- `/status` 返回 position, duration, volume, speed, muted 等完整状态
- 当前返回较简单，需要 IPC 支持

#### 2. 播放列表完整支持 ⬜
- 实现 /playlist 的完整播放列表获取

## 技术方案

### 服务端实现方式

| 功能 | 实现方式 |
|------|----------|
| 播放控制 | CGEvent (Space, ←/→, </>) |
| IPC 状态读取 | IINA HTTP IPC (localhost:8080) |
| 菜单操作 | AppleScript |
| 窗口控制 | CGEvent (f, T) |
| 字幕/音频延迟 | CGEvent (z/Z) |
| 画面比例 | CGEvent (A) |
| 截图 | CGEvent (s) |

### IPC Socket 限制

⚠️ **重要发现**：CONTROL_METHODS.md 指出：
- IPC Socket (`/tmp/iina.sock`) 需要用户重启 IINA 激活
- 部分状态（播放位置、时长、音量）只能通过 IPC 获取
- 章节列表无法通过 IPC 获取（mpv 不暴露）

### 语言兼容性

⚠️ **已知问题**：AppleScript 菜单操作使用中文菜单项（音频、字幕、回放等），在非中文系统会失败。建议增加菜单语言检测。

## 服务端新增 API 完整列表

```
# P0 新增
POST /playback/mute              静音切换
GET  /api/v1/chapters           获取章节列表
POST /api/v1/chapter/:index     跳转章节
POST /api/v1/chapter/next       下一章
POST /api/v1/chapter/prev       上一章
GET  /api/v1/playback/loop/ab   A/B 循环状态
POST /api/v1/playback/loop/ab   设置 A/B 点
GET  /api/v1/video/aspect       画面比例
POST /api/v1/video/aspect       设置画面比例
POST /api/v1/screenshot         截图
POST /api/v1/window/fullscreen  全屏
POST /api/v1/window/ontop      置顶

# P1 增强
GET  /api/v1/audio/delay       音频延迟
POST /api/v1/audio/delay       调整音频延迟
GET  /api/v1/subtitle/delay     字幕延迟
POST /api/v1/subtitle/delay     调整字幕延迟
```

## Android 端新增组件

```
P0:
- ChapterSheet.kt       章节面板
- ABLoopRow.kt          A/B 循环按钮行
- ABLoopSheet.kt        A/B 循环编辑
- MuteButton.kt         静音按钮

P1:
- AspectSheet.kt        画面比例选择
- DelayControlRow.kt    延迟控制行
```
