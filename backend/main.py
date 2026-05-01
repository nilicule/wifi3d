from __future__ import annotations
import re
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.models import GenerateRequest, PreviewMesh
from backend.geometry import build_mesh
from backend.stl_export import export_stl
from backend.threemf_export import export_3mf

app = FastAPI(title="WiFi3D")

_frontend = Path(__file__).parent.parent / "frontend"
if _frontend.exists() and any(_frontend.iterdir()):
    app.mount("/static", StaticFiles(directory=str(_frontend)), name="static")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(str(_frontend / "index.html"))


@app.post("/api/generate")
async def generate(req: GenerateRequest) -> Response:
    mesh = build_mesh(req)
    slug = re.sub(r"[^a-zA-Z0-9]", "-", req.ssid)[:20].strip("-")
    if req.format == "stl":
        data = export_stl(mesh)
        return Response(
            content=data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="wifi3d-{slug}.stl"'},
        )
    else:
        data = export_3mf(mesh, req.base_color_hex, req.module_color_hex)
        return Response(
            content=data,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="wifi3d-{slug}.3mf"'},
        )


@app.post("/api/preview", response_model=PreviewMesh)
async def preview(req: GenerateRequest) -> PreviewMesh:
    mesh = build_mesh(req)
    return PreviewMesh(
        plate_vertices=mesh.plate_verts.flatten().tolist(),
        plate_faces=mesh.plate_faces.flatten().tolist(),
        plate_color=req.base_color_hex,
        module_vertices=mesh.mod_verts.flatten().tolist(),
        module_faces=mesh.mod_faces.flatten().tolist(),
        module_color=req.module_color_hex,
    )
