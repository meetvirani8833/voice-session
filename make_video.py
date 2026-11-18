"""Turn the audio-only call recording into a captioned 1920x1080 video for slide 2."""
import json, re, subprocess

SRC = 'clips/Meet & Mingos Voice Agent.mp4'
OUT = 'clips/mingos_call_captioned.mp4'
words = json.load(open('demo_transcript.json'))['words']

# Each line of the call: who says it, how it is captioned, and how many recognised words it spans.
TURNS = [
    ('Mingos', 'This is Mingos! What can I get you today?', 9),
    ('Meet', 'Uh, hi, can I get two cold coffees, please?', 9),
    ('Mingos', 'Two cold coffees, got it. Where should we deliver them to?', 11),
    ('Meet', 'Uh, it will be to Central Block.', 6),
    ('Mingos', "So that's two cold coffees to Central Block for one hundred and eighty rupees…", 14),
    ('Meet', 'Oh, sorry, wait wait wait. Uh, less sugar in both of them, please.', 13),
    ('Mingos', 'Less sugar in both, got it. So two cold coffees with less sugar to Central Block for one hundred and eighty rupees. Confirm that?', 24),
    ('Meet', "Yeah, that's right.", 3),
    ('Mingos', 'And whose name should the bill be in?', 8),
    ('Meet', 'Uh, put it on Dr. Rajesh Kanna.', 7),
    ('Mingos', "Got it, the bill's in Dr. Rajesh Kanna's name. Thanks for ordering, and have a great day!", 0),
]

# Walk the recognised words to find each line's start and end time.
i = 0
segs = []
for who, text, n in TURNS:
    chunk = words[i:] if n == 0 else words[i:i + n]
    segs.append((who, text, chunk[0]['start'], chunk[-1]['end'], [w['word'] for w in chunk]))
    i += n if n else len(chunk)
assert i == len(words), (i, len(words))
for who, text, a, b, ws in segs:
    print(f'{a:6.2f}-{b:6.2f} {who:6} | {" ".join(ws)}')

def ts(t):
    h, t = divmod(t, 3600); m, s = divmod(t, 60)
    return f'{int(h)}:{int(m):02d}:{s:05.2f}'

def esc(s):
    return s.replace('{', '(').replace('}', ')')

# ASS subtitles: speaker name in its colour above the line. Colours are &HBBGGRR.
ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1920', 'PlayResY: 1080', 'WrapStyle: 0', '',
       '[V4+ Styles]',
       'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
       'Style: Line,Segoe UI Semibold,64,&H003D2414,&H003D2414,&H00FAF6F3,&H00FAF6F3,0,0,0,0,100,100,0,0,1,0,0,7,128,128,470,1',
       'Style: Who,Segoe UI,40,&H001A47B4,&H001A47B4,&H00FAF6F3,&H00FAF6F3,1,0,0,0,100,100,3,0,1,0,0,7,128,128,400,1',
       'Style: Head,Segoe UI,34,&H007A6050,&H007A6050,&H00FAF6F3,&H00FAF6F3,1,0,0,0,100,100,4,0,1,0,0,7,128,128,96,1',
       'Style: Title,Segoe UI Semibold,60,&H003D2414,&H003D2414,&H00FAF6F3,&H00FAF6F3,0,0,0,0,100,100,0,0,1,0,0,7,128,128,150,1',
       '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC]).decode())
ass.append(f'Dialogue: 0,{ts(0)},{ts(dur)},Head,,0,0,0,,RECORDED CALL · AN AI VOICE AGENT TAKES AN ORDER')
ass.append(f'Dialogue: 3,{ts(0)},{ts(dur)},Title,,0,0,0,,Mingos, campus café')
for k, (who, text, a, b, _) in enumerate(segs):
    end = segs[k + 1][2] - 0.1 if k + 1 < len(segs) else dur
    colour = '&H001A47B4&' if who == 'Mingos' else '&H00867C0E&'
    label = 'MINGOS · AI AGENT' if who == 'Mingos' else 'MEET · CALLER'
    ass.append(f'Dialogue: 1,{ts(max(a - 0.1, 0))},{ts(end)},Who,,0,0,0,,{{\\c{colour}}}{label}')
    ass.append(f'Dialogue: 2,{ts(max(a - 0.1, 0))},{ts(end)},Line,,0,0,0,,{esc(text)}')
open('clips/call.ass', 'w', encoding='utf-8').write('\n'.join(ass) + '\n')

filt = ('color=c=0xF3F6FA:s=1920x1080:d={d}[bg];'
        '[0:a]aformat=channel_layouts=mono,showwaves=s=1664x200:mode=cline:draw=full:colors=0x0E7C86:rate=30,format=rgba[w];'
        '[bg][w]overlay=128:800[v];[v]subtitles=clips/call.ass[out]').format(d=dur)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-filter_complex', filt, '-map', '[out]', '-map', '0:a',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '128k', '-shortest',
                '-movflags', '+faststart', OUT], check=True)
print('wrote', OUT)
