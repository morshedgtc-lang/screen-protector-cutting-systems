import re

# Search the patched DEX for URLs and IPs
for fname in ['patched_dex/classes.dex', 'patched_dex/classes2.dex']:
    with open(fname, 'rb') as f:
        data = f.read()
    texts = [m.group() for m in re.finditer(b'[\\x20-\\x7e]{4,}', data)]
    urls = set()
    for t in texts:
        s = t.decode('ascii', errors='replace')
        if 'http' in s.lower() or '192.168' in s or 'api.' in s:
            urls.add(s)
    print(f'{fname}:')
    for u in sorted(urls):
        print(f'  {u}')
    print()
