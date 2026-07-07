"""
Deep static analysis of the original APK.
Extracts: manifest components, hardcoded URLs, server config keys,
SharedPreferences keys, and hidden/debug/DIY mode indicators.
"""
import zipfile, struct, os, re, sys

APK_PATH = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"
REPORT_PATH = r"D:\workspase\screen-protector cutting systems\patched_apk\analysis_report.txt"

# ── Binary XML decoder (AndroidManifest.xml) ──────────────────────────────
CHUNK_TYPE_STRING = 0x0001
CHUNK_TYPE_RES_TABLE = 0x0200
CHUNK_TYPE_XML = 0x0003
START_NAMESPACE = 0x0100
END_NAMESPACE = 0x0101
START_ELEMENT = 0x0102
END_ELEMENT = 0x0103

def decode_utf16le(data):
    """Decode UTF-16LE with null terminator stripped."""
    try:
        s = data.decode('utf-16-le')
        return s.rstrip('\x00')
    except:
        return ''

def parse_string_pool(data, offset):
    """Parse an Android string pool chunk. Returns list of strings."""
    strings = []
    chunk_size = struct.unpack_from('<I', data, offset)[0]
    # string_pool header: chunk_size(4) + chunk_type(4) + header_size(4) + string_count(4) + ...
    str_count = struct.unpack_from('<I', data, offset + 12)[0]
    flags = struct.unpack_from('<I', data, offset + 16)[0]
    strings_start = struct.unpack_from('<I', data, offset + 20)[0]
    styles_start = struct.unpack_from('<I', data, offset + 24)[0]
    
    is_utf8 = (flags & (1 << 8)) != 0
    
    # String offsets start at offset + 28
    for i in range(str_count):
        str_off = struct.unpack_from('<I', data, offset + 28 + i * 4)[0]
        abs_off = offset + strings_start + str_off
        if is_utf8:
            # UTF-8: skip two length bytes, then read string
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
            # UTF-16
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
    return strings

def parse_manifest(data):
    """Parse AndroidManifest.xml binary format to extract components."""
    result = {
        'package': '',
        'activities': [],
        'services': [],
        'receivers': [],
        'providers': [],
        'permissions': [],
        'meta_data': [],
        'intent_filters': [],
        'all_strings': [],
    }
    
    # Find string pool
    pos = 0
    strings = []
    while pos < len(data) - 8:
        chunk_type = struct.unpack_from('<H', data, pos + 2)[0]
        if chunk_type == CHUNK_TYPE_STRING:
            strings = parse_string_pool(data, pos)
            result['all_strings'] = strings
            break
        chunk_size = struct.unpack_from('<I', data, pos)[0]
        if chunk_size == 0:
            break
        pos += chunk_size
    
    if not strings:
        return result
    
    # Now parse XML elements
    pos = 0
    namespace_stack = []
    current_tag = None
    current_attrs = {}
    depth = 0
    
    while pos < len(data) - 8:
        chunk_type = struct.unpack_from('<H', data, pos + 2)[0]
        chunk_size = struct.unpack_from('<I', data, pos)[0]
        if chunk_size == 0:
            break
        
        if chunk_type == START_ELEMENT:
            # Start element: size(2) + type(2) + header_size(2) + line(4) + comment(4) + ns_idx(4) + name_idx(4) + attr_start(2) + attr_size(2) + attr_count(2) + id_idx(2) + class_idx(2) + style_idx(2)
            ns_idx = struct.unpack_from('<i', data, pos + 16)[0]
            name_idx = struct.unpack_from('<i', data, pos + 20)[0]
            attr_count = struct.unpack_from('<H', data, pos + 28)[0]
            
            tag_name = strings[name_idx] if 0 <= name_idx < len(strings) else '?'
            
            attrs = {}
            for a in range(attr_count):
                attr_pos = pos + 36 + a * 20
                if attr_pos + 20 > len(data):
                    break
                a_ns_idx = struct.unpack_from('<i', data, attr_pos)[0]
                a_name_idx = struct.unpack_from('<i', data, attr_pos + 4)[0]
                a_value_idx = struct.unpack_from('<i', data, attr_pos + 8)[0]
                a_type = struct.unpack_from('<H', data, attr_pos + 14)[0]
                a_data = struct.unpack_from('<I', data, attr_pos + 16)[0]
                
                a_name = strings[a_name_idx] if 0 <= a_name_idx < len(strings) else '?'
                
                if a_value_idx >= 0:
                    val = strings[a_value_idx] if 0 <= a_value_idx < len(strings) else str(a_data)
                elif a_type == 0x03:  # string
                    val = strings[a_data] if 0 <= a_data < len(strings) else ''
                elif a_type in (0x10, 0x11):  # int
                    val = str(a_data)
                elif a_type == 0x12:  # bool
                    val = 'true' if a_data else 'false'
                else:
                    val = str(a_data)
                attrs[a_name] = val
            
            current_tag = tag_name
            current_attrs = attrs
            depth += 1
            
            if tag_name == 'activity' or tag_name == 'activity-alias':
                name = attrs.get('android:name', '')
                enabled = attrs.get('android:enabled', 'true')
                exported = attrs.get('android:exported', '')
                result['activities'].append({
                    'name': name,
                    'enabled': enabled,
                    'exported': exported,
                    'meta_data': [],
                    'intent_filters': [],
                })
            elif tag_name == 'service':
                name = attrs.get('android:name', '')
                enabled = attrs.get('android:enabled', 'true')
                exported = attrs.get('android:exported', '')
                result['services'].append({
                    'name': name,
                    'enabled': enabled,
                    'exported': exported,
                })
            elif tag_name == 'receiver':
                name = attrs.get('android:name', '')
                enabled = attrs.get('android:enabled', 'true')
                exported = attrs.get('android:exported', '')
                result['receivers'].append({
                    'name': name,
                    'enabled': enabled,
                    'exported': exported,
                })
            elif tag_name == 'provider':
                name = attrs.get('android:name', '')
                authorities = attrs.get('android:authorities', '')
                result['providers'].append({
                    'name': name,
                    'authorities': authorities,
                })
            elif tag_name == 'uses-permission':
                name = attrs.get('android:name', '')
                result['permissions'].append(name)
            elif tag_name == 'meta-data':
                name = attrs.get('android:name', '')
                value = attrs.get('android:value', '')
                result['meta_data'].append({
                    'name': name,
                    'value': value,
                    'parent': current_tag,
                })
        
        elif chunk_type == END_ELEMENT:
            depth -= 1
            if depth <= 0:
                current_tag = None
                current_attrs = {}
        
        elif chunk_type == START_NAMESPACE:
            pass
        elif chunk_type == END_NAMESPACE:
            pass
        
        pos += chunk_size
    
    return result

# ── DEX string search ─────────────────────────────────────────────────────
def read_uleb128(data, pos):
    result = 0; shift = 0
    while True:
        b = data[pos]; result |= (b & 0x7F) << shift; pos += 1
        if not (b & 0x80): break
        shift += 7
    return result, pos

def extract_dex_strings(dex_data):
    """Extract all strings from a DEX file."""
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
            strings.append(s.decode('latin-1'))
    return strings

# ── Main analysis ─────────────────────────────────────────────────────────
def main():
    report = []
    def log(msg=''):
        print(msg)
        report.append(msg)
    
    log("=" * 70)
    log("DEEP STATIC ANALYSIS REPORT")
    log("=" * 70)
    
    with zipfile.ZipFile(APK_PATH, 'r') as z:
        all_names = z.namelist()
        
        # ── 1. Basic APK info ──
        log("\n## APK Info")
        log(f"  File: {os.path.basename(APK_PATH)}")
        log(f"  Size: {os.path.getsize(APK_PATH):,} bytes")
        log(f"  Total files: {len(all_names)}")
        
        # ── 2. AndroidManifest.xml ──
        log("\n## AndroidManifest.xml (decoded)")
        manifest_data = z.read('AndroidManifest.xml')
        manifest = parse_manifest(manifest_data)
        
        log(f"  Package: {manifest['package']}")
        
        log(f"\n  ### Activities ({len(manifest['activities'])})")
        for act in manifest['activities']:
            flags = []
            if act['enabled'] == 'false': flags.append('DISABLED')
            if act['exported'] == 'true': flags.append('EXPORTED')
            if act['exported'] == 'false': flags.append('not-exported')
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
            log(f"    - {md['name']} = {md['value']} (parent: {md['parent']})")
        
        # ── 3. DEX string analysis ──
        log("\n## DEX String Analysis")
        
        all_strings = []
        for dex_name in ['classes.dex', 'classes2.dex']:
            if dex_name in all_names:
                dex_data = z.read(dex_name)
                dex_strings = extract_dex_strings(dex_data)
                all_strings.extend(dex_strings)
                log(f"  {dex_name}: {len(dex_strings)} strings")
        
        log(f"  Total strings: {len(all_strings)}")
        
        # ── 4. URL / endpoint search ──
        log("\n## Hardcoded URLs & Endpoints")
        url_pattern = re.compile(r'https?://[a-zA-Z0-9._\-/]+')
        found_urls = set()
        for s in all_strings:
            for match in url_pattern.findall(s):
                found_urls.add(match)
        for url in sorted(found_urls):
            log(f"    {url}")
        
        # ── 5. Server / IP / config keywords ──
        log("\n## Server / IP / Config Keywords")
        keywords = [
            'server', 'server_ip', 'serverip', 'server_ip_address',
            'api_url', 'apiurl', 'base_url', 'baseurl', 'host',
            'diy', 'DIY', 'local', 'LOCAL', 'debug', 'DEBUG',
            'admin', 'ADMIN', 'factory', 'FACTORY', 'test', 'TEST',
            'developer', 'DEVELOPER', 'hidden', 'secret',
            'config', 'CONFIG', 'setting', 'SETTING',
            'ip_address', 'ipaddress', 'port', 'PORT',
            'address', 'endpoint', 'url',
            'preference', 'shared', 'prefs',
        ]
        keyword_hits = {}
        for s in all_strings:
            sl = s.lower()
            for kw in keywords:
                if kw.lower() in sl:
                    if kw not in keyword_hits:
                        keyword_hits[kw] = set()
                    keyword_hits[kw].add(s[:120])
        
        for kw in sorted(keyword_hits.keys()):
            hits = keyword_hits[kw]
            log(f"\n  '{kw}' ({len(hits)} hits):")
            for h in sorted(hits)[:20]:
                log(f"    {h}")
        
        # ── 6. SharedPreferences keys ──
        log("\n## SharedPreferences / Preference Keys")
        pref_patterns = [
            r'put(String|Int|Boolean|Long|Float)\([^,]+,\s*"([^"]+)"',
            r'getString\("([^"]+)"',
            r'getInt\("([^"]+)"',
            r'getBoolean\("([^"]+)"',
            r'putString\("([^"]+)"',
            r'putInt\("([^"]+)"',
            r'putBoolean\("([^"]+)"',
            r'"(pref_[a-zA-Z_]+)"',
            r'"(sp_[a-zA-Z_]+)"',
            r'"(key_[a-zA-Z_]+)"',
            r'"(setting_[a-zA-Z_]+)"',
        ]
        pref_keys = set()
        for s in all_strings:
            for pat in pref_patterns:
                for match in re.finditer(pat, s):
                    pref_keys.add(match.group(0)[:100])
        
        for pk in sorted(pref_keys):
            log(f"    {pk}")
        
        # ── 7. Activity names (full list for hidden modes) ──
        log("\n## All Activity Names (looking for hidden/debug/DIY)")
        activity_keywords = ['setting', 'config', 'debug', 'admin', 'diy', 
                           'local', 'server', 'factory', 'test', 'hidden',
                           'developer', 'tool', 'about', 'wallet', 'recharge',
                           'login', 'register', 'main', 'home', 'splash',
                           'photo', 'print', 'cut', 'model', 'brand', 'phone']
        for act in manifest['activities']:
            name = act['name'].lower()
            matched = [kw for kw in activity_keywords if kw in name]
            if matched:
                log(f"    ** {act['name']}  (matches: {matched})")
            else:
                log(f"    {act['name']}")
        
        # ── 8. Interesting strings ──
        log("\n## Interesting Strings (manual review)")
        interesting_kw = [
            'expire', 'count', 'recharge', 'wallet', 'consume',
            'activate', 'machine_code', 'device_id', 'cutter',
            'plt', 'model_name', 'brand', 'series', 'classify',
            'upload', 'download', 'file_path', 'cut', 'print',
        ]
        for s in all_strings:
            sl = s.lower()
            for kw in interesting_kw:
                if kw in sl and len(s) > 3 and len(s) < 200:
                    log(f"    {s[:150]}")
                    break
        
        # ── 9. All strings containing 'server' or 'ip' ──
        log("\n## All Strings Containing 'server' or '_ip' or 'Server'")
        for s in all_strings:
            if ('server' in s.lower() or '_ip' in s.lower() or 'Server' in s) and len(s) < 200:
                log(f"    {s[:150]}")
        
        # ── 10. All strings containing 'url' or 'host' ──
        log("\n## All Strings Containing 'url' or 'host'")
        for s in all_strings:
            if ('url' in s.lower() or 'host' in s.lower() or 'Url' in s or 'Host' in s) and len(s) < 200:
                log(f"    {s[:150]}")
        
        # ── 11. Manifest strings that look like config ──
        log("\n## Manifest Strings (all unique)")
        for s in sorted(set(manifest['all_strings'])):
            if s and len(s) > 1 and len(s) < 200:
                log(f"    {s}")
    
    # Write report
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    print(f"\nReport saved to: {REPORT_PATH}")

if __name__ == '__main__':
    main()
