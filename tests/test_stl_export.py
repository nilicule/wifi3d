import struct
import pytest
from backend.geometry import build_mesh
from backend.models import GenerateRequest
from backend.stl_export import export_stl


def test_stl_bytes_nonzero():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_stl(mesh)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_stl_header():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_stl(mesh)
    assert len(data) > 84
    n_tris = struct.unpack_from("<I", data, 80)[0]
    assert n_tris > 0
