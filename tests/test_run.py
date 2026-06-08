import run


def test_parse_departements_empty():
    assert run.parse_departements("") == []
    assert run.parse_departements(None) == []


def test_parse_departements_json_list():
    assert run.parse_departements("[75, 33]") == [75, 33]


def test_parse_departements_invalid_returns_empty():
    assert run.parse_departements("garbage") == []
