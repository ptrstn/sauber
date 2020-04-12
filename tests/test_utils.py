import pathlib

from sauber.utils import extract_file_suffix, hash_file, get_size


def test_hash_file():
    assert hash_file("test_data/files/base/pdf/document (original).pdf") == hash_file(
        "test_data/files/duplicates/a/very/deep/path/document (copy).pdf"
    )
    assert hash_file("test_data/files/base/pdf/document (original).pdf") == hash_file(
        "test_data/files/duplicates/pdf/document (original).pdf"
    )
    assert hash_file("test_data/files/base/pdf/document (original).pdf") != hash_file(
        "test_data/files/duplicates/pdf/document (slightly different).pdf"
    )

    assert hash_file("test_data/files/base/txt/lorem_ipsum_1000.txt") == hash_file(
        "test_data/files/duplicates/txt/lorem_ipsum_1000.txt"
    )
    assert hash_file("test_data/files/base/txt/lorem_ipsum_1000.txt") == hash_file(
        "test_data/files/partial duplicates/txt/lorem_ipsum_999.txt"
    ), "Almost identical file should have same hash in first bytes"


def test_get_size():
    assert get_size("test_data") == 4096, "Folder should always have 4096 Byte size"
    assert get_size("test_data/files/base/pdf/document (original).pdf") == 73250
    assert (
        get_size("test_data/files/duplicates/pdf/document (slightly different).pdf")
        == 73250
    )
    assert get_size("test_data/files/base/txt/lorem_ipsum_1000.txt") == 6058
    assert (
        get_size("test_data/files/partial duplicates/txt/lorem_ipsum_999.txt") == 6051
    )


def test_extract_file_ending():
    assert extract_file_suffix("song.mp3") == ".mp3"
    assert extract_file_suffix("SONG.MP3") == ".mp3"
    assert extract_file_suffix("another.song.m4a") == ".m4a"
    assert extract_file_suffix("whatami.mp3.mp4.jpeg.mov.wav") == ".wav"
    assert extract_file_suffix("i am with spaces .txt") == ".txt"
    assert extract_file_suffix("i/am/a/path.mkv") == ".mkv"
    assert extract_file_suffix(pathlib.Path("data", "music", "song.mp3")) == ".mp3"
    assert extract_file_suffix("test_data/files/base/empty_file") == ""
