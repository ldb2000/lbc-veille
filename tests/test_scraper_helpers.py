from types import SimpleNamespace

import scraper


def test_is_price_drop_true_when_strictly_lower():
    assert scraper.is_price_drop(1000, 900) is True


def test_is_price_drop_false_when_equal_or_higher_or_none():
    assert scraper.is_price_drop(1000, 1000) is False
    assert scraper.is_price_drop(1000, 1200) is False
    assert scraper.is_price_drop(None, 900) is False
    assert scraper.is_price_drop(1000, None) is False


def test_extract_attr_finds_value():
    attrs = [SimpleNamespace(key="brand", value="Honda"),
             SimpleNamespace(key="model", value="CB500")]
    assert scraper.extract_attr(attrs, "brand") == "Honda"


def test_extract_attr_missing_returns_none():
    attrs = [SimpleNamespace(key="brand", value="Honda")]
    assert scraper.extract_attr(attrs, "model") is None
    assert scraper.extract_attr(None, "brand") is None


def test_build_ad_data_maps_core_fields():
    ad = SimpleNamespace(
        id=42,
        url="https://lbc/42",
        subject="Honda CB500",
        body="nickel",
        price=3000,
        attributes=[
            SimpleNamespace(key="brand", value="Honda"),
            SimpleNamespace(key="model", value="CB500"),
            SimpleNamespace(key="regdate", value="2018"),
            SimpleNamespace(key="mileage", value="12000"),
        ],
        location=SimpleNamespace(department_name="Gironde",
                                 zipcode="33000", city_label="Bordeaux"),
        images=["a.jpg"],
        is_pro=False,
        first_publication_date="2026-06-01T00:00:00Z",
    )
    data = scraper.build_ad_data(ad, "2026-06-08T00:00:00+00:00")
    assert data["lbc_id"] == 42
    assert data["titre"] == "Honda CB500"
    assert data["prix"] == 3000
    assert data["marque"] == "Honda"
    assert data["modele"] == "CB500"
    assert data["annee"] == 2018
    assert data["km"] == 12000
    assert data["ville"] == "Bordeaux"
    assert data["vendeur_type"] == "particulier"
    assert data["images_json"] == ["a.jpg"]
