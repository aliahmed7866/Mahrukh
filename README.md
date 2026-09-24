# Mahrukh

A standalone Pakistani clothing storefront for Termux on Android, built with Flask, SQLite and a pure-Python Waitress server. Premium black (`#0A0A0A`) and gold (`#D4AF37`), responsive catalog, search/category filters, sizes, cart, WhatsApp order enquiries and a password-protected seller studio.

Eight original editable SVG illustrations depict shalwar kameez, unstitched fabrics, abaya, lehenga, peshwas and formal dresses. They appear throughout the hero, category cards, product views and empty bag. All assets and styling are local: no Node.js, Docker, Tailwind build step or CDN is required.

## Install in Termux

Your supplied scan found port **5050 available** and 8080 occupied. Mahrukh therefore defaults to 5050. Availability may change; startup refuses an occupied port without stopping the other process.

If Python/Git are missing, install them with:

```bash
pkg install python python-pip git
```

For a fresh clone:

```bash
cd "$HOME"
git clone https://github.com/aliahmed7866/Mahrukh.git
cd "$HOME/Mahrukh"
bash termux/install-mahrukh.sh
```

If you already cloned this repository, enter that folder and run `git pull --ff-only` instead of cloning again. Do not overwrite a populated non-Git directory; clone into a different folder if needed. There is no need to run a system-wide upgrade or change AYCF's checkout/environment.

The installer creates this repository's `.venv`, installs Flask and Waitress, and asks for:

1. A new admin password of at least 12 characters.
2. Your seller WhatsApp number including country code, e.g. `923001234567`. Use your own number; this is only an example. Leave it blank to disable checkout initially.
3. A local port. Press Enter for **5050**.

The app uses its own SQLite database, private config and `mahrukh_session` cookie. No generic `PORT`, AYCF password, or shared Flask secret is used. Private files live in ignored `instance/`; passwords are hashed and files have restricted permissions. Flask's MarkupSafe dependency can fall back to Python if its optional C extension cannot compile.

## Start and open

If `termux-services` is already installed, the installer creates and starts only the `mahrukh` service. Otherwise start it in the foreground:

```bash
cd "$HOME/Mahrukh"
.venv/bin/python run.py
```

Keep that session running and open:

- Store: **http://localhost:5050**
- Seller studio: **http://localhost:5050/admin**
- Health: **http://localhost:5050/health**

For an optional background service, run `pkg install termux-services`, reopen Termux, then rerun `bash termux/install-mahrukh.sh`. Controls:

```bash
sv status mahrukh
sv down mahrukh
sv up mahrukh
sv restart mahrukh
```

Do not start a foreground instance while the background service is using the same port. No Android process was inspected directly; only the port scan you supplied and the repository configuration were available during implementation. Android battery management may stop Termux in the background.

## Existing app hub

If `~/.config/aycf/apps.json` exists, the installer adds/updates only the Mahrukh entry and preserves the other apps and custom fields. Refresh the hub to see it. This app does not need the AYCF repository. No new hub is created if none exists.

Use `AYCF_CONFIG_DIR` or `AYCF_ADMIN_REGISTRY` when your existing hub registry is elsewhere. The registration checks for ports assigned to other apps, including stopped apps. Startup also checks actual socket availability. The hub Install button requires the initial password/number setup to have been completed interactively first.

## Change settings or port

```bash
cd "$HOME/Mahrukh"
.venv/bin/python setup.py
bash termux/install-mahrukh.sh
```

Blank password preserves the current password; blank WhatsApp number preserves the current number, and `-` disables checkout. The installer refreshes hub URLs after a port change. Restart an already-running foreground process yourself after changing settings. `MAHRUKH_PORT` can override the listening port for temporary foreground testing, but does not update hub URLs; use setup for permanent changes.

`MAHRUKH_INSTANCE` optionally selects a different persistent data directory. Use the same absolute value when running setup, the installer and the server. If you installed the earlier AYCF draft, stop its Mahrukh service and point `MAHRUKH_INSTANCE` at its existing `mahrukh/instance` directory to preserve your inventory/settings. Then run setup to change its saved port to 5050 and install from this repository. The installer replaces only the Mahrukh service launcher.

## Catalog and checkout

The eight seeded products are **illustrated samples** with sample prices and fabric descriptions. Replace them with real inventory before selling. Admin supports adding, editing, hiding and deleting products; whole-PKR prices; optional original prices; sizes; descriptions; and up to six images per product. Use HTTPS URLs for product photos or a bundled SVG path shown in the editor. Bundled art always retains its illustration label. Multiple images produce gallery thumbnails.

The cart stores product IDs, sizes and quantities in a signed session cookie. The server validates them and calculates prices from SQLite at checkout; client-supplied prices are ignored. Limits are 20 selections and 10 units per selection. Deleted/hidden products and invalidated sizes are excluded. The app does not reserve stock or persist orders.

WhatsApp checkout opens an encoded order enquiry containing items, sizes, quantities, total and customer delivery details. The customer reviews the message and presses Send in WhatsApp. The seller confirms availability, delivery charges and payment. No payment is taken on the site. Checkout is disabled until a seller number is configured.

Browsing works offline after installation; external product photos and WhatsApp require connectivity. Core catalog/cart forms work without JavaScript. CSS and system fonts are served locally rather than fetched from a CDN.

## Development and checks

```bash
cd "$HOME/Mahrukh"
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python make_art.py
```

The first command tests filtering, SVG delivery, cart constraints, recalculated prices, WhatsApp encoding, disabled checkout, admin CRUD/authentication, CSRF, throttling and hub preservation. The second regenerates all original SVGs using the Python standard library.

Admin sessions expire after four hours. Forms require CSRF tokens and login attempts are throttled. The server binds only to `127.0.0.1`, intended for phone-local use. Public deployment needs HTTPS and secure-cookie configuration. Back up `instance/` while Mahrukh is stopped, and never commit that directory.

Code and server checks run on Linux. SVGs were rendered and visually inspected. Browser automation was blocked because Chromium could not be downloaded; mobile layout, full browser flows and the WhatsApp handoff still need testing on your Android phone.
