# AGENTS.md

## Repo layout

Each top-level dir (`server/`, `macos/`, `android/`, `figma/`) is a **separate git submodule**. Changes inside a submodule must be committed in both the submodule and the parent repo.

## Build order matters

The macOS app's post-build script copies `server/iina-remote-server` into the app bundle. **Build server first**, then macos.

```bash
# Server (universal binary: Intel + Apple Silicon)
cd server && ./BUILD.sh
# OR quick single-arch build:
cd server && go build -o iina-remote-server .

# macOS (requires XcodeGen + Xcode 15+)
cd macos && xcodegen generate && xcodebuild -project IINARemote.xcodeproj -scheme IINARemote -configuration Debug build

# Android (JDK 21, minSdk 26, targetSdk 35)
cd android && ./gradlew assembleDebug
```

## Go server quirks

- `BUILD.sh` sets `GOPROXY=https://goproxy.cn,direct` and `GOSUMDB=off` (China mirror). Override if needed.
- `BUILD.sh` expects Go at `$HOME/go/go/bin/go`, not system Go.
- The binary is ad-hoc codesigned in the macOS post-build script; without this, macOS Hardened Runtime blocks the Go server.
- Server also listens on `port+1` (127.0.0.1 only) for an internal pair-code endpoint.

## No tests or lint exist

There are **zero tests** and no lint/typecheck/CI configs in any sub-project. Run builds to verify.

## TDD workflow (mandatory)

**Any development must follow strict Red-Green TDD:**

1. **Plan first** — before writing any code, plan the complete test flow: what to test, edge cases, test order.
2. **Red** — write a failing test that captures the expected behavior.
3. **Green** — write the minimal code to make the test pass.
4. **Refactor** — clean up while keeping tests green.
5. **Repeat** — incrementally add tests and implementation.

Do not write production code without a corresponding failing test. Do not skip the planning step.

## macOS app specifics

- LSUIElement app (no Dock icon). Uses XcodeGen (`project.yml`) to generate `.xcodeproj`.
- If `.xcodeproj` already exists, `xcodegen generate` will overwrite it.
- `project.yml` includes `MACOSX_DEPLOYMENT_TARGET: "13.0"`, `SWIFT_VERSION: "5.9"`.
- After building, copy the app to `/Applications` for daily use:
  ```bash
  cp -r macos/build/Debug/IINA\ Remote.app /Applications/
  ```

## Android app specifics

- Kotlin, Jetpack Compose, single-activity with Compose Navigation.
- Uses version catalog (`gradle/libs.versions.toml`) for dependencies.
- `compileSdk = 35`, Java 21 compatibility.

## Key docs to read before editing

| File | Why |
|------|-----|
| `docs/CONTROL_METHODS.md` | Explains IPC socket vs AppleScript dual-control approach |
| `docs/SPEC.md` | Full feature spec |
| `server/README.md` | All API endpoints and pairing flow |

## Figma prototype must stay in sync

`figma/index.html` is an interactive HTML prototype. **Whenever Android app interactions change (UI layout, navigation flow, control behavior, screen structure), the same changes must be applied to `figma/index.html`** so the prototype always matches the real app.

## IINA is required at runtime

The Go server talks to IINA via IPC socket at `localhost:8080`. IINA must be launched with `--input-ipc-server` or have IPC enabled in IINA → Settings → Advanced.
