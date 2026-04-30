# mpv JSON IPC Specification

Source: https://mpv.io/manual/master/#json-ipc

## Overview

mpv can be controlled by external programs using the JSON-based IPC protocol. It can be enabled by specifying the path to a unix socket or a named pipe using the option `--input-ipc-server`, or the file descriptor number of a unix socket or a named pipe using `--input-ipc-client`. Clients can connect to this socket and send commands to the player or receive events from it.

**Warning:** This is not intended to be a secure network protocol. It is explicitly insecure: there is no authentication, no encryption, and the commands themselves are insecure too. For example, the `run` command is exposed, which can run arbitrary system commands. The use-case is controlling the player locally.

---

## Usage Examples

### Socat example

You can use the socat tool to send commands (and receive replies) from the shell. Assuming mpv was started with:

```
mpv file.mkv --input-ipc-server=/tmp/mpvsocket
```

Then you can control it using socat:

```
> echo '{ "command": ["get_property", "playback-time"] }' | socat - /tmp/mpvsocket
{"data":190.482000,"error":"success"}
```

In this case, socat copies data between stdin/stdout and the mpv socket connection.

See the `--idle` option how to make mpv start without exiting immediately or playing a file.

It's also possible to send input.conf style text-only commands:

```
> echo 'show-text ${playback-time}' | socat - /tmp/mpvsocket
```

But you won't get a reply over the socket.

### Windows Command Prompt example

Assuming mpv was started with:

```
mpv file.mkv --input-ipc-server=\\.\pipe\mpvsocket
```

You can send commands from a command prompt:

```
echo show-text ${playback-time} >\\.\pipe\mpvsocket
```

---

## Protocol

The protocol uses UTF-8-only JSON as defined by RFC-8259. Unlike standard JSON, "\u" escape sequences are not allowed to construct surrogate pairs. To avoid getting conflicts, encode all text characters including and above codepoint U+0020 as UTF-8.

### Command Format

Clients can execute commands on the player by sending JSON messages of the following form:

```json
{ "command": ["command_name", "param1", "param2", ...] }
```

where `command_name` is the name of the command to be executed, followed by a list of parameters. Parameters must be formatted as native JSON values (integers, strings, booleans, ...). Every message **must** be terminated with `\n`. Additionally, `\n` must not appear anywhere inside the message. In practice this means that messages should be minified before being sent to mpv.

mpv will then send back a reply indicating whether the command was run correctly, and an additional field holding the command-specific return data (it can also be null).

```json
{ "error": "success", "data": null }
```

### Event Format

mpv will also send events to clients with JSON messages of the following form:

```json
{ "event": "event_name" }
```

where `event_name` is the name of the event. Additional event-specific fields can also be present. See [List of events](#list-of-events) for a list of all supported events.

### Request ID

Because events can occur at any time, it may be difficult at times to determine which response goes with which command. Commands may optionally include a `request_id` which, if provided in the command request, will be copied verbatim into the response. mpv does not interpret the `request_id` in any way; it is solely for the use of the requester.

For example, this request:

```json
{ "command": ["get_property", "time-pos"], "request_id": 100 }
```

Would generate this response:

```json
{ "error": "success", "data": 1.468135, "request_id": 100 }
```

If you don't specify a `request_id`, command replies will set it to 0.

### Message Delimiters

All commands, replies, and events are separated from each other with a line break character (`\n`).

If the first character (after skipping whitespace) is not `{`, the command will be interpreted as non-JSON text command, as they are used in input.conf (or `mpv_command_string()` in the client API). Additionally, lines starting with `#` and empty lines are ignored.

Currently, embedded 0 bytes terminate the current line, but you should not rely on this.

---

## Data Flow

Currently, the mpv-side IPC implementation does not service the socket while a command is executed and the reply is written. It is for example not possible that other events, that happened during the execution of the command, are written to the socket before the reply is written.

This might change in the future. The only guarantee is that replies to IPC messages are sent in sequence.

Also, since socket I/O is inherently asynchronous, it is possible that you read unrelated event messages from the socket, before you read the reply to the previous command you sent. In this case, these events were queued by the mpv side before it read and started processing your command message.

If the mpv-side IPC implementation switches away from blocking writes and blocking command execution, it may attempt to send events at any time.

---

## Asynchronous Commands

Command can be run asynchronously. This behaves exactly as with normal command execution, except that execution is not blocking. Other commands can be sent while it's executing, and command completion can be arbitrarily reordered.

The `async` field controls this. If present, it must be a boolean. If missing, false is assumed.

For example, this initiates an asynchronous command:

```json
{ "command": ["screenshot"], "request_id": 123, "async": true }
```

And this is the completion:

```json
{"request_id":123,"error":"success","data":null}
```

By design, you will not get a confirmation that the command was started. If a command is long running, sending the message will not lead to any reply until much later when the command finishes.

Some commands execute synchronously, but these will behave like asynchronous commands that finished execution immediately.

Cancellation of asynchronous commands is available in the libmpv API, but has not yet been implemented in the IPC protocol.

---

## Commands with Named Arguments

If the command field is a JSON object, named arguments are expected. This is described in the C API `mpv_command_node()` documentation (the `MPV_FORMAT_NODE_MAP` case). In some cases, this may make commands more readable, while some obscure commands basically require using named arguments.

Currently, only "proper" commands (as listed by List of Input Commands) support named arguments.

---

## IPC Commands

In addition to the commands described in List of Input Commands, a few extra commands can also be used as part of the protocol:

### client_name

Return the name of the client as string. This is the string `ipc-N` with N being an integer number.

### get_time_us

Return the current mpv internal time in microseconds as a number. This is basically the system time, with an arbitrary offset.

### get_property

Return the value of the given property. The value will be sent in the data field of the replay message.

Example:
```json
{ "command": ["get_property", "volume"] }
{ "data": 50.0, "error": "success" }
```

### get_property_string

Like `get_property`, but the resulting data will always be a string.

Example:
```json
{ "command": ["get_property_string", "volume"] }
{ "data": "50.000000", "error": "success" }
```

### set_property

Set the given property to the given value. See Properties for more information about properties.

Example:
```json
{ "command": ["set_property", "pause", true] }
{ "error": "success" }
```

### set_property_string

Alias for `set_property`. Both commands accept native values and strings.

### observe_property

Watch a property for changes. If the given property is changed, then an event of type `property-change` will be generated.

Example:
```json
{ "command": ["observe_property", 1, "volume"] }
{ "error": "success" }
{ "event": "property-change", "id": 1, "data": 52.0, "name": "volume" }
```

**Warning:** If the connection is closed, the IPC client is destroyed internally, and the observed properties are unregistered. This happens for example when sending commands to a socket with separate socat invocations. You must keep the IPC connection open to make it work.

### observe_property_string

Like `observe_property`, but the resulting data will always be a string.

Example:
```json
{ "command": ["observe_property_string", 1, "volume"] }
{ "error": "success" }
{ "event": "property-change", "id": 1, "data": "52.000000", "name": "volume" }
```

### unobserve_property

Undo `observe_property` or `observe_property_string`. This requires the numeric id passed to the observed command as argument.

Example:
```json
{ "command": ["unobserve_property", 1] }
{ "error": "success" }
```

### request_log_messages

Enable output of mpv log messages. They will be received as events. The parameter to this command is the log-level.

Log message output is meant for humans only (mostly for debugging). Attempting to retrieve information by parsing these messages will just lead to breakages with future mpv releases.

### enable_event, disable_event

Enables or disables the named event. Mirrors the `mpv_request_event` C API function. If the string `all` is used instead of an event name, all events are enabled or disabled.

By default, most events are enabled, and there is not much use for this command.

### get_version

Returns the client API version the C API of the remote mpv instance provides.

---

## UTF-8

Normally, all strings are in UTF-8. Sometimes it can happen that strings are in some broken encoding (often happens with file tags and such, and filenames on many Unixes are not required to be in UTF-8 either). This means that mpv sometimes sends invalid JSON. If that is a problem for the client application's parser, it should filter the raw data for invalid UTF-8 sequences and perform the desired replacement, before feeding the data to its JSON parser.

mpv will not attempt to construct invalid UTF-8 with broken "\u" escape sequences. This includes surrogate pairs.

---

## JSON Extensions

The following non-standard extensions are supported:

- a list or object item can have a trailing `,`
- object syntax accepts `=` in addition of `:`
- object keys can be unquoted, if they start with a character in `A-Za-z_` and contain only characters in `A-Za-z0-9_`
- byte escapes with `\xAB` are allowed (with AB being a 2 digit hex number)

Example:
```
{ objkey = "value\x0A" }
```

Is equivalent to:
```
{ "objkey": "value\n" }
```

---

## Alternative Ways of Starting Clients

You can create an anonymous IPC connection without having to set `--input-ipc-server`. This is achieved through a mpv pseudo scripting backend that starts processes.

You can put `.run` file extension in the mpv scripts directory in its config directory. These scripts are simply executed with the OS native mechanism. They must have a proper shebang and have the executable bit set.

When executed, a socket (the IPC connection) is passed to them through file descriptor inheritance. The file descriptor is indicated as the special command line argument `--mpv-ipc-fd=N`, where N is the numeric file descriptor.

This does not work in Windows yet.

---

## List of Events

This section describes what `mpv_event_to_node()` returns, which is what scripting APIs and the JSON IPC sees.

Note that events are asynchronous: the player core continues running while events are delivered to scripts and other clients.

All events can have the following fields:

- `event`: Name as the event
- `id`: The reply_userdata field (opaque user value). If reply_userdata is 0, the field is not added.
- `error`: Set to an error string. This field is missing if no error happened.

### start-file (MPV_EVENT_START_FILE)

Happens right before a new file is loaded. When you receive this, the player is loading the file (or possibly already done with it).

Fields:
- `playlist_entry_id`: Playlist entry ID of the file being loaded now.

### end-file (MPV_EVENT_END_FILE)

Happens after a file was unloaded.

Fields:
- `reason`: One of: `eof`, `stop`, `quit`, `error`, `redirect`, `unknown`
- `playlist_entry_id`: Playlist entry ID of the file that was being played
- `file_error`: Set to mpv error string describing why playback failed (if applicable)
- `playlist_insert_id`, `playlist_insert_num_entries`: For playlist redirects

### file-loaded (MPV_EVENT_FILE_LOADED)

Happens after a file was loaded and begins playback.

### seek (MPV_EVENT_SEEK)

Happens on seeking.

### playback-restart (MPV_EVENT_PLAYBACK_RESTART)

Start of playback after seek or after file was loaded.

### shutdown (MPV_EVENT_SHUTDOWN)

Sent when the player quits, and the script should terminate.

### log-message (MPV_EVENT_LOG_MESSAGE)

Receives messages enabled with `mpv_request_log_messages()`.

Fields:
- `prefix`: The module prefix
- `level`: The log level as string
- `text`: The log message (ends with newline)

### hook (MPV_EVENT_HOOK)

Hooks are synchronous events between player core and a script.

Fields:
- `hook_id`: ID to pass to `mpv_hook_continue()`

### property-change (MPV_EVENT_PROPERTY_CHANGE)

Happens when a property that is being observed changes value.

Fields:
- `name`: The name of the property
- `data`: The new value of the property

### client-message (MPV_EVENT_CLIENT_MESSAGE)

The event has the following fields:
- `args`: Array of strings with the message data

### video-reconfig (MPV_EVENT_VIDEO_RECONFIG)

Happens on video output or filter reconfig.

### audio-reconfig (MPV_EVENT_AUDIO_RECONFIG)

Happens on audio output or filter reconfig.

---

## Error Codes

The `error` field in command responses contains either the string `"success"` indicating successful execution, or an error message string describing what went wrong.

Examples of error responses:
```json
{ "error": "success", "data": null }
{ "error": "success", "data": 1.468135, "request_id": 100 }
{ "error": "property not found", "data": null }
```

---

## Common Properties

Properties can be queried with `get_property` and modified with `set_property`.

### Playback Properties

- `pause` (RW): Pause state
- `playback-time` (RW): Current playback position in seconds
- `volume` (RW): Volume level (0-100)
- `mute` (RW): Mute state
- `speed` (RW): Playback speed
- `time-pos` (R): Current position in seconds
- `duration` (R): Total duration in seconds
- `percent-pos` (R): Position as percentage
- `volume-max` (R): Maximum volume
- `metadata` (R): Metadata

### Track Properties

- `audio` (RW): Selected audio track
- `video` (RW): Selected video track
- `sub` (RW): Selected subtitle track
- `track-list` (R): List of all tracks

### File Properties

- `filename` (R): Currently played file name
- `path` (R): Full file path
- `media-title` (R): Media title

### Information Properties

- `avsync` (R): A/V sync difference
- `total-avsync-change` (R): Total A/V sync changes
- `frame-drop-count` (R): Number of dropped frames
- `decoder-frame-drop-count` (R): Decoder dropped frames

### See Also

For a complete list of properties, see: https://mpv.io/manual/master/#properties

---

## Common Commands

### Playback Commands

- `play`: Start playback
- `pause`: Pause playback
- `stop`: Stop playback
- `seek <target> [flags]`: Seek to position
- `revert-seek`: Revert last seek
- `frame-step`: Advance one frame
- `frame-back-step`: Go back one frame

### Playlist Commands

- `playlist-next [weak]`: Go to next entry
- `playlist-prev [weak]`: Go to previous entry
- `playlist-play-index <index>`: Play entry at index
- `loadfile <file> [replace|append]`: Load a file

### Property Commands

- `set <property> <value>`: Set property value
- `add <property> <delta>`: Add delta to property
- `cycle <property> [up|down]`: Cycle property value
- `multiply <property> <factor>`: Multiply property

### See Also

For a complete list of commands, see: https://mpv.io/manual/master/#list-of-input-commands
