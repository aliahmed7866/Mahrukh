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

The GitHub connector used for repository writes does not expose Pages settings. Initial activation may require the repository owner to save this selection. Source files are on the `feat/pages-design-preview` branch; the real app remains on main.

## Regenerating

Rebuild after changing templates, styling or `preview/products.json`, check the result, then commit only the contents of `preview-site/` to `gh-pages`. Keep backend files and the private instance directory out of the published tree. Publishing is separate from Termux deployment.

## Sample imagery

The six `photos/*.webp` files were generated with the built-in image-generation tool and encoded as WebP without cropping or resizing. They are fictional concept images, not photos of real Mahrukh stock. All cards, detail pages and the footer label this clearly.

Prompt set: portrait 4:5 premium studio catalog photographs on warm ivory plaster backgrounds, soft daylight, full modest outfits: emerald embroidered shalwar kameez; dusty rose kameez with ivory trousers; ivory antique-gold peshwas; midnight-black abaya; ruby embroidered lehenga; and folded indigo/cream unstitched fabrics. No logos, text or watermarks. The unstitched image is a textile still life with no person. All images are for a non-commercial website design preview.
