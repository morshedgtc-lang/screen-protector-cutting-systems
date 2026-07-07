import os, struct, re

extracted = r"D:\workspase\screen-protector cutting systems\patched_apk\extracted"

def parse_dex_strings(dex_path):
    with open(dex_path, 'rb') as f:
        data = f.read()
    if data[0:4] != b'dex\n':
        return []
    string_ids_size = struct.unpack('<I', data[0x38:0x3C])[0]
    string_ids_off  = struct.unpack('<I', data[0x3C:0x40])[0]
    out = []
    for i in range(string_ids_size):
        off = struct.unpack('<I', data[string_ids_off + i*4 : string_ids_off + i*4 + 4])[0]
        if off >= len(data): continue
        pos = off; uleb = 0; shift = 0
        while pos < len(data):
            b = data[pos]; uleb |= (b & 0x7F) << shift; shift += 7; pos += 1
            if not (b & 0x80): break
        out.append(data[pos:pos+uleb].decode('utf-8', errors='replace'))
    return out

# Method/field/string names related to cut permission + the data fields returned by user API
patterns = ['cutcount','Cutcount','cutCount','left_count','leftCount','left_num','remain','expired',
            'isExpired','is_expired','isVip','is_vip','canCut','can_cut','checkCut','checkVip',
            'model_cutcount','getCutcount','setCutcount','getBalance','balance','wallet','Wallet',
            'recharge','Recharge','payCut','deduct','consume','enough','insufficient','expired_at',
            'activate','Activate','registered','isRegistered','machineCode','deviceId']

out_path = os.path.join(extracted, '..', 'cutlogic_analysis.txt')
with open(out_path, 'w', encoding='utf-8') as out:
    for dex in ['classes.dex','classes2.dex']:
        p = os.path.join(extracted, dex)
        if not os.path.exists(p): continue
        out.write('='*70 + '\n' + dex + '\n' + '='*70 + '\n')
        strings = parse_dex_strings(p)
        for s in strings:
            if any(pat.lower() in s.lower() for pat in patterns):
                # skip obvious rxjava/observer noise
                if s.startswith('L') and ';' in s and ('Observer' in s or 'rxjava' in s.lower()):
                    continue
                out.write('  ' + s[:220] + '\n')
        out.write('\n')
print('Wrote', out_path)
