from __future__ import annotations
import io
import struct
import zipfile
import numpy as np
from backend.geometry import MeshPair


def _mesh_to_stl(verts: np.ndarray, faces: np.ndarray, label: str) -> bytes:
    header = (label + " " * 80)[:80].encode()
    buf = io.BytesIO()
    buf.write(header)
    buf.write(struct.pack("<I", len(faces)))
    for face in faces:
        v0, v1, v2 = verts[face[0]], verts[face[1]], verts[face[2]]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        norm_len = np.linalg.norm(normal)
        if norm_len > 0:
            normal /= norm_len
        buf.write(struct.pack("<fff", *normal))
        buf.write(struct.pack("<fff", *v0))
        buf.write(struct.pack("<fff", *v1))
        buf.write(struct.pack("<fff", *v2))
        buf.write(struct.pack("<H", 0))
    return buf.getvalue()


def export_stl(mesh: MeshPair) -> bytes:
    """ZIP with base.stl + modules.stl for dual-color printing."""
    base_stl = _mesh_to_stl(mesh.plate_verts, mesh.plate_faces, "WiFi3D base")
    mod_stl = _mesh_to_stl(mesh.mod_verts, mesh.mod_faces, "WiFi3D modules")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("base.stl", base_stl)
        zf.writestr("modules.stl", mod_stl)
    return buf.getvalue()
