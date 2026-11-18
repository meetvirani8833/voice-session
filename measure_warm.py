"""Re-time speech to text and text to speech over one kept-open connection, as a live call would."""
import json, statistics, time, requests
import sa

WAVES = 'https://api.smallest.ai/waves/v1'
REPLY = "Two cold coffees to Central Block, that's one hundred and eighty rupees. Shall I place it?"
VOICE = {'voice_id': 'srishti', 'model': 'lightning_v3.1', 'language': 'en'}
S = requests.Session(); S.headers['Authorization'] = sa.H['Authorization']
S.get('https://api.smallest.ai/atoms/v1/user', timeout=30)  # open the connection once
out = json.load(open('measurements.json'))

audio = open('clips/sentence_16k.wav', 'rb').read()
stt = []
for _ in range(5):
    t = time.perf_counter()
    r = S.post(f'{WAVES}/stt/', params={'model': 'pulse', 'language': 'en'},
               headers={'Content-Type': 'application/octet-stream'}, data=audio, timeout=60)
    r.raise_for_status(); stt.append((time.perf_counter() - t) * 1000)

first, whole = [], []
for _ in range(5):
    t = time.perf_counter(); f = None
    with S.post(f'{WAVES}/tts/live', headers={'Content-Type': 'application/json'},
                json={'text': REPLY, **VOICE, 'sample_rate': 24000}, stream=True, timeout=60) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if f is None and line.startswith(b'data:') and b'"audio"' in line:
                f = (time.perf_counter() - t) * 1000
    first.append(f); whole.append((time.perf_counter() - t) * 1000)

out.update({'warm_stt_whole_sentence_ms': round(statistics.median(stt)),
            'warm_tts_first_audio_ms': round(statistics.median(first)),
            'warm_tts_whole_reply_ms': round(statistics.median(whole)),
            'warm_runs': {'stt': [round(x) for x in stt], 'tts_first': [round(x) for x in first], 'tts_whole': [round(x) for x in whole]}})
json.dump(out, open('measurements.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
