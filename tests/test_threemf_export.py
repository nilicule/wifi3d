import zipfile
import io
from backend.geometry import build_mesh
from backend.models import GenerateRequest
from backend.threemf_export import export_3mf


def test_3mf_is_valid_zip():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_3mf(mesh, base_color="#ffffff", module_color="#000000")
    assert isinstance(data, bytes)
    assert len(data) > 0
    zf = zipfile.ZipFile(io.BytesIO(data))
    names = zf.namelist()
    assert "[Content_Types].xml" in names
    assert "3D/3dmodel.model" in names


def test_3mf_contains_two_objects():
    req = GenerateRequest(ssid="TestNet", password="pw", auth_type="WPA")
    mesh = build_mesh(req)
    data = export_3mf(mesh, base_color="#ffffff", module_color="#000000")
    zf = zipfile.ZipFile(io.BytesIO(data))
    model_xml = zf.read("3D/3dmodel.model").decode()
    assert model_xml.count('<object ') == 2
