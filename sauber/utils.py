import datetime
import hashlib
import os
import pathlib

from .settings import CHUNK_SIZE


def extract_file_suffix(filename):
    return pathlib.Path(str(filename).lower()).suffix


def hash_file(file_path, chunk_size=CHUNK_SIZE):
    hasher = hashlib.md5()
    with open(file_path, "rb") as file:
        first_chunk = file.read(chunk_size)
        hasher.update(first_chunk)
        return hasher.hexdigest()


def hash_text(text):
    hasher = hashlib.md5()
    hasher.update(str.encode(text))
    return hasher.hexdigest()


def get_size(file_path):
    return os.path.getsize(file_path)


def extract_parent(path):
    return pathlib.Path(path).parent


def get_number_of_files_in_directory(path):
    return len(os.listdir(pathlib.Path(path)))
