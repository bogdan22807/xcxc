"""Своя музыка. piano_noir — домашний мотив канала, не чужой трек."""

import numpy as np

SR = 44100


def _piano(freq, dur, sr=SR, vol=0.22):
    n = max(1, int(dur * sr))
    t = np.arange(n) / sr
    env = np.exp(-2.4 * t)
    y = np.sin(2 * np.pi * freq * t) * env
    y += 0.45 * np.sin(2 * np.pi * freq * 2 * t) * np.exp(-4.2 * t)
    y += 0.18 * np.sin(2 * np.pi * freq * 3 * t) * np.exp(-6.5 * t)
    y += 0.08 * np.sin(2 * np.pi * freq * 4 * t) * np.exp(-8 * t)
    # Мягкая атака, чтобы не щёлкало.
    a = min(n, int(0.012 * sr))
    y[:a] *= np.linspace(0, 1, a)
    return (y * vol).astype(np.float32)


def _add(buf, clip, at, sr=SR):
    i = int(at * sr)
    if i >= len(buf) or i < 0:
        return
    end = min(len(buf), i + len(clip))
    buf[i:end] += clip[: end - i]


def piano_noir(duration, sr=SR):
    """Редкий рояль в ля миноре. Мотив написан для канала, петля 9 секунд."""
    # (старт, длина, частота) — четверть ≈ 0.83 с при 72 bpm.
    phrase = [
        (0.00, 0.78, 220.00),
        (0.83, 0.36, 261.63),
        (1.25, 0.36, 329.63),
        (1.66, 0.70, 196.00),
        (2.50, 0.78, 174.61),
        (3.33, 0.36, 220.00),
        (3.74, 0.36, 261.63),
        (4.16, 0.78, 164.81),
        (5.00, 0.70, 220.00),
        (5.83, 0.32, 349.23),
        (6.25, 0.32, 329.63),
        (6.66, 0.50, 246.94),
        (7.50, 1.20, 220.00),
    ]
    loop = 9.0
    n = int(duration * sr)
    y = np.zeros(n, np.float32)
    start = 0.0
    while start < duration + 0.1:
        for at, dur, freq in phrase:
            _add(y, _piano(freq, dur, sr, 0.2), start + at, sr)
            _add(y, _piano(freq / 2, dur * 1.1, sr, 0.07), start + at, sr)
        start += loop
    t = np.arange(n) / sr
    y += (0.015 * np.sin(2 * np.pi * 110 * t)).astype(np.float32)
    peak = float(np.max(np.abs(y)) + 1e-6)
    y *= 0.22 / peak
    return y
