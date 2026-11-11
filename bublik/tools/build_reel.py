"""Сборка ролика: scripts/NN.segments.json → mp4, −14 LUFS.

Пример:
  python3 tools/build_reel.py scripts/15.segments.json output/bublik_15_morkovka.mp4
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from episode_carrot import cover, render_frame  # noqa: E402
from look import H, W, bottom_shade, caption_block, hook_block  # noqa: E402
from make_audio import build_timeline, loudnorm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def line_at(t, lines):
    for ln in lines:
        if ln["start"] <= t < ln["end"]:
            return ln, t - ln["start"]
    prev = lines[0]
    for ln in lines:
        if ln["start"] <= t:
            prev = ln
    return prev, min(prev["dur"] - 0.02, max(0.0, t - prev["start"]))


def active_word(ln, local_t):
    words = ln["text"].split()
    bounds = ln["words"]
    if len(bounds) != len(words):
        speaking = any(w["t"] - 0.02 <= local_t <= w["t"] + w["d"] + 0.04 for w in bounds)
        return None, speaking
    for i, w in enumerate(bounds):
        if w["t"] - 0.02 <= local_t <= w["t"] + w["d"] + 0.03:
            return i, True
    return None, False


def mouth_for(speaking, local_t, expr_shock=False):
    if not speaking:
        return 3 if expr_shock else 0
    return 1 + int(local_t * 12) % 2


def compose(seg, timeline, t):
    ln, local = line_at(t, timeline["lines"])
    scene = ln["scene"]
    if ln.get("mid") and local > ln["dur"] * 0.48:
        scene = ln["mid"]
    active, speaking = active_word(ln, local)
    if ln["speaker"] == "bublik":
        mb = mouth_for(speaking, local)
        mp = 0
    else:
        mb = 0
        mp = mouth_for(speaking, local)
    blink_b = 0.08 < (t % 3.6) < 0.18
    blink_p = 0.08 < ((t + 1.7) % 3.3) < 0.18
    im = render_frame(scene, local, max(ln["dur"], 0.2), ln["speaker"], mb, mp, blink_b, blink_p, global_t=t)
    bottom_shade(im)
    hook_until = timeline["lines"][1]["end"] if len(timeline["lines"]) > 1 else 2
    if t < hook_until:
        hook_block(im, seg["hook"])
    caption_block(im, ln["text"], ln["speaker"], y=1620, active=active)
    return im.convert("RGB")


def preview(seg, timeline, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for ln in timeline["lines"]:
        t = ln["start"] + ln["dur"] * 0.42
        frame = compose(seg, timeline, t)
        if ln["id"] in ("01", "05", "09", "16", "20", "22"):
            frame.save(folder / f"frame_{ln['id']}.png")
        thumbs.append(frame.resize((270, 480), Image.Resampling.LANCZOS))
    cols = 6
    tw, th = thumbs[0].size
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (0, 0, 0))
    for i, thum in enumerate(thumbs):
        sheet.paste(thum, ((i % cols) * tw, (i // cols) * th))
    path = folder / "preview_sheet.png"
    sheet.save(path)
    print("превью", path)


def render_video(seg, timeline, wav: Path, out: Path):
    fps = int(seg.get("fps", 24))
    n = int(round(timeline["duration"] * fps))
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
        "-i", "-",
        "-i", str(wav),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(n):
            frame = compose(seg, timeline, i / fps)
            proc.stdin.write(frame.tobytes())
            if i % fps == 0:
                print(f"  кадр {i}/{n}")
    finally:
        proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "replace")
        code = proc.wait()
    if code != 0:
        raise RuntimeError(err[-2000:])
    print("ролик", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("segments")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    seg_path = Path(args.segments)
    if not seg_path.is_absolute():
        seg_path = ROOT / seg_path
    seg = json.loads(seg_path.read_text())
    cache = ROOT / "audio" / "cache"
    build = ROOT / "build"
    build.mkdir(parents=True, exist_ok=True)
    rough = build / "mix.wav"
    print("озвучка…")
    timeline = build_timeline(seg, cache, rough)
    (build / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2))
    norm = build / "mix_norm.wav"
    print("громкость −14 LUFS…")
    loudnorm(rough, norm)
    cover_path = ROOT / "output" / "bublik_15_cover.png"
    cover_path.parent.mkdir(parents=True, exist_ok=True)
    cover().save(cover_path)
    print("обложка", cover_path)
    if args.preview or not args.output:
        preview(seg, timeline, ROOT / "output")
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        render_video(seg, timeline, norm, out)
        cap = out.with_suffix(".txt")
        cap.write_text(
            "ПОДПИСЬ\n" + seg["caption"].strip() + "\n\nЗАКРЕП\n" + seg["pinned"].strip() + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
