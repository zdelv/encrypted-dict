from pytest import fixture, raises
from encrypted_dict.enc_dict import EncryptedDict


PEPPER = b"\x97\xb6c\xa5t\xfe\xa6\xc1\x88~\x04\xd8\xbe\xd1\x1e\x00"
PASSWORD = "password"


def test_create_encrypted_dict():
    base = {}
    assert EncryptedDict(base, "password", pepper=PEPPER) is not None


@fixture()
def mock_empty_encdb():
    base = {}
    encdb = EncryptedDict(base, "password", pepper=PEPPER)
    return base, encdb


@fixture()
def mock_filled_encdb():
    base = {}
    encdb = EncryptedDict(base, "password", pepper=PEPPER)
    for i in range(1, 10):
        encdb[i.to_bytes()] = f"{i}" * i
    return base, encdb


MockTuple = tuple[dict, EncryptedDict]


def test_key_is_in_db(mock_empty_encdb: MockTuple):
    base, _ = mock_empty_encdb
    assert "__key__" in base


def test_salt_is_in_db(mock_empty_encdb: MockTuple):
    base, _ = mock_empty_encdb
    assert "__key__" in base


def test_pepper_not_in_db(mock_empty_encdb: MockTuple):
    base, _ = mock_empty_encdb
    assert "__pepper__" not in base


def test_cannot_get_key_salt(mock_empty_encdb: MockTuple):
    _, encdb = mock_empty_encdb
    with raises(ValueError):
        _ = encdb["__key__"]

    with raises(ValueError):
        _ = encdb["__salt__"]


def test_setitem_enc(mock_empty_encdb: MockTuple):
    base, encdb = mock_empty_encdb
    encdb["test"] = 10
    assert isinstance(base["test"], bytes)


def test_getitem_enc(mock_filled_encdb: MockTuple):
    _, encdb = mock_filled_encdb
    assert len(encdb) > 0
    assert encdb[(2).to_bytes()] == b"2" * 2


def test_iter_enc(mock_filled_encdb: MockTuple):
    _, encdb = mock_filled_encdb
    assert len(encdb) > 0
    assert [x for x in encdb]


def test_reopen_enc_dict(mock_empty_encdb: MockTuple):
    base, encdb = mock_empty_encdb
    encdb["test"] = 10

    new_encdb = EncryptedDict(base, PASSWORD, PEPPER)
    assert int.from_bytes(new_encdb["test"]) == 10
