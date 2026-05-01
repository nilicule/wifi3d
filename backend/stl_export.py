from __future__ import annotations
import io
import struct
import numpy as np
from backend.geometry import MeshPair


def export_stl(mesh: MeshPair) -> bytes:
    """Merge plate + modules into one binary STL blob."""
    v_offset = len(mesh.plate_verts)
    all_verts = np.concatenate([mesh.plate_verts, mesh.mod_verts])
    all_faces = np.concatenate([mesh.plate_faces, mesh.mod_faces + v_offset])

    buf = io.BytesIO()
    buf.write(b"WiFi3D STL export" + b" " * (80 - 17))
    n = len(all_faces)
    buf.write(struct.pack("<I", n))
    for face in all_faces:
        v0, v1, v2 = all_verts[face[0]], all_verts[face[1]], all_verts[face[2]]
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
