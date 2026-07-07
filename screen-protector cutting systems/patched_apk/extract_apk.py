import zipfile, os

apk_path = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"
out_dir = r"D:\workspase\screen-protector cutting systems\patched_apk\extracted"

with zipfile.ZipFile(apk_path, 'r') as z:
    z.extractall(out_dir)
    print("Files in APK:")
    for f in sorted(z.namelist()):
        info = z.getinfo(f)
        print(f"  {f:50s} {info.file_size:>8,} bytes")

# Now search for the cloud domain in all files
print("\n\nSearching for cloud API domains...")
targets = [b"hsyunqiemo", b"api.hsyunqiemo", b"mietubl", b"cloudcutter"]
for root, dirs, files in os.walk(out_dir):
    for fname in files:
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'rb') as f:
                data = f.read()
            for target in targets:
                if target in data:
                    print(f"  FOUND '{target.decode()}' in: {fpath[len(out_dir)+1:]}")
                    # Show context around the match
                    idx = data.index(target)
                    start = max(0, idx - 20)
                    end = min(len(data), idx + len(target) + 60)
                    context = data[start:end]
                    print(f"    Context: {context}")
        except Exception as e:
            pass

# Also search for the server IP
print("\n\nSearching for IP addresses and URLs...")
for root, dirs, files in os.walk(out_dir):
    for fname in files:
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'rb') as f:
                data = f.read()
            # Look for HTTP URLs
            import re
            urls = re.findall(rb'https?://[^\s"\'<>]+', data)
            for url in urls:
                print(f"  URL in {fpath[len(out_dir)+1:]}: {url.decode('utf-8', errors='replace')}")
        except Exception as e:
            pass
