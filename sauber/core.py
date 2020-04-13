import hashlib
import pathlib

import pandas

from .settings import (
    MUSIC_FILE_EXTENSIONS,
    VIDEO_FILE_EXTENSIONS,
    IMAGE_FILE_EXTENSIONS,
    DOCUMENT_FILE_EXTENSIONS,
)
from .utils import (
    extract_file_suffix,
    hash_file,
    get_size,
    get_modification_time,
    get_number_of_files_in_directory,
    hash_text,
)

pandas.set_option("display.max_columns", None)
pandas.set_option("display.max_rows", None)
pandas.set_option("display.width", 1000)


class FileHashChecker:
    def __init__(self) -> None:
        super().__init__()
        self.file_hash_dict = {}
        self.hasher = hashlib.md5()
        self.df = pandas.DataFrame(
            columns=[
                "path",
                "hash",
                "size",
                "time",
                "name",
                "suffix",
                "is_file",
                "is_dir",
                "number_hashes",
                "number_files",
                "number_no_dir_files",
            ]
        )
        self.df.set_index("path", inplace=True)

    def iterate(self, file_path, debug=False):
        if debug:
            print(f"Iterating through {file_path}")

        all_files = [file_path for file_path in pathlib.Path(file_path).rglob("*")]
        files = [file_path for file_path in all_files if file_path.is_file()]
        directories = [file_path for file_path in all_files if file_path.is_dir()]

        if debug:
            print(f"Adding files to internal dataframe...")
        self._add_files(files, debug)

        if debug:
            print(f"Adding directories to internal dataframe...")
        self._add_directories(directories, debug)

    def _add_files(self, files, debug=False):
        df = pandas.DataFrame(files, columns=["path"])
        if debug:
            print(f"Calculating md5 hashes...")
        df.loc[:, "hash"] = df.apply(lambda row: hash_file(row.path), axis=1)
        df.loc[:, "size"] = df.apply(lambda row: get_size(row.path), axis=1)
        df.loc[:, "time"] = df.apply(
            lambda row: get_modification_time(row.path), axis=1
        )
        df.loc[:, "name"] = df.apply(lambda row: row.path.name, axis=1)
        df.loc[:, "parent"] = df.apply(lambda row: row.path.parent, axis=1)
        df.loc[:, "suffix"] = df.apply(
            lambda row: extract_file_suffix(row.path), axis=1
        )

        df.loc[:, "is_file"] = True
        df.loc[:, "is_dir"] = False

        self.df = self.df.reset_index().append(df, sort=True).set_index("path")

    def _add_directories(self, directories, debug=False):
        directories_df = pandas.DataFrame(directories, columns=["path"])
        directories_df.loc[:, "name"] = directories_df.apply(
            lambda row: row.path.name, axis=1
        )
        directories_df.loc[:, "parent"] = directories_df.apply(
            lambda row: row.path.parent, axis=1
        )
        directories_df.loc[:, "is_file"] = False
        directories_df.loc[:, "is_dir"] = True

        self.df = self.df.append(directories_df.set_index("path"))
        self._update_directories(debug)

    def _update_directories(self, debug=False):
        if debug:
            print(f"Updating directory hashes...")

        counts_df = (
            self.files.groupby("parent").size().reset_index(name="number_no_dir_files")
        )
        counts_df.rename(columns={"parent": "path"}, inplace=True)
        counts_df.loc[:, "number_files"] = counts_df.apply(
            lambda row: get_number_of_files_in_directory(row.path), axis=1
        )

        # Number of hashed files is number of actual files (no directories) in the beginning
        # After iterating through all directories it will (hopefully) be number of all files
        counts_df["number_hashes"] = counts_df.number_no_dir_files

        counts_df.loc[:, "name"] = counts_df.apply(lambda row: row.path.name, axis=1)
        self.df.update(counts_df.set_index("path"))

        self.df.loc[
            (self.df.is_dir == True) & (self.df.number_files.isnull()), "number_files"
        ] = 0
        self.df.loc[(self.df.number_files == 0), "number_hashes"] = 0
        self.df.loc[(self.df.number_files == 0), "number_no_dir_files"] = 0
        self.df.loc[(self.df.number_files == 0), "hash"] = ""
        self._update_folders_hash()

    def _update_folders_hash(self):
        # First the lowest level in path tree
        # TODO iterate levels stepwise higher
        no_hash_folders_df = self.directories.loc[
            (self.directories.number_hashes == self.directories.number_files)
            & (self.directories.hash.isnull())
        ].copy()
        paths = no_hash_folders_df.index.to_list()

        files_df = self.df.copy()
        files_df = files_df[files_df.parent.isin(paths)]

        sum_df = (
            files_df.groupby("parent")[["hash"]]
            .sum()
            .reset_index()
            .rename(columns={"parent": "path"})
        )
        sum_df.loc[:, "hash"] = sum_df.apply(lambda row: hash_text(row.hash), axis=1)
        sum_df.loc[:, "is_file"] = False
        sum_df.loc[:, "is_dir"] = True
        self.df.update(sum_df.set_index("path"))

    @property
    def files(self):
        return self.df.loc[self.df.is_file == True].copy()

    @property
    def directories(self):
        return self.df.loc[self.df.is_dir == True].copy()

    @property
    def duplicates(self):
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
            ["hash", "time", "path"], ascending=[True, True, False]
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
        imported_df = pandas.read_csv(file_path).set_index("path")

        # First update existing rows
        self.df.update(imported_df)

        # Then add remaining rows
        self.df.reset_index(inplace=True)
        imported_df.reset_index(inplace=True)
        self.df = self.df.append(imported_df, ignore_index=True).drop_duplicates()
        self.df.set_index("path", inplace=True)
