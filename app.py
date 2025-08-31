from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3, json, datetime

app = Flask(__name__)
CORS(app)

DB = "database.db"

# Initialize DB
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS shopping_list(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item TEXT,
                        category TEXT,
                        quantity TEXT
                    )""")
        c.execute("""CREATE TABLE IF NOT EXISTS history(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item TEXT,
                        timestamp TEXT
                    )""")
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/list", methods=["GET","POST","DELETE"])
def shopping_list():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if request.method == "GET":
        items = c.execute("SELECT * FROM shopping_list").fetchall()
        return jsonify([{"id":i[0],"item":i[1],"category":i[2],"quantity":i[3]} for i in items])

    elif request.method == "POST":
        data = request.json
        item, category, quantity = data.get("item"), data.get("category","misc"), data.get("quantity","1")
        c.execute("INSERT INTO shopping_list(item,category,quantity) VALUES(?,?,?)",(item,category,quantity))
        c.execute("INSERT INTO history(item,timestamp) VALUES(?,?)",(item,datetime.datetime.now().isoformat()))
        conn.commit()
        return jsonify({"message":"Item added"})

    elif request.method == "DELETE":
        item_id = request.args.get("id")
        c.execute("DELETE FROM shopping_list WHERE id=?",(item_id,))
        conn.commit()
        return jsonify({"message":"Item removed"})

@app.route("/api/suggest", methods=["GET"])
def suggest():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # History-based
    hist = c.execute("SELECT item FROM history ORDER BY id DESC LIMIT 5").fetchall()
    hist = [h[0] for h in hist]

    # Seasonal
    month = datetime.datetime.now().month
    seasonal = ["Mango","Watermelon"] if month in [4,5,6] else ["Oranges","Spinach"]

    # Substitutes
    substitutes = {"milk":"almond milk","bread":"multigrain bread","butter":"margarine"}

    return jsonify({
        "history": hist,
        "seasonal": seasonal,
        "substitutes": substitutes
    })

@app.route("/api/search", methods=["GET"])
def search():
    q = request.args.get("q","").lower()
    brand = request.args.get("brand","").lower()
    price = float(request.args.get("price","999999"))

    with open("data/products.json") as f:
        products = json.load(f)

    results = [p for p in products if q in p["name"].lower() 
               and (brand in p["brand"].lower() if brand else True) 
               and p["price"] <= price]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
