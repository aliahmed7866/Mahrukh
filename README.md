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

## Research-led improvements

Read [RESEARCH-AND-GROWTH.md](RESEARCH-AND-GROWTH.md) for the Pakistan shopper/culture research, evidence limits, assortment and content recommendations, and 90-day business plan.

The collection now filters by occasion, fabric family, size currently in stock and maximum PKR price. Product editing includes supplied/excluded pieces, verified fibre composition, lining/opacity, care, fit, unstitched panel dimensions, craft/origin and a product-specific dispatch note. Optional XS, 2XL and 3XL labels expand the original range; only the seller’s selected, stocked sizes can be ordered.

Garment charts store finished flat measurements in inches, with optional browser conversion to centimetres. They are not body measurements or universal size standards. A new database table is created automatically on startup; existing products remain editable with empty facts. Nothing fills in measurements on behalf of the seller. New order snapshots preserve product facts, and edits invalidate an older checkout quote. Earlier order receipts still work without these fields.

`/our-roots` contains a sourced cultural notebook with four original decorative SVG studies. `/fabric-and-fit` explains measurements, unstitched panels and included pieces. `/admin/insights` lists product information gaps and order figures for the seller. Customers using shared devices can remove their browser’s access from **My orders** without deleting or cancelling the shop’s records.

## A more personal boutique experience

Shoppers can save up to 24 pieces for their current browser session, open a dedicated saved collection, remove individual favourites or clear the list. Saving does not reserve inventory. The live workflow uses the existing signed session cookie and CSRF-protected forms; the design preview uses only tab session storage. Hidden/deleted live products drop out of the saved collection.

Product photographs now open in an accessible enlarged viewer with Escape, previous/next controls and arrow-key navigation when multiple photos are present. Without JavaScript the photo link opens the original image. Selecting a size highlights its measurement row, shows current available quantity and carries the size into topic-specific WhatsApp questions. The customer still chooses whether to send the draft. Fully sold-out pieces have a disabled purchase button and retain the contact route.

Filter chips remove one choice while preserving the others. On narrow screens the filter panel starts closed when no filters are applied; all filters remain available without JavaScript. Related pieces help shoppers continue browsing. These suggestions use category and catalog order, not tracking or personal profiling.

In **Shop settings → Your business**, Mahrukh can write an optional personal welcome and signature. In **Contact & social profiles**, she can list the languages she actually offers for support. The welcome stays hidden until she writes it; only the design preview contains a clearly labelled sample note. This does not translate the storefront.

## Shareable design preview

[Open the Mahrukh design preview](https://aliahmed7866.github.io/Mahrukh/). It contains six fictional AI concept pieces, a sample bag, saved favourites, enlarged photographs, working demo filters, sample measurement charts, a cultural notebook, fit guide, contact-page preview and seller feature tour. It now offers English / اردو page variants, remembered language selection, Urdu layout and a read-only order-journey tour. Urdu preview wording is marked as awaiting fluent review. The live Flask bilingual milestone is still planned. It accepts no orders or payments and collects no customer details. The actual store requires a separately hosted Flask backend.

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

The test suite covers catalog/admin regressions, seller settings, malicious links, payment verification, saved order privacy, stock contention, duplicate submissions, stale edits and core colour contrast, combined filters, factual detail validation, immutable product snapshots and shared-device privacy. The other two commands regenerate the original vector brand artwork with the Python standard library.

Core shopping and seller forms work without JavaScript; JavaScript adds the slide-out bag and gallery controls. CSS/fonts are local. External image URLs, social sites and WhatsApp require connectivity. Uploaded product photos work locally.

The server still defaults to loopback port 5050 and keeps its own environment, database and cookie name. It never stops or reconfigures your other Termux apps. See the launch guide before exposing it publicly. Back up private `instance/` regularly; never commit it.
