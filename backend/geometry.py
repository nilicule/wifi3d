from __future__ import annotations
from typing import NamedTuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from backend.models import GenerateRequest
from backend.qr import encode_wifi_string, get_qr_matrix

PLATE_THICKNESS = 2.0
MODULE_HEIGHT = 1.0
PADDING = 4.0
TEXT_HEIGHT_MM = 8.0
TEXT_DPI = 10


class MeshPair(NamedTuple):
    plate_verts: np.ndarray
    plate_faces: np.ndarray
    mod_verts: np.ndarray
    mod_faces: np.ndarray


def _box_mesh(
    x0: float, y0: float, z0: float,
    x1: float, y1: float, z1: float,
) -> tuple[np.ndarray, np.ndarray]:
    verts = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ], dtype=np.float32)
    faces = np.array([
        [0, 2, 1], [0, 3, 2],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [2, 3, 7], [2, 7, 6],
        [1, 2, 6], [1, 6, 5],
        [3, 0, 4], [3, 4, 7],
    ], dtype=np.int32)
    return verts, faces


def _merge(parts: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    if not parts:
        empty_v = np.zeros((0, 3), dtype=np.float32)
        empty_f = np.zeros((0, 3), dtype=np.int32)
        return empty_v, empty_f
    all_verts, all_faces = [], []
    offset = 0
    for v, f in parts:
        all_verts.append(v)
        all_faces.append(f + offset)
        offset += len(v)
    return np.concatenate(all_verts), np.concatenate(all_faces)


def _rasterize_text(text: str, height_mm: float, width_mm: float) -> np.ndarray:
    h_px = int(height_mm * TEXT_DPI)
    w_px = int(width_mm * TEXT_DPI)
    img = Image.new("L", (w_px, h_px), color=255)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size=int(h_px * 0.75))
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = max(0, (w_px - text_w) // 2)
    y = max(0, (h_px - (bbox[3] - bbox[1])) // 2)
    draw.text((x, y), text, fill=0, font=font)
    arr = np.array(img)
    return arr < 128


def _text_to_boxes(
    bitmap: np.ndarray,
    x_offset: float, y_offset: float,
    z_base: float, z_top: float,
    pixel_size_mm: float,
) -> list[tuple[np.ndarray, np.ndarray]]:
    parts = []
    rows, cols = bitmap.shape
    for r in range(rows):
        for c in range(cols):
            if bitmap[r, c]:
                x0 = x_offset + c * pixel_size_mm
                x1 = x0 + pixel_size_mm
                y0 = y_offset + (rows - 1 - r) * pixel_size_mm
                y1 = y0 + pixel_size_mm
                parts.append(_box_mesh(x0, y0, z_base, x1, y1, z_top))
    return parts


_WIFI_ICON = [
    "0000000",
    "0111110",
    "1000001",
    "0011100",
    "0100010",
    "0001000",
    "0001000",
]


def _get_wifi_bitmap() -> np.ndarray:
    return np.array([[c == "1" for c in row] for row in _WIFI_ICON], dtype=bool)


def build_mesh(req: GenerateRequest) -> MeshPair:
    has_header = bool(req.header_text)
    has_sub = bool(req.sub_label)
    header_h = TEXT_HEIGHT_MM if has_header else 0.0
    sub_h = TEXT_HEIGHT_MM if has_sub else 0.0
    qr_size = float(req.qr_size_mm)
    plate_w = qr_size + 2 * PADDING
    plate_h = qr_size + 2 * PADDING + header_h + sub_h

    wifi_str = encode_wifi_string(req.ssid, req.password, req.auth_type, req.hidden)
    ec = "H" if req.wifi_icon else "M"
    matrix = get_qr_matrix(wifi_str, error_correction=ec)
    n_cells = len(matrix)
    cell_size = qr_size / n_cells

    qr_y_start = PADDING + sub_h
    qr_x_start = PADDING

    plate_parts = [_box_mesh(0, 0, 0, plate_w, plate_h, PLATE_THICKNESS)]

    if req.desk_stand_tab:
        tab_w = plate_w * 0.4
        tab_x = (plate_w - tab_w) / 2
        plate_parts.append(_box_mesh(tab_x, -6.0, 0, tab_x + tab_w, 0, PLATE_THICKNESS))

    plate_verts, plate_faces = _merge(plate_parts)

    mod_parts: list[tuple[np.ndarray, np.ndarray]] = []
    z_base = PLATE_THICKNESS
    z_top = PLATE_THICKNESS + MODULE_HEIGHT

    for row_idx, row in enumerate(matrix):
        for col_idx, dark in enumerate(row):
            if dark:
                x0 = qr_x_start + col_idx * cell_size
                y0 = qr_y_start + (n_cells - 1 - row_idx) * cell_size
                mod_parts.append(_box_mesh(x0, y0, z_base, x0 + cell_size, y0 + cell_size, z_top))

    if req.wifi_icon:
        icon_bm = _get_wifi_bitmap()
        icon_rows, icon_cols = icon_bm.shape
        icon_cell_count = max(5, int(n_cells * 0.18))
        icon_size_mm = icon_cell_count * cell_size
        icon_x = qr_x_start + (qr_size - icon_size_mm) / 2
        icon_y = qr_y_start + (qr_size - icon_size_mm) / 2
        icon_pixel_mm = icon_size_mm / max(icon_rows, icon_cols)
        mod_parts.extend(_text_to_boxes(icon_bm, icon_x, icon_y, z_base, z_top, icon_pixel_mm))

    if has_header:
        bm = _rasterize_text(req.header_text, TEXT_HEIGHT_MM, plate_w - 2 * PADDING)
        pixel_mm = (plate_w - 2 * PADDING) / bm.shape[1]
        header_y = qr_y_start + qr_size + PADDING * 0.5
        mod_parts.extend(_text_to_boxes(bm, PADDING, header_y, z_base, z_top, pixel_mm))

    if has_sub:
        bm = _rasterize_text(req.sub_label, sub_h * 0.8, plate_w - 2 * PADDING)
        pixel_mm = (plate_w - 2 * PADDING) / bm.shape[1]
        sub_y = PADDING * 0.5
        mod_parts.extend(_text_to_boxes(bm, PADDING, sub_y, z_base, z_top, pixel_mm))

    mod_verts, mod_faces = _merge(mod_parts)

    return MeshPair(
        plate_verts=plate_verts,
        plate_faces=plate_faces,
        mod_verts=mod_verts,
        mod_faces=mod_faces,
    )
