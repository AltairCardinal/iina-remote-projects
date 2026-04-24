# IINA Remote API Protocol

## API Overview

The system uses two communication layers:

| Layer | Purpose | Transport |
|-------|---------|-----------|
| **HTTP API** | Go server ↔ Android/macOS clients | TCP (port 8765) |
| **IPC Protocol** | Go server ↔ IINA via mpv IPC socket | Unix socket (`/tmp/iina.sock`) |

---

## Authentication Flow

### Initial Pairing (Code-Based)

```
Client                        Server                       IINA
  |                             |                            |
  |--- GET /api/v1/pair/challenge -->                        |
  | <-- {challenge:"pair_required", expires_in:X} --------- |
  |                             |                            |
  |  [Display code on IINA's Mac screen]                   |
  |                             |                            |
  |-- POST /api/v1/pair ------- -->                         |
  |    {code, device_id, device_name, public_key?}          |
  |                             |                            |
  | <-- {token:JWT, expires_in:604800, server_name} ------- |
  |                             |                            |
```

### Reconnection (Challenge-Response)

```
Client                        Server
  |                             |
  |-- POST /api/v1/pair/challenge/generate?device_id=X --> |
  | <-- {challenge:CHALLENGE} ---------------------------- |
  |                             |
  |  [Sign challenge with private key]                    |
  |                             |
  |-- POST /api/v1/pair/reconnect --> |
  |    {device_id, challenge, signature, device_name}      |
  |                             |
  | <-- {token:JWT, expires_in:604800, server_name} ------ |
  |                             |
```

### JWT Authentication

Protected endpoints require `Authorization: Bearer <token>` header.

JWT payload structure:
```json
{
  "device_id": "string",
  "device_name": "string",
  "exp": 1234567890,
  "iat": 1234567890
}
```

---

## Public Endpoints (No Auth Required)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Basic health check |
| GET | `/api/v1/health` | Health check with IINA status |
| GET | `/api/v1/pair/challenge` | Get pairing challenge |
| POST | `/api/v1/pair` | Submit pairing code |
| POST | `/api/v1/pair/reconnect` | Challenge-response reconnect |
| GET | POST | `/api/v1/pair/challenge/generate` | Generate challenge for reconnect |

### Endpoint Details

#### GET /api/v1/pair/challenge

Response:
```json
{
  "challenge": "pair_required",
  "expires_in": 300
}
```

#### POST /api/v1/pair

Request:
```json
{
  "code": "123456",
  "device_id": "uuid-string",
  "device_name": "My Phone",
  "public_key": "base64-encoded-key (optional, macOS only)"
}
```

Response:
```json
{
  "token": "eyJhbGc...",
  "expires_in": 604800,
  "server_name": "MacBook-Pro"
}
```

#### POST /api/v1/pair/reconnect

Request:
```json
{
  "device_id": "uuid-string",
  "challenge": "server-generated-challenge",
  "signature": "base64-signature",
  "device_name": "My Phone"
}
```

Response: Same as `/api/v1/pair`

#### GET/POST /api/v1/pair/challenge/generate

Query params (GET): `?device_id=uuid-string`
Body (POST):
```json
{
  "device_id": "uuid-string"
}
```

Response:
```json
{
  "challenge": "random-challenge-string"
}
```

---

## Protected Endpoints (JWT Required)

### Status & Listing

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| GET | `/api/v1/status` | ✅ | ✅ | Full status + tracks |
| GET | `/api/v1/audio` | ✅ | ✅ | Audio tracks |
| GET | `/api/v1/subtitle` | ✅ | ✅ | Subtitle tracks |
| GET | `/api/v1/playlist` | ✅ | ✅ | Playlist entries |
| GET | `/api/v1/chapters` | ✅ | ✅ | Chapter list |
| GET | `/api/v1/browse` | ✅ | ✅ | File browser |
| GET | `/api/v1/visible-paths` | ✅ | ✅ | Allowed browse paths |

#### GET /api/v1/status Response

```json
{
  "playing": true,
  "position": 123.45,
  "duration": 3600.0,
  "speed": 1.0,
  "volume": 0.8,
  "subtitle_zoom": 100,
  "filename": "movie.mkv",
  "audio_tracks": [
    {
      "id": "0",
      "label": "Stereo",
      "is_default": true,
      "type": "audio",
      "lang": "en"
    }
  ],
  "subtitle_tracks": [
    {
      "id": "2",
      "label": "English [SDH]",
      "is_default": false,
      "is_off": false,
      "type": "sub",
      "lang": "en",
      "codec": "hdmv_pgs_subtitle"
    }
  ],
  "current_file": "/path/to/movie.mkv",
  "playlist": []
}
```

#### GET /api/v1/browse

Query params: `?path=/Volumes`

Response:
```json
{
  "path": "/Volumes",
  "parent": "",
  "entries": [
    {
      "name": "Macintosh HD",
      "type": "directory",
      "size": 0,
      "has_supported_content": true
    },
    {
      "name": "movie.mkv",
      "type": "video",
      "size": 1500000000,
      "has_supported_content": true
    }
  ]
}
```

File types: `directory`, `file`, `video`, `audio`, `image`, `subtitle`

---

### Playback Control

| Method | Path | Android | macOS | Body |
|--------|------|---------|-------|------|
| POST | `/api/v1/playback/play` | ✅ | ✅ | - |
| POST | `/api/v1/playback/pause` | ✅ | ✅ | - |
| POST | `/api/v1/playback/seek` | ✅ | ✅ | `{position: float}` (seconds) |
| POST | `/api/v1/playback/skip` | ✅ | ✅ | `{seconds: float}` (relative) |
| POST | `/api/v1/playback/speed` | ✅ | ✅ | `{speed: float}` (0.25-8.0) |
| POST | `/api/v1/playback/volume` | ✅ | ✅ | `{volume: float}` (0.0-1.0) |
| POST | `/api/v1/playback/mute` | ✅ | ✅ | - |
| POST | `/api/v1/playback/prev` | ✅ | ✅ | - |
| POST | `/api/v1/playback/next` | ✅ | ✅ | - |
| POST | `/api/v1/playback/loop/ab` | GET | ✅ | GET: - / POST: `{action: "set_a"|"set_b"|"clear"}` |

#### POST /api/v1/playback/seek

```json
{
  "position": 120.5
}
```

#### POST /api/v1/playback/skip

```json
{
  "seconds": 10.0
}
```
Positive = forward, Negative = backward.

#### POST /api/v1/playback/volume

```json
{
  "volume": 0.75
}
```

Volume is normalized to 0.0-1.0 on input. Server converts to 0-100 for IINA IPC.

#### GET /api/v1/playback/loop/ab

```json
{
  "a": 10.5,
  "b": 30.2,
  "active": true
}
```

#### POST /api/v1/playback/loop/ab

```json
{
  "action": "set_a"
}
```

---

### Playlist

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| POST | `/api/v1/playlist/jump/{index}` | ✅ | ✅ | Jump to index |

---

### Chapter Navigation

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| GET | `/api/v1/chapters` | ✅ | ✅ | List chapters |
| POST | `/api/v1/chapter/next` | ✅ | ✅ | Next chapter |
| POST | `/api/v1/chapter/prev` | ✅ | ✅ | Previous chapter |
| POST | `/api/v1/chapter/{index}` | ✅ | ✅ | Jump to chapter |

---

### Window Control

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| GET | `/api/v1/window/fullscreen` | ✅ | ✅ | Get fullscreen state |
| POST | `/api/v1/window/fullscreen` | ✅ | ✅ | Toggle fullscreen (no body) |
| POST | `/api/v1/window/ontop` | ❌ | ✅ | Toggle always on top |

---

### Track Switching

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| POST | `/api/v1/switch/audio/{id}` | ✅ | ✅ | Switch audio track |
| POST | `/api/v1/switch/subtitle/{id}` | ✅ | ✅ | Switch subtitle track |
| POST | `/api/v1/cycle/audio` | ✅ | ✅ | Cycle to next audio |
| POST | `/api/v1/cycle/subtitle` | ✅ | ✅ | Cycle to next subtitle |

Track `id` corresponds to the `id` field from `/api/v1/audio` or `/api/v1/subtitle` responses.

---

### Subtitle & Audio Delay

| Method | Path | Android | macOS | Body |
|--------|------|---------|-------|------|
| GET | `/api/v1/subtitle/delay` | ✅ | ✅ | - |
| POST | `/api/v1/subtitle/delay` | ✅ | ✅ | `{delta: int}` (ms) |
| GET | `/api/v1/audio/delay` | ✅ | ✅ | - |
| POST | `/api/v1/audio/delay` | ✅ | ✅ | `{delta: int}` (ms) |

#### GET /api/v1/subtitle/delay

```json
{
  "delay": 500.0
}
```

Returns delay in **milliseconds**.

#### POST /api/v1/subtitle/delay

```json
{
  "delta": 500
}
```

Delta is in **milliseconds**. Positive shifts subtitles later, negative earlier.

---

### Subtitle Zoom

| Method | Path | Android | macOS | Body |
|--------|------|---------|-------|------|
| POST | `/api/v1/subtitle/zoom/in` | ✅ | ✅ | - |
| POST | `/api/v1/subtitle/zoom/out` | ✅ | ✅ | - |
| POST | `/api/v1/subtitle/zoom/set` | ✅ | ✅ | `{scale: float}` |

---

### Screenshot

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| POST | `/api/v1/screenshot` | ❌ | ✅ | Capture screenshot |

---

### File Operations

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| POST | `/api/v1/open` | ✅ | ✅ | Open file in IINA |
| GET | `/api/v1/video/aspect` | ✅ | ✅ | Get aspect ratio |
| POST | `/api/v1/video/aspect` | ✅ | ✅ | Set aspect ratio |

#### POST /api/v1/open

Query params: `?path=/path/to/file.mkv`

---

### Server Management

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| GET | `/api/v1/server/name` | ✅ | ✅ | Get server name |
| PUT | `/api/v1/server/name` | ✅ | ✅ | Set server name |
| GET | `/api/v1/iina/status` | ✅ | ✅ | IINA process status |
| POST | `/api/v1/iina/restart` | ✅ | ✅ | Restart IINA |

#### PUT /api/v1/server/name

```json
{
  "name": "My-MacBook"
}
```

---

### System Volume (macOS only)

| Method | Path | Android | macOS | Body |
|--------|------|---------|-------|------|
| GET | `/api/v1/system/volume` | ❌ | ✅ | - |
| POST | `/api/v1/system/volume` | ❌ | ✅ | `{volume: int}` (0-100) |

---

### Device Management

| Method | Path | Android | macOS | Description |
|--------|------|---------|-------|-------------|
| GET | `/api/v1/devices` | ❌ | ❌ | List paired devices (internal) |
| DELETE | `/api/v1/devices/{deviceId}` | ❌ | ❌ | Remove device (internal) |

---

## Known Issues

### Volume API Inconsistency

**Issue**: Volume input/output range mismatch.

- **Input** (`/api/v1/playback/volume`): `0.0` to `1.0` (float)
- **Output** (`/api/v1/status`): `0` to `100` (int in `volume` field)

The server converts input `0.75` → IINA IPC `75`, but status returns raw IPC value.

**Workaround**: Clients should normalize the `volume` field from status by dividing by 100.

---

### Delay Unit Documentation

**Issue**: Subtitle and audio delay APIs use inconsistent units internally.

- GET endpoints return values in **milliseconds**
- IINA IPC internally uses **seconds**

The server handles the conversion, but this may cause confusion in debugging.

**Workaround**: Always use milliseconds when setting delays via POST endpoints.

---

### IINA IPC Fullscreen Property

**Issue**: mpv IPC does not expose a reliable way to query fullscreen state.

The server uses a workaround where it tracks toggle requests internally. The GET `/api/v1/window/fullscreen` endpoint may not reflect external changes made directly in IINA.

---

### Playlist Navigation with Single Item

**Issue**: Playlist navigation (`/api/v1/playback/prev`, `/api/v1/playback/next`, `/api/v1/playlist/jump`) only works when the playlist contains multiple items.

**Workaround**: Ensure at least two items are in the playlist before using navigation commands.

---

## Common Error Responses

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | `invalid_body` | Malformed JSON request body |
| 401 | `unauthorized` | Missing or invalid JWT |
| 403 | `forbidden` | Path access denied |
| 404 | `not_found` | Resource not found |
| 503 | `iina_unavailable` | IINA not running or IPC unavailable |
| 503 | `playback_failed` | Playback command failed |
| 503 | `seek_failed` | Seek operation failed |

Error response format:
```json
{
  "error": "error_code_string"
}
```

---

## IPC Protocol (mpv)

The server communicates with IINA via mpv's JSON IPC protocol over Unix socket `/tmp/iina.sock`.

Key commands:
- `play` / `pause` / `stop`
- `seek <position>`
- `set_property volume <0-100>`
- `cycle fullscreen`
- `sub-add` / `audio-add`

Key properties:
- `playback-time` (seconds)
- `duration` (seconds)
- `volume` (0-100)
- `pause` (bool)
- `fullscreen` (bool)
- `aid` / `sid` (audio/subtitle track IDs)

See [mpv-ipc-full-spec.md](./mpv-ipc-full-spec.md) for complete IPC reference.
