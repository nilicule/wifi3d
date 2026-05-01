from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, field_validator
import re


class GenerateRequest(BaseModel):
    ssid: str = Field(..., min_length=1, max_length=32)
    password: str = Field(default="", max_length=63)
    auth_type: Literal["WPA", "WEP", "nopass"] = "WPA"
    hidden: bool = False
    qr_size_mm: int = Field(default=60, ge=30, le=150)
    base_color_hex: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    module_color_hex: str = Field(default="#000000", pattern=r"^#[0-9a-fA-F]{6}$")
    header_text: str = Field(default="", max_length=16)
    sub_label: str = Field(default="", max_length=16)
    wifi_icon: bool = True
    format: Literal["stl", "3mf"] = "stl"

    @field_validator("header_text", "sub_label")
    @classmethod
    def alphanumeric_and_spaces(cls, v: str) -> str:
        if v and not re.match(r"^[A-Za-z0-9 ]+$", v):
            raise ValueError("Only letters, numbers, and spaces allowed")
        return v.upper()


class PreviewMesh(BaseModel):
    plate_vertices: list[float]
    plate_faces: list[int]
    plate_color: str
    module_vertices: list[float]
    module_faces: list[int]
    module_color: str
