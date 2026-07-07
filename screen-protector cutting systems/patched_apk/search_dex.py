import os, re, struct

extracted = r"D:\workspase\screen-protector cutting systems\patched_apk\extracted"

# Search DEX files for strings (DEX format stores strings in a string table)
def search_dex_strings(dex_path):
    """Extract all strings from a DEX file and search for URLs/domains"""
    results = []
    with open(dex_path, 'rb') as f:
        data = f.read()
    
    # DEX header is at offset 0
    # String IDs offset is at 0x38 (56) in DEX 035
    if data[0:4] != b'dex\n':
        return results
    
    # Parse DEX header
    string_ids_off = struct.unpack('<I', data[0x38:0x3C])[0]
    string_ids_size = struct.unpack('<I', data[0x38-4:0x38])[0]  # Actually at 0x34
    
    # Let me fix the offsets
    # DEX header:
    # 0x00: magic 'dex\n035\0'
    # 0x08: checksum
    # 0x0C: sha1 signature (20 bytes)
    # 0x20: file_size
    # 0x24: header_size (usually 0x70)
    # 0x28: endian_tag
    # 0x2C: link_size
    # 0x30: link_off
    # 0x34: map_off
    # 0x38: string_ids_size
    # 0x3C: string_ids_off
    # 0x40: type_ids_size
    # 0x44: type_ids_off
    # 0x48: proto_ids_size
    # 0x4C: proto_ids_off
    # 0x50: field_ids_size
    # 0x54: field_ids_off
    # 0x58: method_ids_size
    # 0x5C: method_ids_off
    # 0x60: class_defs_size
    # 0x64: class_defs_off
    # 0x68: data_size
    # 0x6C: data_off
    
    string_ids_size = struct.unpack('<I', data[0x38:0x3C])[0]
    string_ids_off = struct.unpack('<I', data[0x3C:0x40])[0]
    
    # print(f"String IDs: {string_ids_size} at offset {string_ids_off}")
    
    strings = []
    for i in range(string_ids_size):
        str_off = struct.unpack('<I', data[string_ids_off + i*4 : string_ids_off + i*4 + 4])[0]
        if str_off >= len(data):
            continue
        # DEX strings: ULEB128 length followed by modified UTF-8 data
        # Read ULEB128
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
        try:
            s = str_bytes.decode('utf-8', errors='replace')
            strings.append(s)
        except:
            pass
    
    return strings

# Search DEX files
for dex_file in ['classes.dex', 'classes2.dex', 'classes3.dex']:
    dex_path = os.path.join(extracted, dex_file)
    if not os.path.exists(dex_path):
        continue
    
    print(f"\n=== Searching {dex_file} ===")
    strings = search_dex_strings(dex_path)
    print(f"Found {len(strings)} strings")
    
    # Look for cloud API URLs, domains, IPs
    targets = ['hsyunqiemo', 'cloudcutter', 'aliyuncs.com', 'mietubl', 
               'api.', 'cloud.', 'server', '://', '192.168', 'http']
    
    for s in strings:
        for t in targets:
            if t in s.lower():
                print(f"  MATCH: {s[:200]}")
                break

print("\n\n=== Also searching raw binary for key strings ===")
for dex_file in ['classes.dex', 'classes2.dex']:
    dex_path = os.path.join(extracted, dex_file)
    if not os.path.exists(dex_path):
        continue
    with open(dex_path, 'rb') as f:
        data = f.read()
    
    for target in [b'hsyunqiemo', b'cloudcutter', b'aliyuncs', b'oss-accelerate',
                   b'mietubl.com', b'huansheng', b'api.']:
        if target in data:
            idx = data.index(target)
            print(f"FOUND '{target.decode()}' in {dex_file} at offset {idx}")
            start = max(0, idx - 30)
            end = min(len(data), idx + len(target) + 100)
            print(f"  Context: {data[start:end]}")
