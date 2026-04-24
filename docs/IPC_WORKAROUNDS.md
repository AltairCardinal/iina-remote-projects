# IINA IPC Workarounds

IINA is an mpv-based media player for macOS. The Go server communicates with IINA via mpv's IPC socket at `/tmp/iina.sock`.

## Standard mpv IPC Format

According to the mpv IPC specification, the correct format for loading a file is:

```json
{"command": ["loadfile", "/path/to/file", "replace"]}
```

However, IINA has multiple bugs that cause this command to fail.

## Known IINA IPC Bugs

### Issue #629 (Open Since 2017)
- **Problem**: NIL window crash when loading files via IPC
- **Impact**: App may crash when opening files
- **URL**: https://github.com/iina/iina/issues/629

### Issue #2809
- **Problem**: Video output fails to initialize with IPC loadfile
- **Impact**: Black screen when opening files via IPC
- **URL**: https://github.com/iina/iina/issues/2809

### Issue #4478
- **Problem**: IPC triggers new instance launch loop
- **Impact**: Multiple IINA windows open
- **URL**: https://github.com/iina/iina/issues/4478

### Issue #5996 (April 2026)
- **Problem**: Player hangs on URL open via IPC
- **Impact**: App becomes unresponsive
- **URL**: https://github.com/iina/iina/issues/5996

## The Workaround

Instead of the spec-correct format:

```json
{"command": ["loadfile", "/path/to/file", "replace"]}
```

The server uses a wrapped format:

```json
{"command": ["command", "loadfile", "/path/to/file", "replace"]}
```

The `command` wrapper invokes mpv's input command processing, which happens to work around these IINA-specific bugs.

## Why It Works

The wrapped format `["command", "loadfile", ...]` invokes mpv's input.conf style command processor. This processes the inner command differently than the direct JSON command format, bypassing the code paths where IINA's bugs occur.

This is an IINA/mpv interaction quirk, not a standards-compliant approach.

## Impact on Development

- **Android app**: Cannot open files when using spec-correct format; requires the workaround
- **macOS app**: Uses AppleScript fallback when IPC fails due to these issues
- **Server**: Must maintain the workaround for compatibility with IINA

## Code Location

The workaround is implemented in the server's IPC handling code. Search for `command` wrapper usage in the server codebase for the specific implementation.
