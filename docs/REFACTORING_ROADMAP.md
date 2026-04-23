# Code Organization Refactoring Roadmap

**Created**: 2026-04-24
**Status**: In Progress
**Branch**: `refactor/code-organization` (to be created in each submodule)

---

## Background

Code audit identified **38 issues** across three sub-projects:
- **Server**: 11 issues (1 Critical, 6 Major, 4 Minor)
- **macOS**: 11 issues (0 Critical, 3 Major, 8 Minor)
- **Android**: 16 issues (2 Critical, 7 Major, 7 Minor)

See previous audit reports for detailed findings.

---

## Server Refactoring Plan (Phase 1)

### Objective
Split the 1718-line `iina/applescript.go` into focused files, and separate handler concerns.

### Steps

- [ ] **1.1** Create `iina/types.go` - Extract all type definitions (Status, Track, Chapter, FullStatus, BrowseEntry, BrowseResult, PlaylistEntry, ipcCommand, ipcResponse)
- [ ] **1.2** Create `iina/ipc.go` - Extract IPC socket communication (ipcSend, IsIPCAvailable, toFloat64, getStatusViaIPC, getTracksViaIPC, getChaptersViaIPC, getPlaylistViaIPC, getFileDuration)
- [ ] **1.3** Create `iina/playback.go` - Extract playback control functions (TogglePlay, Play, Pause, Seek, SetVolume, SetSpeed, PrevTrack, NextTrack, etc.)
- [ ] **1.4** Create `iina/status.go` - Extract status queries (GetStatus, GetFullStatus, OpenFile, IsIINARunning, EnsureIINARunning, GetPlaylist)
- [ ] **1.5** Reduce `iina/applescript.go` to ~650 lines - Keep only AppleScript helpers, key constants, menu helpers
- [ ] **1.6** Split `handler/health.go` - Create health.go (health check), pairing.go (pairing handlers), middleware.go (auth middleware)
- [ ] **1.7** Update `main.go` route registrations - Ensure all route references are correct after file moves
- [ ] **1.8** Build and test - Run `go build ./...` and `go test ./...`

### Target Structure

```
server/iina/
├── applescript.go      (~650 lines) - AppleScript helpers only
├── applescript_test.go
├── browse.go           - BrowseEntry, BrowseResult types
├── ipc.go              (~300 lines) - IPC socket communication
├── ipc_test.go
├── playback.go         (~400 lines) - Playback control
├── status.go           (~150 lines) - Status queries, OpenFile
└── types.go            (~100 lines) - All shared types

server/handler/
├── health.go           (~35 lines) - Health check only
├── pairing.go          (~200 lines) - Pair/challenge/reconnect + device management
├── middleware.go       (~50 lines) - Auth middleware
├── browse.go           (~180 lines) - File browsing + path validation
├── playback.go         (~250 lines) - Playback HTTP handlers
├── media.go            (~160 lines) - Media (audio/subtitle) handlers
├── chapter.go          (~60 lines) - Chapter handlers
├── video.go            (~40 lines) - Video handlers
├── window.go           (~35 lines) - Window handlers
├── local.go            (~90 lines) - Localhost-only endpoints
├── iina.go             (~70 lines) - IINA status/restart
├── server.go           (NEW, ~40 lines) - Server name handlers (renamed from server_name.go)
└── device.go           (~50 lines) - Device listing/removal
```

### Verification
- [ ] `go build ./...` succeeds
- [ ] `go test ./...` passes
- [ ] `iina/applescript.go` < 800 lines
- [ ] New files exist: `types.go`, `ipc.go`, `playback.go`, `status.go`

---

## Android Refactoring Plan (Phase 2)

### Objective
Fix critical issues, split large files, move misplaced types.

### Steps

- [ ] **2.1** Delete empty `data/model/Track.kt`
- [ ] **2.2** Fix `VolumeSliderStateTest.kt` - Update test to use source types (behavior difference: initial() isMuted and OnValueChangeFinished)
- [ ] **2.3** Create `data/model/PairedServerInfo.kt` - Move from ConnectionStore.kt
- [ ] **2.4** Create `data/model/DiscoveredServer.kt` - Move from PairingViewModel.kt
- [ ] **2.5** Create `domain/model/PlaybackModels.kt` - Move Chapter and ABLoop from IinaRepository.kt
- [ ] **2.6** Move `VolumeSliderState.kt` from `ui/screens/` to `ui/state/`
- [ ] **2.7** Move `VolumeRow.kt` from `ui/screens/` to `ui/components/`
- [ ] **2.8** Move `PlaylistResponse` from IinaApiService.kt to ApiModels.kt
- [ ] **2.9** Split `MainScreen.kt` (645 lines) into `ui/screens/main/` subpackage
- [ ] **2.10** Split `VideoControlSheet.kt` (530 lines) into `ui/components/video/` subpackage
- [ ] **2.11** Remove empty directories: `ui/browse/`, `ui/main/`, `ui/navigation/`, `ui/pairing/`, `ui/subaudio/`, `domain/usecase/`
- [ ] **2.12** Build and test - Run `./gradlew assembleDebug`

### Verification
- [ ] `./gradlew assembleDebug` succeeds
- [ ] `Track.kt` deleted
- [ ] `ui/state/` exists with VolumeSliderState.kt
- [ ] `ui/components/` exists with VolumeRow.kt
- [ ] `ui/screens/main/` exists with MainScreen components
- [ ] Empty directories removed

---

## macOS Refactoring Plan (Phase 3)

### Objective
Remove dead code, split god classes, fix silent failures.

### Steps

- [ ] **3.1** Delete `UI/TrackTestWindowController.swift` (388 lines of unused debug UI)
- [ ] **3.2** Rename `PairingManager.swift` to `DeviceTokenStore.swift`
- [ ] **3.3** Split `IINAManager.swift` - Create `IINASocketServer.swift` and `IINALifecycleManager.swift`
- [ ] **3.4** Consolidate IINA launch/wait logic - Remove duplication between AppDelegate and IINALifecycleManager
- [ ] **3.5** Split `StatusBarController.swift` - Create `PairingUIController.swift` and `PairCodePollingService.swift`
- [ ] **3.6** Fix HTTPServerManager silent fallback - StatusBarController checks `userInfo["simulated"]` and shows error state
- [ ] **3.7** Fix PairingOverlayWindow retain cycle - Ensure `[weak self]` capture in onDismiss closure
- [ ] **3.8** Split `SettingsWindowController.swift` - Each tab as separate NSView subclass
- [ ] **3.9** Build and test - Run `xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build`

### Verification
- [ ] `xcodebuild` build succeeds
- [ ] `TrackTestWindowController.swift` deleted
- [ ] `StatusBarController.swift` < 300 lines
- [ ] `IINAManager.swift` split into two files
- [ ] Simulated mode shows error state in UI

---

## Documentation (Phase 4)

### Steps

- [ ] **4.1** Create `docs/PROTOCOL.md` - Complete API endpoint documentation with Android/macOS coverage
- [ ] **4.2** Create `docs/ARCHITECTURE.md` - Three-layer architecture diagram (Android ←HTTP→ macOS ←IPC→ IINA)
- [ ] **4.3** Create `docs/IPC_WORKAROUNDS.md` - Document IINA IPC bugs and workarounds

### Verification
- [ ] `docs/PROTOCOL.md` exists and documents all endpoints
- [ ] `docs/ARCHITECTURE.md` exists with architecture diagram
- [ ] `docs/IPC_WORKAROUNDS.md` explains the `["command", "loadfile", ...]` workaround

---

## Issue Log

### Phase 1 Issues Found During Execution
| # | Issue | Resolution |
|---|-------|------------|
| | | |

### Phase 2 Issues Found During Execution
| # | Issue | Resolution |
|---|-------|------------|
| | | |

### Phase 3 Issues Found During Execution
| # | Issue | Resolution |
|---|-------|------------|
| | | |

---

## Notes

- **Server Phase 3 (handler/server_name.go)**: Audit concluded this is NOT duplicate code - handler correctly delegates to auth. No changes needed.
- **IINA IPC Workaround**: The `["command", "loadfile", ...]` format is required due to IINA bugs #629, #2809, #4478, #5996
- **macOS Simulated Mode**: HTTPServerManager falls back to simulated mode when server binary is missing - this should show error, not silently pretend to work

---

## PR Strategy

Each phase creates a PR to `refactor/code-organization` branch:
1. Phase 1 PR → server submodule
2. Phase 2 PR → android submodule
3. Phase 3 PR → macos submodule
4. Phase 4 PR → parent repo (docs only)

Main repository PRs merge refactoring branches after all phase PRs are approved.
