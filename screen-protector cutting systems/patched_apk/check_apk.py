"""Check patched APK for install issues."""
import zipfile, os, hashlib

apk = r"D:\workspase\screen-protector cutting systems\patched_apk\patched.apk"
orig = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"

def check_apk(path, label):
    print(f"\n{'='*60}")
    print(f"  {label}: {os.path.basename(path)}")
    print(f"{'='*60}")
    print(f"  Size: {os.path.getsize(path):,} bytes")
    
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        print(f"  Total files: {len(names)}")
        
        # Check signing
        meta = [n for n in names if 'META-INF' in n]
        print(f"  META-INF files: {len(meta)}")
        for m in meta:
            print(f"    {m} ({z.getinfo(m).file_size:,})")
        
        # Check DEX
        for n in sorted(names):
            if n.endswith('.dex'):
                print(f"  {n}: {z.getinfo(n).file_size:,} bytes")
        
        # Check manifest
        manifest = z.read('AndroidManifest.xml')
        print(f"  AndroidManifest.xml: {len(manifest)} bytes")
        # Binary XML header check
        chunk_type = manifest[0] | (manifest[1] << 8)
        print(f"  Manifest chunk type: 0x{chunk_type:04x} (should be 0x0003)")
        
        # Check if resources.arsc exists
        if 'resources.arsc' in names:
            res = z.read('resources.arsc')
            print(f"  resources.arsc: {len(res):,} bytes")
        
        # Check for certificate files
        rsa = [n for n in names if n.endswith('.RSA') or n.endswith('.DSA') or n.endswith('.EC')]
        print(f"  Signing certs: {rsa}")
        
        # Check Android version requirements
        # Look for minSdkVersion in DEX (rough check)
        for n in names:
            if n.endswith('.dex'):
                data = z.read(n)
                # Search for version strings
                if b'android.permission.INSTALL_PACKAGES' in data:
                    print(f"  WARNING: {n} has INSTALL_PACKAGES permission")
                if b'android.permission.DELETE_PACKAGES' in data:
                    print(f"  WARNING: {n} has DELETE_PACKAGES permission")

check_apk(orig, "ORIGINAL")
check_apk(apk, "PATCHED")

# Check if sizes are dramatically different
orig_size = os.path.getsize(orig)
patch_size = os.path.getsize(apk)
diff = abs(orig_size - patch_size)
print(f"\n{'='*60}")
print(f"  SIZE COMPARISON")
print(f"{'='*60}")
print(f"  Original: {orig_size:,} bytes")
print(f"  Patched:  {patch_size:,} bytes")
print(f"  Diff:     {diff:,} bytes ({diff/orig_size*100:.1f}%)")
if diff > orig_size * 0.3:
    print(f"  WARNING: Size difference > 30% - possible repack issue!")
