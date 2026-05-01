from __future__ import annotations
import io
import zipfile
import numpy as np
from backend.geometry import MeshPair


_CONTENT_TYPES = """\
<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>"""

_RELS = """\
<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0"
    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""


def _mesh_to_xml(verts: np.ndarray, faces: np.ndarray, obj_id: int, color: str) -> str:
    vertex_lines = "\n".join(
        f'          <vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}"/>'
        for v in verts
    )
    triangle_lines = "\n".join(
        f'          <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>'
        for f in faces
    )
    h = color.lstrip("#")
    color_attr = f"#{h}FF"
    return f"""  <object id="{obj_id}" type="model" p:color="{color_attr}">
    <mesh>
      <vertices>
{vertex_lines}
      </vertices>
      <triangles>
{triangle_lines}
      </triangles>
    </mesh>
  </object>"""


def export_3mf(mesh: MeshPair, base_color: str, module_color: str) -> bytes:
    plate_xml = _mesh_to_xml(mesh.plate_verts, mesh.plate_faces, 1, base_color)
    mod_xml = _mesh_to_xml(mesh.mod_verts, mesh.mod_faces, 2, module_color)

    model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter"
  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
  xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">
  <resources>
{plate_xml}
{mod_xml}
  </resources>
  <build>
    <item objectid="1"/>
    <item objectid="2"/>
  </build>
</model>"""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zf.writestr("_rels/.rels", _RELS)
        zf.writestr("3D/3dmodel.model", model_xml)
    return buf.getvalue()
