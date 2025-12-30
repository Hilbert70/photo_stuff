#!/bin/python3
"""This program can move and rename photo files to a destination directory,
based on the exif data in the photo."""

from datetime import datetime
from pathlib import Path
import hashlib
import argparse
import sys
import os
import shutil

import piexif

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def get_hash_from_file(img_file):
    """get sha256 sum of the given file"""
    with open(img_file, "rb") as f:
        buffer = f.read()  # read entire file as bytes
        img_hash = hashlib.sha256(buffer).hexdigest()
        f.close()
    return img_hash


def update_name(old_filename):
    """Find a free new name by adding a ".1" in front of the jpg or increment until one is free"""
    split_name = old_filename.split(".")
    len_split_name = len(split_name)
    try:
        num = str(int(split_name[len_split_name - 2]) + 1)
        replace = True
    except ValueError:
        # ugly but works, can not add anything to an string
        replace = False

    if len_split_name >= 2:
        if replace:
            split_name[len_split_name - 2] = num
        else:
            split_name.insert(len_split_name - 1, "1")
    else:
        print("Ignore this filename")

    new_name = ".".join(split_name)
    return new_name


def get_new_name(old_filename, old_hash):
    """Test if the new filename exists on the filesystem, if so get the next available name"""
    new_filename = update_name(old_filename)
    while Path(new_filename).is_file():
        # check the hash if it is the same exit, or throw something
        file_hash = get_hash_from_file(new_filename)
        if file_hash == old_hash:
            raise ValueError(f"Filenem {new_filename}")
        new_filename = update_name(new_filename)
    return new_filename


def handle_file(photo_file):
    """handle the photo_file, do a number of checks, if it checks out, move the file.
    The major check if the destination file exists, if it does, check the sha256 to see
    if it is the same, if it is, ignore the file ie add ".done"
    it not create a new file with *.<num>.jpg (when jpg is the extension."""
    file_name = str(photo_file.name)
    if args.lower:
        new_name = file_name.lower()
    else:
        new_name = file_name
    exif_dict = piexif.load(str(photo_file))
    date_obj = datetime.strptime(exif_dict["0th"][piexif.ImageIFD.DateTime].decode("latin-1"), "%Y:%m:%d %H:%M:%S")
    img_date = date_obj.strftime("%Y%m%d")
    img_year = date_obj.strftime("%Y")
    img_month = MONTHS[date_obj.month - 1]
    img_time = date_obj.strftime("%H%M%S")
    img_hash = 0
    img_hash = get_hash_from_file(str(photo_file))
    # Note the sequence, do not change
    if args.infix:
        new_name = args.infix + new_name
    if args.time:
        new_name = img_time + new_name
    if args.date:
        new_name = img_date + new_name
    if args.prefix:
        new_name = args.prefix + new_name
    # print(f" photo {p} {img_year}/{img_month}/{new_name} {img_hash}", end='')

    dest_file = Path(args.output + "/" + img_year + "/" + img_month + "/" + new_name)
    dest_dir = Path(args.output + "/" + img_year + "/" + img_month + "/")
    if not dest_dir.is_dir():
        # create dir
        print(f" mkdir -p {dest_dir}")
        if not args.dryrun:
            os.makedirs(dest_dir)
    print(f" photo {photo_file} {dest_file}", end="")
    if dest_file.is_file():
        dest_hash = get_hash_from_file(str(dest_file))
        if img_hash == dest_hash:
            # it is the same, rename origanal file with extention ".done"
            if not args.dryrun:
                os.rename(str(photo_file), str(photo_file) + ".done")
            print(f" {img_hash} exists")
        else:
            print(" same filename but different")

            # find a new filename with a number in the name
            try:
                new_name = get_new_name(str(dest_file), img_hash)
                print(new_name)
                if not args.dryrun:
                    shutil.move(str(photo_file), new_name)
            except ValueError as e:
                print(f"Found the same file: {str(e)} no action needed, original will be marked as done.")
                os.rename(str(photo_file), str(photo_file) + ".done")

    else:
        print(" new file")
        if not args.dryrun:
            shutil.move(str(photo_file), dest_file)


def do_dir(path):
    """Recusivily move through the directory tree in path: source directory."""
    print(path.name)
    for p in Path(path).iterdir():
        if p.is_file():
            split_name = str(p).split(".")
            len_split_name = len(split_name)
            if split_name[len_split_name - 1].lower() == args.extension.lower():
                handle_file(p)
        elif p.is_dir():
            do_dir(p)


parser = argparse.ArgumentParser("do_shoebox")
parser.add_argument("-s", "--srcdir", required=True, help="Source directory of containing the photos.", type=str)
parser.add_argument("-o", "--output", required=True, help="Output directory where the photos should go.", type=str)
parser.add_argument("-l", "--lower", help="Convert filename to lower case.", action="store_true")
parser.add_argument("-t", "--time", help="Add time to the destination filename.", action="store_true")
parser.add_argument("-d", "--date", help="Add date to the destination filename.", action="store_true")
parser.add_argument("-i", "--infix", help="this string is added before the old filename.", type=str)
parser.add_argument("-p", "--prefix", help="this string is added before the date and/or time filename.", type=str)
parser.add_argument("-e", "--extension", required=True, help="Check only files with this extension (case insensitive).", type=str)
parser.add_argument("-n", "--dryrun", help="Do not change any file, it shows what is going to happen.", action="store_true")


args = parser.parse_args()

srcdir = Path(args.srcdir)
if srcdir.is_dir():
    do_dir(srcdir)
else:
    print(f'srcdir "{args.srcdir}" should be a directory')
    sys.exit(1)
