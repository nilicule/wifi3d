from backend.geometry import build_mesh, MeshPair
from backend.models import GenerateRequest


def _req(**kwargs) -> GenerateRequest:
    defaults = dict(ssid="TestNet", password="pw", auth_type="WPA")
    defaults.update(kwargs)
    return GenerateRequest(**defaults)


def test_mesh_pair_has_arrays():
    mesh = build_mesh(_req())
    assert isinstance(mesh, MeshPair)
    assert mesh.plate_verts.shape[1] == 3
    assert mesh.plate_faces.shape[1] == 3
    assert mesh.mod_verts.shape[1] == 3
    assert mesh.mod_faces.shape[1] == 3


def test_plate_thickness_2mm():
    mesh = build_mesh(_req())
    z_min = mesh.plate_verts[:, 2].min()
    z_max = mesh.plate_verts[:, 2].max()
    assert abs(z_max - z_min - 2.0) < 0.01


def test_modules_raised_1mm_above_plate():
    mesh = build_mesh(_req())
    plate_top = mesh.plate_verts[:, 2].max()
    mod_top = mesh.mod_verts[:, 2].max()
    assert abs(mod_top - plate_top - 1.0) < 0.01


def test_nonzero_triangles():
    mesh = build_mesh(_req())
    assert len(mesh.plate_faces) > 0
    assert len(mesh.mod_faces) > 0


def test_with_header_text():
    mesh = build_mesh(_req(header_text="ROOM 641A"))
    mesh_plain = build_mesh(_req())
    plain_h = mesh_plain.plate_verts[:, 1].max() - mesh_plain.plate_verts[:, 1].min()
    text_h = mesh.plate_verts[:, 1].max() - mesh.plate_verts[:, 1].min()
    assert text_h > plain_h
