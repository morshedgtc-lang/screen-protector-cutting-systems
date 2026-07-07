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

# Recharge / activation / payment related keywords
kw = ['recharge','charge','pay','vip','activate','activation','active','register',
      'registered','expire','expired','expiration','left','remain','total','balance',
      'coin','credit','quota','count','coupon','wallet','money','order','buy','purchase',
      '套餐','充值','余额','余','到期','激活','注册','会员','钱包','订单','购买','付费',
      'is_vip','is_expired','left_count','left_num','machine_code','device_id']

out_path = os.path.join(extracted, '..', 'recharge_analysis.txt')
with open(out_path, 'w', encoding='utf-8') as out:
    for dex in ['classes.dex','classes2.dex']:
        p = os.path.join(extracted, dex)
        if not os.path.exists(p): continue
        out.write('='*70 + '\n')
        out.write('ANALYZING ' + dex + '\n')
        out.write('='*70 + '\n')
        strings = parse_dex_strings(p)
        seen = set()
        for s in strings:
            low = s.lower()
            if any(k in low for k in kw):
                if s.startswith('L') and ';' in s:
                    continue
                if s in seen: continue
                seen.add(s)
                out.write('   ' + s[:200] + '\n')
        out.write('\n')
print('Wrote', out_path)

