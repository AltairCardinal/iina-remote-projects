# mpv IPC Documentation

Source: https://mpv.io/manual/master/

## Overview

mpv provides a JSON-based IPC (Inter-Process Communication) interface over Unix domain sockets or named pipes. This allows external programs to control mpv programmatically.

## Documents

| File | Description | Size |
|------|-------------|------|
| [01_protocol.md](01_protocol.md) | JSON IPC Protocol - message format, commands, events | 12KB |
| [02_properties.md](02_properties.md) | Properties Reference - all mpv properties | 25KB |
| [03_commands.md](03_commands.md) | Input Commands Reference - all commands | 57KB |
| [04_events.md](04_events.md) | Events Reference - all event types | 6KB |

## Quick Reference

### Connection

```bash
# Unix socket
mpv file.mkv --input-ipc-server=/tmp/mpvsocket

# Send command
echo '{"command":["get_property", "pause"]}' | socat - /tmp/mpvsocket
```

### Common Operations

```json
// Get property
{ "command": ["get_property", "property-name"] }

// Set property
{ "command": ["set_property", "property-name", value] }

// Execute command
{ "command": ["command_name", "param1", "param2"] }

// Observe property changes
{ "command": ["observe_property", id, "property-name"] }
```

## Key Concepts

- **Properties** - Read/write player state (volume, pause, position, etc.)
- **Commands** - Execute actions (seek, screenshot, loadfile, etc.)
- **Events** - Subscribe to state changes (file loaded, seek happened, etc.)