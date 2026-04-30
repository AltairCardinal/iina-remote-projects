## List of Input Commands

Commands with parameters have the parameter name enclosed in < / \>. Don't add those to the actual command. Optional arguments are enclosed in \[ / \]. If you don't pass them, they will be set to a default value.

Remember to quote string arguments in input.conf (see [Flat command syntax](#flat-command-syntax)).

### Playback Control

seek <target> \[<flags>\]

Change the playback position. By default, seeks by a relative amount of seconds.

The second argument consists of flags controlling the seek mode:

relative (default)

Seek relative to current position (a negative value seeks backwards).

absolute

Seek to a given time (a negative value starts from the end of the file).

absolute-percent

Seek to a given percent position.

relative-percent

Seek relative to current position in percent.

keyframes

Always restart playback at keyframe boundaries (fast).

exact

Always do exact/hr/precise seeks (slow).

Multiple flags can be combined, e.g.: absolute+keyframes.

By default, keyframes is used for relative, relative-percent, and absolute-percent seeks, while exact is used for absolute seeks.

This is a scalable command. See the documentation of nonscalable input command prefix in [Input Command Prefixes](#input-command-prefixes) for details.

revert-seek \[<flags>\]

Undoes the seek command, and some other commands that seek (but not necessarily all of them). Calling this command once will jump to the playback position before the seek. Calling it a second time undoes the revert-seek command itself. This only works within a single file.

The first argument is optional, and can change the behavior:

mark

Mark the current time position. The next normal revert-seek command will seek back to this point, no matter how many seeks happened since last time.

mark-permanent

If set, mark the current position, and do not change the mark position before the next revert-seek command that has mark or mark-permanent set (or playback of the current file ends). Until this happens, revert-seek will always seek to the marked point. This flag cannot be combined with mark.

Using it without any arguments gives you the default behavior.

sub-seek <skip> \[<flags>\]

Change video and audio position such that the subtitle event after <skip> subtitle events is displayed. For example, sub-seek 1 skips to the next subtitle, sub-seek \-1 skips to the previous subtitles, and sub-seek 0 seeks to the beginning of the current subtitle.

This is similar to sub-step, except that it seeks video and audio instead of adjusting the subtitle delay.

Secondary argument:

primary (default)

Seeks through the primary subtitles.

secondary

Seeks through the secondary subtitles.

For embedded subtitles (like with Matroska), this works only with subtitle events that have already been displayed, or are within a short prefetch range. See [Cache](#cache) for details on how to control the available prefetch range.

frame-step \[<frames>\] \[<flags>\]

Go forward or backwards by a given amount of frames. If <frames> is omitted, the value is assumed to be 1.

The second argument consists of flags controlling the frameskip mode:

play (default)

Play the video forward by the desired amount of frames and then pause. This only works with a positive value (i.e. frame stepping forwards).

seek

Perform a very exact seek that attempts to seek by the desired amount of frames. If <frames> is \-1, this will go exactly to the previous frame.

mute

The same as play but mutes the audio stream if there is any during the duration of the frame step.

Note that the default frameskip mode, play, is more accurate but can be slow depending on how many frames you are skipping (i.e. skipping forward 100 frames will play 100 frames of video before stopping). This mode only works when going forwards. Frame stepping back always performs a seek.

When using seek mode, this can still be very slow (it tries to be precise, not fast), and sometimes fails to behave as expected. How well this works depends on whether precise seeking works correctly (e.g. see the \--hr-seek-demuxer-offset option). Video filters or other video post-processing that modifies timing of frames (e.g. deinterlacing) should usually work, but might make framestepping silently behave incorrectly in corner cases. Using \--hr-seek-framedrop=no should help, although it might make precise seeking slower. Also if the video is VFR, framestepping using seeks will probably not work correctly except for the \-1 case.

This does not work with audio-only playback.

frame-back-step

Calls frame-step with a value of \-1 and the seek flag.

This does not work with audio-only playback.

stop \[<flags>\]

Stop playback and clear playlist. With default settings, this is essentially like quit. Useful for the client API: playback can be stopped without terminating the player.

The first argument is optional, and supports the following flags:

keep-playlist

Do not clear the playlist.

### Property Manipulation

set <name> <value>

Set the given property or option to the given value.

del <name>

Delete the given property. Most properties cannot be deleted.

add <name> \[<value>\]

Add the given value to the property or option. On overflow or underflow, clamp the property to the maximum. If <value> is omitted, assume 1.

Whether or not key-repeat is enabled by default depends on the property. Currently properties with continuous values are repeatable by default (like volume), while discrete values are not (like osd-level).

This is a scalable command. See the documentation of nonscalable input command prefix in [Input Command Prefixes](#input-command-prefixes) for details.

multiply <name> <value>

Similar to add, but multiplies the property or option with the numeric value.

cycle <name> \[<value>\]

Cycle the given property or option. The second argument can be up or down to set the cycle direction. On overflow, set the property back to the minimum, on underflow set it to the maximum. If up or down is omitted, assume up.

Whether or not key-repeat is enabled by default depends on the property. Currently properties with continuous values are repeatable by default (like volume), while discrete values are not (like osd-level).

This is a scalable command. See the documentation of nonscalable input command prefix in [Input Command Prefixes](#input-command-prefixes) for details.

cycle-values \[<"!reverse">\] <property> <value1> \[<value2> \[...\]\]

Cycle through a list of values. Each invocation of the command will set the given property to the next value in the list. The command will use the current value of the property/option, and use it to determine the current position in the list of values. Once it has found it, it will set the next value in the list (wrapping around to the first item if needed).

This command has a variable number of arguments, and cannot be used with named arguments.

The special argument !reverse can be used to cycle the value list in reverse. The only advantage is that you don't need to reverse the value list yourself when adding a second key binding for cycling backwards.

change-list <name> <operation> <value>

This command changes list options as described in [List Options](#list-options). The <name> parameter is the normal option name, while <operation> is the suffix or action used on the option.

Some operations take no value, but the command still requires the value parameter. In these cases, the value must be an empty string.

Example

change-list glsl-shaders append file.glsl

Add a filename to the glsl-shaders list. The command line equivalent is \--glsl-shaders-append=file.glsl or alternatively \--glsl-shader=file.glsl.

### Playlist Manipulation

playlist-next \[<flags>\]

Go to the next entry on the playlist.

First argument:

weak (default)

If the last file on the playlist is currently played, do nothing.

force

Terminate playback if there are no more files on the playlist.

playlist-prev \[<flags>\]

Go to the previous entry on the playlist.

First argument:

weak (default)

If the first file on the playlist is currently played, do nothing.

force

Terminate playback if the first file is being played.

playlist-next-playlist

Go to the next entry on the playlist with a different playlist-path.

playlist-prev-playlist

Go to the first of the previous entries on the playlist with a different playlist-path.

playlist-play-index <integer|current|none> \[preserve-options\]\]

Start (or restart) playback of the given playlist index. In addition to the 0-based playlist entry index, it supports the following values:

<current>

The current playlist entry (as in playlist-current-pos) will be played again (unload and reload). If none is set, playback is stopped. (In corner cases, playlist-current-pos can point to a playlist entry even if playback is currently inactive,

<none>

Playback is stopped. If idle mode (\--idle) is enabled, the player will enter idle mode, otherwise it will exit.

Setting preserve-options (MPV\_FORMAT\_FLAG) will not reset file-local options when the playback of the current playlist index is restarted.

This command is similar to loadfile in that it only manipulates the state of what to play next, without waiting until the current file is unloaded, and the next one is loaded.

Setting playlist-pos or similar properties can have a similar effect to this command. However, it's more explicit, and guarantees that playback is restarted if for example the new playlist entry is the same as the previous one.

loadfile <url> \[<flags> \[<index> \[<options>\]\]\]

Load the given file or URL and play it. Technically, this is just a playlist manipulation command (which either replaces the playlist or adds an entry to it). Actual file loading happens independently. For example, a loadfile command that replaces the current file with a new one returns before the current file is stopped, and the new file even begins loading.

Second argument:

<replace> (default)

Stop playback of the current file, and play the new file immediately.

<append>

Append the file to the playlist.

<insert-next>

Insert the file into the playlist, directly after the current entry.

<insert-at>

Insert the file into the playlist, at the index given in the third argument.

<play>

If nothing is currently playing, start playback. (Always starts with the added file, even if the playlist was not empty before running this command).

Multiple flags can be combined, e.g.: append+play.

By default, append, insert-next, and insert-at will not immediately start playback even if the playlist was previously empty. Adding the play flag to them forces playback to start.

The following values are considered deprecated and were the old way (before mpv 0.42) of forcing playback to start before the play flag was added.

<append-play>

Append the file, and if nothing is currently playing, start playback. (Always starts with the added file, even if the playlist was not empty before running this command.)

<insert-next-play>

Insert the file next, and if nothing is currently playing, start playback. (Always starts with the added file, even if the playlist was not empty before running this command.)

<insert-at-play>

Insert the file at the index given in the third argument, and if nothing is currently playing, start playback. (Always starts with the added file, even if the playlist was not empty before running this command.)

The third argument is an insertion index, used only by the insert-at action. When used with those actions, the new item will be inserted at the index position in the playlist, or appended to the end if index is less than 0 or greater than the size of the playlist. This argument will be ignored for all other actions. This argument was added in mpv 0.38.0.

The fourth argument is a list of options and values which should be set while the file is playing. It is of the form opt1=value1,opt2=value2,... When using the client API, this can be a MPV\_FORMAT\_NODE\_MAP (or a Lua table), however the values themselves must be strings currently. These options are set during playback, and restored to the previous value at end of playback (see [Per-File Options](#per-file-options)).

Warning

Since mpv 0.38.0, an insertion index argument is added as the third argument. This breaks all existing uses of this command which make use of the argument to include the list of options to be set while the file is playing. To address this problem, the third argument now needs to be set to -1 if the fourth argument needs to be used.

loadlist <url> \[<flags> \[<index>\]\]

Load the given playlist file or URL (like \--playlist).

Second argument:

<replace> (default)

Stop playback and replace the internal playlist with the new one.

<append>

Append the new playlist at the end of the current internal playlist.

<insert-next>

Insert the new playlist into the current internal playlist, directly after the current entry.

<insert-at>

Insert the new playlist at the index given in the third argument.

<play>

If nothing is currently playing, start playback. (Always starts with the added playlist, even if the internal playlist was not empty before running this command).

Multiple flags can be combined, e.g.: append+play.

By default, append, insert-next, and insert-at will not immediately start playback even if the playlist was previously empty. Adding the play flag to them forces playback to start.

The following values are considered deprecated and were the old way (before mpv 0.42) of forcing playback to start before the play flag was added.

<append-play>

Append the new playlist, and if nothing is currently playing, start playback. (Always starts with the new playlist, even if the internal playlist was not empty before running this command.)

<insert-next-play>

Insert the new playlist, and if nothing is currently playing, start playback. (Always starts with the new playlist, even if the internal playlist was not empty before running this command.)

<insert-at-play>

Insert the new playlist at the index given in the third argument, and if nothing is currently playing, start playback. (Always starts with the new playlist, even if the internal playlist was not empty before running this command.)

The third argument is an insertion index, used only by the insert-at action. When used with those actions, the new playlist will be inserted at the index position in the internal playlist, or appended to the end if index is less than 0 or greater than the size of the internal playlist. This argument will be ignored for all other actions. This argument was added in mpv 0.38.0.

playlist-clear

Clear the playlist, except the currently played file.

playlist-remove <index>

Remove the playlist entry at the given index. Index values start counting with 0. The special value current removes the current entry. Note that removing the current entry also stops playback and starts playing the next entry.

playlist-move <index1> <index2>

Move the playlist entry at index1, so that it takes the place of the entry index2. (Paradoxically, the moved playlist entry will not have the index value index2 after moving if index1 was lower than index2, because index2 refers to the target entry, not the index the entry will have after moving.)

playlist-shuffle

Shuffle the playlist. This is similar to what is done on start if the \--shuffle option is used.

playlist-unshuffle

Attempt to revert the previous playlist-shuffle command. This works only once (multiple successive playlist-unshuffle commands do nothing). May not work correctly if new recursive playlists have been opened since a playlist-shuffle command.

### Track Manipulation

sub-add <url> \[<flags> \[<title> \[<lang>\]\]\]

Load the given subtitle file or stream. By default, it is selected as current subtitle after loading.

The flags argument is one of the following values:

<select>

> Select the subtitle immediately (default).

<auto>

> Don't select the subtitle. (Or in some special situations, let the default stream selection mechanism decide.)

<cached>

> Select the subtitle. If a subtitle with the same filename was already added, that one is selected, instead of loading a duplicate entry. (In this case, title/language are ignored, and if the was changed since it was loaded, these changes won't be reflected.)

Additionally the following flags can be added with a +:

<hearing-impaired>

> Marks the track as suitable for the hearing impaired.

<visual-impaired>

> Marks the track as suitable for the visually impaired.

<forced>

> Marks the track as forced.

<default>

> Marks the track as default.

<original>

> Marks the track as being in the original language.

<commentary>

> Marks the track as containing commentary.

<attached-picture> (only for video-add)

> Marks the track as an attached picture, same as albumart argument for \`video-add.

The title argument sets the track title in the UI.

The lang argument sets the track language, and can also influence stream selection with flags set to auto.

sub-remove \[<id>\]

Remove the given subtitle track. If the id argument is missing, remove the current track. (Works on external subtitle files only.)

sub-reload \[<id>\]

Reload the given subtitle tracks. If the id argument is missing, reload the current track. (Works on external subtitle files only.)

This works by unloading and re-adding the subtitle track.

sub-step <skip> \[<flags>\]

Change subtitle timing such, that the subtitle event after the next <skip> subtitle events is displayed. <skip> can be negative to step backwards.

Secondary argument:

primary (default)

Steps through the primary subtitles.

secondary

Steps through the secondary subtitles.

audio-add <url> \[<flags> \[<title> \[<lang>\]\]\]

Load the given audio file. See sub-add command.

audio-remove \[<id>\]

Remove the given audio track. See sub-remove command.

audio-reload \[<id>\]

Reload the given audio tracks. See sub-reload command.

video-add <url> \[<flags> \[<title> \[<lang> \[<albumart>\]\]\]\]

Load the given video file. See sub-add command for common options.

albumart (MPV\_FORMAT\_FLAG)

If enabled, mpv will load the given video as album art.

video-remove \[<id>\]

Remove the given video track. See sub-remove command.

video-reload \[<id>\]

Reload the given video tracks. See sub-reload command.

rescan-external-files \[<mode>\]

Rescan external files according to the current \--sub-auto, \--audio-file-auto and \--cover-art-auto settings. This can be used to auto-load external files *after* the file was loaded.

The mode argument is one of the following:

<reselect> (default)

Select the default audio and subtitle streams, which typically selects external files with the highest preference. (The implementation is not perfect, and could be improved on request.)

<keep-selection>

Do not change current track selections.

### Text Manipulation

print-text <text>

Print text to stdout. The string can contain properties (see [Property Expansion](#property-expansion)). Take care to put the argument in quotes.

expand-text <text>

Property-expand the argument and return the expanded string. This can be used only through the client API or from a script using mp.command\_native. (see [Property Expansion](#property-expansion)).

expand-path <text>

Expand a path's double-tilde placeholders into a platform-specific path. As expand-text, this can only be used through the client API or from a script using mp.command\_native.

Example

mp.osd\_message(mp.command\_native({"expand-path", "~~home/"}))

This line of Lua would show the location of the user's mpv configuration directory on the OSD.

normalize-path <filename>

Return a canonical representation of the path filename by converting it to an absolute path, removing consecutive slashes, removing . components, resolving .. components, and converting slashes to backslashes on Windows. Symlinks are not resolved unless the platform is Unix-like and one of the path components is ... If filename is a URL, it is returned unchanged. This can only be used through the client API or from a script using mp.command\_native.

Example

mp.osd\_message(mp.command\_native({"normalize-path", "/foo//./bar"}))

This line of Lua prints "/foo/bar" on the OSD.

escape-ass <text>

Modify text so that commands and functions that interpret ASS tags, such as osd-overlay and mp.create\_osd\_overlay, will display it verbatim, and return it. This can only be used through the client API or from a script using mp.command\_native.

Example

mp.osd\_message(mp.command\_native({"escape-ass", "foo {bar}"}))

This line of Lua prints "foo \\{bar}" on the OSD.

### Configuration Commands

apply-profile <name> \[<mode>\]

Apply the contents of a named profile. This is like using profile=name in a config file, except you can map it to a key binding to change it at runtime.

The mode argument:

apply

Apply the profile. Default if the argument is omitted.

restore

Restore options set by a previous apply-profile command for this profile. Only works if the profile has profile-restore set to a relevant mode. Prints a warning if nothing could be done. See [Runtime profiles](#runtime-profiles) for details.

load-config-file <filename>

Load a configuration file, similar to the \--include option. If the file was already included, its previous options are not reset before it is reparsed.

write-watch-later-config

Write the resume config file that the quit-watch-later command writes, but continue playback normally.

delete-watch-later-config \[<filename>\]

Delete any existing resume config file that was written by quit-watch-later or write-watch-later-config. If a filename is specified, then the deleted config is for that file; otherwise, it is the same one as would be written by quit-watch-later or write-watch-later-config in the current circumstance.

### OSD Commands

show-text <text> \[<duration>|-1 \[<level>\]\]

Show text on the OSD. The string can contain properties, which are expanded as described in [Property Expansion](#property-expansion). This can be used to show playback time, filename, and so on. no-osd has no effect on this command.

<duration>

The time in ms to show the message for. By default, it uses the same value as \--osd-duration.

<level>

The minimum OSD level to show the text at (see \--osd-level).

show-progress

Show the progress bar, the elapsed time and the total duration of the file on the OSD. no-osd has no effect on this command.

overlay-add <id> <x> <y> <file> <offset> <fmt> <w> <h> <stride> <dw> <dh>

Add an OSD overlay sourced from raw data. This might be useful for scripts and applications controlling mpv, and which want to display things on top of the video window.

Overlays are usually displayed in screen resolution, but with some VOs, the resolution is reduced to that of the video's. You can read the osd-width and osd-height properties. At least with \--vo-xv and anamorphic video (such as DVD), osd-par should be read as well, and the overlay should be aspect-compensated.

This has the following named arguments. The order of them is not guaranteed, so you should always call them with named arguments, see [Named arguments](#named-arguments).

id is an integer between 0 and 63 identifying the overlay element. The ID can be used to add multiple overlay parts, update a part by using this command with an already existing ID, or to remove a part with overlay-remove. Using a previously unused ID will add a new overlay, while reusing an ID will update it.

x and y specify the position where the OSD should be displayed.

file specifies the file the raw image data is read from. It can be either a numeric UNIX file descriptor prefixed with @ (e.g. @4), or a filename. The file will be read into memory before the command returns. Note that since mpv 0.42.0, if a file descriptor is specified, the file offset of the descriptor will be modified.

It is also possible to pass a raw memory address for use as bitmap memory by passing a memory address as integer prefixed with an & character. Passing the wrong thing here will crash the player. This mode might be useful for use with libmpv. The offset parameter is simply added to the memory address.

offset is the byte offset of the first pixel in the source file.

fmt is a string identifying the image format. Currently, only bgra is defined. This format has 4 bytes per pixels, with 8 bits per component. The least significant 8 bits are blue, and the most significant 8 bits are alpha (in little endian, the components are B-G-R-A, with B as first byte). This uses premultiplied alpha: every color component is already multiplied with the alpha component. This means the numeric value of each component is equal to or smaller than the alpha component. (Violating this rule will lead to different results with different VOs: numeric overflows resulting from blending broken alpha values is considered something that shouldn't happen, and consequently implementations don't ensure that you get predictable behavior in this case.)

w, h, and stride specify the size of the overlay. w is the visible width of the overlay, while stride gives the width in bytes in memory. In the simple case, and with the bgra format, stride==4\*w. In general, the total amount of memory accessed is stride \* h. (Technically, the minimum size would be stride \* (h - 1) + w \* 4, but for simplicity, the player will access all stride \* h bytes.)

dw and dh specify the (optional) display size of the overlay. The overlay visible portion of the overlay (w and h) is scaled to in display to dw and dh. If parameters are not present, the values for w and h are used.

Note

Before mpv 0.42.0, the file was mapped into memory with mmap(), copied, and unmapped before the command returns. Changing the file before the command returns is highly discouraged as this could lead to crashes on versions before 0.42.0.

Before mpv 0.18.1, you had to do manual "double buffering" when updating an overlay by replacing it with a different memory buffer. If you want to use this command before mpv 0.18.1, read the old docs to see how to handle this correctly.

Larger offsets should be avoided as mpv versions before 0.42.0 used to mmap the whole file from position 0 to the end of the image. Before mpv 0.8.0, the offset was actually passed directly to mmap. Since mpv 0.42.0, no mmap happens, so offset is handled by seeking on the file.

overlay-remove <id>

Remove an overlay added with overlay-add and the same ID. Does nothing if no overlay with this ID exists.

osd-overlay

Add/update/remove an OSD overlay.

(Although this sounds similar to overlay-add, osd-overlay is for text overlays, while overlay-add is for bitmaps. Maybe overlay-add will be merged into osd-overlay to remove this oddity.)

You can use this to add text overlays in ASS format. ASS has advanced positioning and rendering tags, which can be used to render almost any kind of vector graphics.

This command accepts the following parameters:

id

Arbitrary integer that identifies the overlay. Multiple overlays can be added by calling this command with different id parameters. Calling this command with the same id replaces the previously set overlay.

There is a separate namespace for each libmpv client (i.e. IPC connection, script), so IDs can be made up and assigned by the API user without conflicting with other API users.

If the libmpv client is destroyed, all overlays associated with it are also deleted. In particular, connecting via \--input-ipc-server, adding an overlay, and disconnecting will remove the overlay immediately again.

format

String that gives the type of the overlay. Accepts the following values (HTML rendering of this is broken, view the generated manpage instead, or the raw RST source):

ass-events

The data parameter is a string. The string is split on the newline character. Every line is turned into the Text part of a Dialogue ASS event. Timing is unused (but behavior of timing dependent ASS tags may change in future mpv versions).

Note that it's better to put multiple lines into data, instead of adding multiple OSD overlays.

This provides 2 ASS Styles. OSD contains the text style as defined by the current \--osd-... options. Default is similar, and contains style that OSD would have if all options were set to the default.

In addition, the res\_x and res\_y options specify the value of the ASS PlayResX and PlayResY header fields. If res\_y is set to 0, PlayResY is initialized to an arbitrary default value (but note that the default for this command is 720, not 0). If res\_x is set to 0, PlayResX is set based on res\_y such that a virtual ASS pixel has a square pixel aspect ratio.

none

Special value that causes the overlay to be removed. Most parameters other than id and format are mostly ignored.

data

String defining the overlay contents according to the format parameter.

res\_x, res\_y

Used if format is set to ass-events (see description there). Optional, defaults to 0/720.

z

The Z order of the overlay. Optional, defaults to 0.

Note that Z order between different overlays of different formats is static, and cannot be changed (currently, this means that bitmap overlays added by overlay-add are always on top of the ASS overlays added by osd-overlay). In addition, the builtin OSD components are always below any of the custom OSD. (This includes subtitles of any kind as well as text rendered by show-text.)

It's possible that future mpv versions will randomly change how Z order between different OSD formats and builtin OSD is handled.

hidden

If set to true, do not display this (default: false).

compute\_bounds

If set to true, attempt to determine bounds and write them to the command's result value as x0, x1, y0, y1 rectangle (default: false). If the rectangle is empty, not known, or somehow degenerate, it is not set. x1/y1 is the coordinate of the bottom exclusive corner of the rectangle.

The result value may depend on the VO window size, and is based on the last known window size at the time of the call. This means the results may be different from what is actually rendered.

For ass-events, the result rectangle is recomputed to PlayRes coordinates (res\_x/res\_y). If window size is not known, a fallback is chosen.

You should be aware that this mechanism is very inefficient, as it renders the full result, and then uses the bounding box of the rendered bitmap list (even if hidden is set). It will flush various caches. Its results also depend on the used libass version.

This feature is experimental, and may change in some way again.

Note

Always use named arguments (mpv\_command\_node()). Lua scripts should use the mp.create\_osd\_overlay() helper instead of invoking this command directly.

### Input and Keybind Commands

mouse <x> <y> \[<button> \[<mode>\]\]

Send a mouse event with given coordinate (<x>, <y>).

Second argument:

<button>

The button number of clicked mouse button. This should be one of 0-19. If <button> is omitted, only the position will be updated.

Third argument:

<single> (default)

The mouse event represents regular single click.

<double>

The mouse event represents double-click.

keypress <name> \[<scale>\]

Send a key event through mpv's input handler, triggering whatever behavior is configured to that key. name uses the input.conf naming scheme for keys and modifiers. scale is used to scale numerical change effected by the bound command (same mechanism as precise scrolling). Useful for the client API: key events can be sent to libmpv to handle internally.

keydown <name>

Similar to keypress, but sets the KEYDOWN flag so that if the key is bound to a repeatable command, it will be run repeatedly with mpv's key repeat timing until the keyup command is called.

keyup \[<name>\]

Set the KEYUP flag, stopping any repeated behavior that had been triggered. name is optional. If name is not given or is an empty string, KEYUP will be set on all keys. Otherwise, KEYUP will only be set on the key specified by name.

keybind <name> <cmd> \[<comment>\]

Binds a key to an input command. cmd must be a complete command containing all the desired arguments and flags. Both name and cmd use the input.conf naming scheme. comment is an optional string which can be read as the comment entry of input-bindings. This is primarily useful for the client API.

enable-section <name> \[<flags>\]

This command is deprecated, except for mpv-internal uses.

Enable all key bindings in the named input section.

The enabled input sections form a stack. Bindings in sections on the top of the stack are preferred to lower sections. This command puts the section on top of the stack. If the section was already on the stack, it is implicitly removed beforehand. (A section cannot be on the stack more than once.)

The flags parameter can be a combination (separated by +) of the following flags:

<exclusive>

All sections enabled before the newly enabled section are disabled. They will be re-enabled as soon as all exclusive sections above them are removed. In other words, the new section shadows all previous sections.

<allow-hide-cursor>

This feature can't be used through the public API.

<allow-vo-dragging>

Same.

disable-section <name>

This command is deprecated, except for mpv-internal uses.

Disable the named input section. Undoes enable-section.

define-section <name> <contents> \[<flags>\]

This command is deprecated, except for mpv-internal uses.

Create a named input section, or replace the contents of an already existing input section. The contents parameter uses the same syntax as the input.conf file (except that using the section syntax in it is not allowed), including the need to separate bindings with a newline character.

If the contents parameter is an empty string, the section is removed.

The section with the name default is the normal input section.

In general, input sections have to be enabled with the enable-section command, or they are ignored.

The last parameter has the following meaning:

<default> (also used if parameter omitted)

Use a key binding defined by this section only if the user hasn't already bound this key to a command.

<force>

Always bind a key. (The input section that was made active most recently wins if there are ambiguities.)

This command can be used to dispatch arbitrary keys to a script or a client API user. If the input section defines script-binding commands, it is also possible to get separate events on key up/down, and relatively detailed information about the key state. The special key name unmapped can be used to match any unmapped key.

load-input-conf <filename>

Load an input configuration file, similar to the \--input-conf option. If the file was already included, its previous bindings are not reset before it is reparsed.

### Execution Commands

run <command> \[<arg1> \[<arg2> \[...\]\]\]

Run the given command.

This doesn't call the shell. Instead, the command is run directly, with each argument passed separately. Each argument is expanded like in [Property Expansion](#property-expansion).

This command has a variable number of arguments, and cannot be used with named arguments.

The program is run in a detached way. mpv doesn't wait until the command is completed, but continues playback right after spawning it.

To get the old behavior, use /bin/sh and \-c as the first two arguments.

Example

run "/bin/sh" "-c" "echo ${title} > /tmp/playing"

This is not a particularly good example, because it doesn't handle escaping, and a specially prepared file might allow an attacker to execute arbitrary shell commands. It is recommended to write a small shell script, and call that with run.

subprocess

Similar to run, but gives more control about process execution to the caller, and does not detach the process.

You can avoid blocking until the process terminates by running this command asynchronously. (For example mp.command\_native\_async() in Lua scripting.)

This has the following named arguments. The order of them is not guaranteed, so you should always call them with named arguments, see [Named arguments](#named-arguments).

args (MPV\_FORMAT\_NODE\_ARRAY\[MPV\_FORMAT\_STRING\])

Array of strings with the command as first argument, and subsequent command line arguments following. This is just like the run command argument list.

The first array entry is either an absolute path to the executable, or a filename with no path components, in which case the executable is searched in the directories in the PATH environment variable. On Unix, this is equivalent to posix\_spawnp and execvp behavior.

playback\_only (MPV\_FORMAT\_FLAG)

Boolean indicating whether the process should be killed when playback of the current playlist entry terminates (optional, default: true). If enabled, stopping playback will automatically kill the process, and you can't start it outside of playback.

capture\_size (MPV\_FORMAT\_INT64)

Integer setting the maximum number of stdout plus stderr bytes that can be captured (optional, default: 64MB). If the number of bytes exceeds this, capturing is stopped. The limit is per captured stream.

capture\_stdout (MPV\_FORMAT\_FLAG)

Capture all data the process outputs to stdout and return it once the process ends (optional, default: no).

capture\_stderr (MPV\_FORMAT\_FLAG)

Same as capture\_stdout, but for stderr.

detach (MPV\_FORMAT\_FLAG)

Whether to run the process in detached mode (optional, default: no). In this mode, the process is run in a new process session, and the command does not wait for the process to terminate. If neither capture\_stdout nor capture\_stderr have been set to true, the command returns immediately after the new process has been started, otherwise the command will read as long as the pipes are open.

env (MPV\_FORMAT\_NODE\_ARRAY\[MPV\_FORMAT\_STRING\])

Set a list of environment variables for the new process (default: empty). If an empty list is passed, the environment of the mpv process is used instead. (Unlike the underlying OS mechanisms, the mpv command cannot start a process with empty environment. Fortunately, that is completely useless.) The format of the list is as in the execle() syscall. Each string item defines an environment variable as in NAME=VALUE.

On Lua, you may use utils.get\_env\_list() to retrieve the current environment if you e.g. simply want to add a new variable.

stdin\_data (MPV\_FORMAT\_STRING)

Feed the given string to the new process' stdin. Since this is a string, you cannot pass arbitrary binary data. If the process terminates or closes the pipe before all data is written, the remaining data is silently discarded. Probably does not work on win32.

passthrough\_stdin (MPV\_FORMAT\_FLAG)

If enabled, wire the new process' stdin to mpv's stdin (default: no).

The command returns the following result (as MPV\_FORMAT\_NODE\_MAP):

status (MPV\_FORMAT\_INT64)

Typically this is the process exit code (0 or positive) if the process terminates normally, or negative for other errors (failed to start, terminated by mpv, and others). The meaning of negative values is undefined, other than meaning error (and does not correspond to OS low level exit status values).

On Windows, it can happen that a negative return value is returned even if the process terminates normally, because the win32 UINT exit code is assigned to an int variable before being set as int64\_t field in the result map. This might be fixed later.

stdout (MPV\_FORMAT\_BYTE\_ARRAY)

Captured stdout stream, limited to capture\_size.

stderr (MPV\_FORMAT\_BYTE\_ARRAY)

Same as stdout, but for stderr.

error\_string (MPV\_FORMAT\_STRING)

Empty string if the process terminated normally. The string killed if the process was terminated in an unusual way. The string init if the process could not be started.

On Windows, killed is only returned when the process has been killed by mpv as a result of playback\_only being set to true.

killed\_by\_us (MPV\_FORMAT\_FLAG)

Whether the process has been killed by mpv, for example as a result of playback\_only being set to true, aborting the command (e.g. by mp.abort\_async\_command()), or if the player is about to exit.

Note that the command itself will always return success as long as the parameters are correct. Whether the process could be spawned or whether it was somehow killed or returned an error status has to be queried from the result value.

This command can be asynchronously aborted via API. Also see [Asynchronous command details](#asynchronous-command-details). Only the run command can start processes in a truly detached way.

Note

The subprocess will always be terminated on player exit if it wasn't started in detached mode, even if playback\_only is false.

Warning

Don't forget to set the playback\_only field to false if you want the command to run while the player is in idle mode, or if you don't want the end of playback to kill the command.

Example

local r = mp.command\_native({
    \_name = "subprocess",
    playback\_only = false,
    capture\_stdout = true,
    args = {"cat", "/proc/cpuinfo"},
})
if r.status == 0 then
    print("result: " .. r.stdout)
end

This is a fairly useless Lua example, which demonstrates how to run a process in a blocking manner, and retrieving its stdout output.

quit \[<code>\]

Exit the player. If an argument is given, it's used as process exit code.

quit-watch-later \[<code>\]

Exit player, and store current playback position. Playing that file later will seek to the previous position on start. The (optional) argument is exactly as in the quit command. See [RESUMING PLAYBACK](#resuming-playback).

### Scripting Commands

script-message \[<arg1> \[<arg2> \[...\]\]\]

Send a message to all clients, and pass it the following list of arguments. What this message means, how many arguments it takes, and what the arguments mean is fully up to the receiver and the sender. Every client receives the message, so be careful about name clashes (or use script-message-to).

This command has a variable number of arguments, and cannot be used with named arguments.

script-message-to <target> \[<arg1> \[<arg2> \[...\]\]\]

Same as script-message, but send it only to the client named <target>. Each client (scripts etc.) has a unique name. For example, Lua scripts can get their name via mp.get\_script\_name(). Note that client names only consist of alphanumeric characters and \_.

This command has a variable number of arguments, and cannot be used with named arguments.

script-binding <name> \[<arg>\]

Invoke a script-provided key binding. This can be used to remap key bindings provided by external Lua scripts.

<name> is the name of the binding. <arg> is a user-provided arbitrary string which can be used to provide extra information.

It can optionally be prefixed with the name of the script, using / as separator, e.g. script-binding scriptname/bindingname. Note that script names only consist of alphanumeric characters and \_.

For completeness, here is how this command works internally. The details could change any time. On any matching key event, script-message-to or script-message is called (depending on whether the script name is included), with the following arguments in string format:

1.  The string key-binding.
2.  The name of the binding (as established above).
3.  The key state as string (see below).
4.  The key name.
5.  The text the key would produce, or empty string if not applicable.
6.  The scale of the key, such as the ones produced by WHEEL\_\* keys. The scale is 1 if the key is nonscalable.
7.  The user-provided string <arg>, or empty string if the argument is not used.

The 5th argument is only set if no modifiers are present (using the shift key with a letter is normally not emitted as having a modifier, and results in upper case text instead, but some backends may mess up).

The key state consists of 3 characters:

1.  One of d (key was pressed down), u (was released), r (key is still down, and was repeated; only if key repeat is enabled for this binding), p (key was pressed; happens if up/down can't be tracked).
2.  Whether the event originates from the mouse, either m (mouse button) or \- (something else).
3.  Whether the event results from a cancellation (e.g. the key is logically released but not physically released), either c (canceled) or \- (something else). Not all types of cancellations set this flag.

Future versions can add more arguments and more key state characters to support more input peculiarities.

This is a scalable command. See the documentation of nonscalable input command prefix in [Input Command Prefixes](#input-command-prefixes) for details.

load-script <filename>

Load a script, similar to the \--script option. Whether this waits for the script to finish initialization or not changed multiple times, and the future behavior is left undefined.

On success, returns a mpv\_node with a client\_id field set to the return value of the mpv\_client\_id() API call of the newly created script handle.

MPV\_FORMAT\_NODE\_MAP
    "client\_id"    MPV\_FORMAT\_STRING

### Screenshot Commands

screenshot \[<flags>\]

Take a screenshot.

Multiple flags are available (some can be combined with +):

<video>

Save the video image in its original resolution, without OSD or subtitles. This is the default when no flag is specified, and it does not need to be explicitly added when combined with other flags.

<scaled>

Save the video image in the current playback resolution.

<subtitles> (default)

Save the video image with subtitles. Some video outputs may still include the OSD in the output under certain circumstances.

<osd>

Save the video image with OSD.

<window>

Save the contents of the mpv window, with OSD and subtitles. This is an alias of scaled+subtitles+osd.

<each-frame>

Take a screenshot each frame. Issue this command again to stop taking screenshots. Note that you should disable frame-dropping when using this mode - or you might receive duplicate images in cases when a frame was dropped. This flag can be combined with the other flags, e.g. video+each-frame.

The exact behaviors of all flags other than each-frame depend on the selected video output.

Older mpv versions required passing single and each-frame as second argument (and did not have flags). This syntax is still understood, but deprecated and might be removed in the future.

If you combine this command with another one using ;, you can use the async flag to make encoding/writing the image file asynchronous. For normal standalone commands, this is always asynchronous, and the flag has no effect.

On success, returns a mpv\_node with a filename field set to the saved screenshot location.

MPV\_FORMAT\_NODE\_MAP
    "filename"    MPV\_FORMAT\_STRING

screenshot-to-file <filename> \[<flags>\]

Take a screenshot and save it to a given file. The format of the file will be guessed by the extension (and \--screenshot-format is ignored - the behavior when the extension is missing or unknown is arbitrary).

The second argument is like the first argument to screenshot and supports subtitles, video, window.

If the file already exists, it's overwritten.

Like all input command parameters, the filename is subject to property expansion as described in [Property Expansion](#property-expansion).

screenshot-raw \[<flags> \[<format>\]\]

Return a screenshot in memory. This can be used only through the client API or from a script using mp.command\_native. The MPV\_FORMAT\_NODE\_MAP returned by this command has the w, h, stride fields set to obvious contents.

The format field is set to the format of the screenshot image data. This can be controlled by the format argument. The format can be one of the following:

bgr0 (default)

This format is organized as B8G8R8X8 (where B is the LSB). The contents of the padding X are undefined.

bgra

This format is organized as B8G8R8A8 (where B is the LSB).

rgba

This format is organized as R8G8B8A8 (where R is the LSB).

rgba64

This format is organized as R16G16B16A16 (where R is the LSB). Each component occupies 2 bytes per pixel. When this format is used, the image data will be high bit depth, and \--screenshot-high-bit-depth is ignored.

The data field is of type MPV\_FORMAT\_BYTE\_ARRAY with the actual image data. The image is freed as soon as the result mpv\_node is freed. As usual with client API semantics, you are not allowed to write to the image data.

The stride is the number of bytes from a pixel at (x0, y0) to the pixel at (x0, y0 + 1). This can be larger than w \* bpp if the image was cropped, or if there is padding. This number can be negative as well. You access a pixel with byte\_index = y \* stride + x \* bpp. Here, bpp is the number of bytes per pixel, which is 8 for rgba64 format and 4 for other formats.

The flags argument is like the first argument to screenshot and supports subtitles, video, window.

MPV\_FORMAT\_NODE\_MAP
    "w"         MPV\_FORMAT\_INT64
    "h"         MPV\_FORMAT\_INT64
    "stride"    MPV\_FORMAT\_INT64
    "format"    MPV\_FORMAT\_STRING
    "data"      MPV\_FORMAT\_BYTE\_ARRAY

### Filter Commands

af <operation> <value>

Change audio filter chain. See vf command.

vf <operation> <value>

Change video filter chain.

The semantics are exactly the same as with option parsing (see [VIDEO FILTERS](#video-filters)). As such the text below is a redundant and incomplete summary.

The first argument decides what happens:

<set>

Overwrite the previous filter chain with the new one.

<add>

Append the new filter chain to the previous one.

<toggle>

Check if the given filter (with the exact parameters) is already in the video chain. If it is, remove the filter. If it isn't, add the filter. (If several filters are passed to the command, this is done for each filter.)

A special variant is combining this with labels, and using @name without filter name and parameters as filter entry. This toggles the enable/disable flag.

<remove>

Like toggle, but always remove the given filter from the chain.

<clr>

Remove all filters. Note that like the other sub-commands, this does not control automatically inserted filters.

The argument is always needed. E.g. in case of clr use vf clr "".

You can assign labels to filter by prefixing them with @name: (where name is a user-chosen arbitrary identifier). Labels can be used to refer to filters by name in all of the filter chain modification commands. For add, using an already used label will replace the existing filter.

The vf command shows the list of requested filters on the OSD after changing the filter chain. This is roughly equivalent to show-text ${vf}. Note that auto-inserted filters for format conversion are not shown on the list, only what was requested by the user.

Normally, the commands will check whether the video chain is recreated successfully, and will undo the operation on failure. If the command is run before video is configured (can happen if the command is run immediately after opening a file and before a video frame is decoded), this check can't be run. Then it can happen that creating the video chain fails.

Example for input.conf

-   a vf set vflip turn the video upside-down on the a key
-   b vf set "" remove all video filters on b
-   c vf toggle gradfun toggle debanding on c

Example how to toggle disabled filters at runtime

-   Add something like vf-add=@deband:!gradfun to mpv.conf. The @deband: is the label, an arbitrary, user-given name for this filter entry. The ! before the filter name disables the filter by default. Everything after this is the normal filter name and possibly filter parameters, like in the normal \--vf syntax.
-   Add a vf toggle @deband to input.conf. This toggles the "disabled" flag for the filter with the label deband when the a key is hit.

vf-command <label> <command> <argument> \[<target>\]

Send a command to the filter. Note that currently, this only works with the lavfi filter. Refer to the libavfilter documentation for the list of supported commands for each filter.

<label> is a mpv filter label, use all to send it to all filters at once.

<command> and <argument> are filter-specific strings.

<target> is a filter or filter instance name and defaults to all. Note that the target is an additional specifier for filters that support them, such as complex lavfi filter chains.

af-command <label> <command> <argument> \[<target>\]

Same as vf-command, but for audio filters.

### Miscellaneous Commands

ignore

Use this to "block" keys that should be unbound, and do nothing. Useful for disabling default bindings, without disabling all bindings with \--input-default-bindings=no.

drop-buffers

Drop audio/video/demuxer buffers, and restart from fresh. Might help with unseekable streams that are going out of sync. This command might be changed or removed in the future.

dump-cache <start> <end> <filename>

Dump the current cache to the given filename. The <filename> file is overwritten if it already exists. <start> and <end> give the time range of what to dump. If no data is cached at the given time range, nothing may be dumped (creating a file with no packets).

Dumping a larger part of the cache will freeze the player. No effort was made to fix this, as this feature was meant mostly for creating small excerpts.

See \--stream-record for various caveats that mostly apply to this command too, as both use the same underlying code for writing the output file.

If <filename> is an empty string, an ongoing dump-cache is stopped.

If <end> is no, then continuous dumping is enabled. Then, after dumping the existing parts of the cache, anything read from network is appended to the cache as well. This behaves similar to \--stream-record (although it does not conflict with that option, and they can be both active at the same time).

If the <end> time is after the cache, the command will \_not\_ wait and write newly received data to it.

The end of the resulting file may be slightly damaged or incomplete at the end. (Not enough effort was made to ensure that the end lines up properly.)

Note that this command will finish only once dumping ends. That means it works similar to the screenshot command, just that it can block much longer. If continuous dumping is used, the command will not finish until playback is stopped, an error happens, another dump-cache command is run, or an API like mp.abort\_async\_command was called to explicitly stop the command. See [Synchronous vs. Asynchronous](#synchronous-vs-asynchronous).

Note

This was mostly created for network streams. For local files, there may be much better methods to create excerpts and such. There are tons of much more user-friendly Lua scripts, that will re-encode parts of a file by spawning a separate instance of ffmpeg. With network streams, this is not that easily possible, as the stream would have to be downloaded again. Even if \--stream-record is used to record the stream to the local filesystem, there may be problems, because the recorded file is still written to.

This command is experimental, and all details about it may change in the future.

ab-loop

Cycle through A-B loop states. The first command will set the A point (the ab-loop-a property); the second the B point, and the third will clear both points.

ab-loop-dump-cache <filename>

Essentially calls dump-cache with the current AB-loop points as arguments. Like dump-cache, this will overwrite the file at <filename>. Likewise, if the B point is set to no, it will enter continuous dumping after the existing cache was dumped.

The author reserves the right to remove this command if enough motivation is found to move this functionality to a trivial Lua script.

ab-loop-align-cache

Re-adjust the A/B loop points to the start and end within the cache the ab-loop-dump-cache command will (probably) dump. Basically, it aligns the times on keyframes. The guess might be off especially at the end (due to granularity issues due to remuxing). If the cache shrinks in the meantime, the points set by the command will not be the effective parameters either.

This command has an even more uncertain future than ab-loop-dump-cache and might disappear without replacement if the author decides it's useless.

begin-vo-dragging

Begin window dragging if supported by the current VO. This command should only be called while a mouse button is being pressed, otherwise it will be ignored. The exact effect of this command depends on the VO implementation of window dragging. For example, on Windows and macOS only the left mouse button can begin window dragging, while X11 and Wayland allow other mouse buttons.

context-menu

Show context menu on the video window. See [Context Menu](#context-menu) section for details.

update-clipboard <type> \[timeout\]

Update the clipboard content so that the clipboard property reflects up-to-date value. This command is required to update the clipboard property value if \--clipboard-monitor=no. <type> must be text or text-primary to indicate whether to update clipboard or primary selection. \[timeout\] specifies the maximum timeout in ms to wait for the clipboard content to be updated. A negative timeout means infinite. The default timeout is 10 ms.

This command returns as soon as the clipboard content is updated or the timeout has reached. On some platforms, this command does nothing and returns immediately.

This command can be asynchronously aborted via API. See [Asynchronous command details](#asynchronous-command-details).

Undocumented commands: ao-reload (experimental/internal).

