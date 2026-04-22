# mpv IPC Reference

## Overview

mpv provides a JSON-based IPC (Inter-Process Communication) interface over Unix domain sockets. IINA uses this IPC to communicate with its embedded mpv instance.

## Connection

- **Socket Path**: `/tmp/iina.sock` (configured in IINA)
- **Protocol**: JSON messages over Unix socket

## Message Format

Send JSON commands via socket:
```bash
echo '{"command":["<command>", <args>...],"request_id":1}' | nc -U /tmp/iina.sock
```

Response:
```json
{"data":<value>,"error":"success","request_id":1}
```

## Key Properties (Tested & Working)

| Property | Type | Description | Example |
|---------|------|-------------|---------|
| `mute` | bool | Mute state | `get_property mute` → `{"data":false}` |
| `pause` | bool | Pause state | `get_property pause` → `{"data":true}` |
| `volume` | double | Volume level (0-130) | `get_property volume` → `{"data":13.0}` |
| `sub-delay` | double | Subtitle delay (seconds) | `get_property sub-delay` → `{"data":0.0}` |
| `sub-scale` | double | Subtitle font scale (0.1-10.0) | `get_property sub-scale` → `{"data":1.0}` |
| `audio-delay` | double | Audio delay (seconds) | `get_property audio-delay` → `{"data":0.0}` |
| `playlist` | array | Full playlist | `get_property playlist` |
| `playlist-pos` | int | Current position | `get_property playlist-pos` → `{"data":0}` |
| `playlist-count` | int | Total items | `get_property playlist-count` |

## Key Commands

| Command | Description |
|---------|-------------|
| `command playlist-prev` | Previous track |
| `command playlist-next` | Next track |
| `command playlist-pos <n>` | Jump to position |
| `set_property <prop> <value>` | Set property |
| `add <prop> <delta>` | Add to property |

## Important Notes

### Mute Property
**Use `mute`, NOT `ao-mute`**
```json
{"command":["get_property","mute"]}
{"command":["set_property","mute",true]}
```

### Subtitle Delay (delta)
Use `add` command for relative changes:
```json
{"command":["add","sub-delay",0.5]}  // +500ms
{"command":["add","sub-delay",-0.5]} // -500ms
```

### Subtitle Scale
Use `set_property` for absolute values:
```json
{"command":["set_property","sub-scale",1.5]}
```

### Audio Delay (delta)
Use `add` command like subtitle delay:
```json
{"command":["add","audio-delay",0.1]}
```

### Playlist Commands
When playlist is empty, `playlist-prev/next` return `"error":"invalid parameter"`.

## Common Errors

| Error | Meaning |
|-------|---------|
| `property unavailable` | Property not available (no media loaded) |
| `invalid parameter` | Invalid command parameters |
| `error accessing property` | Property doesn't exist |

## Testing Commands

```bash
# Test connection
echo '{"command":["get_property","pause"]}' | nc -U /tmp/iina.sock

# Toggle mute
echo '{"command":["get_property","mute"]}' | nc -U /tmp/iina.sock
echo '{"command":["set_property","mute",true]}' | nc -U /tmp/iina.sock

# Navigate playlist
echo '{"command":["command","playlist-next"]}' | nc -U /tmp/iina.sock
echo '{"command":["get_property","playlist-pos"]}' | nc -U /tmp/iina.sock
```

## References

- Official mpv IPC docs: https://mpv.io/manual/master/#json-ipc
- mpv property list: https://mpv.io/manual/master/#properties
