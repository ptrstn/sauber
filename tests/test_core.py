import pathlib

from sauber.core import FileHashChecker


class TestFileHashChecker:
    def test_add(self):
        checker = FileHashChecker()
        checker.add("test_data/files/base/jpeg/asphalt.jpg")
        assert len(checker.df) == 1
        checker.add("test_data/files/base/jpeg/clouds.jpg")
        assert len(checker.df) == 2
        checker.add("test_data/files/base/jpeg/curved_road.jpg")
        checker.add("test_data/files/base/empty_file")
        checker.add("test_data/files/base/mp3/Right_Here_Beside_You.mp3")
        assert len(checker.df) == 5

    def test_iterate(self):
        checker = FileHashChecker()
        checker.iterate("test_data/files/")
        assert len(checker.df) == 21

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
        filenames = set(checker.duplicate_documents.filename.unique())
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
        checker.export_data()
        assert len(checker.df) == 21

        checker2 = FileHashChecker()
        assert len(checker2.df) == 0

        checker2.import_data()
        assert len(checker2.df) == len(checker.df)

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

        actual_duplicates = set(checker.duplicates.index.to_list())
        assert actual_duplicates == expected_duplicates
        assert actual_duplicates - expected_no_duplicates == actual_duplicates
