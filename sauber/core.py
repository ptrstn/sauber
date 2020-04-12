import hashlib
import pathlib

import pandas

from .settings import (
    MUSIC_FILE_EXTENSIONS,
    VIDEO_FILE_EXTENSIONS,
    IMAGE_FILE_EXTENSIONS,
    DOCUMENT_FILE_EXTENSIONS,
)
from .utils import extract_file_suffix, hash_file, get_size, get_modification_time

pandas.set_option("display.max_columns", None)
pandas.set_option("display.max_rows", None)
pandas.set_option("display.width", 1000)


class FileHashChecker:
    def __init__(self) -> None:
        super().__init__()
        self.file_hash_dict = {}
        self.hasher = hashlib.md5()
        self.df = pandas.DataFrame(
            columns=["file", "hash", "size", "time", "filename", "suffix"]
        )
        self.df.set_index("file", inplace=True)

    def iterate(self, file_path):
        files = [
            file_path
            for file_path in pathlib.Path(file_path).rglob("*")
            if file_path.is_file()
        ]
        df = pandas.DataFrame(files, columns=["file"])
        df.loc[:, "hash"] = df.apply(lambda row: hash_file(row.file), axis=1)
        df.loc[:, "size"] = df.apply(lambda row: get_size(row.file), axis=1)
        df.loc[:, "time"] = df.apply(
            lambda row: get_modification_time(row.file), axis=1
        )
        df.loc[:, "filename"] = df.apply(lambda row: row.file.name, axis=1)
        df.loc[:, "suffix"] = df.apply(
            lambda row: extract_file_suffix(row.file), axis=1
        )

        self.df = self.df.reset_index().append(df, sort=True).set_index("file")

    @property
    def duplicates(self):
        # self.df.sort_values(["hash", "size"], inplace=True)

        counts_df = (
            self.df.reset_index()
            .groupby(["hash", "size"])
            .size()
            .reset_index(name="counts")
        )

        duplicate_hash_sizes = counts_df[counts_df.counts > 1][
            ["hash", "size"]
        ].values.tolist()

        self.df.loc[:, "is_duplicate"] = self.df.set_index(["hash", "size"]).index.isin(
            duplicate_hash_sizes
        )

        return self.df[self.df.is_duplicate].sort_values(
            ["hash", "time", "file"], ascending=[True, True, False]
        )

    @property
    def duplicate_music(self):
        return self.duplicates[self.duplicates.suffix.isin(MUSIC_FILE_EXTENSIONS)]

    @property
    def duplicate_videos(self):
        return self.duplicates[self.duplicates.suffix.isin(VIDEO_FILE_EXTENSIONS)]

    @property
    def duplicate_images(self):
        return self.duplicates[self.duplicates.suffix.isin(IMAGE_FILE_EXTENSIONS)]

    @property
    def duplicate_documents(self):
        return self.duplicates[self.duplicates.suffix.isin(DOCUMENT_FILE_EXTENSIONS)]

    def export_data(self, file_path="data.csv"):
        self.df.to_csv(file_path)

    def import_data(self, file_path="data.csv"):
        imported_df = pandas.read_csv(file_path).set_index("file")

        # First update existing rows
        self.df.update(imported_df)

        # Then add remaining rows
        self.df.reset_index(inplace=True)
        imported_df.reset_index(inplace=True)
        self.df = self.df.append(imported_df, ignore_index=True).drop_duplicates()
        self.df.set_index("file", inplace=True)
