from __future__ import annotations
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H


_ESCAPE_CHARS = '\\;,:"'


def _escape(value: str) -> str:
    result = []
    for ch in value:
        if ch in _ESCAPE_CHARS:
            result.append('\\')
        result.append(ch)
    return ''.join(result)


def encode_wifi_string(
    ssid: str,
    password: str,
    auth_type: str,
    hidden: bool = False,
) -> str:
    h = "true" if hidden else "false"
    return f"WIFI:T:{auth_type};S:{_escape(ssid)};P:{_escape(password)};H:{h};;"


_EC_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def get_qr_matrix(data: str, error_correction: str = "M") -> list[list[bool]]:
    ec = _EC_MAP[error_correction.upper()]
    qr = qrcode.QRCode(error_correction=ec, box_size=1, border=0)
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    return [[bool(cell) for cell in row] for row in matrix]
