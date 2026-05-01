# WiFi3D

Generate a dual-color 3D-printable sign from your WiFi credentials. Fill in your network name and password, preview the model in the browser, then export a print-ready file.

## Features

- QR code generated with high error-correction (H level) so it remains scannable even with a WiFi icon embedded in the centre
- Live 3D preview with orbit controls (drag to rotate, scroll to zoom)
- **Export STL** — ZIP containing `base.stl` and `modules.stl` as separate meshes, ready for dual-color slicing
- **Export 3MF** — single file with two objects and embedded material colors, import directly into Bambu Studio or PrusaSlicer and assign filaments per object
- Optional header text, sub-label, embedded WiFi icon, and desk-stand tab
- Dark / light mode

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python · FastAPI · uvicorn |
| Geometry | NumPy · Pillow · qrcode |
| Frontend | Vanilla JS · Tailwind CSS CDN · Three.js |

## Getting started

```bash
# Install dependencies (requires Python 3.13+)
uv sync

# Run the dev server
uv run uvicorn backend.main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000).

## Running tests

```bash
uv run pytest
```

## Privacy

Your WiFi credentials (SSID, password) are used solely to generate the QR code on the server.
They are **never logged, stored, persisted to disk, or transmitted to any third party.**
The server generates the file and discards all input immediately.

## Printing tips

- **Layer height**: 0.12–0.20 mm
- **Infill**: 100% for the QR modules (ensures solid raised squares)
- **Dual-color**: use the 3MF export and assign two filament slots in your slicer — one for the base plate, one for the raised modules
- **Filament swap (single extruder)**: use the STL export, slice as one object, and add a color-change pause at the layer where the modules begin (layer 11 at 0.2 mm, layer 17 at 0.12 mm)

## Credit

The idea for a 3D-printable WiFi sign was inspired by **[PrintMyWifi.com](https://printmywifi.com)**. This project was coded from scratch independently.

## License

MIT
