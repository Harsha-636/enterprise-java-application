from flask import Flask, jsonify, request, session
from flask_cors import CORS
import json, os, uuid, requests
from datetime import datetime

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

def call_claude(prompt, max_tokens=500):
    try:
        res = requests.post(
            ANTHROPIC_API_URL,
            headers={"Content-Type": "application/json"},
            json={"model": "claude-sonnet-4-6", "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=15
        )
        res.raise_for_status()
        return res.json()["content"][0]["text"].strip()
    except Exception as e:
        return None

app = Flask(__name__)
app.secret_key = "alcobrake-ecom-2025"
CORS(app, supports_credentials=True)

PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"
USERS_FILE = "users.json"

# ── DATA HELPERS ──
def load(file):
    if not os.path.exists(file):
        return []
    with open(file) as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def init_data():
    if not os.path.exists(PRODUCTS_FILE):
        products = [
            {"id":"p001","name":"Wireless Headphones","category":"Electronics","price":2999,"stock":45,"description":"Premium noise-cancelling wireless headphones","image":"🎧","status":"active","created_at":"01 Jan 2026"},
            {"id":"p002","name":"Running Shoes","category":"Footwear","price":1899,"stock":30,"description":"Lightweight running shoes with cushioned sole","image":"👟","status":"active","created_at":"02 Jan 2026"},
            {"id":"p003","name":"Python Programming Book","category":"Books","price":599,"stock":100,"description":"Complete guide to Python programming","image":"📘","status":"active","created_at":"03 Jan 2026"},
            {"id":"p004","name":"Yoga Mat","category":"Sports","price":799,"stock":60,"description":"Non-slip eco-friendly yoga mat","image":"🧘","status":"active","created_at":"04 Jan 2026"},
            {"id":"p005","name":"Smart Watch","category":"Electronics","price":4999,"stock":20,"description":"Feature-rich smartwatch with health tracking","image":"⌚","status":"active","created_at":"05 Jan 2026"},
            {"id":"p006","name":"Coffee Maker","category":"Kitchen","price":2499,"stock":15,"description":"Automatic drip coffee maker 12-cup","image":"☕","status":"active","created_at":"06 Jan 2026"},
            {"id":"p007","name":"Backpack","category":"Bags","price":1299,"stock":40,"description":"Water-resistant laptop backpack 30L","image":"🎒","status":"active","created_at":"07 Jan 2026"},
            {"id":"p008","name":"Sunglasses","category":"Accessories","price":899,"stock":55,"description":"UV400 polarized sunglasses","image":"🕶️","status":"active","created_at":"08 Jan 2026"},
        ]
        save(PRODUCTS_FILE, products)

    if not os.path.exists(USERS_FILE):
        users = [
            {"id":"u001","name":"Admin User","email":"admin@alcobrake.com","password":"admin123","role":"admin"},
            {"id":"u002","name":"John Doe","email":"john@example.com","password":"user123","role":"customer"},
            {"id":"u003","name":"Priya Sharma","email":"priya@example.com","password":"user123","role":"customer"},
        ]
        save(USERS_FILE, users)

    if not os.path.exists(ORDERS_FILE):
        orders = [
            {"id":"ORD001","user_id":"u002","user_name":"John Doe","product_id":"p001","product_name":"Wireless Headphones","quantity":1,"total":2999,"status":"delivered","created_at":"10 Jan 2026"},
            {"id":"ORD002","user_id":"u003","user_name":"Priya Sharma","product_id":"p005","product_name":"Smart Watch","quantity":1,"total":4999,"status":"shipped","created_at":"12 Jan 2026"},
            {"id":"ORD003","user_id":"u002","user_name":"John Doe","product_id":"p003","product_name":"Python Programming Book","quantity":2,"total":1198,"status":"processing","created_at":"15 Jan 2026"},
            {"id":"ORD004","user_id":"u003","user_name":"Priya Sharma","product_id":"p002","product_name":"Running Shoes","quantity":1,"total":1899,"status":"pending","created_at":"18 Jan 2026"},
        ]
        save(ORDERS_FILE, orders)

init_data()

@app.route("/")
def index():
    return open("index.html").read()

# ── AUTH ──
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    users = load(USERS_FILE)
    user = next((u for u in users if u["email"] == data.get("email") and u["password"] == data.get("password")), None)
    if user:
        session["user_id"] = user["id"]
        return jsonify({"success": True, "user": {k: v for k, v in user.items() if k != "password"}})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/me")
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"user": None})
    users = load(USERS_FILE)
    user = next((u for u in users if u["id"] == uid), None)
    if user:
        return jsonify({"user": {k: v for k, v in user.items() if k != "password"}})
    return jsonify({"user": None})

# ── PRODUCTS ──
@app.route("/api/products", methods=["GET"])
def get_products():
    products = load(PRODUCTS_FILE)
    category = request.args.get("category")
    search = request.args.get("search", "").lower()
    if category and category != "all":
        products = [p for p in products if p["category"] == category]
    if search:
        products = [p for p in products if search in p["name"].lower() or search in p["description"].lower()]
    return jsonify({"products": products, "total": len(products)})

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.json
    products = load(PRODUCTS_FILE)
    product = {
        "id": "p" + str(uuid.uuid4())[:6],
        "name": data.get("name", "").strip(),
        "category": data.get("category", "General"),
        "price": float(data.get("price", 0)),
        "stock": int(data.get("stock", 0)),
        "description": data.get("description", "").strip(),
        "image": data.get("image", "📦"),
        "status": "active",
        "created_at": datetime.now().strftime("%d %b %Y"),
    }
    if not product["name"]:
        return jsonify({"error": "Name required"}), 400
    products.append(product)
    save(PRODUCTS_FILE, products)
    return jsonify({"product": product}), 201

@app.route("/api/products/<pid>", methods=["PUT"])
def update_product(pid):
    data = request.json
    products = load(PRODUCTS_FILE)
    for p in products:
        if p["id"] == pid:
            p.update({k: v for k, v in data.items() if k != "id"})
            save(PRODUCTS_FILE, products)
            return jsonify({"product": p})
    return jsonify({"error": "Not found"}), 404

@app.route("/api/products/<pid>", methods=["DELETE"])
def delete_product(pid):
    products = load(PRODUCTS_FILE)
    products = [p for p in products if p["id"] != pid]
    save(PRODUCTS_FILE, products)
    return jsonify({"message": "Deleted"})

# ── ORDERS ──
@app.route("/api/orders", methods=["GET"])
def get_orders():
    orders = load(ORDERS_FILE)
    status = request.args.get("status")
    if status and status != "all":
        orders = [o for o in orders if o["status"] == status]
    orders.sort(key=lambda x: x["created_at"], reverse=True)
    return jsonify({"orders": orders, "total": len(orders)})

@app.route("/api/orders", methods=["POST"])
def place_order():
    data = request.json
    orders = load(ORDERS_FILE)
    products = load(PRODUCTS_FILE)
    product = next((p for p in products if p["id"] == data.get("product_id")), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    qty = int(data.get("quantity", 1))
    if product["stock"] < qty:
        return jsonify({"error": "Insufficient stock"}), 400
    order = {
        "id": "ORD" + str(uuid.uuid4())[:6].upper(),
        "user_id": data.get("user_id", "guest"),
        "user_name": data.get("user_name", "Guest"),
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": qty,
        "total": product["price"] * qty,
        "status": "pending",
        "created_at": datetime.now().strftime("%d %b %Y"),
    }
    product["stock"] -= qty
    orders.append(order)
    save(ORDERS_FILE, orders)
    save(PRODUCTS_FILE, products)
    return jsonify({"order": order}), 201

@app.route("/api/orders/<oid>", methods=["PUT"])
def update_order(oid):
    data = request.json
    orders = load(ORDERS_FILE)
    for o in orders:
        if o["id"] == oid:
            o.update({k: v for k, v in data.items() if k != "id"})
            save(ORDERS_FILE, orders)
            return jsonify({"order": o})
    return jsonify({"error": "Not found"}), 404

# ── STATS ──
@app.route("/api/stats")
def get_stats():
    products = load(PRODUCTS_FILE)
    orders = load(ORDERS_FILE)
    users = load(USERS_FILE)
    revenue = sum(o["total"] for o in orders if o["status"] == "delivered")
    low_stock = [p for p in products if p["stock"] < 20]
    return jsonify({
        "total_products": len(products),
        "total_orders": len(orders),
        "total_users": len(users),
        "revenue": revenue,
        "pending_orders": len([o for o in orders if o["status"] == "pending"]),
        "delivered_orders": len([o for o in orders if o["status"] == "delivered"]),
        "low_stock_count": len(low_stock),
        "categories": list(set(p["category"] for p in products)),
    })

# ── AI ENDPOINTS ──
@app.route("/api/ai/describe", methods=["POST"])
def ai_describe():
    data = request.json
    name = data.get("name", "")
    category = data.get("category", "")
    price = data.get("price", "")
    prompt = (f"Write a compelling 1-2 sentence product description for an e-commerce store. "
              f"Product: {name}, Category: {category}, Price: ₹{price}. "
              f"Be concise, highlight key benefits, no fluff. Just the description text, nothing else.")
    result = call_claude(prompt, 150)
    if result:
        return jsonify({"description": result})
    return jsonify({"description": f"High-quality {name} perfect for everyday use. Great value at ₹{price}."})

@app.route("/api/ai/insights", methods=["GET"])
def ai_insights():
    products = load(PRODUCTS_FILE)
    orders = load(ORDERS_FILE)
    revenue = sum(o["total"] for o in orders if o["status"] == "delivered")
    pending = len([o for o in orders if o["status"] == "pending"])
    low_stock = [p["name"] for p in products if p["stock"] < 20]
    top_product = max(orders, key=lambda x: x["total"], default={}).get("product_name", "N/A") if orders else "N/A"

    summary = (f"Store has {len(products)} products, {len(orders)} orders, ₹{revenue} revenue delivered. "
               f"{pending} orders pending. Low stock items: {', '.join(low_stock) if low_stock else 'none'}. "
               f"Highest value order product: {top_product}.")

    prompt = (f"You are a business analyst for an e-commerce store. Based on this data: {summary}\n"
              f"Give exactly 3 short actionable business insights as bullet points. "
              f"Each point max 1 sentence. Format: • insight1\n• insight2\n• insight3. Nothing else.")
    result = call_claude(prompt, 200)
    if result:
        insights = [line.strip().lstrip("•").strip() for line in result.split("\n") if line.strip() and line.strip() != "•"]
        return jsonify({"insights": insights[:3], "summary": summary})
    return jsonify({"insights": [
        f"You have {pending} pending orders — process them quickly to improve customer satisfaction",
        f"Low stock alert on {len(low_stock)} items — restock {low_stock[0] if low_stock else 'items'} soon",
        "Focus marketing on your top-selling electronics category to maximize revenue"
    ], "summary": summary})

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    data = request.json
    message = data.get("message", "")
    products = load(PRODUCTS_FILE)
    product_list = ", ".join([f"{p['name']} (₹{p['price']})" for p in products[:8]])
    prompt = (f"You are a helpful customer support assistant for AlcoBrake, an e-commerce store. "
              f"Available products: {product_list}. "
              f"Customer asks: {message}\n"
              f"Reply in 2-3 sentences max. Be helpful, friendly and specific. If asked about a product not listed, say it's not available.")
    result = call_claude(prompt, 200)
    if result:
        return jsonify({"reply": result})
    return jsonify({"reply": "Thank you for your question! Please browse our products page to find what you need, or contact us at support@alcobrake.com."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
