from collections.abc import MutableMapping, Iterator
import os

from cryptography.hazmat.primitives.ciphers import aead
from cryptography.hazmat.primitives.kdf import argon2


def key_from_password(password: str, salt: bytes, pepper: bytes) -> bytes:
    kdf = argon2.Argon2id(
        salt=salt + pepper,
        length=32,
        iterations=1,
        lanes=4,
        memory_cost=1024 * 1024,
        ad=None,
        secret=None,
    )
    key = kdf.derive(password.encode())
    return key


class EncryptedDict(MutableMapping):
    def __init__(self, dict: MutableMapping, password: str, pepper: bytes) -> None:
        self._dict = dict
        self._pepper = pepper
        if "__key__" not in self._dict:
            self._aes = self._setup_db(password)
        else:
            self._aes = self._get_key_from_db(password)

    def _generate_db_key(self) -> bytes:
        return aead.AESGCMSIV.generate_key(256)

    def _setup_db(self, password: str) -> aead.AESGCMSIV:
        """
        Sets up an empty database by generating a new db encryption key, then
        encrypting it using a key derived from the user's password. The
        encrypted database key is saved into the database. The salt for the
        user's password is also saved.
        """
        salt = os.urandom(16)
        key = key_from_password(password, salt, self._pepper)

        db_key = self._generate_db_key()
        enc_key = self._raw_encrypt(aead.AESGCMSIV(key), db_key)
        self._dict["__key__"] = enc_key
        self._dict["__salt__"] = salt
        return aead.AESGCMSIV(db_key)

    def _get_key_from_db(self, password: str) -> aead.AESGCMSIV:
        """
        Given an already initialized db, fetch the db key and decrypt it using
        the user's password + salt.
        """
        salt = self._dict["__salt__"]
        enc_db_key = self._dict["__key__"]

        key = key_from_password(password, salt, self._pepper)
        db_key = self._raw_decrypt(aead.AESGCMSIV(key), enc_db_key)
        return aead.AESGCMSIV(db_key)

    def change_password(self, old_password: str, new_password: str) -> None:
        """
        Changes the password by re-encrypting the db key using the new
        password. Also replaces the db key salt.
        """
        old_salt = self._dict["__salt__"]
        enc_db_key = self._dict["__key__"]

        new_salt = os.urandom(16)
        old_key = key_from_password(old_password, old_salt, self._pepper)
        new_key = key_from_password(new_password, new_salt, self._pepper)

        db_key = self._raw_decrypt(aead.AESGCMSIV(old_key), enc_db_key)
        self._dict["__key__"] = self._raw_encrypt(aead.AESGCMSIV(new_key), db_key)
        self._dict["__salt__"] = new_salt

    @staticmethod
    def _raw_encrypt(aes: aead.AESGCMSIV, value: bytes) -> bytes:
        nonce = os.urandom(12)
        return nonce + aes.encrypt(nonce, value, b"")

    def _encrypt(self, value: bytes) -> bytes:
        return self._raw_encrypt(self._aes, value)

    @staticmethod
    def _raw_decrypt(aes: aead.AESGCMSIV, enc: bytes) -> bytes:
        nonce = enc[:12]
        return aes.decrypt(nonce, enc[12:], b"")

    def _decrypt(self, enc: bytes) -> bytes:
        return self._raw_decrypt(self._aes, enc)

    def __getitem__(self, key) -> bytes:
        if key in ["__key__", "__salt__"]:
            raise ValueError(f"Cannot get {key}")

        enc_item = self._dict[key]
        return self._decrypt(enc_item)

    def __setitem__(self, key, value) -> None:
        if key in ["__key__", "__salt__"]:
            raise ValueError(f"Cannot set {key}")

        if isinstance(value, int):
            value = value.to_bytes()
        elif isinstance(value, str):
            value = value.encode()
        if not isinstance(value, bytes):
            raise ValueError("Value must be an int, str, or bytes")

        enc_item = self._encrypt(value)  # type: ignore
        self._dict[key] = enc_item

    def __delitem__(self, key, /) -> None:
        if key in ["__key__", "__salt__"]:
            raise ValueError(f"Cannot delete {key}")
        del self._dict[key]

    def __iter__(self) -> Iterator[str]:
        return filter(lambda x: x not in [b"__key__", b"__salt__"], self._dict)

    def __len__(self) -> int:
        return len(self._dict) - 2
