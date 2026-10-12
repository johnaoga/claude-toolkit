#!/usr/bin/env python
"""Headless render of a manim-voiceover episode, with the recorder stubbed out.

The real episodes use RecorderService, which blocks on microphone input. This
harness swaps it for a dummy so the whole `construct` runs unattended, then
reports what a reviewer needs:

  * RENDER_OK (or the traceback)
  * one still per narration block, taken at the moment the visuals are fully
    built (the "padding wait"), tiled into contact sheets to read as images
  * a per-scene runtime estimate from the narration word count

Usage:
    python headless_render.py <episode.py> [--class Name] [--out DIR]
                              [--wpm 150] [--budget 480]
"""
import argparse
import contextlib
import importlib.util
import inspect
import math
import re
import sys
from pathlib import Path

RECORD_PREFIX = re.compile(r"\[Click Record and say:\]", re.I)


def load_module(path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def find_scene_class(mod, name=None):
    from manim_voiceover import VoiceoverScene

    if name:
        return getattr(mod, name)
    found = [c for c in vars(mod).values()
             if inspect.isclass(c) and issubclass(c, VoiceoverScene)
             and c.__module__ == mod.__name__]
    if len(found) != 1:
        names = ", ".join(c.__name__ for c in found) or "none"
        sys.exit(f"Expected exactly 1 VoiceoverScene subclass, found: {names}. Use --class.")
    return found[0]


def current_scene_method():
    """Name of the nearest `scene*` method on the call stack."""
    frame = sys._getframe(2)
    while frame is not None:
        if frame.f_code.co_name.startswith("scene"):
            return frame.f_code.co_name
        frame = frame.f_back
    return "construct"


def fmt(seconds):
    seconds = int(round(seconds))
    return f"{seconds // 60}:{seconds % 60:02d}"


def contact_sheets(stills, out_dir, cols=3, rows=4, width=440):
    from PIL import Image, ImageDraw

    sheets = []
    per = cols * rows
    for s in range(0, len(stills), per):
        chunk = stills[s:s + per]
        thumbs = []
        for label, path in chunk:
            im = Image.open(path).convert("RGB")
            h = round(im.height * width / im.width)
            im = im.resize((width, h))
            ImageDraw.Draw(im).text((6, 4), label, fill=(255, 255, 0))
            thumbs.append(im)
        h = thumbs[0].height
        sheet = Image.new("RGB", (cols * width, math.ceil(len(thumbs) / cols) * h), "black")
        for i, im in enumerate(thumbs):
            sheet.paste(im, ((i % cols) * width, (i // cols) * h))
        dest = out_dir / f"sheet_{s // per + 1:02d}.png"
        sheet.save(dest)
        sheets.append(dest)
    return sheets


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode", type=Path)
    ap.add_argument("--class", dest="cls", default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--wpm", type=float, default=150, help="narration speed (words/min)")
    ap.add_argument("--budget", type=float, default=480, help="runtime target in seconds")
    args = ap.parse_args()

    episode = args.episode.resolve()
    out = (args.out or Path("/tmp/manim-explainer-check") / episode.stem).resolve()
    stills_dir = out / "stills"
    stills_dir.mkdir(parents=True, exist_ok=True)
    for old in list(stills_dir.glob("*.png")) + list(out.glob("sheet_*.png")):
        old.unlink()

    # Episodes load assets with paths relative to the repo root.
    import os
    os.chdir(episode.parent)

    mod = load_module(episode)

    class DummyService:
        def __init__(self, *a, **k):
            self._whisper_model = None

    if hasattr(mod, "RecorderService"):
        mod.RecorderService = DummyService

    from manim import tempconfig
    from PIL import Image

    class DummyTracker:
        duration = 0.05

    base = find_scene_class(mod, args.cls)
    blocks = []   # dicts: scene, words, anim
    stills = []   # (label, path)

    class HeadlessScene(base):
        def set_speech_service(self, *a, **k):
            pass

        @contextlib.contextmanager
        def voiceover(self, text="", **kwargs):
            words = len(RECORD_PREFIX.sub("", text or "").split())
            start = self.renderer.time
            block = {"scene": current_scene_method(), "words": words, "anim": 0.0}
            blocks.append(block)
            yield DummyTracker()
            block["anim"] = self.renderer.time - start

        def wait(self, duration=1.0, *a, **k):
            # With the dummy tracker, `wait(max(0, tracker.duration - t))` becomes
            # wait(0): that is the moment the visuals of a block are complete, so
            # snapshot it. Manim rejects non-positive waits, hence the clamp.
            if duration is None or duration <= 0:
                self._snapshot()
                duration = 0.05
            return super().wait(duration, *a, **k)

        def _snapshot(self):
            try:
                self.renderer.update_frame(self)
                frame = self.renderer.get_frame()
            except Exception as exc:  # stills are a convenience, never fail the render
                print(f"(still skipped: {exc})")
                return
            scene = current_scene_method()
            label = f"{len(stills) + 1:03d} {scene}"
            path = stills_dir / f"{len(stills) + 1:03d}_{scene}.png"
            Image.fromarray(frame).convert("RGB").save(path)
            stills.append((label, path))

    HeadlessScene.__name__ = base.__name__

    with tempconfig({"quality": "low_quality", "frame_rate": 10, "disable_caching": True,
                     "media_dir": str(out / "media"), "verbosity": "WARNING"}):
        HeadlessScene().render()

    print("RENDER_OK")

    # ---- runtime estimate ---------------------------------------------------
    per_scene = {}
    for b in blocks:
        s = per_scene.setdefault(b["scene"], {"words": 0, "narr": 0.0, "anim": 0.0, "est": 0.0, "blocks": 0})
        narr = b["words"] / args.wpm * 60
        s["words"] += b["words"]; s["narr"] += narr; s["anim"] += b["anim"]
        s["est"] += max(narr, b["anim"]); s["blocks"] += 1

    print(f"\nRuntime estimate ({args.wpm:.0f} words/min; per block = max(narration, animation)):")
    print(f"{'scene':<34}{'blocks':>7}{'words':>7}{'narr':>7}{'anim':>7}{'est':>7}")
    for name, s in per_scene.items():
        flag = "  <- animation outlasts narration" if s["anim"] > s["narr"] + 2 else ""
        print(f"{name:<34}{s['blocks']:>7}{s['words']:>7}{fmt(s['narr']):>7}{fmt(s['anim']):>7}{fmt(s['est']):>7}{flag}")
    total = sum(s["est"] for s in per_scene.values())
    words = sum(s["words"] for s in per_scene.values())
    verdict = "within" if total <= args.budget else "OVER"
    print(f"{'TOTAL':<34}{len(blocks):>7}{words:>7}{'':>14}{fmt(total):>7}  ({verdict} the {fmt(args.budget)} budget)")

    # ---- stills -------------------------------------------------------------
    sheets = contact_sheets(stills, out) if stills else []
    print(f"\n{len(stills)} stills in {stills_dir}")
    if sheets:
        print("Contact sheets to read (yellow label = still number + scene):")
        for s in sheets:
            print(f"  {s}")
    mp4 = sorted((out / "media").rglob("*.mp4"), key=lambda p: p.stat().st_size)
    if mp4:
        print(f"Video: {mp4[-1]}")


if __name__ == "__main__":
    main()
