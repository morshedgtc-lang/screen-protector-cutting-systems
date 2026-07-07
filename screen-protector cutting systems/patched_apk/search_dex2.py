import os, re, struct

extracted = r"D:\workspase\screen-protector cutting systems\patched_apk\extracted"

def search_dex_strings(dex_path, target_substrings=None):
    """Extract all strings from a DEX file"""
    results = []
    with open(dex_path, 'rb') as f:
        data = f.read()
    
    if data[0:4] != b'dex\n':
        return results
    
    string_ids_size = struct.unpack('<I', data[0x38:0x3C])[0]
    string_ids_off = struct.unpack('<I', data[0x3C:0x40])[0]
    
    for i in range(string_ids_size):
        str_off = struct.unpack('<I', data[string_ids_off + i*4 : string_ids_off + i*4 + 4])[0]
        if str_off >= len(data):
            continue
        pos = str_off
        uleb = 0
        shift = 0
        while pos < len(data):
            byte = data[pos]
            uleb |= (byte & 0x7F) << shift
            shift += 7
            pos += 1
            if not (byte & 0x80):
                break
        
        str_len = uleb
        str_bytes = data[pos:pos + str_len]
        s = str_bytes.decode('utf-8', errors='replace')
        
        if target_substrings:
            for t in target_substrings:
                if isinstance(t, bytes):
                    t = t.decode('ascii', errors='replace')
                if t.lower() in s.lower():
                    results.append(s)
                    break
        else:
            results.append(s)
    
    return results

# Search for API-related strings
targets = [
    'hsyunqiemo', 'cloudcutter', 'aliyuncs', 'oss-accelerate',
    'mietubl.com', 'huansheng', 'api.', '.com/', '/api/', 
    'base_url', 'BASE_URL', 'baseUrl', 'apiUrl',
    '192.168', 'server', 'host', 'Host', 
    'satelecom', 'pltfile', 'datalist',
    'com/machinery/', 'MatcherApi', 'ApiService',
    '.plt', '/plt',
    'printer', 'PrinterServer', 'print_server',
    'activate', 'register', 'Register',
    'token', 'machineCode',
]

for dex_file in ['classes.dex', 'classes2.dex']:
    dex_path = os.path.join(extracted, dex_file)
    if not os.path.exists(dex_path):
        continue
    
    print(f"\n{'='*60}")
    print(f"Searching {dex_file}...")
    print('='*60)
    
    strings = search_dex_strings(dex_path, targets)
    
    # Deduplicate and sort
    for s in sorted(set(strings)):
        try:
            short = s[:300].replace('\n', '\\n').replace('\r', '')
            print(f"  {short}")
        except:
            pass

print("\n" + "="*60)
print("Searching raw binary for key strings")
print("="*60)

for dex_file in ['classes.dex', 'classes2.dex']:
    dex_path = os.path.join(extracted, dex_file)
    if not os.path.exists(dex_path):
        continue
    with open(dex_path, 'rb') as f:
        data = f.read()
    
    for target in [b'hsyunqiemo', b'cloudcutter', b'aliyuncs', b'oss-accelerate',
                   b'mietubl.com', b'huansheng', b'192.168', b'api.', b'.com/']:
        idx = 0
        while True:
            idx = data.find(target, idx)
            if idx == -1:
                break
            start = max(0, idx - 40)
            end = min(len(data), idx + len(target) + 120)
            ctx = data[start:end]
            try:
                ctx_str = ctx.decode('utf-8', errors='replace')
                print(f"  [{dex_file}] @{idx}: {ctx_str[:200]}")
            except:
                print(f"  [{dex_file}] @{idx}: {ctx.hex()[:200]}")
            idx += 1
