CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL, category TEXT NOT NULL,
 price INTEGER NOT NULL CHECK(price > 0), compare_price INTEGER NOT NULL DEFAULT 0,
 fabric TEXT NOT NULL, description TEXT NOT NULL,
 sizes TEXT NOT NULL, images TEXT NOT NULL,
 active INTEGER NOT NULL DEFAULT 1, illustration INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS login_limit (id INTEGER PRIMARY KEY CHECK(id=1), failures INTEGER NOT NULL, blocked_until INTEGER NOT NULL);
INSERT OR IGNORE INTO login_limit VALUES (1,0,0);
CREATE TABLE IF NOT EXISTS shop_settings (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inventory (
 product_id INTEGER NOT NULL, size TEXT NOT NULL, quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity>=0),
 PRIMARY KEY(product_id,size)
);
CREATE TABLE IF NOT EXISTS orders (
 id INTEGER PRIMARY KEY AUTOINCREMENT, reference TEXT UNIQUE NOT NULL,
 request_id TEXT UNIQUE NOT NULL, owner TEXT NOT NULL, source_hash TEXT NOT NULL,
 name TEXT NOT NULL, contact TEXT NOT NULL, city TEXT NOT NULL, address TEXT NOT NULL,
 items TEXT NOT NULL, subtotal INTEGER NOT NULL, shipping INTEGER NOT NULL, total INTEGER NOT NULL,
 payment_method TEXT NOT NULL, provider TEXT NOT NULL, policies TEXT NOT NULL, merchant TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending', payment_status TEXT NOT NULL DEFAULT 'unpaid',
 invoice_currency TEXT NOT NULL DEFAULT '', invoice_amount TEXT NOT NULL DEFAULT '',
 payment_reference TEXT NOT NULL DEFAULT '', payment_url TEXT NOT NULL DEFAULT '', tracking TEXT NOT NULL DEFAULT '',
 version INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS orders_owner ON orders(owner);
CREATE INDEX IF NOT EXISTS orders_source_time ON orders(source_hash, created_at);
CREATE TABLE IF NOT EXISTS order_events (id INTEGER PRIMARY KEY AUTOINCREMENT, reference TEXT NOT NULL, created_at TEXT NOT NULL, note TEXT NOT NULL);
