import os, json, datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder="../static", static_url_path="")

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
    {"id":1,"seriesId":1,"modelName":"iPhone 15 Pro Max","pltFile":"iphone15promax.plt","pltUrl":"/model/iphone15promax.plt"},
    {"id":2,"seriesId":1,"modelName":"iPhone 15 Pro","pltFile":"iphone15pro.plt","pltUrl":"/model/iphone15pro.plt"},
    {"id":3,"seriesId":1,"modelName":"iPhone 15 Plus","pltFile":"iphone15plus.plt","pltUrl":"/model/iphone15plus.plt"},
    {"id":4,"seriesId":1,"modelName":"iPhone 15","pltFile":"iphone15.plt","pltUrl":"/model/iphone15.plt"},
    {"id":5,"seriesId":2,"modelName":"iPhone 14 Pro Max","pltFile":"iphone14promax.plt","pltUrl":"/model/iphone14promax.plt"},
    {"id":6,"seriesId":2,"modelName":"iPhone 14 Pro","pltFile":"iphone14pro.plt","pltUrl":"/model/iphone14pro.plt"},
    {"id":7,"seriesId":2,"modelName":"iPhone 14 Plus","pltFile":"iphone14plus.plt","pltUrl":"/model/iphone14plus.plt"},
    {"id":8,"seriesId":2,"modelName":"iPhone 14","pltFile":"iphone14.plt","pltUrl":"/model/iphone14.plt"},
    {"id":9,"seriesId":3,"modelName":"iPhone 13 Pro Max","pltFile":"iphone13promax.plt","pltUrl":"/model/iphone13promax.plt"},
    {"id":10,"seriesId":3,"modelName":"iPhone 13 Pro","pltFile":"iphone13pro.plt","pltUrl":"/model/iphone13pro.plt"},
    {"id":11,"seriesId":3,"modelName":"iPhone 13","pltFile":"iphone13.plt","pltUrl":"/model/iphone13.plt"},
    {"id":12,"seriesId":4,"modelName":"Galaxy S24 Ultra","pltFile":"s24ultra.plt","pltUrl":"/model/s24ultra.plt"},
    {"id":13,"seriesId":4,"modelName":"Galaxy S24 Plus","pltFile":"s24plus.plt","pltUrl":"/model/s24plus.plt"},
    {"id":14,"seriesId":4,"modelName":"Galaxy S24","pltFile":"s24.plt","pltUrl":"/model/s24.plt"},
    {"id":15,"seriesId":5,"modelName":"Galaxy S23 Ultra","pltFile":"s23ultra.plt","pltUrl":"/model/s23ultra.plt"},
    {"id":16,"seriesId":5,"modelName":"Galaxy S23 Plus","pltFile":"s23plus.plt","pltUrl":"/model/s23plus.plt"},
    {"id":17,"seriesId":5,"modelName":"Galaxy S23","pltFile":"s23.plt","pltUrl":"/model/s23.plt"},
]

@app.route("/api/datalist/user", methods=["GET", "POST"])
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
def get_categories():
    return jsonify(SEED_CATEGORIES)

@app.route("/api/datalist/brand", methods=["POST"])
def get_brands():
    return jsonify(SEED_BRANDS)

@app.route("/api/datalist/series", methods=["POST"])
def get_series():
    data = request.get_json(silent=True) or {}
    brand_id = data.get("brandId", 0)
    filtered = [s for s in SEED_SERIES if s["brandId"] == brand_id] if brand_id else SEED_SERIES
    return jsonify(filtered)

@app.route("/api/datalist/model", methods=["POST"])
def get_models():
    data = request.get_json(silent=True) or {}
    series_id = data.get("seriesId", 0)
    filtered = [m for m in SEED_MODELS if m["seriesId"] == series_id] if series_id else SEED_MODELS
    return jsonify(filtered)

@app.route("/api/phone/pltfile", methods=["POST"])
def get_plt():
    return jsonify({"code": 0, "msg": "ok", "data": {"pltUrl": "/model/generic.plt"}})

@app.route("/api/cutterMacTest", methods=["GET", "POST"])
def cutter_mac_test():
    return jsonify({"code": 0, "msg": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.datetime.now().isoformat()})

@app.route("/")
def index():
    return send_from_directory("../static", "index.html")

@app.route("/<path:path>")
def serve_files(path):
    if "." in path:
        return send_from_directory("../static", path)
    return jsonify({"code": 0, "msg": "ok"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
