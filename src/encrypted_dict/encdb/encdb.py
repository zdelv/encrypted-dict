from collections.abc import Iterator
from typing import Self, Literal
from dbm.sqlite3 import _Database, open as dbopen
import re

from encrypted_dict.enc_dict import EncryptedDict


_filter = filter


class EncryptedDatabase:
    def __init__(self, base_db: _Database, password: str, pepper: bytes):
        self._db = base_db
        self._enc_db = EncryptedDict(base_db, password, pepper)

    def get(self, key: str) -> bytes | None:
        return self._enc_db.get(key)

    def put(self, key: str, value: str) -> None:
        self._enc_db[key] = value

    def filter(self, filter: str) -> Iterator[bytes]:
        return iter(_filter(lambda x: re.match(filter, x) is not None, self._enc_db))

    def delete(self, key: str) -> None:
        if key in self._enc_db:
            del self._enc_db[key]

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self._db.close()


def open(
    filename, password, pepper, /, flag: Literal["r", "w", "c", "n"] = "w", mode=0o666
) -> EncryptedDatabase:
    db = dbopen(filename, flag, mode)  # type: ignore
    return EncryptedDatabase(db, password, pepper)
