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

The enhanced preview also includes a session-only sample bag, an illustrative contact page, and a read-only seller feature tour. Social/WhatsApp controls open explanatory dialogs; they never send a message or lead to checkout. Preview photos remain fictional AI-generated concepts. Twenty-eight HTML pages are built and checked: fourteen pages in each language. The cultural notebook and fabric/fit guide are shared with the Flask app. Filters use only the fictional fixture data; size charts and fabric dimensions are explicitly illustrative, not real product specifications.

## Boutique refinements

The saved-pieces page and heart controls keep only fictional product IDs in `sessionStorage`. The list can be cleared and never reserves stock. The photo viewer, active filter chips and contextual question preview use the same local scripts/styles as the live storefront where practical. WhatsApp question buttons show a draft-style explanation inside the demo; they never contact a seller. The homepage letter is labelled “Sample brand note”; the real seller supplies her own copy.

Product cards and the homepage now render shared templates directly. The build no longer rewrites template source strings, so future card refinements stay consistent across the live app and preview.

## English / اردو design review

Every preview page has an English and Urdu variant (`index.html` and `index.ur.html`, for example). The always-visible language bar identifies the active language, and ordinary links work without JavaScript. A local preference remembers an explicit choice when storage is available. JavaScript preserves the current page, query filters, sorting, fragment and selected product size. Switching from the sample bag reopens it. Existing demo bag and favourite session keys are retained; no customer details are stored. If storage is blocked, the bag and favourites work only on the current page and show a notice.

The build reuses the existing templates. `localize.py` translates only visible text and labelled attributes from the explicit `ur.json` message catalog; product IDs, monetary values, form values and size codes stay stable. Both languages search the English and Urdu sample names, descriptions and fabric text. Dynamic bag, favourite, measurement and photo messages use the same catalog. `check.py` fails for missing translations and mismatched placeholders. New shared-template copy needs an Urdu catalog entry before publishing.

Urdu uses `lang="ur"`, `dir="rtl"`, logical layout adjustments and the locally served Noto Nastaliq Urdu font with its SIL OFL license. Garment images and the Latin wordmark keep their orientation. Prices and size codes remain in Western digits/Latin characters. No new Flask runtime dependency or build framework is required.

**Review status:** Urdu is visibly marked as draft preview copy awaiting a fluent Urdu reader. It is not approved production translation. Physical Android Chrome, screen-reader pronunciation and fluent-language review still need seller-side checking. Ask a reviewer to compare the English and Urdu variants, especially fit terminology, care, order statuses and privacy wording, before removing the review notice.

This change is limited to the design preview. The Flask storefront remains English; seller-managed Urdu content, bilingual database search, checkout continuity and immutable order-language snapshots remain future implementation work. The seller tour says this explicitly. `journey.html` explains the existing live order workflow without a checkout form, order submission, payment link or customer-data field.

The seller-tour title is repaired. Fictional discount badges are removed, and the festive sample now lists its lehenga skirt among the included pieces. Actual product photographs, stock and orders in the live shop remain separate.
