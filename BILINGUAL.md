# English / اردو release review

Review branch: `feat/english-urdu-storefront`.

This document describes the bilingual release candidate. It does not certify final Urdu wording, Android compatibility or business/legal readiness. Fluent Urdu review, testing on the owner's Android/Termux device, merge and public preview publication remain pending. No human reviewer has yet been confirmed. The draft pull request is the review surface; creating it does not deploy the live shop or publish GitHub Pages.

## Customer behavior

- The header labels both choices **English** and **اردو**, marks the active choice and remains available on mobile. English is the default. The live shop reads `?lang=en` or `?lang=ur`, then remembers that choice in the separate `mahrukh_language` cookie for up to one year. The existing signed customer session is retained.
- Urdu uses the page language attribute, RTL layout and a self-hosted Noto Naskh Arabic font with its included license. Names and other missing seller translations show the original English with an **English** label. Mixed-direction prices, size codes and references remain readable without changing their values.
- The current page, submitted filters, cart and saved pieces survive switching. With JavaScript, a selected product size is carried in the language link. It is still the same stored size code, including `Custom Unstitched`.
- With JavaScript, switching away from an unfinished checkout asks whether to leave and clear the draft or cancel and keep editing. The draft is not saved in local/session storage or placed in a URL. A warning also protects other ordinary page departures. Submitted orders keep the existing privacy and duplicate-submission protections.
- Without JavaScript, both live language versions, server-side filters, cart, checkout and ordinary language links work. Choose the language before filling checkout or selecting an unsubmitted size: the interactive draft warning and size-link update need JavaScript. Browser restoration is not a substitute for submitting an order.
- Search checks the stored English and Urdu product text. Seller-provided Urdu fields are optional; the app does not translate or infer product facts automatically. Delivery-city values, prices, IDs, stock, references and size codes are shared between languages.
- General help, product questions and order-follow-up WhatsApp drafts use the selected language. The customer reviews and sends them in WhatsApp. This website sends no message itself.

## Seller workflow

The seller studio stays in English for this release. In each product editor, enter Urdu only for verified facts already represented accurately in the product record. Names, fabric descriptions, product descriptions, included/excluded pieces, composition, lining, fit, care, fabric dimensions, craft/origin and dispatch text have optional Urdu fields. Numeric measurements and stock remain shared.

**Shop settings** provides optional Urdu versions of the announcement, personal welcome, signature, support languages/hours, business contact address, tax disclosure, delivery estimate, transfer instructions and all four policies. The support-language setting describes languages offered by a person; it does not control the website selector. Keep each language's promises and meaning consistent. Blank Urdu fields use the English source; missing facts remain missing.

Saving a current shop or product translation updates the storefront. Existing order snapshots retain the English source and available Urdu text from submission, together with the purchase language. A customer can view that saved snapshot in either language without adopting later edits. Older English-only orders still render with clear English fallbacks. Seller status, tracking and verified payment updates continue through the existing order workflow.

Changing product/merchant translation content invalidates an already-reviewed checkout quote, just as changing the underlying product or policies does. The customer must review the current bag again. Switching the viewing language alone does not change prices, stock, quote hashes, checkout tokens or reservation rules. Payment links and transfers remain manually verified.

## Repeatable checks

From the repository root with its dependencies installed:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python preview/check.py
```

The tests exercise existing shopping, stock contention, duplicates, privacy, seller editing and payment rules alongside bilingual search, source preservation, quote consistency and translated receipts. The preview check builds the allowlisted static output and checks both languages. These commands operate on test fixtures/generated preview files; they are not production checkout tests and do not prove native Urdu wording or Android rendering quality. Use the final pull-request verification record for the actual run results rather than assuming a test count from this document.

The English preview is generated at `preview-site/index.html`; Urdu is generated at `preview-site/ur/index.html`. Its fictional images/products must stay labelled. It must not contain a functioning checkout, real customer form, live merchant messaging/payment link, database, uploads or private configuration. Publish only reviewed static output following [preview/README.md](preview/README.md); do not publish the repository root.

## Verification recorded for this candidate

On 1 October 2026, the isolated Python test environment passed **69 tests**, including the existing commerce regressions and the new language, snapshot, field-limit and translation-coverage checks. `preview/check.py` validated **26 English/Urdu pages**, equivalent language links, local font/assets and non-selling boundaries. All five customer JavaScript files passed `node --check`.

Visual browser checks could not run here: no local browser executable was available, its download did not return a usable archive, and the cloud browser blocked the isolated localhost fixture. No mobile screenshot, rendered overflow/200% zoom result, real screen-reader result or Android-device result is claimed. The manual checks below and fluent Urdu approval remain release gates.

## Isolated Termux review

The following makes a separate review checkout and empty private review database. It leaves an existing Mahrukh service, its database and other apps alone. The default checkout path below assumes the existing repository is `$HOME/Mahrukh`; use its actual location if different. Do not overwrite an existing `Mahrukh-urdu-review` folder.

After the review branch has been pushed:

```bash
cd "$HOME/Mahrukh"
git fetch origin feat/english-urdu-storefront
git worktree add --detach "$HOME/Mahrukh-urdu-review" origin/feat/english-urdu-storefront
cd "$HOME/Mahrukh-urdu-review"
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python preview/check.py
export MAHRUKH_INSTANCE="$HOME/.local/share/mahrukh-urdu-review"
.venv/bin/python setup.py
.venv/bin/python run.py
```

For this **review-only** setup, choose a new review admin password, leave WhatsApp blank, and choose an unused port such as `5051`. Its availability has not been checked on the phone; startup refuses an occupied port. If another app uses it, choose a different free port by rerunning setup with the same `MAHRUKH_INSTANCE`. Do not run the service installer for this review checkout. The normal Mahrukh installation keeps its default port **5050**.

Open `http://localhost:5051/?lang=en` and `http://localhost:5051/?lang=ur` if 5051 was chosen. Use a separate/private browser profile for review because browser cookies are shared across ports on the same hostname. Enter review-only products and non-customer test data; keep accepting orders off until intentionally exercising a test checkout. Stop this foreground review process with Ctrl-C in its own terminal. No command above stops or changes another app.

When approved changes are later deployed to the actual shop, first stop only Mahrukh, use the existing configured instance and run `.venv/bin/python maintenance.py backup`. Keep the backup private. Preserve its database, uploads, configuration and secret key. Follow the branch/merge-specific deployment instructions supplied with that release; this draft does not direct a production branch switch or replace an existing instance.

## Fluent Urdu review checklist

Assign a fluent Urdu reviewer and record their name, date and reviewed commit in the pull request before declaring the copy final. Do not treat automated catalogue checks as that review. Use realistic shop and product content supplied by the seller.

- Check natural, respectful Pakistani shopping language, spelling, punctuation and consistency. Keep the approved Latin **Mahrukh** wordmark unless the owner approves an Urdu brand spelling. Preserve “Timeless style · Everyday you.” in the brand treatment.
- Read navigation, filters, product facts, measurements, bag, checkout, status labels, help, policies, errors and accessible labels in context. Verify that the Urdu conveys each English action and limitation, especially order acceptance, availability and manual payment verification.
- Compare every seller translation with its source: garment composition, included pieces, dimensions, care, dispatch estimates, delivery costs, transfers, returns and privacy promises. Do not add quality, origin, fit, legal or delivery claims.
- Review English fallback badges and mixed-direction names, emails, phone numbers, `PKR`, comma-separated amounts, size codes, provider names and `MH-…` references. Verify that a missing translation is clear without making the page difficult to read.
- Review all three WhatsApp draft types before sending anything. Ensure numbers, size codes, names and order references remain exact, and no unwanted private details enter a draft.
- Record each wording change in its catalogue or seller field, then repeat affected checks in both languages. Record unresolved questions explicitly.

## Android, accessibility and regression checklist

The owner's phone has not been inspected. Record device, Android/browser version and reviewed commit when completing these checks.

- At narrow mobile widths and 200% text zoom, check Urdu glyph joining, line height, readable contrast, wrapping and absence of sideways scrolling or clipped controls. Test the header selector, filters, size options, bag drawer, product gallery and receipt.
- Use keyboard navigation and an available screen reader. Confirm focus visibility, active-language announcement, labels, validation focus, dialog close/Escape behavior and reading direction. Test the controls using touch as well.
- Switch language on a filtered collection, saved collection and product with a selected size; compare the current item/filter state. Add a bag item, switch twice and verify quantity, price and size. Check a fresh page retains the selected language.
- Start checkout, enter review-only delivery details, choose a payment method and accept the notice. Switch language and cancel: the draft must remain. Switch and continue: the warning must be explicit. Ensure no name, phone or address appears in the destination URL or browser storage.
- Submit a review order, retry the same submission and verify one order/stock reservation. Edit the seller's product/policy translations and verify the old receipt retains its saved content. Confirm another browser cannot open that receipt. Test older English-only receipts.
- Turn JavaScript off: browse, filter, save, add to bag and submit a review checkout in both languages. Choose the language before entering the draft. Re-enable JavaScript and check enhancements still work.
- Review the generated static English and Urdu pages separately: demo state may contain only fictional IDs/quantities and language preference. Confirm demonstration notices remain visible and no real order, payment or message can be submitted.

Record failures and fixes in the pull request. Merge, public preview publication and production rollout follow this review; they are not implied by completing the implementation.
