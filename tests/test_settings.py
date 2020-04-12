from sauber.settings import (
    MUSIC_FILE_EXTENSIONS,
    VIDEO_FILE_EXTENSIONS,
    DOCUMENT_FILE_EXTENSIONS,
    IMAGE_FILE_EXTENSIONS,
)


def test_music_file_types():
    for suffix in MUSIC_FILE_EXTENSIONS:
        assert suffix.startswith(".")


def test_video_file_types():
    for suffix in VIDEO_FILE_EXTENSIONS:
        assert suffix.startswith(".")


def test_image_file_types():
    for suffix in IMAGE_FILE_EXTENSIONS:
        assert suffix.startswith(".")


def test_document_file_types():
    for suffix in DOCUMENT_FILE_EXTENSIONS:
        assert suffix.startswith(".")
