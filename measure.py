"""Make the 16 kHz / 8 kHz clips and time each pipeline step on Smallest AI. Costs a few cents."""
import base64, json, os, socket, statistics, time
import numpy as np, requests
from scipy.io import wavfile
from scipy.signal import resample_poly
import sa
from mingos_prompt import PROMPT

WAVES = 'https://api.smallest.ai/waves/v1'
SENTENCE = 'Two cold coffees to Central Block, please.'
REPLY = "Two cold coffees to Central Block, that's one hundred and eighty rupees. Shall I place it?"
VOICE = {'voice_id': 'srishti', 'model': 'lightning_v3.1', 'language': 'en'}
os.makedirs('clips', exist_ok=True)
H = {'Authorization': sa.H['Authorization']}
RUNS = 5
results = {}


def med(xs):
    return round(statistics.median(xs))


# 1. The clips: the sentence at 16 kHz, then the same audio cut to 8 kHz the way a phone call does
r = requests.post(f'{WAVES}/tts', headers={**H, 'Content-Type': 'application/json', 'Accept': 'audio/wav'},
                  json={'text': SENTENCE, **VOICE, 'sample_rate': 16000, 'output_format': 'wav'}, timeout=60)
r.raise_for_status()
open('clips/sentence_16k.wav', 'wb').write(r.content)
rate, x = wavfile.read('clips/sentence_16k.wav')
assert rate == 16000, rate
y = resample_poly(x.astype(np.float64), 1, 2)  # low-pass filter + keep every second sample
wavfile.write('clips/sentence_8k.wav', 8000, np.clip(y, -32768, 32767).astype(np.int16))
print('clips written:', len(x) / 16000, 'seconds of speech')

# 2. Network: one round trip to the provider (TCP connect time)
rtt = []
for _ in range(RUNS):
    t = time.perf_counter(); s = socket.create_connection(('api.smallest.ai', 443), timeout=10)
    rtt.append((time.perf_counter() - t) * 1000); s.close()
results['network_rtt_ms'] = med(rtt)

# 3. Speech to text on the whole sentence, sent after the caller has finished (no streaming)
audio = open('clips/sentence_16k.wav', 'rb').read()
stt = []
for _ in range(3):
    t = time.perf_counter()
    r = requests.post(f'{WAVES}/stt/', params={'model': 'pulse', 'language': 'en'},
                      headers={**H, 'Content-Type': 'application/octet-stream'}, data=audio, timeout=60)
    stt.append((time.perf_counter() - t) * 1000)
r.raise_for_status()
results['stt_whole_sentence_ms'] = med(stt)
results['stt_heard'] = r.json().get('transcription')

# 4. Language model: no direct API access on this plan; its timing comes from the call log

# 5. Text to speech: time to the first audio, and time to the whole reply's audio
tfirst, tall = [], []
for _ in range(RUNS):
    t = time.perf_counter(); got_first = None
    with requests.post(f'{WAVES}/tts/live', headers={**H, 'Content-Type': 'application/json'},
                       json={'text': REPLY, **VOICE, 'sample_rate': 24000}, stream=True, timeout=60) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line.startswith(b'data:') and b'"audio"' in line and got_first is None:
                got_first = (time.perf_counter() - t) * 1000
    tfirst.append(got_first); tall.append((time.perf_counter() - t) * 1000)
results['tts_first_audio_ms'] = med(tfirst)
results['tts_whole_reply_ms'] = med(tall)

results['endpointing_wait_ms'] = 800  # the agent's release time setting
json.dump(results, open('measurements.json', 'w'), indent=1)
print(json.dumps(results, indent=1))
