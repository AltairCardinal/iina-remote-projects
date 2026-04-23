# Control Functions Implementation Status

**Document Date:** 2026-04-23
**Source:** `server/iina/applescript.go`, `server/handler/*.go`

---

## Architecture

The Go server uses an **IPC-first** design with **AppleScript fallback**:

1. **IPC Path** (Primary): Commands sent via Unix socket `/tmp/iina.sock`
2. **AppleScript Fallback** (Secondary): When IPC unavailable, uses `osascript` via `System Events`
3. **AppleScript-only**: Some functions have no IPC implementation

**Accessibility Permission Requirement**: AppleScript fallback requires macOS Accessibility permission. IPC does not.

---

## Category A: IPC + AppleScript Fallback

These functions try IPC first, then fall back to AppleScript if IPC fails.

| Function | IPC Command | AppleScript Fallback | Notes |
|---------|------------|---------------------|-------|
| `TogglePlay()` | `get_property pause` + `set_property pause !paused` | Space key (keyCode 49) | |
| `Play()` | `set_property pause false` | Space key | |
| `Pause()` | `set_property pause true` | Space key | |
| `Seek()` | `add time-pos <delta>` | Left/Right arrows (123/124) in 5s increments | Clamped to +/-300s |
| `PrevTrack()` | `playlist-prev` | Shift+Comma (43) | |
| `NextTrack()` | `playlist-next` | Shift+Period (44) | |
| `ToggleMute()` | `get_property mute` + `set_property mute !muted` | M key (46) | |
| `WindowFullscreen()` | `cycle fullscreen` | F key (3) | |
| `ChapterNext()` | `add chapter 1` | PageUp key (116) | |
| `ChapterPrev()` | `add chapter -1` | PageDown key (121) | |
| `AspectRatio()` | `cycle video-aspect-override` | Shift+A key (0) | |
| `GetAudioTracks()` | `track-list` + `aid` | Menu reading (音频 → 音频轨道) | |
| `GetSubtitleTracks()` | `track-list` + `sid` | Menu reading (字幕 → 字幕轨道) | |
| `SwitchAudio()` | `set_property aid <id>` | Menu click (音频 → 音频轨道 → track) | |
| `SwitchSubtitle()` | `set_property sid <id>` | Menu click (字幕 → 字幕轨道 → track) | |
| `CycleAudio()` | `cycle audio` | Menu click (音频 → 循环切换音频轨道) | |
| `CycleSubtitle()` | `cycle sub` | Menu click (字幕 → 循环切换字幕轨道) | |
| `SubtitleZoomIn()` | `get_property sub-scale` + `set_property sub-scale` | Menu click (字幕 → 放大) | |
| `SubtitleZoomOut()` | `get_property sub-scale` + `set_property sub-scale` | Menu click (字幕 → 等比缩小) | |
| `SubtitleSetScale()` | `set_property sub-scale <scale>` | Multiple menu clicks for delta | |
| `SetSubtitleDelay()` | `add sub-delay <deltaSec>` | Menu click (字幕 → 字幕延迟) | |
| `GetStatus()` | Multiple `get_property` calls | Window title + volume parsing | |
| `GetFullStatus()` | `GetStatus()` + `getTracksViaIPC()` + `sub-scale` | `GetAudioTracks()` + `GetSubtitleTracks()` via menu | |
| `OpenFile()` | `command loadfile <path> replace` | `tell application "IINA" to quit` + open | |
| `GetPlaylist()` | `get_property playlist` | `GetStatus()` for current file only | |

---

## Category B: IPC Only (No AppleScript Fallback)

These functions use IPC only. If IPC is unavailable, they return an error.

| Function | IPC Command | Error Message | Notes |
|---------|------------|---------------|-------|
| `SeekTo()` | `set_property time-pos <seconds>` | "absolute seeking requires IPC" | |
| `SetVolume()` | `set_property volume <vol>` | "volume control requires IPC" | |
| `SetSpeed()` | `set_property speed <speed>` | "speed control requires IPC" | |
| `JumpToPlaylistItem()` | `playlist-play-index <index>` | "playlist jump requires IPC" | |
| `GetFullscreen()` | `get_property fullscreen` | "fullscreen state requires IPC" | Read-only |
| `GetChapters()` | `get_property chapter-list` | "chapters require IPC" | |
| `ChapterJump()` | `set_property chapter <index>` | - | |
| `SetABLoopA()` | `set_property ab-loop-a <time>` | - | Uses GetStatus internally |
| `SetABLoopB()` | `set_property ab-loop-b <time>` | - | Uses GetStatus internally |
| `ClearABLoop()` | `set_property ab-loop-a "no"` + `ab-loop-b "no"` | - | |
| `SetAspectRatio()` | `set_property video-aspect-override <aspect>` | "aspect ratio setting requires IPC" | |
| `SubtitleZoomGet()` | `get_property sub-scale` | "could not get sub-scale" | Read-only |
| `GetSubtitleDelay()` | `get_property sub-delay` | - | Read-only |
| `GetAudioDelay()` | `get_property audio-delay` | - | Read-only |
| `SetAudioDelay()` | `add audio-delay <deltaSec>` | - | |

---

## Category C: AppleScript Only (No IPC)

These functions have **no IPC implementation**. Two types:

**C1: Requires Accessibility permission** (uses `tell application "System Events"`):

| Function | AppleScript | Notes |
|---------|------------|-------|
| `Screenshot()` | `tell application "IINA" to activate` + S key (31) | Triggers IINA's built-in screenshot |
| `WindowOntop()` | `tell application "IINA" to activate` + T key (17) | Cycles "窗口置顶" state |

**C2: No special permission required** (uses built-in AppleScript commands):

| Function | AppleScript | Notes |
|---------|------------|-------|
| `SetSystemVolume()` | `set volume output volume <vol>` | macOS system volume, **verified: no permission needed** |
| `GetSystemVolume()` | `output volume of (get volume settings)` | macOS system volume, **verified: no permission needed** |

> **Tested:** `set volume output volume` and `output volume of (get volume settings)` execute successfully without Accessibility permission.

---

## HTTP API Handlers

All handlers in `server/handler/` wrap the iina package functions:

| Handler | File | Function | Category | Accessibility Required? |
|---------|------|----------|----------|----------------------|
| `PlaybackPlay` | playback.go:13 | `iina.Play()` | A | Only if IPC fails |
| `PlaybackPause` | playback.go:22 | `iina.Pause()` | A | Only if IPC fails |
| `PlaybackSeek` | playback.go:36 | `iina.SeekTo()` | B | No |
| `PlaybackSkip` | playback.go:55 | `iina.Seek()` | A | Only if IPC fails |
| `PlaybackSpeed` | playback.go:74 | `iina.SetSpeed()` | B | No |
| `PlaybackVolume` | playback.go:99 | `iina.SetVolume()` | B | No |
| `PlaybackPrev` | playback.go:120 | `iina.PrevTrack()` | A | Only if IPC fails |
| `PlaybackNext` | playback.go:129 | `iina.NextTrack()` | A | Only if IPC fails |
| `PlaylistJump` | playback.go:138 | `iina.JumpToPlaylistItem()` | B | No |
| `PlaybackMute` | playback.go:149 | `iina.ToggleMute()` | A | Only if IPC fails |
| `GetABLoop` | playback.go:163 | `iina.GetABLoop()` | In-memory | No |
| `SetABLoop` | playback.go:180 | `iina.SetABLoopA/B/ClearABLoop()` | B | No |
| `GetSystemVolume` | playback.go:206 | `iina.GetSystemVolume()` | C2 | No (built-in AS) |
| `SetSystemVolume` | playback.go:221 | `iina.SetSystemVolume()` | C2 | No (built-in AS) |
| `GetPlaylist` | playback.go:236 | `iina.GetPlaylist()` | A | Only if IPC fails |
| `GetStatus` | health.go:195 | `iina.GetFullStatus()` | A | Only if IPC fails |
| `GetAudio` | media.go:12 | `iina.GetAudioTracks()` | A | Only if IPC fails |
| `GetSubtitle` | media.go:22 | `iina.GetSubtitleTracks()` | A | Only if IPC fails |
| `SwitchAudio` | media.go:32 | `iina.SwitchAudio()` | A | Only if IPC fails |
| `SwitchSubtitle` | media.go:42 | `iina.SwitchSubtitle()` | A | Only if IPC fails |
| `CycleAudio` | media.go:52 | `iina.CycleAudio()` | A | Only if IPC fails |
| `CycleSubtitle` | media.go:61 | `iina.CycleSubtitle()` | A | Only if IPC fails |
| `SubZoomIn` | media.go:70 | `iina.SubtitleZoomIn()` | A | Only if IPC fails |
| `SubZoomOut` | media.go:79 | `iina.SubtitleZoomOut()` | A | Only if IPC fails |
| `SubSetScale` | media.go:88 | `iina.SubtitleSetScale()` | A | Only if IPC fails |
| `Screenshot` | media.go:104 | `iina.Screenshot()` | C | **YES** |
| `SubDelayGet` | media.go:113 | `iina.GetSubtitleDelay()` | B | No |
| `SubDelaySet` | media.go:123 | `iina.SetSubtitleDelay()` | A | Only if IPC fails |
| `GetAudioDelay` | media.go:139 | `iina.GetAudioDelay()` | B | No |
| `SetAudioDelay` | media.go:149 | `iina.SetAudioDelay()` | A | Only if IPC fails |
| `GetChapters` | chapter.go:13 | `iina.GetChapters()` | B | No |
| `ChapterJump` | chapter.go:28 | `iina.ChapterJump()` | B | No |
| `ChapterNext` | chapter.go:43 | `iina.ChapterNext()` | A | Only if IPC fails |
| `ChapterPrev` | chapter.go:52 | `iina.ChapterPrev()` | A | Only if IPC fails |
| `GetAspectRatio` | video.go:16 | N/A | - | Returns empty |
| `SetAspectRatio` | video.go:24 | `iina.AspectRatio()` / `iina.SetAspectRatio()` | A/B | |
| `WindowFullscreenGet` | window.go:11 | `iina.GetFullscreen()` | B | No |
| `WindowFullscreen` | window.go:21 | `iina.WindowFullscreen()` | A | Only if IPC fails |
| `WindowOntop` | window.go:30 | `iina.WindowOntop()` | C | **YES** |
| `IINAStatus` | iina.go:21 | `iina.IsIPCAvailable()` | - | IPC check only |
| `RestartIINA` | iina.go:29 | N/A | Socket notification + AS | No |
| `Browse` | browse.go:27 | N/A | File system | Not IINA control |
| `OpenFile` | browse.go:98 | `iina.OpenFile()` | A | Only if IPC fails |

---

## Summary by Accessibility Permission Need

| Category | Count | Accessibility Required? |
|----------|-------|------------------------|
| **A: IPC + AppleScript Fallback** | 25 | Only when IPC fails |
| **B: IPC Only (No Fallback)** | 15 | **Never** (IPC required) |
| **C1: AppleScript Only (Accessibility required)** | 2 | Screenshot, WindowOntop |
| **C2: AppleScript Only (no permission needed)** | 2 | GetSystemVolume, SetSystemVolume |

### Functions Requiring Accessibility Permission (when IPC unavailable)

| Function | Category | When IPC Fails |
|----------|----------|----------------|
| TogglePlay, Play, Pause | A | Falls back to Space key |
| Seek | A | Falls back to arrow keys |
| PrevTrack, NextTrack | A | Falls back to Shift+comma/period |
| ToggleMute | A | Falls back to M key |
| WindowFullscreen | A | Falls back to F key |
| ChapterNext, ChapterPrev | A | Falls back to PageUp/PageDown |
| AspectRatio | A | Falls back to Shift+A |
| GetAudioTracks, GetSubtitleTracks | A | Falls back to menu reading |
| SwitchAudio, SwitchSubtitle | A | Falls back to menu click |
| CycleAudio, CycleSubtitle | A | Falls back to menu click |
| SubtitleZoomIn/Out/SetScale | A | Falls back to menu click |
| SetSubtitleDelay | A | Falls back to menu click |
| GetStatus, GetFullStatus | A | Limited fallback |
| OpenFile | A | Falls back to quit+open |
| GetPlaylist | A | Limited fallback |
| **Screenshot** | **C1** | **No IPC - always requires Accessibility** |
| **WindowOntop** | **C1** | **No IPC - always requires Accessibility** |

### Functions NOT Requiring Any Special Permission

| Function | Category | Why No Permission Needed |
|----------|----------|------------------------|
| **GetSystemVolume** | **C2** | Built-in AppleScript (`get volume settings`) - **tested, works without permission** |
| **SetSystemVolume** | **C2** | Built-in AppleScript (`set volume`) - **tested, works without permission** |

---

## IPC Socket Path

- **Socket**: `/tmp/iina.sock`
- **Protocol**: JSON over Unix socket
- **Connection Timeout**: 2 seconds
- **Command Timeout**: 10 seconds (single command), 30 seconds (multi-line script)

---

## Key Findings

1. **Most control functions (25) have both IPC and AppleScript fallback** - works even without Accessibility permission when IPC is available

2. **15 functions are IPC-only** - will fail if IPC unavailable, but don't require Accessibility

3. **2 functions are AppleScript-only and require Accessibility**:
   - `Screenshot()` - IINA's built-in screenshot
   - `WindowOntop()` - toggle always-on-top

4. **2 functions are AppleScript-only but require NO special permission** (verified by testing):
   - `GetSystemVolume()` / `SetSystemVolume()` - use built-in AppleScript commands

5. **IPC-first design means Accessibility is not strictly required** for most operations - only when IPC socket is unavailable AND using functions in Category C1

---

## References

- `server/iina/applescript.go` - Core implementation
- `server/handler/*.go` - HTTP API handlers
- `docs/MPV_IPC_REFERENCE.md` - IPC protocol details
