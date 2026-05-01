# WiFi3D — WiFi credentials, printed in 3D.

Generate 3D-printable WiFi QR code signs as STL (single-color) or 3MF (dual-color) files.

## Quickstart

```bash
uv sync
uv run uvicorn backend.main:app --reload
```

Then open http://localhost:8000.

## Privacy

Your WiFi credentials (SSID, password) are used solely to generate the QR code on the server.
They are **never logged, stored, persisted to disk, or transmitted to any third party.**
The server generates the file and discards all input immediately.
