# Mahrukh

A standalone Pakistani clothing storefront for Termux on Android, built with Flask, SQLite and a pure-Python Waitress server. Premium black (`#0A0A0A`) and gold (`#D4AF37`), responsive catalog, search/category filters, sizes, cart, saved order requests, stock reservations, WhatsApp help and a password-protected seller studio.

Original editable SVG women in traditional dress, garment vignettes and botanical borders establish the brand style in the hero, category navigation, editorial section and empty bag. Product cards and galleries use actual seller-provided photographs. All assets and styling are local: no Node.js, Docker, Tailwind build step or CDN is required.

## Visual direction

The supplied Mahrukh packaging guides the wordmark and tone: spaced gold serif lettering on textured charcoal, with its “Timeless style · Everyday you” tagline. Warm ivory, antique gold, muted rose and emerald add a welcoming feel. Decorative SVG portraits, floral borders and jaali-inspired geometry reference Pakistani dress and architectural patterns. The packaging photo is a reference only, not embedded in the site; the wordmark remains editable text so a future logo can replace it easily. Product photography stays separate from these decorative elements.

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

## Change password or port

```bash
cd "$HOME/Mahrukh"
.venv/bin/python setup.py
bash termux/install-mahrukh.sh
```

Blank password preserves the current password. The setup WhatsApp number is used as an initial fallback; after saving Shop settings, manage WhatsApp there. To pause checkout use the Accept orders switch in Shop settings. The installer refreshes hub URLs after a port change. Restart an already-running foreground process yourself after changing settings. `MAHRUKH_PORT` can override the listening port for temporary foreground testing, but does not update hub URLs; use setup for permanent changes.

`MAHRUKH_INSTANCE` optionally selects a different persistent data directory. Use the same absolute value when running setup, the installer and the server. If you installed the earlier AYCF draft, stop its Mahrukh service and point `MAHRUKH_INSTANCE` at its existing `mahrukh/instance` directory to preserve your inventory/settings. Then run setup to change its saved port to 5050 and install from this repository. The installer replaces only the Mahrukh service launcher.

## Seller studio and shopping

Open `/admin` → **Shop settings** to configure WhatsApp, email, response hours, social links, merchant identity, shipping fees/cities, policies and payment choices without a restart. Set available stock for each size, upload actual product photos from your phone (JPG/PNG/WebP, 4 MB each, six total), or use HTTPS photo URLs. Product artwork stays separate from real inventory.

New installations have no demo inventory. Upgrades preserve products, hide old bundled illustration listings and start with zero stock. The order switch defaults off until business details and policies are completed. The live app never reads `preview/products.json`.

The server calculates prices/delivery, rejects stale quotes, reserves stock in a transaction and stores private order snapshots. Repeated submissions return the same order. Customers can open a structured WhatsApp follow-up themselves. Seller studio tracks pending, confirmed, dispatched, completed and cancelled requests; pre-dispatch cancellation returns stock once. Review the dashboard regularly — no automatic seller notification is sent.

Payment methods are cash on delivery, manual merchant bank/mobile-wallet transfer, or order-specific hosted invoices via Safepay / an eligible PayPal account. **These are manually verified workflows, not an automated payment gateway.** No card data is collected. Payment links, provider onboarding and actual refunds are handled in the provider dashboard. All prices in the shop are PKR.

Read [BUSINESS-LAUNCH.md](BUSINESS-LAUNCH.md) for the seller setup sequence, payment limitations, Pakistan business/tax review, public HTTPS hosting, backups and privacy/retention operations. The app supports startup operations; it does not certify compliance or issue statutory tax invoices.

## Shareable design preview

[Open the Mahrukh design preview](https://aliahmed7866.github.io/Mahrukh/). It contains six fictional AI concept pieces, a sample bag, contact-page preview and seller feature tour. It accepts no orders or payments and collects no customer details. The actual store requires a separately hosted Flask backend.

```bash
.venv/bin/python preview/check.py
```

This builds and validates `preview-site/`, an allowlisted output with no live database or config. Publish only that output to `gh-pages`; see [preview/README.md](preview/README.md).

## Development and checks

```bash
cd "$HOME/Mahrukh"
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python make_art.py
.venv/bin/python make_brand_art.py
```

The test suite covers catalog/admin regressions, seller settings, malicious links, payment verification, saved order privacy, stock contention, duplicate submissions, stale edits and core colour contrast. The other two commands regenerate the original vector brand artwork with the Python standard library.

Core shopping and seller forms work without JavaScript; JavaScript adds the slide-out bag and gallery controls. CSS/fonts are local. External image URLs, social sites and WhatsApp require connectivity. Uploaded product photos work locally.

The server still defaults to loopback port 5050 and keeps its own environment, database and cookie name. It never stops or reconfigures your other Termux apps. See the launch guide before exposing it publicly. Back up private `instance/` regularly; never commit it.
