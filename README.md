[![Build Status](https://travis-ci.com/ptrstn/sauber.svg?branch=master)](https://travis-ci.com/ptrstn/sauber)
[![codecov](https://codecov.io/gh/ptrstn/sauber/branch/master/graph/badge.svg)](https://codecov.io/gh/ptrstn/sauber)

# Sauber

*Sauber bleiben*

A tool for cleaning up the file system. Detects duplicate files in your file system and tries to remove them intelligently.

## Installation

```bash
pip install git+https://github.com/ptrstn/sauber
```

## Usage

Under Linux you can simply run ```sauber```. On Windows you have to run ```python -m sauber``` instead.

### Help

```bash
sauber --help
```

```bash
usage: sauber [-h] [--debug {True,False}] [--duplicates] [--duplicate-files] [--duplicate-directories] [--duplicate-music] [--duplicate-videos] [--duplicate-images] [--duplicate-documents] path

Sauber - A tool for cleaning up the file system

positional arguments:
  path                     Search path for your files

optional arguments:
  -h, --help               show this help message and exit
  --debug {True,False}     Display debug messages

Show duplicates:
  --duplicates             Show all duplicates
  --duplicate-files        Show all duplicate files (without folders)
  --duplicate-directories  Show all duplicate directories
  --duplicate-music        Show all duplicate music
  --duplicate-videos       Show all duplicate videos
  --duplicate-images       Show all duplicate images
  --duplicate-documents    Show all duplicate documents
```

### Example

To find all duplicate music and image files in the ```test_data``` folder path, simply run the following command:

```bash
sauber --duplicate-music --duplicate-images test_data
```

```
███████╗ █████╗ ██╗   ██╗██████╗ ███████╗██████╗ 
██╔════╝██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗
███████╗███████║██║   ██║██████╔╝█████╗  ██████╔╝
╚════██║██╔══██║██║   ██║██╔══██╗██╔══╝  ██╔══██╗
███████║██║  ██║╚██████╔╝██████╔╝███████╗██║  ██║
╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝

Iterating through test_data
Adding files to internal dataframe...
Calculating md5 hashes...
Adding directories to internal dataframe...
Updating directory information...
Updating directory hashes...
Iteration 1...
Iteration 2...
Iteration 3...
Done iterating

============ Duplicate music ============
                                                                                hash is_file     size                       name parent_name
path                                                                                                                                        
test_data/files/partial duplicates/music/Right ...  399b26ccd1e02682657ea22a2608b59d    True  6977865  Right Here Beside You.mp3       music
test_data/files/duplicates/mp3/Right_Here_Besid...  399b26ccd1e02682657ea22a2608b59d    True  6977865  Right_Here_Beside_You.mp3         mp3
test_data/files/base/mp3/Right_Here_Beside_You.mp3  399b26ccd1e02682657ea22a2608b59d    True  6977865  Right_Here_Beside_You.mp3         mp3

============ Duplicate images ============
                                                                                hash is_file    size             name parent_name
path                                                                                                                             
test_data/files/partial duplicates/jpeg/clouds.jpg  12a372e938765c8eeb3a0ad36680e7d1    True   65139       clouds.jpg        jpeg
test_data/files/duplicates/jpeg/clouds.jpg          12a372e938765c8eeb3a0ad36680e7d1    True   65139       clouds.jpg        jpeg
test_data/files/base/jpeg/clouds.jpg                12a372e938765c8eeb3a0ad36680e7d1    True   65139       clouds.jpg        jpeg
test_data/files/partial duplicates/jpeg/curved_...  c8484bb3b898d4ce1bcae81b8be76a7e    True  102608  curved_road.jpg        jpeg
test_data/files/duplicates/jpeg/curved_road.jpg     c8484bb3b898d4ce1bcae81b8be76a7e    True  102608  curved_road.jpg        jpeg
test_data/files/base/jpeg/curved_road.jpg           c8484bb3b898d4ce1bcae81b8be76a7e    True  102608  curved_road.jpg        jpeg
```
