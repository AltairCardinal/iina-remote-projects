# IINA Remote 开发进度

## 2026-04-10 完成内容

### 服务端 (Go) - P0 API 实现

#### 新增文件
- `handler/chapter.go` - 章节相关 API
- `handler/video.go` - 画面比例 API
- `handler/window.go` - 全屏/置顶 API

#### 修改文件
- `handler/playback.go` - 新增 Mute、AB Loop API
- `handler/media.go` - 新增 Screenshot API
- `iina/applescript.go` - 新增底层函数
- `main.go` - 注册所有新路由

#### 实现详情

**1. Mute API**
- 路由: `POST /api/v1/playback/mute`
- 实现: CGEvent 发送 'm' 键切换静音

**2. 章节 API**
- `GET /api/v1/chapters` - 获取章节列表 (experimental, mpv 不暴露章节)
- `POST /api/v1/chapter/:index` - 跳转指定章节
- `POST /api/v1/chapter/next` - 下一章 (CGEvent PGUP)
- `POST /api/v1/chapter/prev` - 上一章 (CGEvent PGDWN)

**3. A-B 循环 API**
- `GET /api/v1/playback/loop/ab` - 返回 {a, b, active}
- `POST /api/v1/playback/loop/ab` - body: {action: "set_a"|"set_b"|"clear"}
- 注意: mpv 无原生 A-B 循环命令，记录状态在内存中

**4. 画面比例 API**
- `GET /api/v1/video/aspect` - 获取当前比例
- `POST /api/v1/video/aspect` - 设置比例 (CGEvent 'A' 循环)

**5. 截图 API**
- `POST /api/v1/screenshot` - 执行截图 (CGEvent 's')

**6. 窗口控制 API**
- `POST /api/v1/window/fullscreen` - 全屏切换 (CGEvent 'f')
- `POST /api/v1/window/ontop` - 窗口置顶 (CGEvent 'T')

### 编译验证
```bash
cd /Volumes/File/OpenClaw/workspace/iina-remote-server && go build -o iina-remote-server
# 输出: 9.2MB binary 编译成功
```

### 完整 API 列表 (截至 2026-04-10)

```
播放控制:
POST /api/v1/playback/play
POST /api/v1/playback/pause
POST /api/v1/playback/seek       body: {position: float}
POST /api/v1/playback/skip       body: {seconds: float}
POST /api/v1/playback/speed      body: {speed: float}
POST /api/v1/playback/volume     body: {volume: float}
POST /api/v1/playback/mute
POST /api/v1/playback/prev
POST /api/v1/playback/next
GET  /api/v1/playback/loop/ab
POST /api/v1/playback/loop/ab    body: {action: "set_a"|"set_b"|"clear"}

轨道切换:
GET  /api/v1/audio
GET  /api/v1/subtitle
POST /api/v1/switch/audio/:id
POST /api/v1/switch/subtitle/:id
POST /api/v1/cycle/audio
POST /api/v1/cycle/subtitle
POST /api/v1/subtitle/zoom/in
POST /api/v1/subtitle/zoom/out

章节:
GET  /api/v1/chapters
POST /api/v1/chapter/:index
POST /api/v1/chapter/next
POST /api/v1/chapter/prev

视频:
GET  /api/v1/video/aspect
POST /api/v1/video/aspect       body: {aspect: string}
POST /api/v1/screenshot
POST /api/v1/window/fullscreen
POST /api/v1/window/ontop

播放列表:
GET  /api/v1/playlist
POST /api/v1/playlist/jump/:index

状态:
GET  /api/v1/status
GET  /api/v1/health

配对:
GET  /api/v1/pair/challenge
POST /api/v1/pair

文件浏览:
GET  /api/v1/browse?path=xxx
POST /api/v1/open              body: {path: string}
```

## 待完成

### P0 服务端
- [x] 全部完成 ✅

### P1 Android 端
- [x] Mute 按钮 → MainScreen VolumeRow ✅
- [x] 章节面板 (ChapterSheet) ✅
- [x] AB 循环 UI (ABLoopSheet) ✅
- [x] 画面比例选择 (AspectSheet) ✅
- [x] 音频/字幕延迟控制 → SubAudioScreen ✅

#### 实现详情

**1. Mute 按钮**
- 位置: MainScreen VolumeRow，音量滑块左侧
- API: `POST /api/v1/playback/mute`
- 图标: VolumeOff (静音时) / VolumeUp (有声音时)

**2. 章节面板 ChapterSheet**
- 新建: `ui/components/ChapterSheet.kt`
- BottomSheet 模式，简洁列表: 章节名 + 时间
- API: `getChapters()`, `prevChapter()`, `nextChapter()`, `seekToChapter(index)`
- 触发: ExtraControlsRow 中的「章节」按钮

**3. A-B 循环 UI ABLoopSheet**
- 新建: `ui/components/ABLoopSheet.kt`
- 三个按钮: [设置 A] [设置 B] [清除]
- 状态显示: A/B 点时间
- API: `getABLoop()`, `setABLoopA()`, `setABLoopB()`, `clearABLoop()`
- 触发: ExtraControlsRow 中的「A-B 循环」按钮

**4. 画面比例选择 AspectSheet**
- 新建: `ui/components/AspectSheet.kt`
- 选项: 默认, 4:3, 16:9, 16:10, 1:1, 3:2, 2.21:1, 2.35:1, 2.39:1
- API: `getAspectRatio()`, `setAspectRatio(aspect)`
- 触发: ExtraControlsRow 中的「画面比例」按钮

**5. 延迟控制 → SubAudioScreen**
- 位置: SubAudioScreen 字幕Tab和音轨Tab 底部
- 四个按钮: [-0.5s] [-0.1s] [+0.1s] [+0.5s]
- API: `setAudioDelay(delta)`, `setSubtitleDelay(delta)` (delta 单位: ms)

#### 新增/修改文件
- `ui/components/ChapterSheet.kt` (新建)
- `ui/components/ABLoopSheet.kt` (新建)
- `ui/components/AspectSheet.kt` (新建)
- `ui/screens/MainScreen.kt` (修改: 添加3个按钮行 + Mute + Sheet集成)
- `ui/screens/MainViewModel.kt` (修改: 添加状态和方法)
- `ui/screens/SubAudioScreen.kt` (修改: 添加延迟控制行)
- `ui/screens/SubAudioViewModel.kt` (修改: 添加延迟方法)
- `data/api/IinaApiService.kt` (修改: 添加全部新API)
- `data/api/ApiModels.kt` (修改: 添加响应数据类)
- `domain/IinaRepository.kt` (修改: 添加全部新方法)

#### 编译验证
```bash
cd /Volumes/File/OpenClaw/workspace/iina-remote-android
./gradlew assembleDebug
# BUILD SUCCESSFUL in 32s (首次) / 6s (增量)
```

### P2 完善
- [x] IPC 状态增强 (播放位置、时长需 IPC socket)
- [x] 播放列表完整支持
- [x] 菜单语言检测 (中/英文兼容)

#### 实现详情

**1. IPC 状态增强**
- 新增 `ipcSend()` 函数: 通过 Unix socket `/tmp/iina.sock` 发送 JSON 命令
- 新增 `IsIPCAvailable()`: 检测 IPC socket 是否可用
- `GetStatus()` 优先使用 IPC socket 获取: `playback-time`, `duration`, `pause`, `volume`, `speed`, `filename`
- `GetFullStatus()` 返回完整状态:
```json
{
  "playing": true,
  "position": 125.5,
  "duration": 3600.0,
  "speed": 1.0,
  "volume": 80,
  "filename": "xxx.mkv",
  "audio_tracks": [...],
  "subtitle_tracks": [...]
}
```

**2. 播放列表完整支持**
- 新增 `GetPlaylist()` 函数: 通过 IPC `playlist` 属性获取完整列表
- `GET /api/v1/playlist` 返回格式:
```json
{
  "playlist": [
    {"index": 0, "name": "Movie.mkv", "path": "/xxx/Movie.mkv", "duration": 3600.0, "is_playing": true},
    {"index": 1, "name": "S02E01.mkv", "path": "/xxx/S02E01.mkv", "duration": 2700.0, "is_playing": false}
  ]
}
```

**3. 菜单语言检测**
- 新增 `systemLanguage()`: 检测系统语言 (zh/en)，通过 `defaults read -g AppleLanguages`
- 新增 `menuBarItemMap()`: 中文菜单名 → 英文菜单名映射
- 新增 `submenuNameMap()`: 中文子菜单名 → 英文映射
- `GetAudioTracks()` / `GetSubtitleTracks()` / `SwitchAudio()` / `SwitchSubtitle()` 等全部支持中/英文菜单
- `ChapterJump()` 支持中/英文"章节"菜单
