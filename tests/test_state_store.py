import state_store


def test_load_cursor_missing_file_returns_zero(tmp_path):
    assert state_store.load_cursor(str(tmp_path / "nope.json")) == 0


def test_save_then_load_roundtrip(tmp_path):
    path = str(tmp_path / "state.json")
    state_store.save_cursor(path, 7)
    assert state_store.load_cursor(path) == 7


def test_load_cursor_corrupt_file_returns_zero(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("not json{")
    assert state_store.load_cursor(str(path)) == 0


def test_save_cursor_overwrites(tmp_path):
    path = str(tmp_path / "state.json")
    state_store.save_cursor(path, 3)
    state_store.save_cursor(path, 9)
    assert state_store.load_cursor(path) == 9
