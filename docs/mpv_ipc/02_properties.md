# mpv Properties Reference

Source: https://mpv.io/manual/master/#properties

## Property Access Commands

Properties can be manipulated using these commands:

### set

```
set <name> <value>
```

Set the given property or option to the given value.

### del

```
del <name>
```

Delete the given property. Most properties cannot be deleted.

### add

```
add <name> [<value>]
```

Add the given value to the property or option. On overflow or underflow, clamp the property to the maximum. If `<value>` is omitted, assume 1.

Whether or not key-repeat is enabled by default depends on the property. Currently properties with continuous values are repeatable by default (like volume), while discrete values are not (like osd-level).

### multiply

```
multiply <name> <value>
```

Similar to add, but multiplies the property or option with the numeric value.

### cycle

```
cycle <name> [<value>]
```

Cycle the given property or option. The second argument can be up or down to set the cycle direction. On overflow, set the property back to the minimum, on underflow set it to the maximum. If up or down is omitted, assume up.

Whether or not key-repeat is enabled by default depends on the property. Currently properties with continuous values are repeatable by default (like volume), while discrete values are not (like osd-level).

### cycle-values

```
cycle-values [<"!reverse">] <property> <value1> [<value2> [...]]
```

Cycle through a list of values. Each invocation of the command will set the given property to the next value in the list. The command will use the current value of the property/option, and use it to determine the current position in the list of values. Once it has found it, it will set the next value in the list (wrapping around to the first item if needed).

The special argument `!reverse` can be used to cycle the value list in reverse.

## Properties Overview

Properties are used to set mpv options during runtime, or to query arbitrary information. They can be manipulated with the set/add/cycle commands, and retrieved with show-text, or anything else that uses property expansion.

If an option is referenced, the property will normally take/return exactly the same values as the option. In these cases, properties are merely a way to change an option at runtime.

Note that many properties are unavailable at startup.

## Property List

**Note:** Most options can be set at runtime via properties as well. Just remove the leading `--` from the option name. These are not documented below. Only properties which do not exist as option with the same name, or which have very different behavior from the options are documented below.

Properties marked as **(RW)** are writeable, while those that aren't are read-only.

---

### Playback Properties

#### audio-speed-correction, video-speed-correction

Factor multiplied with speed at which the player attempts to play the file. Usually it's exactly 1. (Display sync mode will make this useful.)

OSD formatting will display it in the form of +1.23456%, with the number being (raw - 1) \* 100 for the given raw property value.

#### display-sync-active

Whether `--video-sync=display` is actually active.

#### percent-pos (RW)

Position in current file (0-100). The advantage over using this instead of calculating it out of other properties is that it properly falls back to estimating the playback position from the byte position, if the file duration is not known.

#### time-pos (RW)

Position in current file in seconds.

**Sub-property:** `time-pos/full` - time-pos with milliseconds.

#### time-remaining

Remaining length of the file in seconds. Note that the file duration is not always exactly known, so this is an estimate.

**Sub-property:** `time-remaining/full` - time-remaining with milliseconds.

#### audio-pts

Current audio playback position in current file in seconds. Unlike time-pos, this updates more often than once per frame.

**Sub-property:** `audio-pts/full` - audio-pts with milliseconds.

#### playtime-remaining

time-remaining scaled by the current speed.

**Sub-property:** `playtime-remaining/full` - playtime-remaining with milliseconds.

#### playback-time (RW)

Alias for time-pos.

**Sub-property:** `playback-time/full` - playback-time with milliseconds.

#### remaining-file-loops

How many more times the current file is going to be looped. This is initialized from the value of `--loop-file`. -1 corresponds to infinity.

#### remaining-ab-loops

How many more times the current A-B loop is going to be looped, if one is active. This is initialized from the value of `--ab-loop-count`. -1 corresponds to infinity.

#### chapter (RW)

Current chapter number. The number of the first chapter is 0. A value of -1 indicates that the current playback position is before the start of the first chapter.

Setting this property results in an absolute seek to the start of the chapter.

#### edition (RW)

Current edition number. Setting this property to a different value will restart playback. The number of the first edition is 0.

#### current-edition

Currently selected edition. This property is unavailable if no file is loaded, or the file has no editions.

#### chapters

Number of chapters.

#### editions

Number of editions.

#### edition-list

List of editions, current entry marked.

**Sub-properties:**
- `edition-list/count` - Number of editions
- `edition-list/N/id` - Edition ID as integer
- `edition-list/N/default` - Whether this is the default edition
- `edition-list/N/title` - Edition title as stored in the file
- `edition-list/N/metadata` - Per-edition metadata key/value pairs

#### avsync

Last A/V synchronization difference. Unavailable if audio or video is disabled.

#### total-avsync-change

Total A-V sync correction done. Unavailable if audio or video is disabled.

#### decoder-frame-drop-count

Video frames dropped by decoder, because video is too far behind audio.

#### frame-drop-count

Frames dropped by VO (when using `--framedrop=vo`).

#### mistimed-frame-count

Number of video frames that were not timed correctly in display-sync mode.

#### vsync-ratio

For how many vsyncs a frame is displayed on average. Available if display-sync is active only.

#### vo-delayed-frame-count

Estimated number of frames delayed due to external circumstances in display-sync mode.

#### duration

Duration of the current file in seconds. If the duration is unknown, the property is unavailable.

**Sub-property:** `duration/full` - duration with milliseconds.

#### filename

Currently played file, with path stripped. If this is an URL, try to undo percent encoding as well.

**Sub-property:** `filename/no-ext` - Like filename, but strips extension.

#### file-size

Length in bytes of the source file/stream.

#### estimated-frame-count

Total number of frames in current file. This is only an estimate.

#### estimated-frame-number

Number of current frame in current stream. This is only an estimate.

#### path

Full absolute path of the currently played file.

#### media-title

If the currently played file has a title tag, use that. Otherwise, return the filename property.

#### file-format

Symbolic name of the file format.

#### current-demuxer

Name of the current demuxer.

#### stream-path

Filename (full path) of the stream layer filename.

#### stream-pos

Raw byte position in source stream.

#### stream-end

Raw end position in bytes in source stream.

#### seekable

Whether it's generally possible to seek in the current file.

#### partially-seekable

Whether the current file is considered seekable, but only because the cache is active.

#### playback-abort

Whether playback is stopped or is to be stopped.

---

### Track Properties

#### track-list

List of audio/video/sub tracks, current entry marked.

**Sub-properties:**
- `track-list/count` - Total number of tracks
- `track-list/video` - List of video tracks
- `track-list/audio` - List of audio tracks
- `track-list/sub` - List of subtitle tracks
- `track-list/N/id` - Track ID
- `track-list/N/type` - String describing media type (audio, video, sub)
- `track-list/N/src-id` - Track ID in source file
- `track-list/N/title` - Track title
- `track-list/N/lang` - Track language
- `track-list/N/image` - Whether this is a video track that consists of a single picture
- `track-list/N/albumart` - Whether this is an image embedded in an audio file
- `track-list/N/default` - Whether track has default flag
- `track-list/N/forced` - Whether track has forced flag
- `track-list/N/dependent` - Whether track has dependent flag
- `track-list/N/visual-impaired` - Whether track has visual impaired flag
- `track-list/N/hearing-impaired` - Whether track has hearing impaired flag
- `track-list/N/codec` - Codec name (e.g., h264)
- `track-list/N/codec-desc` - Codec descriptive name
- `track-list/N/codec-profile` - Codec profile
- `track-list/N/external` - Whether track is from external file
- `track-list/N/external-filename` - Filename if external track
- `track-list/N/selected` - Whether track is currently decoded
- `track-list/N/format-name` - Short name for format
- `track-list/N/demux-w, demux-h` - Video size hint from container
- `track-list/N/demux-crop-*` - Crop parameters
- `track-list/N/demux-channel-count` - Audio channel count from container
- `track-list/N/demux-samplerate` - Audio sample rate from container
- `track-list/N/demux-fps` - Video FPS from container
- `track-list/N/demux-bitrate` - Average bitrate in bits per second
- `track-list/N/demux-rotation` - Video rotation in degrees
- `track-list/N/demux-duration` - Track duration from container

#### current-tracks/...

Gives access to currently selected tracks. Redirects to the correct entry in track-list.

The following sub-entries are defined: video, audio, sub, sub2

Example: `current-tracks/audio/lang` returns the current audio track's language.

#### chapter-list (RW)

List of chapters, current entry marked.

**Sub-properties:**
- `chapter-list/count` - Number of chapters
- `chapter-list/N/title` - Chapter title
- `chapter-list/N/time` - Chapter start time in seconds

---

### Audio Properties

#### audio-params

Audio format as output by the audio decoder.

**Sub-properties:**
- `audio-params/format` - Sample format as string
- `audio-params/samplerate` - Samplerate
- `audio-params/channels` - Channel layout as string
- `audio-params/hr-channels` - Human readable channel layout
- `audio-params/channel-count` - Number of audio channels

#### audio-out-params

Same as audio-params, but the format of the data written to the audio API.

#### ao-volume (RW)

System volume. This property is available only if mpv audio output is currently active, and only if the underlying implementation supports volume control.

#### ao-mute (RW)

Similar to ao-volume, but controls the mute state.

#### mixer-active

Whether the audio mixer is active.

#### audio-device (RW)

Set the audio device. This directly reads/writes the `--audio-device` option.

#### audio-device-list

The list of discovered audio devices.

#### current-ao

Current audio output driver (name as used with `--ao`).

#### audio-speed-correction

See Playback Properties.

#### video-speed-correction

See Playback Properties.

#### audio-bitrate

Bitrate calculated on packet level. Unit is bits per second.

#### sub-bitrate

Bitrate calculated on packet level for subtitles.

---

### Video Properties

#### width, height

Video size. This uses the size of the video as decoded, or if no video frame has been decoded yet, the (possibly incorrect) container indicated size.

#### dwidth, dheight

Video display size after filters and aspect scaling have been applied.

#### video-params

Video parameters, as output by the decoder (with overrides like aspect etc. applied).

**Sub-properties:**
- `video-params/pixelformat` - Pixel format
- `video-params/hw-pixelformat` - Underlying pixel format for hardware decoding
- `video-params/average-bpp` - Average bits-per-pixel
- `video-params/w, video-params/h` - Video size integers
- `video-params/dw, video-params/dh` - Scaled video size for correct aspect
- `video-params/crop-x, crop-y, crop-w, crop-h` - Crop parameters
- `video-params/aspect` - Display aspect ratio as double
- `video-params/aspect-name` - Display aspect ratio name
- `video-params/par` - Pixel aspect ratio
- `video-params/sar` - Storage aspect ratio
- `video-params/colormatrix` - Colormatrix in use
- `video-params/colorlevels` - Colorlevels
- `video-params/primaries` - Primaries
- `video-params/gamma` - Gamma function
- `video-params/light` - Light type
- `video-params/chroma-location` - Chroma location
- `video-params/rotate` - Intended display rotation in degrees
- `video-params/stereo-in` - Source file stereo 3D mode
- `video-params/alpha` - Alpha type
- `video-params/min-luma, max-luma` - Luminance from HDR10 metadata (cd/m²)
- `video-params/max-cll` - Maximum content light level (cd/m²)
- `video-params/max-fall` - Maximum frame average light level (cd/m²)
- `video-params/scene-max-r/g/b` - MaxRGB for HDR10+ metadata
- `video-params/max-pq-y, avg-pq-y` - PQ luminance from peak detection
- `video-params/prim-*-x, prim-*-y` - Chromaticity coordinates

#### video-dec-params

Exactly like video-params, but no overrides applied.

#### video-out-params

Same as video-params, but after video filters have been applied.

#### video-target-params

Same as video-params, but with the target properties that VO outputs to.

#### video-frame-info

Approximate information of the current frame.

**Sub-properties:**
- `video-frame-info/picture-type` - I, P, B or unavailable
- `video-frame-info/interlaced` - Whether content is interlaced
- `video-frame-info/tff` - Whether top field is displayed first
- `video-frame-info/repeat` - Whether frame must be delayed when decoding
- `video-frame-info/gop-timecode` - GOP timecode
- `video-frame-info/smpte-timecode` - SMPTE timecode
- `video-frame-info/estimated-smpte-timecode` - Estimated timecode

#### container-fps

Container FPS. This can easily contain bogus values.

#### estimated-vf-fps

Estimated/measured FPS of the video filter chain output.

#### hwdec (RW)

Reflects the `--hwdec` option. Writing may change the currently used hardware decoder.

#### hwdec-current

The current hardware decoding in use. `no` indicates software decoding.

#### hwdec-interop

Returns the currently loaded hardware decoding/output interop driver.

#### current-window-scale (RW)

The window-scale value calculated from the current window size.

#### current-vo

Current video output driver (name as used with `--vo`).

#### current-gpu-context

Current GPU context of video output driver.

#### colormatrix

Redirects to video-params/colormatrix.

#### colormatrix-input-range

See colormatrix.

#### colormatrix-primaries

See colormatrix.

#### deinterlace-active

Returns yes/true if mpv's deinterlacing filter is active.

#### video-bitrate

Bitrate calculated on packet level for video.

#### focused

Whether the window has focus.

#### vo-configured

Whether the VO is configured right now.

#### vo-passes

Contains introspection about the VO's active render passes.

**Sub-properties:**
- `vo-passes/TYPE/count` - Number of passes
- `vo-passes/TYPE/N/desc` - Human-friendly description
- `vo-passes/TYPE/N/last` - Last measured execution time in nanoseconds
- `vo-passes/TYPE/N/avg` - Average execution time in nanoseconds
- `vo-passes/TYPE/N/peak` - Peak execution time in nanoseconds
- `vo-passes/TYPE/N/count` - Number of samples

#### perf-info

Further performance data.

#### display-swapchain

Direct3D 11 swapchain address (int64).

---

### Subtitle Properties

#### sub-ass-extradata

The current ASS subtitle track's extradata.

#### sub-text

The current subtitle text regardless of sub visibility. Formatting is stripped.

**Sub-properties:**
- `sub-text/ass` - Return text in ASS format
- `sub-text/ass-full` - Return full event with all fields

#### secondary-sub-text

Same as sub-text, but for secondary subtitles.

#### sub-start

The current subtitle start time (in seconds).

**Sub-property:** `sub-start/full` - sub-start with milliseconds.

#### secondary-sub-start

Same as sub-start, but for secondary subtitles.

#### sub-end

The current subtitle end time (in seconds).

**Sub-property:** `sub-end/full` - sub-end with milliseconds.

#### secondary-sub-end

Same as sub-end, but for secondary subtitles.

---

### Playlist Properties

#### playlist-pos (RW)

Current position on playlist. The first entry is on position 0.

#### playlist-pos-1 (RW)

Same as playlist-pos, but 1-based.

#### playlist-current-pos (RW)

Index of the "current" item on playlist.

#### playlist-playing-pos

Index of the "playing" item on playlist.

#### playlist-count

Number of total playlist entries.

#### playlist-path

The original path of the playlist for the current entry.

#### playlist

Playlist, current entry marked.

**Sub-properties:**
- `playlist/count` - Number of playlist entries
- `playlist/N/filename` - Filename of the Nth entry
- `playlist/N/playing` - yes/true if this entry is playing
- `playlist/N/current` - yes/true if this entry is current
- `playlist/N/title` - Name of the Nth entry
- `playlist/N/id` - Unique ID for this entry
- `playlist/N/playlist-path` - Original playlist path

---

### Metadata Properties

#### metadata

Metadata key/value pairs.

**Sub-properties:**
- `metadata/by-key/<key>` (RW) - Value of metadata entry
- `metadata/list/count` - Number of metadata entries
- `metadata/list/N/key` - Key name of Nth entry
- `metadata/list/N/value` - Value of Nth entry
- `metadata/<key>` - Old version of metadata/by-key/<key>

#### filtered-metadata

Like metadata, but includes only fields listed in `--display-tags`.

#### chapter-metadata

Metadata of current chapter. Works similar to metadata property.

#### vf-metadata/<filter-label>

Metadata added by video filters.

#### af-metadata/<filter-label>

Metadata added by audio filters. Equivalent to vf-metadata for audio.

---

### Filter Properties

#### af, vf (RW)

Audio/video filters. See `--vf`/`--af` and the vf/af command.

---

### Window Properties

#### display-names

Names of the displays that the mpv window covers.

#### display-fps

The refresh rate of the current display.

#### estimated-display-fps

The actual rate at which display refreshes seem to occur.

#### display-width, display-height

The current display's horizontal and vertical resolution in pixels.

#### display-hidpi-scale

The HiDPI scale factor as reported by the windowing backend.

#### osd-width, osd-height

Last known OSD width/height.

#### osd-par

Last known OSD display pixel aspect.

#### osd-dimensions

Last known OSD dimensions.

**Sub-properties:**
- `osd-dimensions/w` - VO window width in OSD render units
- `osd-dimensions/h` - VO window height in OSD render units
- `osd-dimensions/par` - Pixel aspect ratio of the OSD
- `osd-dimensions/aspect` - Display aspect ratio of the VO window
- `osd-dimensions/mt, mb, ml, mr` - OSD to video margins

#### term-size

The current terminal size.

**Sub-properties:**
- `term-size/w` - width of terminal in cells
- `term-size/h` - height of terminal in cells

#### window-id

mpv's window id. May not always be available.

#### mouse-pos

Read-only - last known mouse position, normalized to OSD dimensions.

**Sub-properties:**
- `mouse-pos/x, mouse-pos/y` - Last known coordinates
- `mouse-pos/hover` - Boolean - whether mouse hovers video window

#### touch-pos

Read-only - last known touch point positions, normalized to OSD dimensions.

#### tablet-pos

Read-only - last known tablet tool position and tool state.

#### cursor-autohide (RW)

See `--cursor-autohide`. Setting this to a new value will always update the cursor.

---

### OSD Properties

#### osd-sym-cc

Inserts the current OSD symbol as opaque OSD control code.

#### osd-ass-cc

`${osd-ass-cc/0}` disables escaping ASS sequences, `${osd-ass-cc/1}` enables it.

#### term-clip-cc

Inserts the symbol to force line truncation to the current terminal width.

---

### System Properties

#### mpv-version

The mpv version/copyright string.

#### mpv-configuration

The configuration arguments that were passed to the build system.

#### ffmpeg-version

The contents of the av_version_info() API call.

#### libass-version

The value of ass_library_version().

#### libplacebo-version

The contents of the PL_VERSION macro.

#### platform

Returns a string describing what target platform mpv was built for (windows, darwin, linux, android, freebsd).

#### pid

Process-id of mpv.

#### env

Read-only table of all environment variables. `${env/HOME}` returns $HOME.

---

### Cache Properties

#### cache-speed

Current I/O read speed between the cache and the lower layer in bytes per second.

#### demuxer-cache-duration

Approximate duration of video buffered in the demuxer, in seconds.

#### demuxer-cache-time

Approximate time of video buffered in demuxer, in seconds.

#### demuxer-cache-idle

Whether the demuxer is idle.

#### demuxer-cache-state

Detailed cache state information.

**Sub-properties:**
- `seekable-ranges` - Regions in the demuxer cache that can be seeked to
- `bof-cached` - Whether lowest timestamp points to beginning of stream
- `eof-cached` - Whether highest timestamp points to end of stream
- `fw-bytes` - Bytes buffered from current position
- `file-cache-bytes` - Bytes stored in file cache
- `cache-end` - Same as demuxer-cache-time
- `reader-pts` - Approximate timestamp of buffered range start
- `raw-input-rate` - Estimated input rate in bytes per second
- `ts-per-stream` - Array with cache details per stream type

#### demuxer-via-network

Whether the stream demuxed via the main demuxer is most likely played via network.

#### demuxer-start-time

The start time reported by the demuxer in fractional seconds.

#### paused-for-cache

Whether playback is paused because of waiting for the cache.

#### cache-buffering-state

The percentage (0-100) of the cache fill status.

#### eof-reached

Whether the end of playback was reached.

#### seeking

Whether the player is currently seeking.

#### idle-active

Returns yes/true if no file is loaded, but the player is staying around because of the `--idle` option.

#### core-idle

Whether the playback core is paused. This can differ from pause in special situations.

---

### Other Properties

#### user-data (RW)

A recursive key/value map of arbitrary nodes shared between clients.

Sub-paths can be accessed directly; e.g., `user-data/my-script/state/a`.

#### menu-data (RW)

This property stores the raw menu definition.

#### working-directory

The working directory of the mpv process.

#### current-watch-later-dir

The directory in which watch later config files are stored.

#### protocol-list

List of protocol prefixes recognized by the player.

#### decoder-list

List of decoders supported.

#### encoder-list

List of libavcodec encoders.

#### demuxer-lavf-list

List of available libavformat demuxers' names.

#### input-key-list

List of key names.

#### property-list

The list of top-level properties.

#### profile-list

The list of profiles and their contents.

#### command-list

The list of input commands.

#### input-bindings

The list of current input key bindings.

#### clipboard (RW)

The clipboard contents.

**Sub-properties:**
- `clipboard/text` (RW) - Text content in the clipboard
- `clipboard/text-primary` (RW) - Text content in the primary selection

#### current-clipboard-backend

A string containing the currently active clipboard backend.

#### clock

The current local time in hour:minutes format.

---

## Property Expansion

All string arguments to input commands as well as certain options are subject to property expansion.

### Expansion Syntax

```
${NAME}
```

Expands to the value of the property NAME. If retrieving fails, expands to an error string. Use `${NAME:}` with trailing colon to expand to empty string.

```
${NAME:STR}
```

Expands to the value of NAME, or STR if property cannot be retrieved.

```
${?NAME:STR}
```

Expands to STR if property NAME is available.

```
${!NAME:STR}
```

Expands to STR if property NAME cannot be retrieved.

```
${?NAME==VALUE:STR}
```

Expands to STR if property NAME equals VALUE.

```
${!NAME==VALUE:STR}
```

Expands to STR if property NAME does not equal VALUE.

```
$$
```

Expands to $.

```
$}
```

Expands to }.

```
$>
```

Disable property expansion for the rest of the string.

### Raw and Formatted Properties

Normally, properties are formatted as human-readable text. Retrieve raw values by prefixing with `=`:

```
${=time-pos}  # expands to 863.4 (raw value)
${time-pos}   # expands to 00:14:23 (formatted)
```

Use `>` prefix for formatted with fixed precision:

```
${>avsync}  # expands to +0.0030
```

---

## Inconsistencies between Options and Properties

Some options behave differently when accessed as properties:

- **vid, aid, sid** - During playback, these return the actually active tracks
- **display-fps** - The reported value and option value are cleanly separated
- **vf, af** - If set during playback and filter chain fails to reinitialize, the option will be set but runtime filter chain doesn't change
- **playlist** - Property is read-only, option is for loading playlists
- **profile, include** - These are write-only and perform actions when written to
