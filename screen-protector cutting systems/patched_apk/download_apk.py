import urllib.request, os

apk_dir = r"D:\workspase\screen-protector cutting systems\patched_apk"
apk_path = os.path.join(apk_dir, "original.apk")

# Try different APKPure download URLs
urls = [
    "https://d.apkpure.com/b/APK/com.machinery.mietubl?version=latest",
    "https://apkpure.com/intelligent-cloud-cutter/com.machinery.mietubl/download?d=com.machinery.mietubl",
    "https://download.apkpure.com/b/APK/com.machinery.mietubl?version=latest",
]

for url in urls:
    print(f"Downloading: {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if len(data) > 100000:
                with open(apk_path, 'wb') as f:
                    f.write(data)
                print(f"SUCCESS! Downloaded {len(data)} bytes")
                break
            else:
                print(f"Too small ({len(data)} bytes), probably not the APK")
    except Exception as e:
        print(f"Failed: {e}")
else:
    print("All URLs failed")
    # Fallback: just search what we can find online
    print("Will try alternative approaches...")
