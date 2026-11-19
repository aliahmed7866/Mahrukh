# Product categories and description builder

Research reviewed on 19 November 2026. This is a practical product-entry taxonomy, not a claim that regional clothing traditions have one fixed classification.

## Sources

| Source | What it informs |
| --- | --- |
| [Sapphire women](https://pk.sapphireonline.pk/collections/woman) | Separate shirts and bottoms; two-piece shirt/trouser and shirt/dupatta combinations; three-piece outfits; stitched and unstitched stock. |
| [Sapphire three-piece unstitched](https://pk.sapphireonline.pk/collections/three-piece-unstitched) | Unstitched fabric needs component lengths rather than sewn garment sizes; individual components may use different fabrics. |
| [Gul Ahmed kurtas](https://www.gulahmedshop.com/collections/mens-clothes-eastern-gents-kurta) and [men's basics](https://www.gulahmedshop.com/collections/mens-basic) | Kurtas sold separately or with pajamas; shalwar kameez sets, separate shalwars/pajamas and waistcoats. |
| [Sana Safinaz pishwas, gharara and dupatta](https://sanasafinaz.com/products/stitched-organza-pishwas-gharara-dupatta-ss25nur005p3) | Formal outfits have variable combinations: do not assume every set contains the same bottom or includes a dupatta. |
| [British Council Pakistan, Textile Legacies report](https://www.britishcouncil.pk/sites/default/files/textile_legacies_report.pdf), garment glossary | Garment terminology, including shalwar kameez, kurta pajama, gharara/sharara trousers, lehenga skirts, choli blouses and sherwani coats. |

## Product groups

| Group | Examples |
| --- | --- |
| Suits & sets | Shalwar kameez, kurta pajama, kurta shalwar, shirt/trousers, shirt/dupatta, gharara or sharara suit, lehenga choli, pishwas or anarkali with trousers. |
| Upperwear / tops | Kurta, kameez, kurti, angarkha, anarkali, pishwas and choli. |
| Lowerwear / bottoms | Shalwar, farshi shalwar, pajama, churidar, straight/cigarette/palazzo trousers, culottes, gharara, sharara and lehenga. |
| Waistcoats & outerwear | Waistcoat/koti, sherwani and achkan. |
| Dupattas & shawls | Dupatta, shawl/chadar and stole. |

Each group has a custom option. Garment type is independent of audience, fabric, colour, occasion and stitching. A single kurta or pajama is a separate garment, not a complete suit. For an unusual combination, use a custom set and select the actual components.

Named sets preselect and retain their named components. Dupattas, shawls and waistcoats are optional additions. The piece count follows the selected components, so a shalwar kameez starts as two pieces and becomes three only when the seller includes another piece. Gharara and sharara remain distinct choices. Component checkboxes describe types of included pieces, not stock quantities or duplicate garments.

## Description behaviour

- The shared product-builder module supplies browser choices, server validation, public category labels and deterministic English suggestions. No external generation service is called.
- All optional facts start blank. The builder does not infer fibre percentages, artisan work, comfort, authenticity, stock availability or washing instructions.
- Fabric notes can describe different materials for each part of an outfit. A commercial fabric label such as lawn or jacquard is not expanded to a fibre composition.
- Unstitched products omit sewn sizes, fit, sleeve and neckline details. Their selected parts are described as fabric; measurements accept lengths and widths with units.
- Suggestions can fill empty listing fields or replace English wording after an explicit checkbox. The last fill can be undone. Photos, price, availability and Urdu copy are preserved.
- Structured groups drive public collection filters, and garment names support English/Urdu search. Existing entries without structured data keep their previous category and copy.
- Add a similar piece creates a private copy with a new ID. The seller reviews its retained photo and details before publishing.

The optional product object is stored alongside each existing item in the D1 JSON document; no database migration or content reseed is required. Server validation rejects mismatched types, missing named components and invalid dropdown values. Product photos and publication gates continue to use the existing upload and publishing flows.
