# IINA Control Methods Report

**Research Date:** 2026-04-07  
**IINA Version:** Unknown (latest)  
**Test File:** `/Users/altair/Documents/Michiko and Hatchin - 14.mkv`  
**IINA IPC Socket:** Configured at `ipc:///tmp/iina.sock` (preference set but socket not active)

---

## Executive Summary

IINA is a macOS media player built on mpv. It offers **three viable control methods**:

1. **AppleScript UI Menu Bar** (PRIMARY) — Full access to all menus, track switching, playback control
2. **Keyboard Shortcuts via AppleScript** (SECONDARY) — mpv keybindings sent via CGEvent
3. **mpv IPC Socket** (POTENTIAL) — Configured but socket file doesn't exist; requires IINA restart

**Critical Finding:** IINA has **NO native AppleScript scripting dictionary** — it cannot be scripted via `tell application "IINA" to...`. All control must go through **UI scripting** via System Events + Process.

**Getting playback position** is the biggest gap — none of the methods provide direct position readout. Window title only shows filename.

---

## Method 1: AppleScript UI Menu Bar (Primary)

### What
Control IINA by programmatically clicking menu bar items via `System Events` → `process "IINA"` → `menu item`.

### How
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "<menu-item-name>" of menu "<menu-name>" of menu bar item "<menu-bar-item>" of menu bar 1
    end tell
end tell
```

### Menu Bar Structure (Chinese UI)

**Menu Bar Items (top to bottom):**
```
Apple, IINA, 文件, 编辑, 回放, 视频, 音频, 字幕, Plugin, 窗口, 帮助
```

### 回放 (Playback) Menu — Full Contents
| Menu Item | Description |
|-----------|-------------|
| 继续 / 暂停 | Play/Pause toggle |
| 停止并清空播放列表 | Stop and clear playlist |
| 渐进 5秒 | Fade in 5 seconds |
| 渐退 5秒 | Fade out 5 seconds |
| 下一帧 | Next frame |
| 上一帧 | Previous frame |
| 跳转到开始 | Jump to beginning |
| 跳转至… | Go to time… |
| 播放速度 | Speed submenu |
| → 加速 2 倍 | 2x speed |
| → 加速 1.1 倍 | 1.1x speed |
| → 减速 0.5 倍 | 0.5x speed |
| → 减速 0.9091 倍 | 0.9091x speed |
| → 重置速度 | Reset speed |
| A-B 循环 | A-B loop |
| 单文件循环 | Single file loop |
| 显示播放列表面板 | Show playlist panel |
| 播放列表循环 | Playlist loop |
| 播放列表 | Playlist |
| 下一个媒体 | Next media |
| 上一个媒体 | Previous media |
| 显示章节面板 | Show chapter panel |
| 章节 | Chapters |
| 下一章节 | Next chapter |
| 上一章节 | Previous chapter |

### 音频 (Audio) Menu — Full Contents
| Menu Item | Description |
|-----------|-------------|
| 显示音频面板 | Show audio panel |
| 循环切换音频轨道 | Cycle audio track |
| 音频轨道 | Submenu with all audio tracks |
| 加载外置音频… | Load external audio… |
| 音量: 100 | Volume display |
| 音量 + 5% | Volume +5% |
| 音量 + 1% | Volume +1% |
| 音量 - 5% | Volume -5% |
| 音量 - 1% | Volume -1% |
| 静音 | Mute |
| 音频延迟: 0秒 | Audio delay |
| 音频延迟 + 0.5秒 | Audio delay +0.5s |
| 音频延迟 + 0.1秒 | Audio delay +0.1s |
| 音频延迟 - 0.5秒 | Audio delay -0.5s |
| 音频延迟 - 0.1秒 | Audio delay -0.1s |
| 重置音频延迟 | Reset audio delay |
| 音频设备 | Audio device |
| 音频滤镜… | Audio filters… |
| 保存的音频滤镜 | Saved audio filters |

### 字幕 (Subtitle) Menu — Full Contents
| Menu Item | Description |
|-----------|-------------|
| 显示字幕面板 | Show subtitle panel |
| 循环切换字幕轨道 | Cycle subtitle track |
| 字幕 | Submenu with all subtitle tracks |
| 隐藏字幕 | Hide subtitles |
| 二级字幕 | Secondary subtitles |
| 隐藏二级字幕 | Hide secondary subtitles |
| 加载外置字幕… | Load external subtitle… |
| 从 opensubtitles.com 查找在线字幕 | Search online |
| 查找在线字幕… | Search subtitles… |
| 保存下载的字幕… | Save downloaded subtitles… |
| 编码 | Encoding |
| 放大 | Zoom in |
| 等比缩小 | Scale proportionally |
| 重置字幕缩放 | Reset scale |
| 字幕延迟: 0秒 | Subtitle delay |
| 字幕延迟 + 0.5秒 | Delay +0.5s |
| 字幕延迟 + 0.1秒 | Delay +0.1s |
| 字幕延迟 - 0.5秒 | Delay -0.5s |
| 字幕延迟 - 0.1秒 | Delay -0.1s |
| 重置字幕延迟 | Reset delay |
| 字体… | Font… |

### Audio Track Submenu Format
```
<无>, #1 [English] English aac, 2ch, 48kHz (默认), #2 Japanese aac, 2ch, 48kHz
```

### Subtitle Track Submenu Format
```
<无>, #1 [English] hdmv_pgs_subtitle (默认), #2 Michiko and Hatchin - 14.ass ass
```

### Video Menu — Key Contents
| Menu Item | Description |
|-----------|-------------|
| 显示视频面板 | Show video panel |
| 循环切换视频轨道 | Cycle video track |
| 一半大小 | Half size |
| 原始大小 | Original size |
| 双倍大小 | Double size |
| 适应屏幕 | Fit to screen |
| 进入「画中画」模式 | PiP mode |
| 进入全屏模式 | Fullscreen |
| 窗口置顶 | Always on top |
| 长宽比 | Aspect ratio submenu |

### Aspect Ratio Submenu
```
默认, 4:3, 5:4, 16:9, 16:10, 1:1, 3:2, 2.21:1, 2.35:1, 2.39:1
```

### Pros
- Full access to all IINA features
- Works reliably for track switching
- Can read track lists
- No configuration needed beyond Accessibility permissions

### Cons
- Requires Accessibility permissions (System Preferences → Security & Privacy → Accessibility)
- Requires menu bar to be accessible (no Spaces interference)
- Cannot read playback position directly
- Slower than keyboard shortcuts
- Menu items must be clicked individually — cannot send keyboard shortcuts for track cycling

### Tested Commands

**Get audio track list:**
```applescript
tell application "System Events"
    tell process "IINA"
        get name of every menu item of menu "音频轨道" of menu item "音频轨道" of menu "音频" of menu bar item "音频" of menu bar 1
    end tell
end tell
```
Output: `<无>, #1 [English] English aac, 2ch, 48kHz (默认), #2 Japanese aac, 2ch, 48kHz`

**Switch to audio track #2:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "#2 Japanese aac, 2ch, 48kHz" of menu "音频轨道" of menu item "音频轨道" of menu "音频" of menu bar item "音频" of menu bar 1
    end tell
end tell
```

**Get subtitle track list:**
```applescript
tell application "System Events"
    tell process "IINA"
        get name of every menu item of menu "字幕" of menu item "字幕" of menu "字幕" of menu bar item "字幕" of menu bar 1
    end tell
end tell
```
Output: `<无>, #1 [English] hdmv_pgs_subtitle (默认), #2 Michiko and Hatchin - 14.ass ass`

**Switch to subtitle #2:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "#2 Michiko and Hatchin - 14.ass ass" of menu "字幕" of menu item "字幕" of menu "字幕" of menu bar item "字幕" of menu bar 1
    end tell
end tell
```

**Turn off subtitles:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "<无>" of menu "字幕" of menu item "字幕" of menu "字幕" of menu bar item "字幕" of menu bar 1
    end tell
end tell
```

**Cycle audio track:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "循环切换音频轨道" of menu "音频" of menu bar item "音频" of menu bar 1
    end tell
end tell
```

**Cycle subtitle track:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "循环切换字幕轨道" of menu "字幕" of menu bar item "字幕" of menu bar 1
    end tell
end tell
```

**Play/Pause (via menu):**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "继续" of menu "回放" of menu bar item "回放" of menu bar 1
        -- or "暂停" if currently playing
    end tell
end tell
```

**Get filename from window title:**
```applescript
tell application "System Events"
    tell process "IINA"
        get value of static text 1 of window 1
    end tell
end tell
```
Output: `Michiko and Hatchin - 14.mkv`

**Volume up 5%:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "音量 + 5%" of menu "音频" of menu bar item "音频" of menu bar 1
    end tell
end tell
```

**Mute:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "静音" of menu "音频" of menu bar item "音频" of menu bar 1
    end tell
end tell
```

**Seek forward 5s (via menu):**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "渐进 5秒" of menu "回放" of menu bar item "回放" of menu bar 1
    end tell
end tell
```

**Set playback speed 2x:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "加速 2 倍" of menu "播放速度" of menu item "播放速度" of menu "回放" of menu bar item "回放" of menu bar 1
    end tell
end tell
```

**Toggle fullscreen:**
```applescript
tell application "System Events"
    tell process "IINA"
        click menu item "进入全屏模式" of menu "视频" of menu bar item "视频" of menu bar 1
    end tell
end tell
```

---

## Method 2: Keyboard Shortcuts (Secondary)

### What
Send keyboard events to IINA using macOS's CGEvent API (or AppleScript keystroke). IINA uses mpv's keybinding system.

### How
```applescript
tell application "System Events"
    keystroke "j"  -- cycle subtitle forward
    keystroke " "  -- play/pause (mpv default)
end tell
```

### Complete mpv Key Bindings (from IINA's `input.conf`)

#### Playback Control
| Key | Command | Description |
|-----|---------|-------------|
| `Space` | `cycle pause` | Toggle play/pause |
| `p` | `cycle pause` | Toggle play/pause |
| `q` | `quit` | Quit |
| `Q` | `quit-watch-later` | Quit and remember position |
| `ESC` | `set fullscreen no` | Exit fullscreen |
| `.` | `frame-step` | Next frame |
| `,` | `frame-back-step` | Previous frame |

#### Seeking
| Key | Command | Description |
|-----|---------|-------------|
| `RIGHT` | `seek 5` | Seek +5 seconds |
| `LEFT` | `seek -5` | Seek -5 seconds |
| `UP` | `seek 60` | Seek +1 minute |
| `DOWN` | `seek -60` | Seek -1 minute |
| `Shift+RIGHT` | `seek 1 exact` | Exact seek +1 second |
| `Shift+LEFT` | `seek -1 exact` | Exact seek -1 second |
| `Shift+UP` | `seek 5 exact` | Exact seek +5 seconds |
| `Shift+DOWN` | `seek -5 exact` | Exact seek -5 seconds |
| `Shift+PGUP` | `seek 600` | Seek +10 minutes |
| `Shift+PGDWN` | `seek -600` | Seek -10 minutes |
| `PGUP` | `add chapter 1` | Next chapter |
| `PGDWN` | `add chapter -1` | Previous chapter |

#### Audio/Subtitle Track Switching
| Key | Command | Description |
|-----|---------|-------------|
| `j` | `cycle sub` | Cycle subtitle track forward |
| `J` | `cycle sub down` | Cycle subtitle track backward |
| `#` (SHARP) | `cycle audio` | Cycle audio track |
| `v` | `cycle sub-visibility` | Toggle subtitles on/off |
| `z` | `add sub-delay -0.1` | Subtitle delay -0.1s |
| `Z` | `add sub-delay +0.1` | Subtitle delay +0.1s |

#### Volume
| Key | Command | Description |
|-----|---------|-------------|
| `9` | `add volume -2` | Volume down |
| `/` | `add volume -2` | Volume down |
| `0` | `add volume 2` | Volume up |
| `*` | `add volume 2` | Volume up |
| `m` | `cycle mute` | Toggle mute |

#### Speed
| Key | Command | Description |
|-----|---------|-------------|
| `[` | `multiply speed 1/1.1` | Slow down 0.909x |
| `]` | `multiply speed 1.1` | Speed up 1.1x |
| `{` | `multiply speed 0.5` | Halve speed |
| `}` | `multiply speed 2.0` | Double speed |
| `BS` | `set speed 1.0` | Reset speed |

#### Playlist
| Key | Command | Description |
|-----|---------|-------------|
| `>` | `playlist-next` | Next file |
| `ENTER` | `playlist-next` | Next file |
| `<` | `playlist-prev` | Previous file |

#### Video
| Key | Command | Description |
|-----|---------|-------------|
| `f` | `cycle fullscreen` | Toggle fullscreen |
| `T` | `cycle ontop` | Toggle always on top |
| `d` | `cycle deinterlace` | Toggle deinterlace |
| `A` | `cycle-values video-aspect-override "16:9" "4:3" "2.35:1" "-1"` | Cycle aspect ratio |

#### Screenshot
| Key | Command | Description |
|-----|---------|-------------|
| `s` | `screenshot` | Screenshot with subtitles |
| `S` | `screenshot video` | Screenshot without subtitles |
| `Ctrl+s` | `screenshot window` | Screenshot window |

### IINA-Specific Bindings
| Key | Command | Description |
|-----|---------|-------------|
| `Shift+Meta+v` | `video-panel` | Show video panel |
| `Shift+Meta+a` | `audio-panel` | Show audio panel |
| `Shift+Meta+s` | `sub-panel` | Show subtitle panel |
| `Shift+Meta+p` | `playlist-panel` | Show playlist panel |
| `Shift+Meta+c` | `chapter-panel` | Show chapter panel |
| `Shift+Meta+m` | `toggle-music-mode` | Toggle music mode |
| `Ctrl+Meta+p` | `toggle-pip` | Picture-in-picture |
| `Shift+Meta+r` | `show-current-file-in-finder` | Show in Finder |

### Mouse Bindings
| Input | Command | Description |
|-------|---------|-------------|
| `MBTN_LEFT_DBL` | `cycle fullscreen` | Double-click for fullscreen |
| `MBTN_RIGHT` | `cycle pause` | Right-click for play/pause |
| `MBTN_BACK` | `playlist-prev` | Back button - previous |
| `MBTN_FORWARD` | `playlist-next` | Forward button - next |
| `WHEEL_UP` | `seek 10` | Scroll up - seek +10s |
| `WHEEL_DOWN` | `seek -10` | Scroll down - seek -10s |
| `WHEEL_LEFT` | `add volume -2` | Scroll left - volume down |
| `WHEEL_RIGHT` | `add volume 2` | Scroll right - volume up |

### Pros
- Fast, no menu interaction needed
- Can combine multiple key chords
- Full access to mpv functionality
- Works well for play/pause, seeking, volume, speed

### Cons
- Cannot read state (position, current track name, etc.)
- Key sending may be blocked if another app has focus
- For track cycling (`j`, `#`), cannot specify which track — only cycles
- Requires Accessibility permissions for CGEvent

### Tested Commands
All standard mpv keybindings work when IINA is the frontmost app. Direct track switching (specifying exact track) requires menu bar method.

---

## Method 3: Accessibility API

### What
Use macOS Accessibility APIs to query UI elements of the IINA window.

### What Works
```applescript
tell application "System Events"
    tell process "IINA"
        -- Get window title (filename)
        get value of static text 1 of window 1
        -- Returns: "Michiko and Hatchin - 14.mkv"
        
        -- Get all UI elements
        get every UI element of window 1
        -- Returns: AXButton x3, AXImage, AXStaticText
        
        -- Get window role
        get role of window 1
        -- Returns: "AXStandardWindow"
    end tell
end tell
```

### What DOESN'T Work
- Cannot read playback position
- Cannot read current track info from UI
- Cannot read volume, speed, or other playback state
- Menu bar items cannot be queried for descriptions when menu is closed

### Window UI Elements (only these exist)
| Element | Role | Value |
|---------|------|-------|
| Button 1 | AXButton | — |
| Button 2 | AXButton | — |
| Button 3 | AXButton | — |
| Image | AXImage | filename |
| Static Text | AXStaticText | filename |

### Pros
- Can get filename
- Can bring IINA to front

### Cons
- Very limited — no playback state exposed
- Only filename is readable

---

## Method 4: mpv IPC Socket

### What
Direct communication with mpv via a Unix domain socket. IINA's preferences show IPC is configured but the socket doesn't exist.

### Configuration
IINA preferences (`com.colliderli.iina.plist`):
```
"mpv-input-ipc-server" = "ipc:///tmp/iina.sock";
"mpv-options" = "--input-ipc-server=/tmp/iina.sock";
```

### If Socket Existed — mpv IPC Commands
```json
{"command":["get_property","playback-time"]}       // Get position in seconds
{"command":["get_property","duration"]}           // Get duration in seconds
{"command":["get_property","filename"]}            // Get filename
{"command":["get_property","volume"]}             // Get volume (0-100)
{"command":["get_property","speed"]}              // Get playback speed
{"command":["get_property","pause"]}              // Get pause state
{"command":["get_property","track-list"]}        // Get all tracks
{"command":["get_property","audio"]}              // Get current audio track
{"command":["get_property","sub"]}               // Get current subtitle track

// Commands
{"command":["set_property","pause",true]}         // Pause
{"command":["set_property","pause",false]}        // Play
{"command":["set_property","volume",80]}          // Set volume
{"command":["set_property","speed",1.5]}         // Set speed
{"command":["seek",100,"absolute"]}              // Seek to 100s
{"command":["sub","2"]}                           // Select subtitle track 2
{"command":["audio","2"]}                         // Select audio track 2
{"command":["quit"]}                              // Quit
```

### Requirements to Enable
1. IINA must be restarted after setting the preference
2. The socket file `/tmp/iina.sock` must exist
3. Need `socat` or `nc -U` to communicate

### Limitations
- Socket file not currently present — IINA needs restart
- Requires `socat` or `nc` for communication (neither installed by default on macOS)
- Requires manual preference setting (cannot enable via CLI)

### How to Enable
```bash
# The preference is already set but socket doesn't exist
# IINA needs to be quit and restarted to create the socket
# After restart, communicate via:
printf '{"command":["get_property","playback-time"]}\n' | nc -U /tmp/iina.sock
```

---

## Method 5: Command Line

### What
Control IINA via command-line arguments when launching.

### IINA CLI Options
```
--help                    Show help
--version                Show version
--no-playback            Don't start playback
--force-window           Force window opening
--keep-running           Keep player running after file ends
--stdin                  Read from stdin
--stream-lavfd-option <key=value>
                         Set lavfd options for streaming
--script <file>          Load Lua script
--script-opts <key=value>
                         Set script options
```

### URL Scheme
IINA registers the `iina://` URL scheme:

```
iina://open?url=<encoded-url>
iina://open?url=<encoded-url>&new-window=true
iina://open?file=<encoded-path>
```

### Opening Files
```bash
# Open a file
open -a IINA "/path/to/video.mkv"

/# Or via URL scheme
open "iina://open?file=/path/to/video.mkv"
```

### Limitations
- CLI only handles file opening, not playback control
- Cannot control an already-running instance via CLI (IINA doesn't support instance control flags)
- `--input-ipc-server` flag is NOT supported — must be set in Preferences

---

## Comparison Table

| Feature | Method 1 (Menu Bar) | Method 2 (Keys) | Method 3 (AX) | Method 4 (IPC Socket) | Method 5 (CLI) |
|---------|:------------------:|:----------------:|:-------------:|:--------------------:|:--------------:|
| Switch audio | ✅ | ✅ (cycle only) | ❌ | ✅ | ❌ |
| Switch subtitle | ✅ | ✅ (cycle only) | ❌ | ✅ | ❌ |
| Get position | ❌ | ❌ | ❌ | ✅ | ❌ |
| Get duration | ❌ | ❌ | ❌ | ✅ | ❌ |
| Get filename | ✅ | ❌ | ✅ | ✅ | ❌ |
| Get track list | ✅ | ❌ | ❌ | ✅ | ❌ |
| Get volume | ❌ | ❌ | ❌ | ✅ | ❌ |
| Seek | ✅ (menus) | ✅ | ❌ | ✅ | ❌ |
| Play/Pause | ✅ | ✅ | ❌ | ✅ | ❌ |
| Volume | ✅ | ✅ | ❌ | ✅ | ❌ |
| Speed | ✅ | ✅ | ❌ | ✅ | ❌ |
| Fullscreen | ✅ | ✅ | ❌ | ✅ | ❌ |
| Playlist nav | ✅ | ✅ | ❌ | ✅ | ❌ |
| Screenshot | ✅ | ✅ | ❌ | ✅ | ❌ |
| Mute | ✅ | ✅ | ❌ | ✅ | ❌ |
| Read current audio/sub | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## Recommended Approach

### For Track Switching (Primary Need)
**Use Method 1 (AppleScript Menu Bar)** — it provides exact track selection (not just cycling) and can read track lists.

### For Playback Control (Play/Pause/Seek/Volume)
**Use Method 2 (Keyboard Shortcuts)** via `CGEventPost` or `osascript keystroke` — faster than menu clicking.

### For Getting Playback State
**Enable Method 4 (mpv IPC Socket)** by restarting IINA:
1. IINA already has IPC configured in preferences
2. Quit IINA completely
3. Start IINA again
4. The socket at `/tmp/iina.sock` should be created
5. Use `socat` or `nc -U` to query

### Combined Architecture
```
┌─────────────────────────────────────────────────────┐
│  Android App                                        │
│  ┌─────────┐  ┌──────────┐  ┌─────────────────┐    │
│  │ Track   │  │ Playback │  │ State (IPC)     │    │
│  │ UI      │  │ Controls │  │ Position/Duration│    │
│  └────┬────┘  └────┬─────┘  └────────┬────────┘    │
│       │             │                  │             │
│       │             │                  │             │
└───────┼─────────────┼──────────────────┼─────────────┘
        │             │                  │
        ▼             ▼                  ▼
   Menu Bar      Keyboard          IPC Socket
   AppleScript   Shortcuts          (needs restart)
   (exact track  (fast play/        (full state
    selection)    pause/seek)        read)
```

### Implementation Priority
1. **Phase 1:** Menu bar AppleScript for track switching (proven working)
2. **Phase 2:** Keyboard shortcuts for playback control
3. **Phase 3:** Enable IPC socket for state monitoring (requires IINA restart)

---

## Working Code Examples

### Python: Get Audio Track List
```python
import subprocess

def get_audio_tracks():
    script = '''tell application "System Events"
        tell process "IINA"
            get name of every menu item of menu "音频轨道" of menu item "音频轨道" of menu "音频" of menu bar item "音频" of menu bar 1
        end tell
    end tell'''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    tracks = result.stdout.strip().split(', ')
    return tracks
```

### Python: Switch Subtitle Track
```python
import subprocess

def switch_subtitle(track_text):
    """track_text: exact menu item like '#2 Michiko and Hatchin - 14.ass ass'"""
    script = f'''tell application "System Events"
        tell process "IINA"
            click menu item "{track_text}" of menu "字幕" of menu item "字幕" of menu "字幕" of menu bar item "字幕" of menu bar 1
        end tell
    end tell'''
    subprocess.run(['osascript', '-e', script], capture_output=True)
```

### Python: Cycle Audio Track
```python
def cycle_audio():
    script = '''tell application "System Events"
        tell process "IINA"
            click menu item "循环切换音频轨道" of menu "音频" of menu bar item "音频" of menu bar 1
        end tell
    end tell'''
    subprocess.run(['osascript', '-e', script], capture_output=True)
```

### Python: Get Filename
```python
import subprocess

def get_filename():
    script = '''tell application "System Events"
        tell process "IINA"
            get value of static text 1 of window 1
        end tell
    end tell'''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    return result.stdout.strip()
```

### Python: Send Keyboard Shortcut (Play/Pause)
```python
import subprocess

def toggle_play_pause():
    # Method: Use mpv's key binding via osascript
    script = '''tell application "System Events"
        keystroke " " using {command down, control down}
    end tell'''
    # Note: This specific combo may not be correct - need to verify
```

### Python: IPC Socket Query (if socket exists)
```python
import subprocess

def get_playback_position():
    """Requires socat: brew install socat"""
    cmd = ['socat', '-', '/tmp/iina.sock']
    request = '{"command":["get_property","playback-time"]}\n'
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = proc.communicate(input=request.encode())
    # Parse JSON response
```

---

## Appendix: Known Limitations

1. **No native AppleScript dictionary** — IINA doesn't expose scripting terminology
2. **No built-in HTTP API** — external server (iina-remote-server) exists but requires auth
3. **Position cannot be read** via menu bar or accessibility APIs
4. **IPC socket not active** — requires IINA restart to create `/tmp/iina.sock`
5. **Menu bar language** — IINA uses Chinese menu items on this system; English installation would use English names
6. **Accessibility permission required** — all AppleScript UI control needs Accessibility grant

---

## Appendix: IINA URL Scheme

IINA registers `iina://` for opening files:
```
iina://open?url=<URL-encoded-path-or-url>
iina://open?file=<URL-encoded-path>
```
