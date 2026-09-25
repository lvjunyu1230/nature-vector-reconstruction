# Panel a v02 source manifest

## Construction

- **Bioicons** supplies the object geometry for the animal, bird, flower and image examples. The source vectors are embedded as native nested SVG geometry; source canvas plates, gradients and decorative border paths are removed.
- **Inkscape normalization** is applied in the build: fills are rebound to the panel palette, dark strokes are unified to `#263238`, and the objects remain vector-editable.
- **Tabler Icons** supplies only the small network/globe symbol next to “Unlabeled data reveal the data structure”.
- The panel contains no raster `<image>` elements, gradients or filters.

## Source files and licenses

| File | Source | License | Use in panel |
|---|---|---|---|
| `bio_mouse.svg` | Bioicons / Ben Murrell / Mouse | CC0 | animal class exemplar |
| `bio_avocet.svg` | Bioicons / EwaOz / avocet | CC0 | bird class exemplar |
| `bio_flower.svg` | Bioicons / Frédéric Bouché / Arabidopsis Flower | CC BY 4.0 | plant class exemplar; attribution required |
| `bio_image.svg` | Bioicons / OpenClipart / image | CC0 | image/landscape exemplar |
| `tabler_network.svg` | Tabler Icons / network | MIT | structural symbol |

Original source URLs are recorded in the source comparison manifest in `asset_probe/ASSET_SOURCES.md`. Preserve the CC BY 4.0 attribution for `bio_flower.svg` in any redistributed figure or supplement.
