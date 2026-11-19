# Mahrukh on Cloudflare

The public boutique and owner studio run on a Cloudflare Worker with durable D1 content and photo storage.

- Website: https://mahrukh.ammeemughal.workers.dev/
- Owner studio: https://mahrukh.ammeemughal.workers.dev/studio
- Runtime health: `/health`

This is a separate cloud publishing surface. The existing Flask/Termux shop, its inventory, customers, stock reservations and orders remain independent. No private Termux database was available during this deployment, so no inventory, customer records, seller number or credentials have been migrated. The initial public entries are explicitly labelled original art studies, not saleable stock or photographs.

## First visit

Use the private one-time setup link supplied with deployment within seven days. Choose a unique password with at least 12 characters. The setup link is consumed once; subsequent visits use `/studio` and your password. No default production password exists. Keep the setup link private.

If setup expires or an owner password is lost, an account administrator must perform a verified recovery through the Cloudflare account. Do not create an unauthenticated public password-reset route. The database contains password derivations, never plaintext passwords.

## Edit without code

1. **Website mode:** portfolio, enquiries, or WhatsApp catalogue.
2. **Words & language:** edit English and Urdu hero copy, introductions, story, signature and notices. Blank optional Urdu fields use English.
3. **Collection:** create, hide, reorder or remove entries. Add your own photos, descriptive alt text, category, story, garment facts and prices. Real pieces require an uploaded photograph.
4. **Appearance:** select Garden noir, Indigo night or Rose dusk; choose one of four original SVG illustrations; show, hide and reorder homepage sections.
5. **Contact & policies:** enter your real WhatsApp number with country code, Instagram username, email, response note, delivery and returns policies.
6. **History & backups:** load one of the previous 12 revisions into the editor, export/import a content draft, and remove unreferenced uploads.

**Save draft** is private. **Preview draft** shows the last saved draft (the editor saves unsaved changes before opening it). **Publish changes** presents a review dialog, then updates the public website. Conflicting edits from another tab are rejected without clearing the current editor; export your edits before reloading. There is no automatic publication when switching modes or choosing a palette.

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

The build bundles the allowlisted local CSS, JavaScript, SVG and Urdu font as Worker module assets. `assets.mjs` is generated and ignored. Editable vector sources and the generator `art.mjs` are tracked; run `node cloudflare/art.mjs` to regenerate the four illustrations.

For later deployments using an authenticated Cloudflare CLI:

```sh
npm run build
npx wrangler@4.163.0 deploy
```

`wrangler.jsonc` identifies the existing Worker and D1 database. Do not create a new D1 database for a normal code release. The initial deployment used the connected Cloudflare API to upload the same ES modules and configure the binding. The `schema.sql` migration is additive; seed defaults only if the `site` row is absent. Setup tokens must be generated randomly, stored as SHA256 hashes with an expiry and never committed. No automatic GitHub-to-Cloudflare deployment hook has been installed.

## Verification

`npm test` exercises Worker routes, auth boundaries, one-time setup, session revocation, private drafts, publishing, stale revisions, bounded uploads, media visibility, catalogue gates, safe rendering and editor interactions. The legacy Flask tests remain under `tests/`.

Visual review of the deployed public website covers the hero, collection search, saved pieces, detail views, photo enlargement and Urdu navigation. Fluent Urdu proofreading remains advisable before a commercial launch. All artwork is a contemporary original interpretation; it is not presented as an authenticated historical pattern or an artisan-made product.
