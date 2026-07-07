import os, struct

def read_uleb128(data, pos):
    result = 0; shift = 0
    while True:
        b = data[pos]; result |= (b & 0x7F) << shift; pos += 1
        if not (b & 0x80): break
        shift += 7
    return result, pos

def check_dex(dex_path):
    with open(dex_path, 'rb') as f:
        data = f.read()
    if data[0:4] != b'dex\n':
        print("Not DEX"); return
    string_ids_size = struct.unpack('<I', data[0x38:0x3C])[0]
    string_ids_off  = struct.unpack('<I', data[0x3C:0x40])[0]
    found_cloud = 0
    found_our = 0
    for i in range(string_ids_size):
        off = struct.unpack('<I', data[string_ids_off + i*4 : string_ids_off + i*4 + 4])[0]
        length, pos = read_uleb128(data, off)
        s = data[pos:pos+length]
        if b'mietubl.com' in s or b'aliyuncs' in s or b'mobile-films' in s:
            found_cloud += 1
            print(f"  STILL CLOUD: {s[:80]}")
        if b'satelecom.up.railway.app' in s:
            found_our += 1
            print(f"  PATCHED OK: {s[:80]}")
    print(f"  cloud refs={found_cloud}, our refs={found_our}")

base = r"D:\workspase\screen-protector cutting systems\patched_apk\patched_dex"
for dex in ["classes.dex", "classes2.dex"]:
    p = os.path.join(base, dex)
    if os.path.exists(p):
        print(f"== {dex} ==")
        check_dex(p)
