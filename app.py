import os, json, datetime, hashlib, secrets
from flask import Flask, request, jsonify, send_from_directory

# ---------- CutOS v1 API mock (admin only) ----------
ADMIN_EMAIL = "admin@satelecom.com"
ADMIN_PASS = "admin"
ADMIN_NAME = "Admin"
ADMIN_USER = {"id": 1, "email": ADMIN_EMAIL, "name": ADMIN_NAME, "role": "admin"}
_tokens = {}  # token -> user

def _get_user_from_token():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else None
    return _tokens.get(token) if token else None

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if not os.path.isdir(STATIC_DIR):
    STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")

# ---------- CutOS v1 API endpoints (mock) ----------
@app.route("/api/v1/auth/register", methods=["POST"])
def api_register():
    return jsonify({"access_token": secrets.token_hex(32), "refresh_token": secrets.token_hex(32), "user": ADMIN_USER})

@app.route("/api/v1/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    if data.get("email") == ADMIN_EMAIL and data.get("password") == ADMIN_PASS:
        token = secrets.token_hex(32)
        _tokens[token] = ADMIN_USER
        return jsonify({"access_token": token, "refresh_token": secrets.token_hex(32), "user": ADMIN_USER})
    return jsonify({"detail": "Invalid email or password"}), 401

@app.route("/api/v1/auth/refresh", methods=["POST"])
def api_refresh():
    token = secrets.token_hex(32)
    _tokens[token] = ADMIN_USER
    return jsonify({"access_token": token, "refresh_token": secrets.token_hex(32)})

@app.route("/api/v1/auth/me", methods=["GET"])
def api_me():
    user = _get_user_from_token()
    if user:
        return jsonify(user)
    return jsonify({"detail": "Not authenticated"}), 401

@app.route("/api/v1/users", methods=["GET"])
def api_users():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([ADMIN_USER])

@app.route("/api/v1/users/<int:uid>", methods=["GET"])
def api_user(uid):
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify(ADMIN_USER)

@app.route("/api/v1/machines", methods=["GET"])
def api_machines():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/jobs", methods=["GET"])
def api_jobs():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/templates", methods=["GET"])
def api_templates():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/subscriptions", methods=["GET"])
def api_subscriptions():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/machine-types", methods=["GET"])
def api_machine_types():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/logs", methods=["GET"])
def api_logs():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/updates", methods=["GET"])
def api_updates():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([])

@app.route("/api/v1/downloads", methods=["GET"])
def api_downloads():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify([
        {"id": 1, "name": "CutOS Terminal (Cloud)", "url": "/CutOS-Terminal-Cloud.apk", "version": "1.0", "size": 8038187},
        {"id": 2, "name": "CutOS Terminal (Local)", "url": "/CutOS-Terminal-Local.apk", "version": "1.0", "size": 8038225},
        {"id": 3, "name": "Launcher", "url": "/launcher.apk", "version": "1.0", "size": 1024000},
        {"id": 4, "name": "File Manager", "url": "/filemanager.apk", "version": "1.0", "size": 2048000},
    ])

@app.route("/api/v1/analytics/dashboard", methods=["GET"])
def api_dashboard():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify({
        "total_machines": 1, "active_machines": 0, "total_jobs": 0,
        "today_jobs": 0, "total_templates": 0, "active_subscriptions": 0,
        "machines": [], "recent_jobs": [],
    })

@app.route("/api/v1/brands", methods=["GET"])
def api_brands():
    if not _get_user_from_token():
        return jsonify({"detail": "Not authenticated"}), 401
    return jsonify(SEED_BRANDS)

# ---------- Cloud API emulator (cutting machine) ----------
SEED_CATEGORIES = [
    {"id":1,"name":"Phone","chn":"手机","icon":"","sort":1,"status":"A"},
    {"id":2,"name":"Watch","chn":"手表","icon":"","sort":2,"status":"A"},
    {"id":3,"name":"Tablet","chn":"平板","icon":"","sort":3,"status":"A"},
]
SEED_BRANDS = [
    {"id":1,"categoryId":1,"name":"Apple","icon":""},
    {"id":2,"categoryId":1,"name":"Samsung","icon":""},
    {"id":3,"categoryId":1,"name":"Huawei","icon":""},
    {"id":4,"categoryId":1,"name":"Xiaomi","icon":""},
    {"id":5,"categoryId":1,"name":"OnePlus","icon":""},
    {"id":6,"categoryId":1,"name":"Google","icon":""},
]
SEED_SERIES = [
    {"id":1,"brandId":1,"name":"iPhone 15"},
    {"id":2,"brandId":1,"name":"iPhone 14"},
    {"id":3,"brandId":1,"name":"iPhone 13"},
    {"id":4,"brandId":2,"name":"Galaxy S24"},
    {"id":5,"brandId":2,"name":"Galaxy S23"},
    {"id":6,"brandId":3,"name":"P60"},
    {"id":7,"brandId":4,"name":"14"},
]
SEED_MODELS = [
    {"id":1,"seriesId":1,"modelName":"iPhone 15 Pro Max","pltFile":"iphone15promax.plt","pltUrl":"/oss/model/iphone15promax.plt"},
    {"id":2,"seriesId":1,"modelName":"iPhone 15 Pro","pltFile":"iphone15pro.plt","pltUrl":"/oss/model/iphone15pro.plt"},
    {"id":3,"seriesId":1,"modelName":"iPhone 15 Plus","pltFile":"iphone15plus.plt","pltUrl":"/oss/model/iphone15plus.plt"},
    {"id":4,"seriesId":1,"modelName":"iPhone 15","pltFile":"iphone15.plt","pltUrl":"/oss/model/iphone15.plt"},
    {"id":5,"seriesId":2,"modelName":"iPhone 14 Pro Max","pltFile":"iphone14promax.plt","pltUrl":"/oss/model/iphone14promax.plt"},
    {"id":6,"seriesId":2,"modelName":"iPhone 14 Pro","pltFile":"iphone14pro.plt","pltUrl":"/oss/model/iphone14pro.plt"},
    {"id":7,"seriesId":2,"modelName":"iPhone 14 Plus","pltFile":"iphone14plus.plt","pltUrl":"/oss/model/iphone14plus.plt"},
    {"id":8,"seriesId":2,"modelName":"iPhone 14","pltFile":"iphone14.plt","pltUrl":"/oss/model/iphone14.plt"},
    {"id":9,"seriesId":3,"modelName":"iPhone 13 Pro Max","pltFile":"iphone13promax.plt","pltUrl":"/oss/model/iphone13promax.plt"},
    {"id":10,"seriesId":3,"modelName":"iPhone 13 Pro","pltFile":"iphone13pro.plt","pltUrl":"/oss/model/iphone13pro.plt"},
    {"id":11,"seriesId":3,"modelName":"iPhone 13","pltFile":"iphone13.plt","pltUrl":"/oss/model/iphone13.plt"},
    {"id":12,"seriesId":4,"modelName":"Galaxy S24 Ultra","pltFile":"s24ultra.plt","pltUrl":"/oss/model/s24ultra.plt"},
    {"id":13,"seriesId":4,"modelName":"Galaxy S24 Plus","pltFile":"s24plus.plt","pltUrl":"/oss/model/s24plus.plt"},
    {"id":14,"seriesId":4,"modelName":"Galaxy S24","pltFile":"s24.plt","pltUrl":"/oss/model/s24.plt"},
    {"id":15,"seriesId":5,"modelName":"Galaxy S23 Ultra","pltFile":"s23ultra.plt","pltUrl":"/oss/model/s23ultra.plt"},
    {"id":16,"seriesId":5,"modelName":"Galaxy S23 Plus","pltFile":"s23plus.plt","pltUrl":"/oss/model/s23plus.plt"},
    {"id":17,"seriesId":5,"modelName":"Galaxy S23","pltFile":"s23.plt","pltUrl":"/oss/model/s23.plt"},
]

@app.route("/api/datalist/user", methods=["GET", "POST"])
@app.route("/datalist/user", methods=["GET", "POST"])
def user_info():
    return jsonify({
        "code": 0, "msg": "ok",
        "data": {
            "device_id": "SELFHOSTED",
            "machine_code": "LOCAL",
            "expired_at": "2099-12-31 23:59:59",
            "expire": "2099-12-31 23:59:59",
            "expiration": "2099-12-31 23:59:59",
            "status": 1,
            "left_count": 999999,
            "left_num": 999999,
            "remain": 999999,
            "total": 999999,
            "registered": 1,
            "is_expired": 0,
            "is_vip": 1,
            "version": "1.0.0",
            "server_ip": request.host.split(":")[0] if request.host else "0.0.0.0",
            "message": "",
            "activate_time": "2025-01-01 00:00:00",
            "now": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    })

@app.route("/api/datalist/category", methods=["GET", "POST"])
@app.route("/datalist/category", methods=["GET", "POST"])
def get_categories():
    return jsonify(SEED_CATEGORIES)

@app.route("/api/datalist/brand", methods=["POST"])
@app.route("/datalist/brand", methods=["POST"])
def get_brands():
    return jsonify(SEED_BRANDS)

@app.route("/api/datalist/series", methods=["POST"])
@app.route("/datalist/series", methods=["POST"])
def get_series():
    data = request.get_json(silent=True) or {}
    brand_id = data.get("brandId", 0)
    filtered = [s for s in SEED_SERIES if s["brandId"] == brand_id] if brand_id else SEED_SERIES
    return jsonify(filtered)

@app.route("/api/datalist/model", methods=["POST"])
@app.route("/datalist/model", methods=["POST"])
def get_models():
    data = request.get_json(silent=True) or {}
    series_id = data.get("seriesId", 0)
    filtered = [m for m in SEED_MODELS if m["seriesId"] == series_id] if series_id else SEED_MODELS
    return jsonify(filtered)

@app.route("/api/phone/pltfile", methods=["POST"])
@app.route("/phone/pltfile", methods=["POST"])
def get_plt():
    return jsonify({"code": 0, "msg": "ok", "data": {"pltUrl": "/oss/model/generic.plt"}})

@app.route("/api/cutterMacTest", methods=["GET", "POST"])
@app.route("/cutterMacTest", methods=["GET", "POST"])
def cutter_mac_test():
    return jsonify({"code": 0, "msg": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.datetime.now().isoformat()})

@app.route("/")
def index():
    if os.path.isfile(os.path.join(STATIC_DIR, "index.html")):
        return send_from_directory(STATIC_DIR, "index.html")
    return ''

# Serve PLT cutting files (mirrors aliyuncs OSS path the app expects)
import os as _os2
OSS_DIR = _os2.path.join(_os2.path.dirname(_os2.path.abspath(__file__)), "oss")
@app.route("/oss/model/<path:filename>")
def serve_plt(filename):
    # try exact, then case-insensitive match (Android filenames vary)
    base = _os2.path.join(OSS_DIR, "model")
    target = _os2.path.join(base, filename)
    if _os2.path.isfile(target):
        return send_from_directory(_os2.path.join(OSS_DIR, "model"), filename, as_attachment=False)
    # case-insensitive fallback
    lname = filename.lower()
    if _os2.path.isdir(base):
        for fn in _os2.listdir(base):
            if fn.lower() == lname:
                return send_from_directory(base, fn, as_attachment=False)
    return jsonify({"code": 1, "msg": "plt not found: " + filename}), 404

# Also serve PLT at /model/<file> (matches aliyuncs OSS path the STOCK app expects)
@app.route("/model/<path:filename>")
def serve_plt_model(filename):
    base = _os2.path.join(OSS_DIR, "model")
    target = _os2.path.join(base, filename)
    if _os2.path.isfile(target):
        return send_from_directory(base, filename, as_attachment=False)
    lname = filename.lower()
    if _os2.path.isdir(base):
        for fn in _os2.listdir(base):
            if fn.lower() == lname:
                return send_from_directory(base, fn, as_attachment=False)
    return jsonify({"code": 1, "msg": "plt not found: " + filename}), 404

@app.errorhandler(404)
def spa_fallback(e):
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return send_from_directory(STATIC_DIR, "index.html")
    return jsonify({"code": 0, "msg": "ok"})

# ---------- APK backup / upload (SA Telecom) ----------
import os as _os

APK_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "apks")
_os.makedirs(APK_DIR, exist_ok=True)

@app.route("/apks", methods=["GET"])
def list_apks():
    files = []
    for fn in sorted(_os.listdir(APK_DIR)):
        fp = _os.path.join(APK_DIR, fn)
        if _os.path.isfile(fp):
            files.append({
                "name": fn,
                "size": _os.path.getsize(fp),
                "url": "/apks/" + fn,
                "modified": datetime.datetime.fromtimestamp(_os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M:%S"),
            })
    return jsonify({"code": 0, "msg": "ok", "data": files})

@app.route("/apks/<path:filename>", methods=["GET"])
def download_apk(filename):
    return send_from_directory(APK_DIR, filename, as_attachment=True)

@app.route("/upload", methods=["GET"])
def upload_page():
    return '''<!doctype html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SA Telecom - APK Backup</title>
<style>body{font-family:system-ui,Arial;max-width:600px;margin:40px auto;padding:0 16px;}
h1{color:#0a6;} .box{border:2px dashed #0a6;border-radius:12px;padding:24px;text-align:center;margin:20px 0;}
input[type=file]{margin:12px 0;} button{background:#0a6;color:#fff;border:0;padding:10px 20px;border-radius:8px;cursor:pointer;}
.back{display:inline-block;margin-top:16px;color:#0a6;text-decoration:none;}</style></head>
<body>
<h1>SA Telecom - APK Backup</h1>
<p>Upload APK files to back them up on this server. Files appear in the list below and are downloadable.</p>
<div class="box">
  <form id="f" method="post" action="/upload" enctype="multipart/form-data">
    <input type="file" name="apk" accept=".apk,.xapk"><br>
    <button type="submit">Upload APK</button>
  </form>
</div>
<h3>Saved APKs</h3>
<ul id="list"></ul>
<a class="back" href="/">&#8592; Back to home</a>
<script>
fetch('/apks').then(r=>r.json()).then(j=>{
  const ul=document.getElementById('list');
  (j.data||[]).forEach(a=>{const li=document.createElement('li');
    li.innerHTML='<a href="'+a.url+'">'+a.name+'</a> ('+(a.size/1048576).toFixed(1)+' MB) - '+a.modified;
    ul.appendChild(li);});
});
</script>
</body></html>'''

@app.route("/upload", methods=["POST"])
def upload_apk():
    if "apk" not in request.files:
        return jsonify({"code": 1, "msg": "no file field 'apk'"}), 400
    f = request.files["apk"]
    if not f.filename:
        return jsonify({"code": 1, "msg": "empty filename"}), 400
    # only allow apk/xapk
    if not (f.filename.lower().endswith(".apk") or f.filename.lower().endswith(".xapk")):
        return jsonify({"code": 1, "msg": "only .apk/.xapk allowed"}), 400
    # safe filename
    name = _os.path.basename(f.filename)
    dest = _os.path.join(APK_DIR, name)
    f.save(dest)
    return jsonify({"code": 0, "msg": "ok", "data": {"name": name, "size": _os.path.getsize(dest)}})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

