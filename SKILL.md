---
name: clipstack
description: Turn a 16:9 video into 9:16 short clips with the whole picture in the middle, an optional logo and one text line, keeping the original audio. Use when asked to cut vertical clips from a trailer, stream or podcast video without re-editing by hand.
---
# clipstack: 16:9 to 9:16, no editing software

1. Put the source video (and a logo, if the campaign needs one) next to a `spec.json`.
2. List the moments: `{"id": "clip-1", "start": 16.0, "dur": 12.5, "text": "One plain line"}`. Pick moments by transcript if the video is long (any speech-to-text works).
3. Run `python clipstack.py spec.json`. Output: `<id>.mp4` plus `<id>_check.jpg` (first, middle, last frame).
4. Look at every check image before posting: the text must be fully visible, nothing cut off, the picture complete.

Rules that keep clips safe: never crop the middle out of a 16:9 picture (the whole picture sits on a black background), keep the text inside the free zone, use only the original audio, use only material you are allowed to use.
