from backend.qr import encode_wifi_string, get_qr_matrix


def test_encode_basic():
    s = encode_wifi_string("MyNet", "pass123", "WPA")
    assert s == "WIFI:T:WPA;S:MyNet;P:pass123;H:false;;"


def test_encode_nopass():
    s = encode_wifi_string("OpenNet", "", "nopass")
    assert s == "WIFI:T:nopass;S:OpenNet;P:;H:false;;"


def test_encode_hidden():
    s = encode_wifi_string("HiddenNet", "pw", "WPA", hidden=True)
    assert "H:true" in s


def test_encode_escaping():
    # special chars: \ ; , : " must be escaped with backslash
    s = encode_wifi_string('Net;"name', 'p:ass\\w"ord', "WPA")
    assert r"S:Net\;\"name" in s
    assert r"P:p\:ass\\w\"ord" in s


def test_qr_matrix_returns_bool_grid():
    matrix = get_qr_matrix("WIFI:T:WPA;S:test;P:pw;H:false;;", error_correction="M")
    assert isinstance(matrix, list)
    assert all(isinstance(row, list) for row in matrix)
    assert all(isinstance(cell, bool) for row in matrix for cell in row)
    size = len(matrix)
    assert size == len(matrix[0])
    assert size >= 21


def test_qr_matrix_high_correction():
    matrix = get_qr_matrix("WIFI:T:WPA;S:test;P:pw;H:false;;", error_correction="H")
    assert len(matrix) >= 21
