import pathlib

import pandas

from sauber.core import FileHashChecker


class TestFileHashChecker:
    def test_iterate(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")
        assert len(checker.files) == 21

    def test_duplicate_music(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")

        assert (
            pathlib.Path("test_data/files/base/mp3/Right_Here_Beside_You.mp3")
            in checker.duplicate_music.index
        )
        assert (
            pathlib.Path("test_data/files/duplicates/mp3/Right_Here_Beside_You.mp3")
            in checker.duplicate_music.index
        )
        assert (
            pathlib.Path(
                "test_data/files/partial duplicates/music/Right Here Beside You.mp3"
            )
            in checker.duplicate_music.index
        )
        assert len(checker.duplicate_music.index) == 3, "Only 3 songs in test data"

    def test_duplicate_videos(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")

        assert len(checker.duplicate_videos) == 0

    def test_duplicate_images(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")

        assert len(checker.duplicate_images) == 2 * 3

    def test_duplicate_documents(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")
        filenames = set(checker.duplicate_documents.name.unique())
        assert filenames == {
            "document (original).pdf",
            "document (copy).pdf",
            "document (recreated).pdf",
            "lorem_ipsum_1000.txt",
        }

        assert "document (slightly different).pdf" not in filenames
        assert len(checker.duplicate_documents) == 6

    def test_export_import_data(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")
        checker.export_data("test_data/data.csv")
        assert len(checker.files) == 21

        checker2 = FileHashChecker()
        assert len(checker2.files) == 0

        checker2.import_data("test_data/data.csv")
        assert len(checker2.files) == len(checker.files)

    def test_duplicates(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")

        expected_duplicates = [
            "test_data/files/base/jpeg/clouds.jpg",
            "test_data/files/base/jpeg/curved_road.jpg",
            "test_data/files/base/pdf/document (original).pdf",
            "test_data/files/base/txt/lorem_ipsum_1000.txt",
            "test_data/files/base/mp3/Right_Here_Beside_You.mp3",
            "test_data/files/duplicates/a/very/deep/path/document (copy).pdf",
            "test_data/files/duplicates/jpeg/clouds.jpg",
            "test_data/files/duplicates/jpeg/curved_road.jpg",
            "test_data/files/duplicates/pdf/document (original).pdf",
            "test_data/files/duplicates/pdf/document (recreated).pdf",
            "test_data/files/duplicates/txt/lorem_ipsum_1000.txt",
            "test_data/files/duplicates/mp3/Right_Here_Beside_You.mp3",
            "test_data/files/partial duplicates/jpeg/clouds.jpg",
            "test_data/files/partial duplicates/jpeg/curved_road.jpg",
            "test_data/files/partial duplicates/a new folder/unique_file",
            "test_data/files/partial duplicates/music/Right Here Beside You.mp3",
            "test_data/files/base/empty_file",
        ]

        expected_no_duplicates = [
            "test_data/files/base/jpeg/asphalt.jpg",
            "test_data/files/partial duplicates/jpeg/roses.jpg",
            "test_data/files/duplicates/pdf/document (slightly different).pdf",
            "test_data/files/partial duplicates/txt/lorem_ipsum_999.txt",
        ]

        expected_duplicates = {pathlib.Path(p) for p in expected_duplicates}
        expected_no_duplicates = {pathlib.Path(p) for p in expected_no_duplicates}

        for file in expected_no_duplicates:
            assert file.exists()

        actual_duplicates = set(checker.duplicate_files.index.to_list())
        assert actual_duplicates == expected_duplicates
        assert actual_duplicates - expected_no_duplicates == actual_duplicates

    def test_duplicate_folders(self):
        checker = FileHashChecker()

        assert checker.directories is not None
        assert checker.directories.empty

        checker.iterate("test_data/files2/")
        folder_paths = checker.directories.index.to_list()

        assert pathlib.Path("test_data/files2/A") in folder_paths
        assert pathlib.Path("test_data/files2/Subfolder") in folder_paths
        assert pathlib.Path("test_data/files2/Subfolder/A") in folder_paths
        assert len(checker.directories) == 8

        assert (
            checker.df.loc[
                pathlib.Path("test_data/files2/Subfolder"), "number_no_dir_files"
            ]
            == 1
        ), "Should only count the actual files"
        assert (
            checker.directories.loc[
                pathlib.Path("test_data/files2/Subfolder"), "number_files"
            ]
            == 3
        ), "Should contain 2 folders and 1 file"

        assert (
            checker.directories.loc[
                pathlib.Path("test_data/files2/A"), "number_no_dir_files"
            ]
            == 3
        )
        assert (
            checker.directories.loc[pathlib.Path("test_data/files2/A"), "number_files"]
            == 3
        )

        assert (
            len(
                checker.directories[
                    checker.directories.number_no_dir_files
                    != checker.directories.number_files
                ]
            )
            == 1
        ), "Only 1 path with subfolders"

    def test_directory_hashes(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files2/")

        assert (
            checker.df.loc[pathlib.Path("test_data/files2/A"), "hash"]
            == "a8f963f199e83660cd8ff21ac94d440a"
        )
        assert (
            checker.df.loc[pathlib.Path("test_data/files2/Subfolder/A"), "hash"]
            == checker.df.loc[pathlib.Path("test_data/files2/A"), "hash"]
        ), "Excact directory copies should have exact hash"

        assert (
            checker.df.loc[pathlib.Path("test_data/files2/Subfolder/Empty"), "hash"]
            == "d41d8cd98f00b204e9800998ecf8427e"
        ), "Empty directories should have empty hash"

        assert not pandas.isnull(
            checker.df.loc[pathlib.Path("test_data/files2/Subfolder"), "hash"]
        )

    def test_duplicate_directories(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files2/")

        assert set(checker.duplicate_directories.index.to_list()) == {
            pathlib.Path("test_data/files2/A"),
            pathlib.Path("test_data/files2/A_copy"),
            pathlib.Path("test_data/files2/Subfolder/A"),
        }

    def test_no_folders(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files2/A")

    def test_no_files(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files2/Empty")
