from enum import Enum

import departments


class FakeDept(Enum):
    ALLIER = ("3", "AUVERGNE", "3", "ALLIER")
    PARIS = ("11", "ILE_DE_FRANCE", "75", "PARIS")
    AIN = ("8", "RHONE_ALPES", "1", "AIN")


def test_ordered_departments_sorts_by_numeric_code():
    ordered = departments.ordered_departments(FakeDept)
    assert [d.value[2] for d in ordered] == ["1", "3", "75"]


def test_resolve_maps_codes_to_members_in_order():
    result = departments.resolve(FakeDept, [75, 1])
    assert [d.value[2] for d in result] == ["1", "75"]


def test_resolve_accepts_strings_and_ignores_unknown():
    result = departments.resolve(FakeDept, ["75", "999"])
    assert [d.value[2] for d in result] == ["75"]


def test_all_metro_returns_94_metropolitan_departments():
    result = departments.all_metro()
    codes = [d.value[2] for d in result]
    assert len(result) == 94
    assert "20" not in codes
    assert codes == sorted(codes, key=int)
