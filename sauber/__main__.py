import argparse
import pathlib

from sauber import __version__
from sauber.core import FileHashChecker

parser = argparse.ArgumentParser(
    description="Sauber - A tool for cleaning up the file system",
    formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=30),
)


def parse_arguments():
    parser.add_argument("path", help="Search path for your files")

    parser.add_argument(
        "--debug",
        help="Display debug messages",
        type=eval,
        choices=[True, False],
        default="True",
    )

    duplicates_group = parser.add_argument_group("Show duplicates")

    duplicates_group.add_argument(
        "--duplicates", help="Show all duplicates", action="store_true",
    )

    duplicates_group.add_argument(
        "--duplicate-files",
        help="Show all duplicate files (without folders)",
        action="store_true",
    )

    duplicates_group.add_argument(
        "--duplicate-directories",
        help="Show all duplicate directories",
        action="store_true",
    )

    duplicates_group.add_argument(
        "--duplicate-music", help="Show all duplicate music", action="store_true",
    )

    duplicates_group.add_argument(
        "--duplicate-videos", help="Show all duplicate videos", action="store_true",
    )

    duplicates_group.add_argument(
        "--duplicate-images", help="Show all duplicate images", action="store_true",
    )

    duplicates_group.add_argument(
        "--duplicate-documents",
        help="Show all duplicate documents",
        action="store_true",
    )

    return parser.parse_args()


# Text generated with http://patorjk.com/software/taag/#p=display&f=Doom&t=Sauber
sauber_text = """
███████╗ █████╗ ██╗   ██╗██████╗ ███████╗██████╗ 
██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗
███████╗███████║██║   ██║██████╔╝█████╗  ██████╔╝
╚════██║██╔══██║██║   ██║██╔══██╗██╔══╝  ██╔══██╗
███████║██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║
╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
"""


def print_sauber():
    try:
        print(sauber_text)
    except UnicodeEncodeError:
        print(f"sauber v{__version__}\n")


def print_print_usage_if_no_args(args):
    if not any(vars(args).values()):
        parser.print_usage()
        return


def handle_arguments(args, checker):
    args_dict = {
        key: value for (key, value) in vars(args).items() if key.startswith("duplicate")
    }

    for key, value in args_dict.items():
        if value:
            print(
                f'\n============ {(" ".join(key.split("_"))).capitalize()} ============'
            )
            df = getattr(checker, key)
            if len(df) > 0:
                print(df[["hash", "is_file", "size", "name", "parent_name"]])
            else:
                print("None found.")


def main():
    args = parse_arguments()

    print_sauber()
    print_print_usage_if_no_args(args)

    checker = FileHashChecker()
    checker.iterate(pathlib.Path(args.path), debug=args.debug)

    handle_arguments(args, checker)


if __name__ == "__main__":
    main()
