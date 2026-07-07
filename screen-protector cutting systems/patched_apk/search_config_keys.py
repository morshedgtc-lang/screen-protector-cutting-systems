"""Search for SharedPreferences keys and server config in DEX."""
import zipfile, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APK = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"
with zipfile.ZipFile(APK) as z:
    data2 = z.read('classes2.dex')
    
    # Find what's near the URL strings
    for url in [b'https://app.mietubl.com/api/', b'https://mietubl.oss-accelerate.aliyuncs.com/']:
        pos = data2.find(url)
        if pos >= 0:
            start = max(0, pos - 200)
            end = min(len(data2), pos + 250)
            context = data2[start:end]
            printable = bytes(b if 32 <= b < 127 else 46 for b in context).decode('ascii')
            print(f"=== Context around {url.decode()} ===")
            print(f"  {printable}")
    
    # Find all putString keys that look config-related
    pattern = rb'putString\("([^"]+)"'
    matches = list(re.finditer(pattern, data2))
    print(f"\n=== putString keys ({len(matches)} total) ===")
    for m in matches:
        key = m.group(1).decode('ascii', errors='replace')
        low = key.lower()
        if any(x in low for x in ['server', 'ip', 'url', 'api', 'host', 'config', 
                                    'setting', 'machine', 'device', 'token', 'auth',
                                    'user', 'account', 'cut', 'recharge', 'expire',
                                    'password', 'login', 'register', 'phone', 'email']):
            pos = m.start()
            start = max(0, pos - 30)
            end = min(len(data2), pos + 80)
            context = data2[start:end]
            printable = bytes(b if 32 <= b < 127 else 46 for b in context).decode('ascii')
            print(f"  KEY: {key}")
            print(f"    ...{printable}...")
            print()

    # Find all getString keys
    pattern2 = rb'getString\("([^"]+)"'
    matches2 = list(re.finditer(pattern2, data2))
    print(f"\n=== getString keys ({len(matches2)} total) ===")
    for m in matches2:
        key = m.group(1).decode('ascii', errors='replace')
        low = key.lower()
        if any(x in low for x in ['server', 'ip', 'url', 'api', 'host', 'config',
                                    'setting', 'machine', 'device', 'token', 'auth',
                                    'user', 'account', 'cut', 'recharge', 'expire',
                                    'password', 'login', 'register']):
            pos = m.start()
            start = max(0, pos - 30)
            end = min(len(data2), pos + 80)
            context = data2[start:end]
            printable = bytes(b if 32 <= b < 127 else 46 for b in context).decode('ascii')
            print(f"  KEY: {key}")
            print(f"    ...{printable}...")
            print()
    
    # Also search classes.dex
    data1 = z.read('classes.dex')
    
    # Find putString keys in classes.dex
    matches3 = list(re.finditer(pattern, data1))
    print(f"\n=== classes.dex: putString keys ({len(matches3)} total) ===")
    for m in matches3:
        key = m.group(1).decode('ascii', errors='replace')
        low = key.lower()
        if any(x in low for x in ['server', 'ip', 'url', 'api', 'host', 'config',
                                    'setting', 'machine', 'device', 'token', 'auth',
                                    'user', 'account', 'cut', 'recharge', 'expire',
                                    'password', 'login', 'register', 'phone', 'email']):
            pos = m.start()
            start = max(0, pos - 30)
            end = min(len(data1), pos + 80)
            context = data1[start:end]
            printable = bytes(b if 32 <= b < 127 else 46 for b in context).decode('ascii')
            print(f"  KEY: {key}")
            print(f"    ...{printable}...")
            print()
