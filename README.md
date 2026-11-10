# clipstack

Turn a 16:9 video into 9:16 short clips. The whole picture sits in the middle on black, with an optional logo and one text line above it. Original audio stays. Only `ffmpeg` is needed, no AI at run time.

```
python clipstack.py spec.json            # all clips
python clipstack.py spec.json clip-1     # one clip
```

`spec.json`:

```json
{"src": "video.mp4", "logo": "logo.png",
 "clips": [{"id": "clip-1", "start": 16.0, "dur": 12.5, "text": "One plain line"}]}
```

`logo` and `font` are optional. Every clip also gets a `_check.jpg` with three frames: look at it before you post.

Works as a Claude skill: copy the folder to `.claude/skills/clipstack/`.
Made while building my own Jarvis: discord.gg/6PdHN4pz3q
