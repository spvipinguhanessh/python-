from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

inventory = [
    {"id": 1, "name": "Rice (5kg)", "price": 250.0, "quantity": 12},
    {"id": 2, "name": "Cooking Oil (1L)", "price": 130.0, "quantity": 4},
    {"id": 3, "name": "Sugar (1kg)", "price": 45.0, "quantity": 2},
]
next_id = 4

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Inventra — Inventory Manager</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet"/>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Nunito',sans-serif; background:#eef2ff; min-height:100vh; padding:30px 16px 60px; }
  .wrapper { max-width:860px; margin:0 auto; }

  .header { text-align:center; margin-bottom:36px; }
  .header .emo { font-size:48px; display:block; margin-bottom:8px; }
  .header h1 { font-size:36px; font-weight:800; color:#4f46e5; letter-spacing:-1px; }
  .header p { color:#6b7280; font-size:14px; margin-top:4px; }

  .stats { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:28px; }
  .stat { background:#fff; border-radius:18px; padding:20px 16px; text-align:center; box-shadow:0 2px 12px #4f46e512; border-top:4px solid; transition:transform .2s; }
  .stat:hover { transform:translateY(-3px); }
  .stat.s1{border-color:#6366f1} .stat.s2{border-color:#f59e0b} .stat.s3{border-color:#ef4444}
  .stat .val { font-size:28px; font-weight:800; }
  .stat.s1 .val{color:#6366f1} .stat.s2 .val{color:#f59e0b} .stat.s3 .val{color:#ef4444}
  .stat .lbl { font-size:12px; color:#9ca3af; font-weight:600; margin-top:4px; text-transform:uppercase; letter-spacing:.8px; }

  .add-card { background:#fff; border-radius:20px; padding:28px; margin-bottom:24px; box-shadow:0 2px 16px #4f46e510; }
  .add-card h2 { font-size:17px; font-weight:700; color:#4f46e5; margin-bottom:18px; }
  .form-row { display:grid; grid-template-columns:2fr 1fr 1fr auto; gap:12px; align-items:end; }
  label { display:block; font-size:12px; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:.7px; margin-bottom:6px; }
  input {
    width:100%; background:#eff6ff; border:2px solid #bfdbfe;
    border-radius:12px; padding:11px 14px;
    font-family:'Nunito',sans-serif; font-size:14px; color:#1e3a8a;
    outline:none; transition:border-color .2s, box-shadow .2s;
  }
  input:focus { border-color:#6366f1; box-shadow:0 0 0 3px #6366f120; background:#fff; }
  input::placeholder { color:#93c5fd; }
  input.error { border-color:#ef4444; background:#fff5f5; }

  .btn-add { background:linear-gradient(135deg,#6366f1,#818cf8); color:#fff; border:none; border-radius:12px; padding:12px 22px; font-family:'Nunito',sans-serif; font-size:14px; font-weight:700; cursor:pointer; white-space:nowrap; transition:opacity .2s,transform .15s; box-shadow:0 4px 14px #6366f140; }
  .btn-add:hover { opacity:.88; transform:translateY(-1px); }
  .btn-add:active { transform:scale(.97); }

  .err-msg { color:#ef4444; font-size:13px; font-weight:700; background:#fff1f2; border:2px solid #fecdd3; border-radius:12px; padding:10px 16px; margin-bottom:16px; }

  .table-card { background:#fff; border-radius:20px; overflow:hidden; box-shadow:0 2px 16px #4f46e510; }
  .tbar { padding:18px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f3f4f6; }
  .tbar h2 { font-size:17px; font-weight:700; color:#1f2937; }
  .tbar span { font-size:13px; color:#9ca3af; font-weight:600; }
  table { width:100%; border-collapse:collapse; }
  th { font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#9ca3af; font-weight:700; padding:12px 20px; text-align:left; background:#f8faff; border-bottom:1px solid #e0e7ff; }
  td { padding:15px 20px; font-size:14px; border-bottom:1px solid #f1f5ff; color:#374151; }
  tr:last-child td { border-bottom:none; }
  tr:hover td { background:#f5f8ff; }
  .iname { font-weight:700; color:#1f2937; }
  .price { font-weight:700; color:#f59e0b; }
  .badge { display:inline-block; padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; }
  .ok  { background:#d1fae5; color:#065f46; }
  .low { background:#fee2e2; color:#991b1b; }
  .btn-del { background:none; border:2px solid #fecdd3; color:#ef4444; border-radius:10px; padding:6px 14px; font-family:'Nunito',sans-serif; font-size:13px; font-weight:700; cursor:pointer; transition:all .2s; }
  .btn-del:hover { background:#ef4444; color:#fff; border-color:#ef4444; }

  .alert { background:#ecfdf5; border:2px solid #6ee7b7; color:#065f46; border-radius:14px; padding:12px 20px; margin-bottom:20px; font-size:14px; font-weight:600; }
  .empty { text-align:center; padding:48px 20px; color:#bfdbfe; font-size:15px; font-weight:600; }
  .empty span { font-size:40px; display:block; margin-bottom:10px; }
  .footer { text-align:center; margin-top:32px; color:#c7d2fe; font-size:13px; font-weight:600; }
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <span class="emo">🛒</span>
    <h1>Inventra</h1>
    <p>Simple &amp; Smart Inventory Management &nbsp;&middot;&nbsp; Group 7 &nbsp;&middot;&nbsp; Alliance University</p>
  </div>

  {ALERT}
  {ERROR}

  <div class="stats">
    <div class="stat s1"><div class="val">{TOTAL_ITEMS}</div><div class="lbl">Total Items</div></div>
    <div class="stat s2"><div class="val">&#8377;{TOTAL_VALUE}</div><div class="lbl">Stock Value</div></div>
    <div class="stat s3"><div class="val">{LOW_STOCK}</div><div class="lbl">Low Stock</div></div>
  </div>

  <div class="add-card">
    <h2>&#10024; Add New Item</h2>
    <form method="POST" action="/add">
      <div class="form-row">
        <div><label>Item Name</label><input type="text" name="name" placeholder="e.g. Wheat Flour 2kg" required/></div>
        <div><label>Price (&#8377;)</label><input type="number" name="price" step="0.01" min="0.01" placeholder="0.00" required/></div>
        <div><label>Quantity</label><input type="number" name="quantity" min="1" placeholder="0" required/></div>
        <div><label>&nbsp;</label><button class="btn-add" type="submit">+ Add Item</button></div>
      </div>
    </form>
  </div>

  <div class="table-card">
    <div class="tbar">
      <h2>&#128230; Stock Overview</h2>
      <span>{TOTAL_ITEMS} items tracked</span>
    </div>
    <table>
      <thead><tr><th>#</th><th>Item Name</th><th>Price</th><th>Quantity</th><th>Status</th><th>Action</th></tr></thead>
      <tbody>{ROWS}</tbody>
    </table>
  </div>

  <div class="footer">Made with &#128013; Python &nbsp;&middot;&nbsp; Alliance College of Engineering and Design</div>
</div>
</body>
</html>"""

def build_rows(inv):
    if not inv:
        return '<tr><td colspan="6"><div class="empty"><span>&#128451;</span>No items yet — add your first item above!</div></td></tr>'
    rows = ""
    for i, item in enumerate(inv, 1):
        low = item["quantity"] < 5
        badge = '<span class="badge low">&#9888; Low Stock</span>' if low else '<span class="badge ok">&#10004; In Stock</span>'
        rows += f"""<tr>
          <td style="color:#c7d2fe;font-weight:700">{i}</td>
          <td><span class="iname">{item['name']}</span></td>
          <td><span class="price">&#8377;{item['price']:.2f}</span></td>
          <td><b>{item['quantity']}</b></td>
          <td>{badge}</td>
          <td><form method="POST" action="/delete" style="display:inline">
            <input type="hidden" name="id" value="{item['id']}"/>
            <button class="btn-del" type="submit">&#128465; Delete</button>
          </form></td>
        </tr>"""
    return rows

def render(alert="", error=""):
    total = len(inventory)
    value = sum(i["price"] * i["quantity"] for i in inventory)
    low = sum(1 for i in inventory if i["quantity"] < 5)
    rows = build_rows(inventory)
    alert_html = f'<div class="alert">&#9989; {alert}</div>' if alert else ""
    error_html  = f'<div class="err-msg">&#10060; {error}</div>' if error else ""
    return HTML.replace("{TOTAL_ITEMS}", str(total)) \
               .replace("{TOTAL_VALUE}", f"{value:,.0f}") \
               .replace("{LOW_STOCK}", str(low)) \
               .replace("{ROWS}", rows) \
               .replace("{ALERT}", alert_html) \
               .replace("{ERROR}", error_html).encode()

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def send_page(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self.send_page(render())

    def do_POST(self):
        global next_id
        length = int(self.headers.get("Content-Length", 0))
        data = urllib.parse.parse_qs(self.rfile.read(length).decode())

        if self.path == "/add":
            name = data.get("name", [""])[0].strip()
            price_raw = data.get("price", [""])[0].strip()
            qty_raw   = data.get("quantity", [""])[0].strip()

            # --- Validation ---
            if not name or not name.replace(" ", "").isascii():
                return self.send_page(render(error="Item name cannot be empty."))
            if any(i["name"].lower() == name.lower() for i in inventory):
                return self.send_page(render(error=f"'{name}' already exists in inventory!"))
            try:
                price = float(price_raw)
                if price <= 0:
                    raise ValueError
            except ValueError:
                return self.send_page(render(error="Price must be a positive number (e.g. 49.99)."))
            try:
                qty = int(qty_raw)
                if qty < 1:
                    raise ValueError
            except ValueError:
                return self.send_page(render(error="Quantity must be a whole number of at least 1."))

            inventory.append({"id": next_id, "name": name, "price": price, "quantity": qty})
            next_id += 1
            self.send_page(render(alert=f"'{name}' added successfully!"))

        elif self.path == "/delete":
            del_id = int(data.get("id", [0])[0])
            item = next((i for i in inventory if i["id"] == del_id), None)
            if item:
                inventory.remove(item)
                self.send_page(render(alert=f"'{item['name']}' removed from inventory."))
            else:
                self.send_page(render())

if __name__ == "__main__":
    port = 8080
    print("=" * 45)
    print("  Inventra is running!")
    print(f"  Open this in your browser:")
    print(f"  -->  http://localhost:{port}")
    print("  Press Ctrl+C to stop.")
    print("=" * 45)
    HTTPServer(("", port), Handler).serve_forever()