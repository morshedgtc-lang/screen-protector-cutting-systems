import os, sys, shutil

BASE = r"D:\workspase\screen-protector cutting systems\patched_apk"
FRONTEND_PUBLIC = r"D:\workspase\frontend\public"

os.chdir(BASE)

def run(cmd):
    print(f"> {cmd}")
    ret = os.system(cmd)
    if ret != 0:
        raise SystemExit(f"Command failed: {cmd}")

def build_variant(variant, dex_dir, out_apk_name):
    print(f"\n{'='*60}")
    print(f"  Building {variant} APK")
    print(f"{'='*60}")
    # Patch DEXes
    run(f'C:\\Python314\\python.exe patch_dex.py {variant}')
    if variant == "local":
        # also need to patch the cloud patched DEX → local if we're doing a second pass
        pass
    # Sign
    run(f'C:\\Python314\\python.exe sign_apk.py {dex_dir} {out_apk_name}')
    # Copy to frontend
    src = os.path.join(BASE, out_apk_name)
    dst = os.path.join(FRONTEND_PUBLIC, out_apk_name)
    shutil.copy2(src, dst)
    print(f"  Copied to frontend: {dst} ({os.path.getsize(dst)} bytes)")

if __name__ == "__main__":
    # Build cloud variant (already exists, just copy)
    cloud_apk = "CutOS-Terminal-Cloud.apk"
    src_cloud = os.path.join(BASE, "patched.apk")
    if os.path.exists(src_cloud):
        dst_cloud = os.path.join(FRONTEND_PUBLIC, cloud_apk)
        shutil.copy2(src_cloud, dst_cloud)
        print(f"Cloud APK: {dst_cloud} ({os.path.getsize(dst_cloud)} bytes)")
    else:
        print("Cloud APK not found, building from scratch...")
        build_variant("cloud", "patched_dex", cloud_apk)

    # Build local variant
    local_apk = "CutOS-Terminal-Local.apk"
    build_variant("local", "patched_dex_local", local_apk)

    # Also copy launcher and filemanager
    for f in ["launcher.apk", "filemanager.apk"]:
        src = os.path.join(r"D:\workspase\screen-protector cutting systems\plt_cache", f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(FRONTEND_PUBLIC, f))
            print(f"Copied {f} to frontend")

    print(f"\n{'='*60}")
    print("  All APKs ready in frontend/public/")
    print(f"{'='*60}")
