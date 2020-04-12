import datetime
import hashlib
import os
import pathlib

from sauber.settings import CHUNK_SIZE


def extract_file_suffix(filename):
    return pathlib.Path(str(filename).lower()).suffix


def hash_file(file_path, chunk_size=CHUNK_SIZE):
    hasher = hashlib.md5()
    with open(file_path, "rb") as file:
        first_chunk = file.read(chunk_size)
        hasher.update(first_chunk)
        return hasher.hexdigest()


def get_size(file_path):
    return os.path.getsize(file_path)


def get_modification_time(file_path):
    return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))


def get_size2(file_path):
    return pathlib.Path(file_path).stat().st_size
