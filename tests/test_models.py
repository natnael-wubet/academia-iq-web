from apps.api.models import Author, Citation, Institution, Venue, Work


def test_model_attrs() -> None:
    assert Work.__tablename__ == "works"
    assert Author.__tablename__ == "authors"
    assert Citation.__tablename__ == "citations"
    assert Institution.__tablename__ == "institutions"
    assert Venue.__tablename__ == "venues"
