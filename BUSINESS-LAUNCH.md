# Mahrukh: preparing the live shop

This release provides a working small-shop workflow. It does not certify a business, replace professional advice, file tax returns, issue FBR digital tax invoices, integrate couriers or automatically settle payments. Check the rules for your operating province, legal structure, products and customer locations with a qualified Pakistan adviser before trading. No legal identity, registration number, return promises or tax status has been invented for Mahrukh.

## Seller setup

1. Visit `/admin` on your live Flask installation and open **Shop settings**.
2. Add your trading/legal name, business correspondence address, support email, WhatsApp number, response hours and genuine social profiles. Blank social profiles stay hidden. Never enter a CNIC, password, PIN, OTP or payment API secret here.
3. Enter each supported delivery city on its own line, the flat delivery fee, any free-delivery threshold and realistic delivery estimate. The displayed fee is final for the supported cities; include any courier/COD surcharge. This release does not calculate carrier-specific rates.
4. Choose approved payment methods. Add merchant transfer instructions only after account approval. Keep hosted payments disabled until your provider account is approved for your business, country and currency.
5. Write and review shipping, returns/refunds, privacy and terms policies. State dispatch times, delivery coverage, lost/damaged parcels, defective or incorrect goods, returns window/conditions, cancellation, return postage, refund method/timing and a complaints route. Avoid blanket disclaimers that override customer rights. Only advertise real discounts against genuine comparison prices.
6. Explain customer-data purpose, access, retention and rights/contact route. The app stores submitted contact/address information, immutable order item and policy snapshots, and essential session information. It does not include analytics/advertising trackers. External product photo hosts, WhatsApp, payment providers, your courier and hosting provider may process data; accurately describe your choices. Do not put customer details in product text or public settings.
7. Add real product photos, fabric, included pieces, measurements/care information and stock per size. Stock means **available unreserved units**, not physical units including existing orders. Sold-out sizes cannot be ordered. Stock on older installations begins at zero until set.
8. Complete all required shop fields, review the storefront, then enable **Accept orders**. This switch can pause checkout at any time. A completed form is not proof of regulatory compliance.

## Payment workflow

- **Cash on delivery:** only enable where supported by your courier. Mark paid after verifying collection/settlement according to your accounting procedure.
- **Bank / Easypaisa / JazzCash:** this is a manual merchant transfer workflow, not an API integration. The customer sees the saved merchant instructions after you confirm the order. Confirm the reference and actual credited funds before marking paid.
- **Safepay hosted invoice:** create a separate payment link in your approved merchant dashboard for each confirmed order. Set the correct merchant, amount, PKR currency, order reference and expiration. Paste that link into the order and attest that you checked it. Safepay documents no-code payment links; provider onboarding/fees still apply.
- **PayPal:** optional hosted invoice support for an eligible merchant account, not a default Pakistan gateway. Check country availability and supported currencies directly with PayPal. This app does not create a PayPal account, bypass eligibility or convert PKR. PKR is absent from PayPal’s supported currency list. This app therefore requires a separately agreed USD, GBP or EUR invoice quote for PayPal, shown to the customer alongside the original PKR order total. The seller must agree the amount/conversion with the customer before attaching a link. If you cannot provide that accurately, use another enabled method.
- A redirect, customer screenshot or query parameter cannot mark an order paid. Verify in your bank/provider dashboard and record the verified transaction reference. There are no automatic payment webhooks in this release.
- Recording “refunded” does not send money. Execute the refund separately with the provider and record its reference here.

## Daily order handling

Check **Seller studio → Orders** regularly; there is no automatic seller email/SMS/push notification. Each request gets a private reference and reserves stock atomically. Customers can optionally open a WhatsApp draft after submission; the app does not automatically send messages.

Confirm → dispatch → complete. Add courier/tracking information as text. Pre-dispatch cancellation restores reserved inventory exactly once. For a return after dispatch, handle the return/refund with the customer and add returned sellable units through the product editor after inspection. An accepted order keeps its original prices, merchant details, delivery fee and policies when settings/products change. It is an order summary, **not a statutory tax invoice**.

A customer’s order summary requires their browser session; knowing an order reference alone does not reveal personal information. If they lose their session/device, verify identity through support before disclosing details. Seller sign-in expires after four hours. Guest session signatures expire after 30 days; browsers may clear session cookies earlier.

## Hosting and operations

Termux remains a local testing environment at `http://localhost:5050`; the server binds to loopback. GitHub Pages is only the separately generated, non-selling design preview. Neither is a public production Flask hosting deployment.

For real customers, use a maintained Python host with persistent private storage, HTTPS, a dedicated host name, process supervision, disk monitoring and off-device encrypted backups. Keep Flask debug off. Forward requests through a correctly configured HTTPS reverse proxy; keep the application socket private. Configure:

```bash
export MAHRUKH_SECURE_COOKIES=1
export MAHRUKH_TRUSTED_HOSTS=shop.your-owned-domain.example
export MAHRUKH_INSTANCE=/absolute/private/persistent/mahrukh-instance
.venv/bin/python run.py
```

Replace the sample domain/path with your actual deployment. Secure cookies will prevent sign-in over plain HTTP; keep these production settings out of local Termux HTTP testing. Configure TLS/HSTS, request-size limits and login/order rate limits at the edge. Do not blindly trust public `X-Forwarded-For` headers. The application has a conservative five-orders-per-source-address-per-ten-minutes limit; behind a proxy that does not pass a trusted client address all visitors share that limit. Configure an authenticated/trusted proxy arrangement appropriate to the host before public launch. No generic ProxyFix trust is enabled by this release.

Upload limits are six JPG/PNG/WebP photos, up to 4 MB each and 25 MB total request. Server checks image signatures, size and generated filenames, serves with fixed MIME types and nosniff, and rejects SVG/HTML uploads. It does not resize, decode/re-encode or remove EXIF metadata. Strip location/private metadata from photos yourself before uploading. Removed photo URLs do not immediately erase their files; review orphan uploads during maintenance. Actual product photos and accurate descriptions remain the seller’s responsibility.

### Backup / recovery

Stop only Mahrukh before backup so uploads/config cannot change during the snapshot; SQLite uses its backup API. The archive contains the admin password hash/secret, customer information and photographs. Protect it as private data, never commit or send it to a public host.

```bash
cd "$HOME/Mahrukh"
sv down mahrukh
.venv/bin/python maintenance.py backup
sv up mahrukh
```

If running in the foreground, stop it with Ctrl+C, run the backup, then restart with `.venv/bin/python run.py`; do not use `sv` unless you installed that service. Copy the archive under `instance/backups/` to your private encrypted backup destination. Regularly test restoring a trusted backup to a **new empty private instance directory**, run setup against that directory, verify catalog/order counts and photos, and only then switch the server to it. Preserve the secret if customer sessions should survive; rotate it if compromised. Do not extract untrusted archives.

### Retention

Choose and document a retention period after checking tax/accounting and dispute obligations. `maintenance.py redact --days 365` is a dry-run count of old, completed/cancelled records that are not still marked paid. Add `--apply` only after reviewing the count and policy. It redacts contact fields and session ownership while retaining amounts/items for records. Paid records are intentionally excluded for manual accounting review. It does not erase provider, courier, backup or filesystem-level copies; apply the same retention policy to those systems. Redaction is not a comprehensive legal-erasure or forensic deletion tool.

## Launch checks

- Test a real product on Android: image views, keyboard/focus, screen-reader labels, 200% zoom, quantity changes and WhatsApp handoff.
- Verify totals, delivery cities, free-delivery boundary, stock, a duplicate submission, cancellation and the private order view.
- Use provider test facilities for payment verification; never make a real charge merely to test a page.
- Review the business’s current registration, income/sales tax, e-commerce withholding, invoicing and province-specific consumer obligations with an adviser. The software does not determine applicability or implement FBR integration.
- Verify your hosting, backups, customer complaint handling and seller response process before advertising the live store.

## Primary references checked 30 September 2026

- [Safepay payment links](https://safepay.com.pk/payment-links): hosted invoices and dashboard setup.
- [PayPal country availability](https://www.paypal.com/webapps/mpp/country-worldwide) and [supported currencies](https://developer.paypal.com/docs/reports/reference/paypal-supported-currencies/): verify account/currency eligibility directly; these may change.
- [FBR registration guidance](https://fbr.gov.pk/categ/register-sales/51148/30846/%2071150), [Finance Acts](https://urdu.fbr.gov.pk/Categ/Finance-Acts/620) and [digital invoicing FAQs](https://fbr.gov.pk/faqs/173967/173969): current official starting points, not a claim that every rule applies to Mahrukh.
- [Ministry of Commerce FAQs](https://www.commerce.gov.pk/about-us/faqs/): e-commerce policy context; policy is not a substitute for applicable law.
- [W3C contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) and [target sizes](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).
- [Flask security guidance](https://flask.palletsprojects.com/en/stable/web-security/).

## Listing confidence and growth

Use **Seller studio → Shop health** to find incomplete buying information. Add included/excluded pieces, supplier-verified composition, lining/opacity, care and actual measurements. Garment chart chest/hip entries are flat one-side widths in inches, not body circumference. For unstitched pieces, supply each panel’s length and width with units. Optional occasion and fabric labels enable discovery filters; they do not prove origin, fibre content or handmade technique.

New orders save the product facts as reviewed at checkout. Changes to facts force a fresh quote review; editing a live product does not rewrite earlier orders. Customers can remove browser order access for a shared device; shop records remain for fulfilment and applicable retention obligations.

The shop-health paid total is manually recorded, includes delivery and is not audited revenue or profit. Use [RESEARCH-AND-GROWTH.md](RESEARCH-AND-GROWTH.md) for source-backed design decisions, customer interviews, merchandising, unit economics, metrics and the proposed 90-day plan. Legal/tax review remains specific to the actual business and current rules.

## Your own voice and personal shopping help

Add an optional welcome note/signature and actual support languages in Shop settings. Publish claims and response hours that match your service. These settings do not invent a founder biography or translate the site.

Saved favourites use the essential signed browser-session cookie in the live store, while the public demo uses tab session storage for fictional product IDs. Describe this convenience in your privacy/cookie notice. Customers can clear favourites independently of their orders; saving does not reserve inventory. WhatsApp product questions carry the product name/reference and selected size where supplied, with no delivery address or customer contact data added automatically. The customer opens the draft and decides whether to send it.
