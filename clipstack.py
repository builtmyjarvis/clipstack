#!/usr/bin/env python3
"""clipstack: turn a 16:9 video into 9:16 short clips (whole picture in the middle, optional logo, one text line, original audio).
No AI at run time, only ffmpeg. Layout stays inside the area TikTok/Shorts leave free (about 14 % to 72 % of the height).
Usage:  python clipstack.py spec.json [clip-id ...] [--out folder]
spec.json: {"src": "video.mp4", "logo": "logo.png" (optional), "font": "path/to/font.ttf" (optional),
            "clips": [{"id": "clip-1", "start": 16.0, "dur": 12.5, "text": "One plain line"}]}
Paths in the spec are relative to the spec file. For every clip it writes <id>.mp4 and <id>_check.jpg (first, middle, last frame): LOOK at it before you post."""
import json, os, shutil, subprocess, sys, tempfile, textwrap
from pathlib import Path


def find_font(spec_font):
    cands = [spec_font] if spec_font else []
    cands += [r"C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]
    for c in cands:
        if c and Path(c).exists():
            return str(c).replace("\\", "/").replace(":", r"\:")
    sys.exit("No font found: set \"font\" in the spec to a .ttf file")


def build(spec, base, c, out_dir, ff, font):
    out = out_dir / f"{c['id']}.mp4"
    lines = textwrap.wrap(c["text"], 30)[:3]
    tf = Path(tempfile.gettempdir()) / f"clipstack_{c['id']}.txt"
    tf.write_bytes("\n".join(lines).encode("utf-8"))   # bytes: Windows text mode adds \r, drawtext would show an empty line
    tfp = str(tf).replace("\\", "/").replace(":", r"\:")
    ty = 600 - 62 * len(lines)                         # text block ends just above the picture (y 656)
    logo = spec.get("logo")
    ins = ["-i", str(base / logo)] if logo else []
    fc = (("[1:v]scale=400:-1[lg];" if logo else "") + "[0:v]scale=1080:608,setsar=1[v];"
          "color=black:s=1080x1920:r=30[bg];[bg][v]overlay=0:656:shortest=1[a];" +
          (f"[a][lg]overlay=(W-w)/2:{ty - 165}[b];" if logo else "[a]null[b];") +
          f"[b]drawtext=fontfile='{font}':textfile='{tfp}':fontcolor=white:fontsize=54:line_spacing=12:text_align=C:x=(w-text_w)/2:y={ty}[o]")
    cmd = [ff, "-y", "-loglevel", "error", "-ss", str(c["start"]), "-t", str(c["dur"]), "-i", str(base / spec["src"]), *ins,
           "-filter_complex", fc, "-map", "[o]", "-map", "0:a?", "-af", f"afade=t=out:st={max(0, c['dur'] - 0.25)}:d=0.25",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    sheet = out_dir / f"{c['id']}_check.jpg"
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", str(out), "-vf",
                    f"select='eq(n,1)+eq(n,{int(c['dur'] * 15)})+eq(n,{max(2, int(c['dur'] * 29) - 3)})',scale=360:640,tile=3x1",
                    "-fps_mode", "passthrough", "-frames:v", "1", "-q:v", "4", str(sheet)], check=True)
    print(out.name, round(out.stat().st_size / 1e6, 1), "MB")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    spec_path = Path(args[0])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else spec_path.parent / "out"
    if "--out" in sys.argv:
        args = [a for a in args if a != str(out_dir)]
    out_dir.mkdir(parents=True, exist_ok=True)
    ff = shutil.which("ffmpeg") or sys.exit("ffmpeg not found")
    font = find_font(spec.get("font"))
    want = set(args[1:])
    for c in spec["clips"]:
        if not want or c["id"] in want:
            build(spec, spec_path.parent, c, out_dir, ff, font)
