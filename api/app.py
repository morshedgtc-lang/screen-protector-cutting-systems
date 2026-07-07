import os, json, datetime
from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

app = Flask(__name__, static_folder="../static", static_url_path="")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///cutter.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL) if DATABASE_URL else None

def db():
    return engine.connect()

def init_db():
    if not engine: return
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path) as f:
            schema = f.read()
        with engine.begin() as conn:
            for stmt in schema.split(";"):
                if stmt.strip():
                    conn.execute(text(stmt))

@app.route("/")
def index():
    return send_from_directory("../static", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("../static", path)

@app.route("/api/datalist/user", methods=["GET", "POST"])
def user_info():
    if not engine: return jsonify({"code": 0, "msg": "ok", "data": {"registered": 1, "is_expired": 0, "is_vip": 1, "left_count": 999999, "server_ip": os.environ.get("HOST", "0.0.0.0")}})
    data = request.get_json(silent=True) or {}
    device_id = data.get("deviceId", "UNKNOWN")
    with db() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE device_id = :did"), {"did": device_id}).fetchone()
    if not result:
        return jsonify({"code": 0, "msg": "ok", "data": {"registered": 1, "is_expired": 0, "is_vip": 1, "left_count": 999999, "device_id": device_id}})
    return jsonify({"code": 0, "msg": "ok", "data": {
        "device_id": device_id, "machine_code": result[2], "expired_at": str(result[6]),
        "expire": str(result[6]), "is_expired": 0, "is_vip": 1 if result[5] else 0,
        "left_count": result[7], "registered": 1 if result[8] else 0, "status": 1
    }})

@app.route("/api/datalist/category", methods=["GET", "POST"])
def get_categories():
    if not engine: return jsonify([])
    with db() as conn:
        rows = conn.execute(text("SELECT id, name, chn_name, icon, sort_order, status FROM categories ORDER BY sort_order")).fetchall()
    return jsonify([{"id": r[0], "name": r[1], "chn": r[2], "icon": r[3], "sort": r[4], "status": r[5]} for r in rows])

@app.route("/api/datalist/brand", methods=["POST"])
def get_brands():
    if not engine: return jsonify([])
    data = request.get_json(silent=True) or {}
    cat_id = data.get("categoryId", 0)
    with db() as conn:
        if cat_id:
            rows = conn.execute(text("SELECT id, category_id, name, icon FROM brands WHERE category_id=:cid ORDER BY sort_order"), {"cid": cat_id}).fetchall()
        else:
            rows = conn.execute(text("SELECT id, category_id, name, icon FROM brands ORDER BY sort_order")).fetchall()
    return jsonify([{"id": r[0], "categoryId": r[1], "name": r[2], "icon": r[3]} for r in rows])

@app.route("/api/datalist/series", methods=["POST"])
def get_series():
    if not engine: return jsonify([])
    data = request.get_json(silent=True) or {}
    brand_id = data.get("brandId", 0)
    with db() as conn:
        rows = conn.execute(text("SELECT id, brand_id, name FROM series WHERE brand_id=:bid ORDER BY sort_order"), {"bid": brand_id}).fetchall()
    return jsonify([{"id": r[0], "brandId": r[1], "name": r[2]} for r in rows])

@app.route("/api/datalist/model", methods=["POST"])
def get_models():
    if not engine: return jsonify([])
    data = request.get_json(silent=True) or {}
    series_id = data.get("seriesId", 0)
    with db() as conn:
        rows = conn.execute(text("SELECT id, series_id, model_name, plt_file, plt_url FROM phone_models WHERE series_id=:sid ORDER BY sort_order"), {"sid": series_id}).fetchall()
    return jsonify([{"id": r[0], "seriesId": r[1], "modelName": r[2], "pltFile": r[3], "pltUrl": r[4]} for r in rows])

@app.route("/health")
def health():
    return jsonify({"status": "ok", "time": datetime.datetime.now().isoformat()})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
