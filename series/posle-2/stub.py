"""Заглушка озвучки: примерный тайминг без голоса, пока нет квоты ElevenLabs. Настоящая озвучка: python3 tts.py"""
import json, os, subprocess
from script import SCENES
D = os.path.dirname(os.path.abspath(__file__))
for i, s in enumerate(SCENES, 1):
    t = 0.0; st = []; en = []
    for ch in s["text"]:
        d = 0.066 if ch != " " else 0.05
        st.append(round(t, 3)); t += d; en.append(round(t, 3))
        if ch in ".?!": t += 0.38
        if ch == ",": t += 0.18
    json.dump(dict(characters=list(s["text"]), character_start_times_seconds=st, character_end_times_seconds=en), open(f"{D}/v{i}.json", "w"), ensure_ascii=False)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(en[-1]), f"{D}/v{i}.mp3"])
    print(i, round(en[-1], 2))
