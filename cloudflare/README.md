# Mahrukh on Cloudflare

The public boutique and owner studio run on a Cloudflare Worker with durable D1 content and photo storage.

- Website: https://mahrukh.uk/
- Owner studio: https://mahrukh.uk/studio
- Runtime health: `/health`

`www.mahrukh.uk` and the former Workers address redirect to the main hostname, preserving paths and language choices. Owner sessions are host-specific: sign in at the new studio address. Existing private setup links retain their fragment through the redirect. POST requests to an old hostname are rejected with instructions to reopen the studio; they are never forwarded.

This is a separate cloud publishing surface. The existing Flask/Termux shop, its inventory, customers, stock reservations and orders remain independent. No private Termux database was available during this deployment, so no inventory, customer records, seller number or credentials have been migrated. The initial public entries are explicitly labelled original art studies, not saleable stock or photographs.

## First visit

Use the private one-time setup link supplied with deployment within seven days. Choose a unique password with at least 12 characters. The setup link is consumed once; subsequent visits use `/studio` and your password. No default production password exists. Keep the setup link private.

If setup expires or an owner password is lost, an account administrator must perform a verified recovery through the Cloudflare account. Do not create an unauthenticated public password-reset route. The database contains password derivations, never plaintext passwords.

## Edit without code

1. **Website mode:** portfolio, enquiries, or WhatsApp catalogue.
2. **Words & language:** edit English and Urdu hero copy, introductions, story, signature and notices. Blank optional Urdu fields use English.
3. **Collection:** create, hide, reorder or remove entries. Editorial notes appear as text-led cultural notes without shopping controls; real clothing pieces use the product gallery. Add your own photos, descriptive alt text, category, story, garment facts and prices. Visible real pieces require an uploaded photograph. Use **Add clothing piece** for products and **Add editorial note** for cultural notes. New pieces start hidden so unfinished entries can be saved privately; add a photo, enable **Show on website**, then publish.
4. **Appearance:** select Garden noir, Indigo night or Rose dusk; choose a new fashion portrait or one of the original vector studies; show, hide and reorder homepage sections.
5. **Contact & policies:** enter your real WhatsApp number with country code, Instagram username, email, response note, delivery and returns policies.
6. **History & backups:** load one of the previous 12 revisions into the editor, export/import a content draft, and remove unreferenced uploads.

**Save draft** is private. **Preview draft** shows the last saved draft (the editor saves unsaved changes before opening it). **Publish changes** presents a review dialog, then updates the public website. Conflicting edits from another tab are rejected without clearing the current editor; export your edits before reloading. There is no automatic publication when switching modes or choosing a palette. The studio and publish review report clothing pieces separately from editorial notes and explain hidden entries or a hidden homepage collection. Selecting enquiries or catalogue enables the collection section in the draft. An empty published catalogue shows a collection-coming-soon message and WhatsApp contact instead of silently looking like portfolio mode; decorative art is never converted into merchandise. Custom collection headings are preserved.

### Add clothing with the guided form

In **Collection → Add clothing piece**, add the photo and choose a **Product group** and **Garment or set**. Suits and sets are separate from upperwear, lowerwear, outerwear and dupattas/shawls. The garment dropdown narrows to the selected group. For a set, review the included pieces: a dupatta is not assumed, and the piece count updates when you add one.

Choose stitched, unstitched or made to order; select fabric, colour, design detail, occasion and sizes as applicable. Leave unknown facts blank. Optional sections hold fit, sleeve/neckline details, measurements and care. Unstitched fabric uses lengths instead of sewn sizes. Mixed-fabric notes can describe each component.

**Suggested listing** previews the name, introduction, description and product facts. **Fill empty fields** preserves existing wording. Tick **Replace existing English wording and product facts** to replace it, or use **Undo last fill** to restore the previous fields. Review **Your listing**, set the price and availability, then enable **Show on website** and publish. Urdu wording remains editable separately. **Add a similar piece** makes a hidden copy for quicker entry of related products.

Existing products keep their content. Structured groups drive public category filters after publication. See [category research and description rules](PRODUCT-CATEGORIES.md) for terminology and behaviour.

### What the modes do

| Mode | Portfolio | Product prices | Product enquiry button |
| --- | --- | --- | --- |
| Portfolio | Visible entries | Hidden | Hidden; general contact can still be public |
| Enquiries | Visible entries | Hidden | WhatsApp for real pieces that are not sold out |
| WhatsApp catalogue | Visible entries | PKR or price on request | WhatsApp for real pieces that are not sold out |

Enquiries and catalogue require a public WhatsApp number. Catalogue also requires English delivery and returns information. Art studies never have product order buttons. A WhatsApp enquiry is not a payment, reservation, confirmed order or automated message. Customers send their own message; WhatsApp conversations do not sync into this app. The cloud site does not implement the transactional checkout from the separate Flask shop.

## Photographs and data

The editor accepts JPEG, PNG and WebP sources, resizes to at most 1800 pixels and encodes JPEG. The server validates JPEG structure and dimensions and strips APP/COM metadata including EXIF/GPS. Uploads are bounded to 300 KB each, 100 photos and 15 MB in total; these are application safeguards, not claims about the provider plan. Original photographs should be retained separately. Draft/history-only photos require an owner session. Removing an entry does not remove its photo while any retained revision references it.

Draft JSON exports include content and media references, **not image files or credentials**. They restore against the same uploaded media store. For a complete operational backup, export the D1 database in Cloudflare and retain your original photos. New code deployments preserve the database and published content. Do not reseed a populated database or overwrite published content with defaults.

Sessions expire after 12 hours and use Secure, HttpOnly, SameSite=Strict host cookies. Writes require the same Origin and a CSRF header. Password verification uses PBKDF2-SHA256 (100,000 iterations, unique random salts); online attempts are limited in D1. The optional `AUTH_PEPPER` secret protects login-abuse IP hashes. It is provisioned on the deployed Worker and must be preserved. Password changes revoke all sessions. Server rendering escapes seller content; raw HTML, SVG uploads and arbitrary remote image URLs are not accepted. Security headers and a restrictive CSP are applied to all responses.

The public site is server-rendered, with local fonts and assets, English/Urdu navigation, accessible image enlargement, browser-local saved pieces, search, filters, reduced-motion support, sitemap and meaningful 404 responses. Search/favourites and the editor require JavaScript. No analytics trackers or external scripts are included.

## Development and deployment

Node 24+; production has no npm runtime dependencies. Development DOM tests use pinned jsdom. The original Python application continues to use `requirements.txt`.

```sh
npm ci
npm run build
npm test
npm run dev
```

The development adapter uses a separate ignored SQLite file in `cloudflare/.local/`. Its fixed setup token is **development-only** (64 lowercase `a` characters in `/studio#setup=...`). Never deploy `dev.mjs` or the development database. The production entrypoint is only `cloudflare/worker.mjs`.

The build bundles the local CSS, JavaScript, SVG, responsive WebP illustrations and Urdu font as Worker module assets. `assets.mjs` is generated and ignored. Editable vector sources, the layered portrait generator `figure-art.mjs` and the generator `art.mjs` are tracked; run `node cloudflare/art.mjs` to regenerate the five SVG studies. This command leaves the new lookbook artwork untouched. See [artwork sources and generation notes](ARTWORK.md) for the two new fashion portraits. The shared artwork catalogue in `content.mjs` keeps the public site, detail pages and studio previews consistent. The default brand artwork is a transparent courtyard conversation scene paired with a native SVG fabric-and-botanical composition. Decorative studies are editorial notes, not product cards. Legacy study URLs render as reading pages without save, zoom, price or enquiry controls. Real clothing pieces retain their gallery, filters, favourites, zoom and WhatsApp behaviour.

For later deployments using an authenticated Cloudflare CLI:

```sh
npm run build
npx wrangler@4.163.0 deploy
```

`wrangler.jsonc` identifies the existing Worker, D1 database, custom domains and primary-origin variables. Preserve these variables and the existing `AUTH_PEPPER` secret when uploading with the API. Do not create a new D1 database for a normal code release. The initial deployment used the connected Cloudflare API to upload the same ES modules and configure the binding. The `schema.sql` migration is additive; seed defaults only if the `site` row is absent. Setup tokens must be generated randomly, stored as SHA256 hashes with an expiry and never committed. No automatic GitHub-to-Cloudflare deployment hook has been installed.

## Verification

`npm test` verifies uploaded JPEG response bodies byte for byte using D1-style BLOB arrays, as well as Worker routes, auth boundaries, one-time setup, session revocation, private drafts, publishing, stale revisions, bounded uploads, media visibility, catalogue gates, safe rendering and editor interactions. The legacy Flask tests remain under `tests/`.

Visual review of the deployed public website covers the hero, collection search, saved pieces, detail views, photo enlargement and Urdu navigation. Fluent Urdu proofreading remains advisable before a commercial launch. All artwork is a contemporary original interpretation; it is not presented as an authenticated historical pattern or an artisan-made product.
