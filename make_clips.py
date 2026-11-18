"""Mingos's voice saying the sentence at 16 kHz and cut to 8 kHz, as short spectrogram videos for slide 29."""
import subprocess, requests, numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly
import sa

SENTENCE = 'Two cold coffees to Central Block, please.'
r = requests.post('https://api.smallest.ai/waves/v1/tts',
                  headers={**sa.H, 'Accept': 'audio/wav'},
                  json={'text': SENTENCE, 'voice_id': 'meher', 'model': 'lightning_v3.1_pro', 'language': 'en',
                        'sample_rate': 16000, 'output_format': 'wav'}, timeout=60)
r.raise_for_status()
open('clips/sentence_16k.wav', 'wb').write(r.content)
rate, x = wavfile.read('clips/sentence_16k.wav'); assert rate == 16000
y = resample_poly(x.astype(np.float64), 1, 2)                       # what a phone call keeps: 8 kHz
wavfile.write('clips/sentence_8k.wav', 8000, np.clip(y, -32768, 32767).astype(np.int16))
z = resample_poly(y, 2, 1)                                          # back to 16 kHz only so both pictures share an axis
wavfile.write('clips/sentence_8k_as16k.wav', 16000, np.clip(z, -32768, 32767).astype(np.int16))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

CMAP = LinearSegmentedColormap.from_list('blueprint', ['#FBFCFE', '#F8CDB4', '#E0662A', '#B4471A', '#14243D'])
REF = None

def spectrogram(wav, png, label):
    global REF
    rate, a = wavfile.read(wav)
    a = a.astype(np.float64)
    fig = plt.figure(figsize=(16, 8), dpi=100, facecolor='#F3F6FA')
    ax = fig.add_axes([0.12, 0.14, 0.85, 0.72], facecolor='#FBFCFE')
    Pxx, freqs, bins, im = ax.specgram(a, NFFT=512, Fs=rate, noverlap=384, cmap=CMAP, scale='dB', mode='psd')
    db = 10 * np.log10(Pxx + 1e-20)
    if REF is None:
        REF = db.max()                      # same loudness scale for both pictures
    im.set_clim(REF - 75, REF)
    ax.set_ylim(0, 8000)
    ax.set_yticks([0, 4000, 8000]); ax.set_yticklabels(['0 kHz', '4 kHz', '8 kHz'])
    ax.set_xticks([])
    ax.axhline(4000, color='#0E7C86', lw=3, ls='--')
    for side in ax.spines.values():
        side.set_color('#14243D'); side.set_linewidth(3)
    ax.tick_params(colors='#14243D', labelsize=26, length=0, pad=12)
    fig.text(0.12, 0.9, label, fontsize=34, color='#14243D', fontweight='bold', family='Segoe UI')
    fig.text(0.12, 0.05, 'time →', fontsize=24, color='#50607A', family='Segoe UI')
    fig.savefig(png, facecolor='#F3F6FA'); plt.close(fig)

def video(png, wav, mp4):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-i', png, '-i', wav, '-c:v', 'libx264', '-tune', 'stillimage',
                    '-pix_fmt', 'yuv420p', '-r', '10', '-c:a', 'aac', '-b:a', '128k', '-ar', '44100', '-shortest',
                    '-movflags', '+faststart', mp4], check=True)

spectrogram('clips/sentence_16k.wav', 'clips/spec_16k.png', '16 kHz, like a laptop: sound up to 8 kHz')
spectrogram('clips/sentence_8k_as16k.wav', 'clips/spec_8k.png', '8 kHz, like a phone call: nothing above 4 kHz')
video('clips/spec_16k.png', 'clips/sentence_16k.wav', 'clips/sentence_16k.mp4')
video('clips/spec_8k.png', 'clips/sentence_8k.wav', 'clips/sentence_8k.mp4')
print('done', len(x) / 16000, 'seconds')
