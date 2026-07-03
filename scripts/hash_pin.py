"""Create a BCrypt hash for a PIN/password.

Usage:
    python scripts/hash_pin.py 2580
"""
import argparse

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("password", help="PIN/password to hash")
    args = parser.parse_args()
    print(pwd_context.hash(args.password))


if __name__ == "__main__":
    main()
