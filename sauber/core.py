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
    hash_text,
)

pandas.set_option("display.max_columns", None)
pandas.set_option("display.max_rows", None)
pandas.set_option("display.width", 1000)


class FileHashChecker:
    def __init__(self) -> None:
        super().__init__()
        self.df = initialize_file_hash_checker_dataframe()

    def iterate(self, file_path, debug=False):
        if debug:
            print(f"Iterating through {file_path}")

        all_files = [file_path for file_path in pathlib.Path(file_path).rglob("*")]
        files = [file_path for file_path in all_files if file_path.is_file()]
        directories = [file_path for file_path in all_files if file_path.is_dir()]

        self._add_files(files, debug)
        self._add_directories(directories, debug)
        self._update_duplicates()

        if debug:
            print(f"Done iterating")

    def _add_files(self, files, debug=False):
        if debug:
            print(f"Adding files to internal dataframe...")

        if not files:
            if debug:
                print(f"No files to add found.")
            return

        df = pandas.DataFrame(files, columns=["path"])

        if debug:
            print(f"Setting meta data...")

        set_size_column(df)
        set_name_column(df)
        set_parent_column(df)
        set_is_file_column(df)
        set_suffix_column(df)

        if debug:
            print(f"Calculating md5 hashes...")

        df.loc[:, "hash"] = df.apply(lambda row: hash_file(row.path), axis=1)

        self.df = self.df.reset_index().append(df, sort=False).set_index("path")

    def _add_directories(self, directories, debug=False):
        if debug:
            print(f"Adding directories to internal dataframe...")

        if not directories:
            if debug:
                print(f"No directories to add found.")
            return

        directories_df = pandas.DataFrame(directories, columns=["path"])

        set_size_column(directories_df)
        set_name_column(directories_df)
        set_parent_column(directories_df)
        set_is_dir_column(directories_df)

        self.df = self.df.append(directories_df.set_index("path"), sort=False)
        self._update_directories(debug)

    def _update_directories(self, debug=False):
        if debug:
            print(f"Updating directory information...")

        no_dir_counts_df = (
            self.files.groupby("parent").size().reset_index(name="number_no_dir_files")
        )
        no_dir_counts_df.rename(columns={"parent": "path"}, inplace=True)

        # Number of hashed files is number of actual files (no directories) in the beginning
        # After iterating through all directories it will be number of all files
        no_dir_counts_df["number_hashes"] = no_dir_counts_df.number_no_dir_files

        self.df.update(no_dir_counts_df.set_index("path"))

        all_file_counts_df = (
            self.df.groupby("parent").size().reset_index(name="number_files")
        )
        all_file_counts_df.rename(columns={"parent": "path"}, inplace=True)
        all_file_counts_df.loc[:, "name"] = all_file_counts_df.apply(
            lambda row: row.path.name, axis=1
        )

        self.df.update(all_file_counts_df.set_index("path"))

        self._handle_empty_folders(debug)

        self.df.sort_index(inplace=True)

        self._update_folders_hash(debug)

    def _handle_empty_folders(self, debug):
        self.df.loc[
            (self.df.is_dir == True) & (self.df.number_files.isnull()), "number_files"
        ] = 0
        self.df.loc[(self.df.number_files == 0), "number_hashes"] = 0
        self.df.loc[(self.df.number_files == 0), "number_no_dir_files"] = 0

    def _update_folders_hash(self, debug=False):
        # First the lowest level in path tree

        if debug:
            print(f"Updating directory hashes...")
            count = 1

        while True:
            if debug:
                print(f"Iteration {count}...")
                count += 1

            no_hash_folders_df = self.directories.loc[
                (
                    (self.directories.number_hashes == self.directories.number_files)
                    & (self.directories.hash.isnull())
                )
            ].copy()

            if len(no_hash_folders_df) == 0:
                break

            paths = no_hash_folders_df.index.to_list()
            files_df = self.df[self.df.parent.isin(paths)].copy()

            sum_df = (
                files_df.groupby("parent")[["hash"]]
                .sum()
                .reset_index()
                .rename(columns={"parent": "path"})
            )

            empty_directories_df = no_hash_folders_df[
                no_hash_folders_df.number_files == 0
            ].copy()
            empty_directories_df.loc[:, "hash"] = ""
            empty_directories_df = empty_directories_df[["hash"]]
            empty_directories_df.reset_index(inplace=True)

            sum_df = sum_df.append(empty_directories_df, sort=False)

            sum_df.loc[:, "hash"] = sum_df.apply(
                lambda row: hash_text(row.hash), axis=1
            )
            self.df.update(sum_df.set_index("path").copy())

            sum_df.loc[:, "parent"] = sum_df.apply(lambda row: row.path.parent, axis=1)
            parents_df = (
                sum_df.groupby("parent")
                .size()
                .reset_index(name="number_hashes")
                .rename(columns={"parent": "path"})
            )
            parents_to_update_list = parents_df.path.to_list()
            sum_df_to_update = self.df[self.df.index.isin(parents_to_update_list)][
                ["number_hashes"]
            ]
            result_df = sum_df_to_update.add(
                parents_df[
                    parents_df.path.isin(sum_df_to_update.index.to_list())
                ].set_index("path")
            )
            self.df.update(result_df)

    def _update_duplicates(self):
        counts_df = (
            self.df.reset_index()
            .groupby(["hash", "size", "is_file"])
            .size()
            .reset_index(name="counts")
        )

        duplicate_hash_sizes = counts_df[counts_df.counts > 1][
            ["hash", "size", "is_file"]
        ].values.tolist()

        self.df.loc[:, "is_duplicate"] = self.df.set_index(
            ["hash", "size", "is_file"]
        ).index.isin(duplicate_hash_sizes)

        self.df["is_duplicate"] = self.df["is_duplicate"].astype("bool")

    @property
    def files(self):
        return self.df.loc[self.df.is_file].copy()

    @property
    def directories(self):
        return self.df.loc[self.df.is_dir].copy()

    @property
    def duplicates(self):
        return self.df[self.df.is_duplicate].sort_values(
            ["hash", "size", "path"], ascending=[True, True, False]
        )

    @property
    def duplicate_files(self):
        return self.df[self.df.is_duplicate & self.df.is_file].sort_values(
            ["hash", "size", "path"], ascending=[True, True, False]
        )

    @property
    def duplicate_directories(self):
        return self.df[self.df.is_duplicate & self.df.is_dir].sort_values(
            ["hash", "size", "path"], ascending=[True, True, False]
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
        self.df = self.df.append(
            imported_df, ignore_index=True, sort=False
        ).drop_duplicates()
        self.df.set_index("path", inplace=True)


def set_size_column(dataframe):
    dataframe.loc[:, "size"] = dataframe.apply(lambda row: get_size(row.path), axis=1)


def set_name_column(dataframe):
    dataframe.loc[:, "name"] = dataframe.apply(lambda row: row.path.name, axis=1)


def set_parent_column(dataframe):
    dataframe.loc[:, "parent"] = dataframe.apply(lambda row: row.path.parent, axis=1)
    dataframe.loc[:, "parent_name"] = dataframe.apply(
        lambda row: row.parent.name, axis=1
    )


def _set_is_file_and_is_dir_column(dataframe, is_file):
    dataframe.loc[:, "is_file"] = is_file
    dataframe.loc[:, "is_dir"] = not is_file


def set_is_file_column(dataframe):
    _set_is_file_and_is_dir_column(dataframe, is_file=True)


def set_is_dir_column(dataframe):
    _set_is_file_and_is_dir_column(dataframe, is_file=False)


def set_suffix_column(dataframe):
    dataframe.loc[:, "suffix"] = dataframe.apply(
        lambda row: extract_file_suffix(row.path), axis=1
    )


def initialize_file_hash_checker_dataframe():
    df = pandas.DataFrame(
        columns=[
            "path",
            "hash",
            "size",
            "name",
            "parent",
            "parent_name",
            "suffix",
            "is_file",
            "is_dir",
            "is_duplicate",
            "number_hashes",
            "number_files",
            "number_no_dir_files",
        ]
    )
    df.is_duplicate = df.is_duplicate.astype("bool")
    df.set_index("path", inplace=True)

    return df
