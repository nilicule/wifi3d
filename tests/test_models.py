import pytest
from pydantic import ValidationError
from backend.models import GenerateRequest


def test_valid_request():
    req = GenerateRequest(ssid="MyNet", password="secret", auth_type="WPA")
    assert req.ssid == "MyNet"
    assert req.format == "stl"  # default


def test_invalid_auth_type():
    with pytest.raises(ValidationError):
        GenerateRequest(ssid="MyNet", password="x", auth_type="INVALID")


def test_ssid_too_long():
    with pytest.raises(ValidationError):
        GenerateRequest(ssid="A" * 33, password="x", auth_type="WPA")


def test_header_text_bad_chars():
    with pytest.raises(ValidationError):
        GenerateRequest(ssid="x", password="x", auth_type="WPA", header_text="Hello!")
