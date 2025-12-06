# app.py
from flask import Flask, render_template, request, jsonify, abort
from models import db, Drink
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, template_folder="templates")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "drinks.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 建表與種子資料
def seed_data():
    sample = [
        {"name":"珍珠奶茶 (中杯)","brand":"某手搖","size":"中杯","calories":450,"sugar_grams":55},
        {"name":"紅茶 (無糖)","brand":"某手搖","size":"中杯","calories":5,"sugar_grams":0},
        {"name":"奶茶 (中糖)","brand":"某手搖","size":"中杯","calories":280,"sugar_grams":30},
        {"name":"水果茶 (少糖)","brand":"某手搖","size":"中杯","calories":120,"sugar_grams":15},
    ]
    for s in sample:
        if not Drink.query.filter_by(name=s["name"]).first():
            d = Drink(name=s["name"], brand=s.get("brand"), size=s.get("size"),
                      calories=s["calories"], sugar_grams=s["sugar_grams"])
            db.session.add(d)
    db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

# ----------------------
# RESTful API for drinks
# ----------------------

@app.route("/api/drinks", methods=["GET"])
def api_get_drinks():
    # optional query ?q=name substring
    q = request.args.get("q", "").strip()
    if q:
        drinks = Drink.query.filter(Drink.name.ilike(f"%{q}%")).order_by(Drink.name).all()
    else:
        drinks = Drink.query.order_by(Drink.name).all()
    return jsonify([d.to_dict() for d in drinks]), 200

@app.route("/api/drinks/<int:drink_id>", methods=["GET"])
def api_get_drink(drink_id):
    d = Drink.query.get(drink_id)
    if not d:
        return jsonify({"error":"Not found"}), 404
    return jsonify(d.to_dict()), 200

@app.route("/api/drinks", methods=["POST"])
def api_create_drink():
    data = request.get_json()
    if not data:
        return jsonify({"error":"Invalid JSON"}), 400
    name = data.get("name","").strip()
    calories = data.get("calories")
    sugar_grams = data.get("sugar_grams")
    if not name or calories is None or sugar_grams is None:
        return jsonify({"error":"name, calories and sugar_grams required"}), 400

    if Drink.query.filter_by(name=name).first():
        return jsonify({"error":"Drink already exists"}), 400

    d = Drink(name=name, brand=data.get("brand"), size=data.get("size"),
              calories=float(calories), sugar_grams=float(sugar_grams))
    db.session.add(d)
    db.session.commit()
    return jsonify(d.to_dict()), 201

@app.route("/api/drinks/<int:drink_id>", methods=["PUT"])
def api_update_drink(drink_id):
    d = Drink.query.get(drink_id)
    if not d:
        return jsonify({"error":"Not found"}), 404
    data = request.get_json()
    if not data:
        return jsonify({"error":"Invalid JSON"}), 400
    name = data.get("name","").strip()
    calories = data.get("calories")
    sugar_grams = data.get("sugar_grams")
    if not name or calories is None or sugar_grams is None:
        return jsonify({"error":"name, calories and sugar_grams required"}), 400

    # optional: check unique name
    if name != d.name and Drink.query.filter_by(name=name).first():
        return jsonify({"error":"Another drink with same name exists"}), 400

    d.name = name
    d.brand = data.get("brand")
    d.size = data.get("size")
    d.calories = float(calories)
    d.sugar_grams = float(sugar_grams)
    db.session.commit()
    return jsonify(d.to_dict()), 200

@app.route("/api/drinks/<int:drink_id>", methods=["DELETE"])
def api_delete_drink(drink_id):
    d = Drink.query.get(drink_id)
    if not d:
        return jsonify({"error":"Not found"}), 404
    db.session.delete(d)
    db.session.commit()
    return jsonify({"message":"deleted"}), 200

# ----------------------
# Frontend routes
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin_list():
    return render_template("admin_list.html")

@app.route("/admin/new")
def admin_new():
    return render_template("admin_new.html")

@app.route("/admin/<int:drink_id>/edit")
def admin_edit(drink_id):
    return render_template("admin_edit.html", drink_id=drink_id)

if __name__ == "__main__":
    app.run(debug=True)
