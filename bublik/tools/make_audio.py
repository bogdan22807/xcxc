"""Озвучка без кредитов ElevenLabs, звуки действий и сведение."""

import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from gtts import gTTS

from make_music import SR, piano_noir

# Бесплатный русский голос. Бублик ровнее,
# Пончик выше и быстрее — так их можно различить.
VOICES = {
    "bublik": "atempo=1.48",
    "ponchik": "asetrate=29280,aresample=44100,atempo=1.34",
}


def _tone(freq, dur, decay=8, vol=0.3):
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)
    a = min(n, int(0.008 * SR))
    y[:a] *= np.linspace(0, 1, a)
    return (y * vol).astype(np.float32)


def _noise(dur, decay=12, vol=0.2, seed=1):
    n = max(1, int(dur * SR))
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    y = rng.standard_normal(n) * np.exp(-decay * t)
    return (y * vol).astype(np.float32)


def _mix(*clips):
    n = max(len(c) for c in clips)
    y = np.zeros(n, np.float32)
    for c in clips:
        y[: len(c)] += c
    return y


def _add(buf, clip, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    i = max(0, i)
    end = min(len(buf), i + len(clip))
    buf[i:end] += clip[: end - i]


def sfx_clip(name, dur):
    dur = max(0.2, float(dur))
    if name in (None, "", "none"):
        return np.zeros(1, np.float32)
    if name == "sting":
        return _mix(_tone(110, 0.28, 6, 0.45), _noise(0.22, 10, 0.3, 1))
    if name == "radar":
        y = np.zeros(int(dur * SR), np.float32)
        tt = 0.04
        while tt < dur - 0.05:
            _add(y, _tone(1040, 0.07, 22, 0.32), tt)
            tt += 0.38
        return y
    if name == "scope":
        y = np.zeros(int(dur * SR), np.float32)
        tt = 0.02
        k = 0
        while tt < dur - 0.05:
            _add(y, _tone(880 + k * 40, 0.06, 24, 0.28), tt)
            tt += 0.28
            k += 1
        return y
    if name == "crunch":
        return _mix(_noise(0.16, 18, 0.45, 2), _tone(180, 0.08, 20, 0.2))
    if name == "plane":
        n = int(dur * SR)
        t = np.arange(n) / SR
        rng = np.random.default_rng(8)
        y = 0.12 * np.sin(2 * np.pi * 78 * t)
        y += 0.05 * np.sin(2 * np.pi * 156 * t)
        y += rng.standard_normal(n) * 0.025
        env = np.clip(t / 0.12, 0, 1) * np.clip((dur - t) / 0.18, 0, 1)
        return (y * env).astype(np.float32)
    if name == "flash":
        return _mix(_noise(0.07, 30, 0.4, 3), _tone(1800, 0.05, 30, 0.15))
    if name == "paper":
        return _mix(_noise(0.25, 8, 0.28, 4), _noise(0.12, 16, 0.2, 5))
    if name == "mic":
        return _mix(_tone(640, 0.05, 30, 0.25), _noise(0.04, 40, 0.15, 6))
    if name == "steps":
        y = np.zeros(int(min(dur, 1.6) * SR), np.float32)
        for i, tt in enumerate((0.02, 0.18, 0.34, 0.5, 0.66)):
            _add(y, _noise(0.06, 28, 0.35, 10 + i), tt)
            _add(y, _tone(90, 0.05, 20, 0.15), tt)
        return y
    if name == "slap":
        return _mix(_noise(0.12, 22, 0.5, 7), _tone(140, 0.1, 14, 0.25))
    if name == "thud":
        return _mix(_tone(70, 0.25, 8, 0.5), _noise(0.08, 20, 0.2, 9))
    if name == "chop":
        return _mix(_noise(0.09, 26, 0.45, 11), _tone(220, 0.06, 24, 0.2))
    if name == "sparkle":
        y = np.zeros(int(0.45 * SR), np.float32)
        for i, f in enumerate((880, 1174, 1568, 1976)):
            _add(y, _tone(f, 0.12, 10, 0.16), i * 0.06)
        return y
    if name == "shimmer":
        return _mix(_tone(1320, 0.25, 6, 0.12), _tone(1760, 0.2, 7, 0.08))
    if name == "dim":
        n = int(0.4 * SR)
        t = np.arange(n) / SR
        freq = 500 - 320 * (t / 0.4)
        y = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-3 * t)
        return (y * 0.2).astype(np.float32)
    if name == "deny":
        y = np.zeros(int(0.4 * SR), np.float32)
        _add(y, _tone(420, 0.12, 8, 0.28), 0)
        _add(y, _tone(280, 0.16, 6, 0.3), 0.14)
        return y
    if name == "munch":
        y = np.zeros(int(0.4 * SR), np.float32)
        _add(y, _noise(0.1, 16, 0.4, 12), 0.0)
        _add(y, _noise(0.1, 16, 0.35, 13), 0.16)
        return y
    if name == "squish":
        return _mix(_noise(0.18, 8, 0.3, 14), _tone(160, 0.15, 6, 0.12))
    if name == "pop":
        return _tone(520, 0.09, 16, 0.3)
    if name == "switch":
        y = np.zeros(int(0.3 * SR), np.float32)
        _add(y, _noise(0.03, 40, 0.45, 15), 0.02)
        _add(y, _tone(90, 0.18, 10, 0.25), 0.05)
        return y
    if name == "dark":
        return _tone(55, 0.5, 3, 0.12)
    if name == "whoosh":
        n = int(0.35 * SR)
        t = np.arange(n) / SR
        freq = 300 + 1600 * (t / 0.35)
        y = np.sin(2 * np.pi * np.cumsum(freq) / SR)
        env = np.sin(np.pi * np.clip(t / 0.35, 0, 1))
        return (y * env * 0.18).astype(np.float32)
    if name == "car":
        n = int(min(dur, 2.0) * SR)
        t = np.arange(n) / SR
        y = 0.1 * np.sin(2 * np.pi * 62 * t) + 0.04 * np.sin(2 * np.pi * 124 * t)
        return (y * np.clip(t / 0.1, 0, 1)).astype(np.float32)
    return _noise(0.1, 12, 0.2, 1)


def _fade(x):
    x = np.array(x, dtype=np.float32, copy=True)
    n = min(len(x) // 3, int(0.02 * SR))
    if n > 1:
        x[:n] *= np.linspace(0, 1, n)
        x[-n:] *= np.linspace(1, 0, n)
    return x


def _read_wav(path):
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise RuntimeError(f"ожидался pcm16, пришло {sw}")
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        idx = np.linspace(0, len(a) - 1, int(len(a) * SR / sr))
        a = np.interp(idx, np.arange(len(a)), a).astype(np.float32)
    return a


def _write_wav(path, mono):
    stereo = np.column_stack([mono, mono])
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def _align(text, dur):
    """Раскладка слов по длине реплики: у gTTS нет покадровых меток."""
    parts = text.split()
    weights = [max(1, sum(ch.isalpha() for ch in w)) for w in parts]
    total = sum(weights) or 1
    lead = min(0.06, dur * 0.08)
    usable = max(0.15, dur - lead - 0.04)
    t = lead
    out = []
    for w, wt in zip(parts, weights):
        d = usable * wt / total
        out.append({"t": round(t, 3), "d": round(d, 3), "w": w})
        t += d
    return out


def _line_audio(line, cache: Path):
    fx = VOICES[line["speaker"]]
    key = hashlib.sha1(f"gtts|{line['speaker']}|{fx}|{line['text']}".encode()).hexdigest()[:16]
    mp3 = cache / f"{key}.mp3"
    wav = cache / f"{key}.wav"
    cache.mkdir(parents=True, exist_ok=True)
    if not mp3.exists():
        gTTS(line["text"], lang="ru").save(str(mp3))
    if not wav.exists():
        subprocess.check_call(
            ["ffmpeg", "-y", "-i", str(mp3), "-af", fx, "-ar", str(SR), "-ac", "1", str(wav)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    audio = _fade(_read_wav(wav))
    return audio, _align(line["text"], len(audio) / SR)


def _duck(music, spans):
    env = np.ones(len(music), np.float32)
    for a, b in spans:
        i, j = int(a * SR), int(b * SR)
        env[max(0, i) : min(len(env), j)] = 0.32
    win = np.ones(int(0.06 * SR), np.float32)
    win /= win.sum()
    smooth = np.convolve(env, win, mode="same")
    return music * smooth


def build_timeline(seg, cache: Path, wav_path: Path):
    spoken = []
    for line in seg["lines"]:
        audio, words = _line_audio(line, cache)
        spoken.append((audio, words))
        print(f"  голос {line['id']} {line['speaker']}: {len(audio)/SR:.2f} с")
    raw = sum(len(a) / SR for a, _ in spoken)
    n = len(spoken)
    gap = 0.12
    tail = 0.45
    total = raw + gap * (n - 1) + tail
    if total < 46:
        gap = min(0.32, (46 - raw - tail) / max(1, n - 1))
        total = raw + gap * (n - 1) + tail
        if total < 45:
            tail += 45 - total
            total = 45
    print(f"черновая длина {total:.1f} с, пауза {gap:.2f} с")

    mix = np.zeros(int((total + 0.2) * SR), np.float32)
    timeline = []
    cursor = 0.0
    spans = []
    for line, (audio, words) in zip(seg["lines"], spoken):
        dur = len(audio) / SR
        _add(mix, audio, cursor)
        spans.append((cursor, cursor + dur))
        _add(mix, sfx_clip(line.get("sfx"), dur) * 0.55, cursor)
        if line.get("sfx_mid"):
            _add(mix, sfx_clip(line["sfx_mid"], dur * 0.5) * 0.5, cursor + dur * 0.5)
        timeline.append(
            {
                "id": line["id"],
                "speaker": line["speaker"],
                "text": line["text"],
                "scene": line["scene"],
                "mid": line.get("mid"),
                "start": cursor,
                "end": cursor + dur,
                "dur": dur,
                "words": words,
            }
        )
        cursor += dur + gap
    cursor = timeline[-1]["end"] + tail
    music = piano_noir(cursor + 0.1)
    if len(music) < len(mix):
        music = np.pad(music, (0, len(mix) - len(music)))
    mix = mix[: int(cursor * SR)]
    music = _duck(music[: len(mix)], spans)
    # Короткий вход, чтобы первый кадр не съела тишина, но без щелчка.
    fin = min(len(music), int(0.05 * SR))
    music[:fin] *= np.linspace(0, 1, fin)
    fout = min(len(music), int(0.3 * SR))
    music[-fout:] *= np.linspace(1, 0, fout)
    mix = mix + music
    peak = float(np.max(np.abs(mix)) + 1e-6)
    if peak > 0.9:
        mix *= 0.9 / peak
    _write_wav(wav_path, mix)

    scale = 1.0
    duration = len(mix) / SR
    if duration > 59.5:
        sped = wav_path.with_name("sped.wav")
        tempo = duration / 55.0
        subprocess.check_call(
            ["ffmpeg", "-y", "-i", str(wav_path), "-af", f"atempo={tempo:.4f}", str(sped)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sped.replace(wav_path)
        new_len = _read_wav(wav_path)
        scale = (len(new_len) / SR) / duration
        duration = len(new_len) / SR
        for ln in timeline:
            ln["start"] *= scale
            ln["end"] *= scale
            ln["dur"] *= scale
            for w in ln["words"]:
                w["t"] *= scale
                w["d"] *= scale
        print(f"ускорение {tempo:.2f} → {duration:.1f} с")
    return {"duration": duration, "lines": timeline, "fps": seg.get("fps", 24)}


def loudnorm(src: Path, dst: Path):
    probe = subprocess.run(
        [
            "ffmpeg", "-i", str(src),
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
            "-f", "null", "-",
        ],
        capture_output=True, text=True,
    )
    err = probe.stderr
    meta = json.loads(err[err.rfind("{") : err.rfind("}") + 1])
    af = (
        "loudnorm=I=-14:TP=-1.5:LRA=11:"
        f"measured_I={meta['input_i']}:measured_TP={meta['input_tp']}:"
        f"measured_LRA={meta['input_lra']}:measured_thresh={meta['input_thresh']}:"
        f"offset={meta['target_offset']}:linear=true"
    )
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(src), "-af", af, str(dst)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
