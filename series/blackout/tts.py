import json, base64, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import SCENES
D = os.path.dirname(os.path.abspath(__file__))
VOICE = "nPczCjzI2devNBz1zQrb"  # тот же голос, что в прошлой версии: голос сериала
T = [s["text"] for s in SCENES]
for i, text in enumerate(T, 1):
    body = {"text": text, "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.6, "similarity_boost": 0.75, "style": 0.0}}
    if i > 1: body["previous_text"] = T[i - 2]
    if i < len(T): body["next_text"] = T[i]
    open(f"{D}/req.json", "w").write(json.dumps(body, ensure_ascii=False))
    r = subprocess.run(["curl", "-sS", "-m", "120", "-X", "POST",
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}/with-timestamps?output_format=mp3_44100_128",
        "-H", "Content-Type: application/json", "--data-binary", f"@{D}/req.json"], capture_output=True)
    d = json.loads(r.stdout)
    if "audio_base64" not in d:
        print(i, str(d)[:400]); sys.exit(1)
    open(f"{D}/v{i}.mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    a = d["alignment"]; json.dump(a, open(f"{D}/v{i}.json", "w"), ensure_ascii=False)
    print(i, "len", round(a["character_end_times_seconds"][-1], 2), "match", "".join(a["characters"]) == text, flush=True)
