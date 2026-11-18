"""Tiny Smallest AI helper. Reads SMALLEST_API_KEY and MY_PHONE from .env; never prints them."""
import json, os, sys, requests

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = {}
for line in open(os.path.join(HERE, '.env'), encoding='utf-8'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        ENV[k.strip()] = v.strip().strip('"')
KEY = ENV['SMALLEST_API_KEY']
PHONE = ENV.get('MY_PHONE', '')
ATOMS = 'https://api.smallest.ai/atoms/v1'
H = {'Authorization': f'Bearer {KEY}', 'Content-Type': 'application/json'}


def _clean(text):
    return text.replace(KEY, '[key]').replace(PHONE, '[my phone]') if PHONE else text.replace(KEY, '[key]')


def call(method, path, body=None, base=ATOMS, headers=None, quiet=False):
    r = requests.request(method, base + path, headers={**H, **(headers or {})}, json=body, timeout=60)
    try:
        data = r.json()
    except ValueError:
        data = r.text
    if not quiet:
        print(method, path, r.status_code)
        print(_clean(json.dumps(data, indent=1)[:6000] if not isinstance(data, str) else data[:3000]))
    return r.status_code, data


if __name__ == '__main__':
    call(sys.argv[1], sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else None)
