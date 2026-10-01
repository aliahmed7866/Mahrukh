# Public design preview

A static, non-selling demonstration for GitHub Pages. It uses six fictional products and AI-generated concept photographs. No real inventory, credentials, SQLite database, checkout, order form, analytics or customer information is included.

The warm Mahrukh styling, SVG brand portraits and navigation are reused from the app. Photo assets belong only to this preview; they do not populate the real product database.

## Build

From the repository root, with the app virtual environment active:

```bash
python preview/build.py
python preview/check.py
python -m http.server 8090 --directory preview-site
```

Visit http://localhost:8090. The output uses relative links, so it works beneath the GitHub Pages `/Mahrukh/` path. `preview-site/` is generated and ignored. Only that folder should be published, never the Flask repository root.

## Pages setup

The generated site is published to the `gh-pages` branch. In repository Settings → Pages, choose **Deploy from a branch**, then **gh-pages**, **/(root)**, and Save. The expected project URL is `https://aliahmed7866.github.io/Mahrukh/`; confirm the live URL in GitHub after deployment.

The GitHub connector used for repository writes does not expose Pages settings. Initial activation may require the repository owner to save this selection. The source for each preview revision is retained in the corresponding feature branch/pull request, then main after merging.

## Regenerating

Rebuild after changing templates, styling or `preview/products.json`, check the result, then commit only the contents of `preview-site/` to `gh-pages`. Keep backend files and the private instance directory out of the published tree. Publishing is separate from Termux deployment.

## Sample imagery

The six `photos/*.webp` files were generated with the built-in image-generation tool and encoded as WebP without cropping or resizing. They are fictional concept images, not photos of real Mahrukh stock. All cards, detail pages and the footer label this clearly.

Prompt set: portrait 4:5 premium studio catalog photographs on warm ivory plaster backgrounds, soft daylight, full modest outfits: emerald embroidered shalwar kameez; dusty rose kameez with ivory trousers; ivory antique-gold peshwas; midnight-black abaya; ruby embroidered lehenga; and folded indigo/cream unstitched fabrics. No logos, text or watermarks. The unstitched image is a textile still life with no person. All images are for a non-commercial website design preview.

The enhanced preview also includes a session-only sample bag, an illustrative contact page, and a read-only seller feature tour. Social/WhatsApp controls open explanatory dialogs; they never send a message or lead to checkout. Preview photos remain fictional AI-generated concepts. Thirteen HTML pages are built and checked. The cultural notebook and fabric/fit guide are shared with the Flask app. Filters use only the fictional fixture data; size charts and fabric dimensions are explicitly illustrative, not real product specifications.

## Boutique refinements

The saved-pieces page and heart controls keep only fictional product IDs in `sessionStorage`. The list can be cleared and never reserves stock. The photo viewer, active filter chips and contextual question preview use the same local scripts/styles as the live storefront where practical. WhatsApp question buttons show a draft-style explanation inside the demo; they never contact a seller. The homepage letter is labelled “Sample brand note”; the real seller supplies her own copy.

Product cards and the homepage now render shared templates directly. The build no longer rewrites template source strings, so future card refinements stay consistent across the live app and preview.

## English / اردو preview

The builder now emits the same 13 pages twice: English at `index.html` and Urdu at `ur/index.html` (26 HTML pages total). Every page has a labelled language selector linking to its equivalent page. Urdu pages use `lang="ur"`, right-to-left layout and the locally bundled Noto Naskh Arabic font; the font's open-source licence is copied with the assets. Assets and links stay relative for `/Mahrukh/` hosting.

Switching keeps query filters, the page fragment and selected sample size. The sample bag and saved pieces share their existing tab-session storage across languages. The browser remembers the chosen preview language; no customer details are stored. Search checks the fictional fixture's stored English and Urdu names, descriptions and fabric text. Prices, IDs, measurements and size codes are shared unchanged. Sample product Urdu fields are translations of the explicitly fictional fixture, not real product information.

`python preview/check.py` builds and validates both languages, all locale links, font/asset paths and the no-transactions boundary. `python -m unittest tests.test_preview_i18n` checks template translation coverage and stable fixture values. The Urdu copy is a draft and still needs review by a fluent Urdu speaker before publication. The source changes do not publish `gh-pages`; review the bilingual preview and pull request first.

## Latest feature tour (1 October 2026)

The preview now follows the shared English/Urdu implementation merged in PR #7. It builds 28 pages, including a bilingual read-only shopping-journey tour. The tour explains stock reservation, private order summaries, order statuses, manual payment verification and shared-device access. The seller tour includes optional Urdu product/settings/policy fields and immutable order-language snapshots. These are implemented Flask features; the static site cannot run them.

Urdu copy is visibly marked as awaiting fluent review. The preview is a review surface, not approval of production wording or an announcement that the shop is accepting orders. Physical Android and screen-reader checks remain necessary before treating the bilingual release as final.

Fictional discount badges have been removed and the festive sample correctly lists a lehenga skirt. Sample bags revalidate stored items against the public fixtures rather than trusting arbitrary stored prices/names. Clearing generated output before each build prevents old page/assets from leaking into publication. Only the allowlisted static output is published.
