import struct, os

# Mapping of old URL -> new URL (old app.mietubl.com -> our server)
# We keep the same base path idea:
#   old base:  https://app.mietubl.com/api/        -> app calls base + "datalist/user"
#   new base:  https://satelecom.up.railway.app/   -> our server serves /datalist/user (and /api/datalist/user)
#   old oss:   https://mietubl.oss-accelerate.aliyuncs.com/       -> app downloads plt from here
#   new oss:   https://satelecom.up.railway.app/oss/ -> our server serves /oss/model/xxx.plt
#   old oss model: https://mietubl.oss-accelerate.aliyuncs.com/model/ -> https://satelecom.up.railway.app/oss/model/

BASE = r"D:\workspase\screen-protector cutting systems\patched_apk"

REPLACEMENTS_CLOUD = [
    (b"https://app.mietubl.com/api/",        b"https://satelecom.up.railway.app/"),
    (b"https://mietubl.oss-accelerate.aliyuncs.com/",     b"https://satelecom.up.railway.app/oss/"),
    (b"https://mietubl.oss-accelerate.aliyuncs.com/model/", b"https://satelecom.up.railway.app/oss/model/"),
    # mobile-films variant
    (b"https://app.mobile-films.com/api/",   b"https://satelecom.up.railway.app/"),
    (b"https://mobile-films.oss-cn-hongkong.aliyuncs.com/",      b"https://satelecom.up.railway.app/oss/"),
    (b"https://mobile-films.oss-cn-hongkong.aliyuncs.com/model/", b"https://satelecom.up.railway.app/oss/model/"),
]

REPLACEMENTS_LOCAL = [
    (b"https://app.mietubl.com/api/",        b"http://192.168.0.100:8000/"),
    (b"https://mietubl.oss-accelerate.aliyuncs.com/",     b"http://192.168.0.100:8000/oss/"),
    (b"https://mietubl.oss-accelerate.aliyuncs.com/model/", b"http://192.168.0.100:8000/oss/model/"),
    # mobile-films variant
    (b"https://app.mobile-films.com/api/",   b"http://192.168.0.100:8000/"),
    (b"https://mobile-films.oss-cn-hongkong.aliyuncs.com/",      b"http://192.168.0.100:8000/oss/"),
    (b"https://mobile-films.oss-cn-hongkong.aliyuncs.com/model/", b"http://192.168.0.100:8000/oss/model/"),
]

def read_uleb128(data, pos):
    result = 0
    shift = 0
    while True:
        b = data[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if not (b & 0x80):
            break
        shift += 7
    return result, pos

def write_uleb128(value):
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)

def patch_dex(dex_path, out_path):
    with open(dex_path, 'rb') as f:
        data = bytearray(f.read())

    if data[0:4] != b'dex\n':
        raise SystemExit("Not a DEX file: " + dex_path)

    # Header fields
    string_ids_size = struct.unpack('<I', data[0x38:0x3C])[0]
    string_ids_off  = struct.unpack('<I', data[0x3C:0x40])[0]
    data_size       = struct.unpack('<I', data[0x68:0x6C])[0]
    data_off        = struct.unpack('<I', data[0x6C:0x70])[0]
    file_size       = struct.unpack('<I', data[0x20:0x24])[0]

    # Collect (offset, original_string) for every string id
    strings = []
    for i in range(string_ids_size):
        off = struct.unpack('<I', data[string_ids_off + i*4 : string_ids_off + i*4 + 4])[0]
        # read ULEB128 length
        length, pos = read_uleb128(data, off)
        s = bytes(data[pos:pos+length])
        strings.append((off, s))

    # Build replacement map keyed by original bytes
    repl_map = {old: new for old, new in REPLACEMENTS}

    # Apply replacements (only if exact match found)
    changed = False
    new_strings = []
    for off, s in strings:
        if s in repl_map:
            new_strings.append((off, repl_map[s]))
            changed = True
        else:
            new_strings.append((off, s))

    if not changed:
        print(f"  [!] No target strings found in {os.path.basename(dex_path)}")
        return False

    # Rebuild the string DATA section. The string data lives in the data section.
    # We need to find where string data starts and ends within the data section.
    # String data region: from min(string offset) to max(string offset + strlen)
    str_start = min(off for off, _ in strings)
    str_end = max(off + len(s) for off, s in strings)

    # The rest of the data section (after str_end) stays the same.
    # But other data before str_start (e.g., type lists, proto lists) also stays.
    # We only rewrite the [str_start, str_end) region and pad/shift the rest.

    # Rebuild string data blob (in original id order)
    new_blob = bytearray()
    new_offsets = []
    for off, s in new_strings:
        new_offsets.append(str_start + len(new_blob))
        new_blob += write_uleb128(len(s))
        new_blob += s

    # The new blob may differ in size from old region
    old_region_len = str_end - str_start
    delta = len(new_blob) - old_region_len

    # Construct new data section: [0:str_start] + new_blob + [str_end:]
    new_data_section = bytearray(data[data_off:str_start]) + new_blob + bytearray(data[str_end:])

    # Update all string_ids offsets
    for i, (off, s) in enumerate(new_strings):
        new_off = new_offsets[i]
        struct.pack_into('<I', data, string_ids_off + i*4, new_off)

    # Rebuild whole file: header + id tables + new data section
    # id tables are between header(0x70) and data_off; they are unchanged.
    head_part = bytearray(data[0:data_off])
    new_file = head_part + new_data_section

    # Update header: file_size and data_size (data_size may change by delta)
    new_file_size = len(new_file)
    struct.pack_into('<I', new_file, 0x20, new_file_size)
    struct.pack_into('<I', new_file, 0x68, data_size + delta)

    # recompute DEX checksum (optional but good) and sha1
    # checksum = adler32 of everything after first 32 bytes (magic+checksum)
    import zlib
    # zero out checksum + signature fields before compute
    struct.pack_into('<I', new_file, 0x20, 0)  # file_size already set, keep
    # Actually checksum covers from offset 32 (after magic+checksum) to end? Spec: checksum over entire file except magic(8) and checksum(4) = bytes [12:]? 
    # DEX spec: checksum is adler32 over all bytes of the file following the magic and checksum fields (i.e., from offset 12? No). 
    # Standard: checksum = adler32(data[12:])  -- but many tools use data[12:]. Let's follow: adler32 over bytes from offset 12 to end BEFORE checksum insertion.
    # We'll compute over new_file[12:] with checksum field zeroed.
    # First zero the 4-byte checksum field at offset 8-12.
    struct.pack_into('<I', new_file, 8, 0)
    checksum = zlib.adler32(bytes(new_file[12:])) & 0xFFFFFFFF
    struct.pack_into('<I', new_file, 8, checksum)
    # sha1 signature over bytes from offset 32 to end (after magic+checksum+signature)
    import hashlib
    sha = hashlib.sha1(bytes(new_file[32:])).digest()
    struct.pack_into('<20s', new_file, 12, sha)

    with open(out_path, 'wb') as f:
        f.write(new_file)

    print(f"  [OK] Patched {os.path.basename(dex_path)} -> {os.path.basename(out_path)} (delta={delta:+d} bytes)")
    return True

def run_variant(label, reps, out_dir):
    global REPLACEMENTS
    REPLACEMENTS = reps
    out_base = os.path.join(BASE, out_dir)
    os.makedirs(out_base, exist_ok=True)
    print(f"\n=== Patching DEXes ({label}) ===")
    for dex in ["classes.dex", "classes2.dex", "classes3.dex"]:
        src = os.path.join(BASE, "extracted", dex)
        if os.path.exists(src):
            patch_dex(src, os.path.join(out_base, dex))


if __name__ == "__main__":
    import sys
    variant = sys.argv[1] if len(sys.argv) > 1 else "cloud"
    if variant == "cloud":
        run_variant("cloud", REPLACEMENTS_CLOUD, "patched_dex")
    elif variant == "local":
        run_variant("local", REPLACEMENTS_LOCAL, "patched_dex_local")
    else:
        print(f"Unknown variant: {variant}")
        print("Usage: python patch_dex.py [cloud|local]")
