import io
import struct
import zipfile
from backend.geometry import build_mesh
from backend.models import GenerateRequest
from backend.stl_export import export_stl, _mesh_to_stl


def test_stl_zip_nonzero():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_stl(mesh)
    assert isinstance(data, bytes)
    assert len(data) > 0


def test_stl_zip_contains_two_stls():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_stl(mesh)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = zf.namelist()
    assert "base.stl" in names
    assert "modules.stl" in names


def test_stl_mesh_bytes_valid():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_stl(mesh)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        base_stl = zf.read("base.stl")
        mod_stl = zf.read("modules.stl")
    assert len(base_stl) > 84
    n_tris = struct.unpack_from("<I", base_stl, 80)[0]
    assert n_tris > 0
    assert len(mod_stl) > 84
    n_tris_mod = struct.unpack_from("<I", mod_stl, 80)[0]
    assert n_tris_mod > 0
