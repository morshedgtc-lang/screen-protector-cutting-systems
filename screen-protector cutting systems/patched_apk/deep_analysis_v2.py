"""
Deep static analysis of the original APK.
V2: Fixed manifest parser + encoding safety.
"""
import zipfile, struct, os, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

APK_PATH = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"
REPORT_PATH = r"D:\workspase\screen-protector cutting systems\patched_apk\analysis_report.txt"

# ── Binary XML decoder ────────────────────────────────────────────────────
def parse_string_pool(data, offset):
    """Parse an Android string pool chunk."""
    strings = []
    try:
        chunk_size = struct.unpack_from('<I', data, offset)[0]
        str_count = struct.unpack_from('<I', data, offset + 12)[0]
        flags = struct.unpack_from('<I', data, offset + 16)[0]
        strings_start = struct.unpack_from('<I', data, offset + 20)[0]
        is_utf8 = (flags & (1 << 8)) != 0

        for i in range(min(str_count, 10000)):
            str_off = struct.unpack_from('<I', data, offset + 28 + i * 4)[0]
            abs_off = offset + strings_start + str_off
            if abs_off >= len(data):
                strings.append('')
                continue
            if is_utf8:
                char_len = data[abs_off]
                if char_len & 0x80:
                    abs_off += 2
                else:
                    abs_off += 1
                byte_len = data[abs_off]
                if byte_len & 0x80:
                    byte_len = ((byte_len & 0x7F) << 8) | data[abs_off + 1]
                    abs_off += 2
                else:
                    abs_off += 1
                try:
                    s = data[abs_off:abs_off + byte_len].decode('utf-8')
                except:
                    s = ''
                strings.append(s)
            else:
                char_len = struct.unpack_from('<H', data, abs_off)[0]
                abs_off += 2
                if char_len & 0x8000:
                    char_len = ((char_len & 0x7FFF) << 16) | struct.unpack_from('<H', data, abs_off)[0]
                    abs_off += 2
                try:
                    s = data[abs_off:abs_off + char_len * 2].decode('utf-16-le').rstrip('\x00')
                except:
                    s = ''
                strings.append(s)
    except Exception as e:
        strings.append(f'ERROR: {e}')
    return strings

def parse_manifest(data):
    """Parse AndroidManifest.xml binary format."""
    result = {
        'package': '',
        'activities': [],
        'services': [],
        'receivers': [],
        'providers': [],
        'permissions': [],
        'meta_data': [],
        'all_strings': [],
    }

    # Find string pool first
    strings = []
    pos = 0
    while pos < len(data) - 8:
        chunk_type = struct.unpack_from('<H', data, pos + 2)[0]
        if chunk_type == 0x0001:  # STRING
            strings = parse_string_pool(data, pos)
            result['all_strings'] = strings
            break
        chunk_size = struct.unpack_from('<I', data, pos)[0]
        if chunk_size == 0:
            break
        pos += chunk_size

    if not strings:
        return result

    # Parse XML elements
    pos = 0
    depth = 0
    parent_tags = []

    while pos < len(data) - 8:
        chunk_type = struct.unpack_from('<H', data, pos + 2)[0]
        chunk_size = struct.unpack_from('<I', data, pos)[0]
        if chunk_size == 0:
            break

        if chunk_type == 0x0102:  # START_ELEMENT
            ns_idx = struct.unpack_from('<i', data, pos + 16)[0]
            name_idx = struct.unpack_from('<i', data, pos + 20)[0]
            attr_count = struct.unpack_from('<H', data, pos + 28)[0]

            tag_name = strings[name_idx] if 0 <= name_idx < len(strings) else '?'

            attrs = {}
            for a in range(attr_count):
                a_pos = pos + 36 + a * 20
                if a_pos + 20 > len(data):
                    break
                a_name_idx = struct.unpack_from('<i', data, a_pos + 4)[0]
                a_value_idx = struct.unpack_from('<i', data, a_pos + 8)[0]
                a_type = struct.unpack_from('<H', data, a_pos + 14)[0]
                a_data = struct.unpack_from('<I', data, a_pos + 16)[0]

                a_name = strings[a_name_idx] if 0 <= a_name_idx < len(strings) else '?'

                if a_value_idx >= 0 and a_value_idx < len(strings):
                    val = strings[a_value_idx]
                elif a_type == 0x03:
                    val = strings[a_data] if 0 <= a_data < len(strings) else ''
                elif a_type in (0x10, 0x11):
                    val = str(a_data)
                elif a_type == 0x12:
                    val = 'true' if a_data else 'false'
                else:
                    val = str(a_data)
                attrs[a_name] = val

            parent_tags.append(tag_name)

            if tag_name in ('activity', 'activity-alias'):
                result['activities'].append({
                    'name': attrs.get('android:name', ''),
                    'enabled': attrs.get('android:enabled', 'true'),
                    'exported': attrs.get('android:exported', ''),
                })
            elif tag_name == 'service':
                result['services'].append({
                    'name': attrs.get('android:name', ''),
                    'enabled': attrs.get('android:enabled', 'true'),
                    'exported': attrs.get('android:exported', ''),
                })
            elif tag_name == 'receiver':
                result['receivers'].append({
                    'name': attrs.get('android:name', ''),
                    'enabled': attrs.get('android:enabled', 'true'),
                    'exported': attrs.get('android:exported', ''),
                })
            elif tag_name == 'provider':
                result['providers'].append({
                    'name': attrs.get('android:name', ''),
                    'authorities': attrs.get('android:authorities', ''),
                })
            elif tag_name == 'uses-permission':
                result['permissions'].append(attrs.get('android:name', ''))
            elif tag_name == 'meta-data':
                result['meta_data'].append({
                    'name': attrs.get('android:name', ''),
                    'value': attrs.get('android:value', attrs.get('android:resource', '')),
                })
            elif tag_name == 'application':
                result['package'] = attrs.get('android:name', '')

            depth += 1

        elif chunk_type == 0x0103:  # END_ELEMENT
            depth -= 1
            if parent_tags:
                parent_tags.pop()

        pos += chunk_size

    return result

# ── DEX string extraction ─────────────────────────────────────────────────
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

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    report = []
    def log(msg=''):
        print(msg, flush=True)
        report.append(msg)

    log("=" * 70)
    log("DEEP STATIC ANALYSIS REPORT")
    log("=" * 70)

    with zipfile.ZipFile(APK_PATH, 'r') as z:
        all_names = z.namelist()

        log(f"\n## APK Info")
        log(f"  File: {os.path.basename(APK_PATH)}")
        log(f"  Size: {os.path.getsize(APK_PATH):,} bytes")
        log(f"  Total files: {len(all_names)}")

        # ── AndroidManifest.xml ──
        log(f"\n## AndroidManifest.xml")
        manifest_data = z.read('AndroidManifest.xml')
        manifest = parse_manifest(manifest_data)
        log(f"  Package/AppClass: {manifest['package']}")

        log(f"\n  ### Activities ({len(manifest['activities'])})")
        for act in manifest['activities']:
            flags = []
            if act['enabled'] == 'false': flags.append('DISABLED')
            if act['exported'] == 'true': flags.append('EXPORTED')
            elif act['exported'] == 'false': flags.append('not-exported')
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            log(f"    - {act['name']}{flag_str}")

        log(f"\n  ### Services ({len(manifest['services'])})")
        for svc in manifest['services']:
            flags = []
            if svc['enabled'] == 'false': flags.append('DISABLED')
            if svc['exported'] == 'true': flags.append('EXPORTED')
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            log(f"    - {svc['name']}{flag_str}")

        log(f"\n  ### Receivers ({len(manifest['receivers'])})")
        for rcv in manifest['receivers']:
            flags = []
            if rcv['enabled'] == 'false': flags.append('DISABLED')
            if rcv['exported'] == 'true': flags.append('EXPORTED')
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            log(f"    - {rcv['name']}{flag_str}")

        log(f"\n  ### Providers ({len(manifest['providers'])})")
        for prv in manifest['providers']:
            log(f"    - {prv['name']} (authority: {prv['authorities']})")

        log(f"\n  ### Permissions ({len(manifest['permissions'])})")
        for perm in manifest['permissions']:
            log(f"    - {perm}")

        log(f"\n  ### Meta-data ({len(manifest['meta_data'])})")
        for md in manifest['meta_data']:
            log(f"    - {md['name']} = {md['value']}")

        # ── All manifest strings ──
        log(f"\n## All Manifest Strings ({len(manifest['all_strings'])})")
        for s in manifest['all_strings']:
            if s and len(s) > 1:
                log(f"    {s}")

        # ── DEX strings ──
        log(f"\n## DEX String Analysis")
        all_strings = []
        for dex_name in ['classes.dex', 'classes2.dex']:
            if dex_name in all_names:
                dex_data = z.read(dex_name)
                dex_strings = extract_dex_strings(dex_data)
                all_strings.extend(dex_strings)
                log(f"  {dex_name}: {len(dex_strings)} strings")

        # ── URLs ──
        log(f"\n## Hardcoded URLs")
        url_set = set()
        for s in all_strings:
            for m in re.findall(r'https?://[a-zA-Z0-9._\-/:~=&?%#+]+', s):
                url_set.add(m)
        for u in sorted(url_set):
            log(f"    {u}")

        # ── Server/Config keywords in strings ──
        log(f"\n## Server / IP / Config Strings")
        target_kws = ['server', 'serverip', 'server_ip', 'api_url', 'base_url',
                       'diy', 'local_mode', 'localserver', 'debug_mode',
                       'admin', 'factory', 'developer', 'hidden', 'secret',
                       'setting_url', 'setting_server', 'change_ip',
                       'ip_address', 'server_address', 'server_port',
                       'custom_server', 'custom_url', 'self_host',
                       'machine_ip', 'cutter_ip', 'host_ip']
        for s in all_strings:
            sl = s.lower().replace('_', '').replace('-', '')
            for kw in target_kws:
                if kw.replace('_', '').replace('-', '') in sl:
                    log(f"    [{kw}] {s[:150]}")
                    break

        # ── SharedPreferences keys ──
        log(f"\n## SharedPreferences Keys")
        pref_set = set()
        for s in all_strings:
            for m in re.finditer(r'"((?:pref|sp|key|setting|config|server|ip|url|api|token|user|pass|machine|device|cutter|cut)[a-zA-Z0-9_]*)"', s):
                pref_set.add(m.group(1))
            # Also catch putXxx("key" patterns
            for m in re.finditer(r'put(?:String|Int|Boolean|Long|Float)\("([^"]+)"', s):
                pref_set.add(m.group(1))
        for k in sorted(pref_set):
            log(f"    {k}")

        # ── Interesting method/class names ──
        log(f"\n## Interesting Class/Method Names")
        interesting_cls = set()
        for s in all_strings:
            # Match Lcom/xxx/yyy/ClassName patterns that contain interesting words
            for m in re.finditer(r'L[a-zA-Z0-9/_$]+/(?:Server|Config|Setting|Debug|Admin|Factory|DIY|Local|Home|Main|Wallet|Recharge|Login|Cut|Print|Model|Phone|Brand|Cutter)[a-zA-Z0-9_$]*;', s):
                interesting_cls.add(m.group(0))
            # Method names
            for m in re.finditer(r'(?:get|set|change|update|modify)(?:Server|IP|Url|Host|Port|Config|Setting|Mode|Debug|Admin|Local|DIY)[a-zA-Z]*\(', s):
                interesting_cls.add(m.group(0))
        for c in sorted(interesting_cls):
            log(f"    {c}")

        # ── String literals containing 'expire'/'count'/'recharge' ──
        log(f"\n## Business Logic Strings")
        biz_kws = ['expire', 'count', 'recharge', 'wallet', 'consume',
                    'activate', 'machine_code', 'device_id', 'cutter',
                    'left_count', 'left_num', 'remain', 'total',
                    'is_expired', 'is_vip', 'status', 'version']
        for s in all_strings:
            sl = s.lower()
            for kw in biz_kws:
                if kw in sl and 3 < len(s) < 200:
                    log(f"    {s[:150]}")
                    break

        # ── pgyer (crash reporting) endpoints ──
        log(f"\n## Third-party Services")
        third_party = set()
        for s in all_strings:
            if 'pgyer' in s.lower():
                third_party.add(s[:100])
            if 'umeng' in s.lower():
                third_party.add(s[:100])
            if 'bugly' in s.lower():
                third_party.add(s[:100])
            if 'sentry' in s.lower():
                third_party.add(s[:100])
            if 'firebase' in s.lower():
                third_party.add(s[:100])
            if 'ip-api' in s.lower() or 'ipapi' in s.lower():
                third_party.add(s[:100])
        for tp in sorted(third_party):
            log(f"    {tp}")

        # ── All strings with 'ip' that look like IP:PORT ──
        log(f"\n## IP:PORT Patterns")
        for s in all_strings:
            if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', s) and len(s) < 100:
                log(f"    {s}")
            if 'ip:' in s.lower() or 'port:' in s.lower() or 'addr:' in s.lower():
                if len(s) < 200:
                    log(f"    {s[:150]}")

    # Write report
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print(f"\nReport saved to: {REPORT_PATH}")

if __name__ == '__main__':
    main()
