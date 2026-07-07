"""Search for SharedPreferences keys and server config in DEX strings."""
import zipfile, struct, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def read_uleb128(data, pos):
    result = 0; shift = 0
    while pos < len(data):
        b = data[pos]; result |= (b & 0x7F) << shift; pos += 1
        if not (b & 0x80): break
        shift += 7
    return result, pos

def extract_dex_strings(dex_data):
    strings = []
    if dex_data[0:4] != b'dex\n':
        return strings
    string_ids_size = struct.unpack_from('<I', dex_data, 0x38)[0]
    string_ids_off = struct.unpack_from('<I', dex_data, 0x3C)[0]
    for i in range(string_ids_size):
        off = struct.unpack_from('<I', dex_data, string_ids_off + i * 4)[0]
        length, pos = read_uleb128(dex_data, off)
        s = dex_data[pos:pos + length]
        try:
            strings.append(s.decode('utf-8'))
        except:
            strings.append(s.decode('latin-1', errors='replace'))
    return strings

APK = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"
with zipfile.ZipFile(APK) as z:
    for dex_name in ['classes.dex', 'classes2.dex']:
        dex_data = z.read(dex_name)
        strings = extract_dex_strings(dex_data)
        print(f"=== {dex_name}: {len(strings)} strings ===")
        
        # Find config-related strings
        config_kws = ['server', 'ip', 'url', 'api', 'host', 'config', 'setting',
                      'machine', 'device', 'token', 'auth', 'user', 'account',
                      'cut', 'recharge', 'expire', 'password', 'login', 'register',
                      'phone', 'email', 'admin', 'debug', 'diy', 'local', 'factory',
                      'shared_pref', 'pref_name', 'key_', 'pref_', 'sp_',
                      'base_url', 'baseUrl', 'SERVER', 'IP', 'URL', 'API']
        
        found = []
        for i, s in enumerate(strings):
            sl = s.lower()
            for kw in config_kws:
                if kw.lower() in sl and 3 < len(s) < 100:
                    found.append((i, s, kw))
                    break
        
        # Print found strings
        for idx, s, kw in found:
            print(f"  [{idx:5d}] ({kw}) {s}")
        print()
