from getpass import getpass
from argparse import ArgumentParser
from encrypted_dict.encdb import open as dbopen
from os.path import expanduser
import sys


PEPPER = b"\xeb\xf2\x04\x14\xc7\x84\xcd\x8b\x8f\xc7\x059\x03\x1d!\x82"

DEFAULT = expanduser("~/.encdb")


def main():
    parser = ArgumentParser()
    parser.add_argument("--file", "-f", default=DEFAULT)
    parser.add_argument("--password-stdin", action="store_true")

    subparser = parser.add_subparsers(dest="subparser")

    get_parser = subparser.add_parser("get")
    get_parser.add_argument("key")

    put_parser = subparser.add_parser("put")
    put_parser.add_argument("key")
    put_parser.add_argument("value")

    filter_parser = subparser.add_parser("filter")
    filter_parser.add_argument("filter")

    delete_parser = subparser.add_parser("delete")
    delete_parser.add_argument("key")

    opts = parser.parse_args()

    if not getattr(opts, "subparser"):
        parser.print_help()
        return

    if opts.password_stdin:
        password = sys.stdin.read(-1).strip("\n")
    else:
        password = getpass()

    with dbopen(opts.file, password, PEPPER, flag="c") as db:
        match opts.subparser:
            case "get":
                print((db.get(opts.key) or b"").decode())
            case "put":
                db.put(opts.key, opts.value)
            case "filter":
                for k in db.filter(opts.filter.encode()):
                    print(k.decode())
            case "delete":
                db.delete(opts.key)
            case _:
                pass
