# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

IINA Remote is a system for controlling the IINA media player (macOS) from an Android phone over a local network. It consists of four sub-projects:

```
Android App  <--HTTP REST / JWT-->  Go Server  <--IPC socket / AppleScript-->  IINA (mpv)
  (Kotlin)                        (Go :8765)     (localhost:8080 IPC)
                                        ^
                                macOS Menu Bar App
                                 (Swift/AppKit)
```

## Build Commands

### Go Server

```bash
cd server/
./BUILD.sh                    # Universal binary (Intel + Apple Silicon)
go build -o iina-remote-server .  # Simple build (current arch only)
go run . --port 8765 --pairing-dir ~/Library/ApplicationSupport/IINARemote --iina-url http://localhost:8080
```

### macOS Menu Bar App

```bash
cd macos/
xcodegen generate             # Generate .xcodeproj from project.yml
xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build
```

Requirements: macOS 13.0+, Xcode 15.0+. The XcodeGen `project.yml` includes a post-build script that copies the Go server binary into the app bundle and ad-hoc signs it.

### Android App

```bash
cd android/
./gradlew assembleDebug       # Build debug APK -> app/build/outputs/apk/debug/app-debug.apk
./gradlew installDebug        # Build and install on connected device
adb install app/build/outputs/apk/debug/app-debug.apk
```

Min SDK 26, target/compile SDK 35.

### No tests exist yet in any sub-project.

## Architecture

### Server (Go) — `server/`

- **`main.go`** — CLI flags (`--port`, `--pairing-dir`, `--iina-url`), router setup (gorilla/mux), graceful shutdown. Routes are organized as: public endpoints (`/health`, `/api/v1/pair/*`) and protected endpoints (`/api/v1/*` with JWT auth middleware).
- **`auth/jwt.go`** — Pairing flow (6-char alphanumeric code), JWT token generation (7-day validity), rate limiting (5 attempts then 30s lockout), device management. Token store persisted in `devices.json` in the pairing directory.
- **`handler/`** — HTTP handlers split by domain:
  - `health.go` — Health check + pairing endpoints + `RequireAuth` middleware
  - `playback.go` — Play, pause, seek, skip, speed, volume, mute, AB loop, playlist
  - `media.go` — Audio/subtitle track listing, switching, cycling, screenshot
  - `browse.go` — Directory browsing and file opening (path security via `VisiblePaths`)
  - `chapter.go` — Chapter navigation (experimental)
  - `video.go` — Aspect ratio cycling
  - `window.go` — Fullscreen and always-on-top toggle
- **`iina/applescript.go`** — All IINA interaction via two mechanisms:
  1. **Unix IPC socket** (`/tmp/iina.sock`) — preferred for reading playback state, position, duration, volume, playlist data
  2. **AppleScript/System Events** — used for sending commands (play/pause/seek via key codes) and reading track lists from IINA's menu bar UI. Requires macOS Accessibility permissions.

### macOS App (Swift) — `macos/`

- LSUIElement app (menu bar only, no Dock icon)
- **`AppDelegate.swift`** — Startup: permissions check → IINA launch → server start
- **`StatusBarController.swift`** — Menu bar UI, polls server `/api/v1/pair/challenge` every 5s for pairing code display
- **`HTTPServerManager.swift`** — Manages Go server process lifecycle (launch, monitor, restart)
- **`PairingManager.swift`** — Pairing state management
- **`SettingsManager.swift`** — Port and visible directory settings, writes `settings.json` read by Go server on startup
- **`PermissionsManager.swift`** — TCC permission checks (Accessibility, etc.)
- **`PairingOverlayWindow.swift`** — Floating NSPanel showing pairing code on screen

### Android App (Kotlin) — `android/`

- Single-activity architecture with Jetpack Compose Navigation
- **`data/api/`** — Retrofit API interface (`IinaApiService.kt`), client builder (`ApiClient.kt`), request/response models (`ApiModels.kt`)
- **`data/model/`** — Domain models (Track, etc.)
- **`data/ConnectionStore.kt`** — Saved server connections
- **`domain/IinaRepository.kt`** — Business logic / data layer
- **`navigation/`** — Route definitions and NavHost
- **`ui/components/`** — Reusable composables (sheets, bars, lists)
- **`ui/screens/`** — Screen composables + ViewModels (Main, Pairing, SubAudio, Browse, App)

### Figma Plugin — `figma/`

- `code.js` / `ui.html` — Figma plugin for generating UI screens
- `.sketch` files — Design source files

## Key Design Decisions

- **Dual IINA control**: IPC socket for reads (fast, reliable), AppleScript for writes and menu UI access (requires Accessibility permission). See `docs/CONTROL_METHODS.md` for detailed rationale.
- **File browsing security**: `browse` endpoint restricts access to `VisiblePaths` (defaults to `/Volumes` and user home). Configured via macOS app's `SettingsManager` → `settings.json`.
- **Each sub-project has its own `.git`** — originally separate repositories collected into this workspace.
- **IINA must have IPC enabled**: IINA → Settings → Advanced → Enable IPC Server, or launch with `--input-ipc-server`.

## Documentation Map

- `docs/SPEC.md` — Complete feature specification
- `docs/CONTROL_METHODS.md` — IINA control methods reference (IPC vs AppleScript)
- `docs/IMPLEMENTATION_PLAN.md` — Development plan
- `docs/PROGRESS.md` — Development progress log
- `docs/DEPLOY.md` — Deployment guide
- `server/README.md` — Server deployment and API docs
- `macos/README.md` — macOS app development guide
- `android/README.md` — Android app development guide
