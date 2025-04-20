# Encrypted Dict

A simple Python package for storing encrypted secrets in a local database file.
Uses Cryptography and the builtin `dbm.sqlite` module for storing data.

**DO NOT USE THIS FOR ANYTHING IMPORTANT**. This is a toy project, not a
production-grade application.

## Installation

```bash
curl https://raw.githubusercontent.com/zdelv/encrypted-dict/refs/heads/main/install.sh
chmod +x install.sh
./install.sh --install-dir <INSTALL LOCATION>
```

The `encdb` binary will be installed into `~/.local/bin/`. This directory must
exist.

## Usage

An `encdb` binary is used to create and interact with an encrypted database:

```
zdelv:~/code/encrypted-dict$ encdb
usage: encdb [-h] [--file FILE] [--password-stdin] {get,put,filter,delete} ...

positional arguments:
  {get,put,filter,delete}

options:
  -h, --help            show this help message and exit
  --file, -f FILE
  --password-stdin
```

`get` will fetch a value from the database. `put` will add a new key,
overwriting one if it already exists. `filter` accepts a regex string and can
filter across keys in the database, writing matches to stdout. `delete` will
delete a matching key-value from the database

## Encryption

The database is encrypted with two keys. One key is the data encryption key,
which does the actual encryption of values in the database. The other key is
derived from a user password, and is used to encrypt the data encryption key.
The encrpyted data encryption key is saved into the database. This structure
allows for users to change their password without needing to completely
re-encrypt the database.

Database keys are not encrypted. Values are encrypted using AES-GCM-SIV. The
key used for unlocking/locking the database is derived from the user password
using Argon2id. The derived key uses both salt and pepper to prevent rainbow
table attacks. All encrypted values use a salt appended to the front of the
encrypted value.
