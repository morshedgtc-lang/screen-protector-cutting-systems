import zipfile, os

apk = r"D:\workspase\screen-protector cutting systems\patched_apk\original.apk"
print("File exists:", os.path.exists(apk))
print("Size:", os.path.getsize(apk), "bytes")

with zipfile.ZipFile(apk) as z:
    print("ZIP testzip:", "OK" if z.testzip() is None else "BAD")
    names = z.namelist()
    print("Total entries:", len(names))
    manifest = z.read("AndroidManifest.xml")
    print("Package com.machinery in manifest:", b"com.machinery" in manifest)
    for dex in ["classes.dex", "classes2.dex", "classes3.dex"]:
        if dex in names:
            d = z.read(dex)
            print(dex, "-> app.mietubl.com:", b"app.mietubl.com" in d,
                  "| aliyuncs:", b"aliyuncs" in d,
                  "| satelecom:", b"satelecom" in d)
    # show certificate issuer from META-INF
    for n in names:
        if n.endswith(".RSA") or n.endswith(".DSA"):
            print("Sig file:", n)
