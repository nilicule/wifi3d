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


def _mesh_to_xml(
    verts: np.ndarray,
    faces: np.ndarray,
    obj_id: int,
    mat_group_id: int,
    pindex: int,
) -> str:
    vertex_lines = "\n".join(
        f'          <vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}"/>'
        for v in verts
    )
    triangle_lines = "\n".join(
        f'          <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>'
        for f in faces
    )
    return f"""  <object id="{obj_id}" type="model" pid="{mat_group_id}" pindex="{pindex}">
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
    base_hex = base_color.lstrip("#")
    mod_hex = module_color.lstrip("#")

    # Materials group (id=1): index 0 = base plate color, index 1 = module color.
    # m:basematerials is the 3MF Materials Extension; slicers use displaycolor for
    # per-object colour in the viewport and when assigning filaments.
    materials_xml = (
        f'  <m:basematerials id="1">\n'
        f'    <m:base name="Base" displaycolor="#{base_hex}"/>\n'
        f'    <m:base name="Modules" displaycolor="#{mod_hex}"/>\n'
        f'  </m:basematerials>'
    )

    plate_xml = _mesh_to_xml(mesh.plate_verts, mesh.plate_faces, 2, 1, 0)
    mod_xml = _mesh_to_xml(mesh.mod_verts, mesh.mod_faces, 3, 1, 1)

    model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter"
  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
  xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">
  <resources>
{materials_xml}
{plate_xml}
{mod_xml}
  </resources>
  <build>
    <item objectid="2"/>
    <item objectid="3"/>
  </build>
</model>"""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", _CONTENT_TYPES)
        zf.writestr("_rels/.rels", _RELS)
        zf.writestr("3D/3dmodel.model", model_xml)
    return buf.getvalue()
