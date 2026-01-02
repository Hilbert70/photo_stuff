# photo_stuff
This repo holds the code on a radxa zero w3 with emmc and serverside code to handle photos with exif information

TODO:
 - [ ] create a server side script to move the photos to
 - [ ] create a server config
'server' 

## Code formating and spacing

Show what `black` does

```
black -l 150  --diff --color do_shoebox.py
```

Make it do stuff and see how your code is in pylint, should be 10/10 ;-)

```
black -l 150  do_shoebox.py
pylint --max-line-length 150 do_shoebox.py 
```

## do_shoebox

The syntax of the command:

```
do_shoebox.py 
usage: do_shoebox [-h] -s SRCDIR -o OUTPUT [-l] [-t] [-d] [-i INFIX] [-p PREFIX] -e EXTENSION [-n]
do_shoebox: error: the following arguments are required: -s/--srcdir, -o/--output, -e/--extension
```

- `-s` is mandatory
- `-o` is mandatory
- `-e` is mandatory


The long help:
```
do_shoebox.py --help
usage: do_shoebox [-h] -s SRCDIR -o OUTPUT [-l] [-t] [-d] [-i INFIX] [-p PREFIX] -e EXTENSION [-n]

options:
  -h, --help            show this help message and exit
  -s, --srcdir SRCDIR   Source directory of containing the photos.
  -o, --output OUTPUT   Output directory where the photos should go.
  -l, --lower           Convert filename to lower case.
  -t, --time            Add time to the destination filename.
  -d, --date            Add date to the destination filename.
  -i, --infix INFIX     this string is added before the old filename.
  -p, --prefix PREFIX   this string is added before the date and/or time filename.
  -e, --extension EXTENSION
                        Check only files with this extension (case insensitive).
  -n, --dryrun          Do not change any file, it shows what is going to happen.
```


### Exaples of using do_shoubox.py

`-n` does a dry run, and does not change a thing and shows what it is going to do, note that it shows that it creates directories more than once, when running without the `-n` it only creates the directory once.

What the command below does:
 - `-l` converts the origanal filename to lower case
 - `-s ./shoe_box` it looks in the direcory `./shoe_box` recursivly
 - `-e jpg` checks for extension 'jpg', case insensitive
 - `-p dig` adds `dig` in front of the origianal filename
 - `-d` adds the date `yyyymmdd` after `dig`
 - `-t` adss the time `HHMMSS` afer the date (24h clock)
 - `-i .` adds a dot after the time
 - `-o /srv/media/photos` moves the file to this direcory.

So if the original filename was `DSC_12345.JPG` then the new name is going to be `dig20251229111009.dsc_12345.jpg` and the target direcory will be /srv/media/photos/2025/dec`.

If the destination file exist, it will check if both sha256 sums of the file are the same, if so, it add `.done` to the original file and no more. If the sums are not the same it will try to create a file with `.1` in it, so the new filename in the above example becomes `dig20251229111009.dsc_12345.1.jpg` it that one also exist it will make it .2 and so on.

```
do_shoebox.py -l -i . -p dig -t -d -s ./shoe_box -o /srv/media/photos -e jpg -n
do_shoebox.py -l -i . -p dig -t -d -s ./shoe_box -o /srv/media/photos -e jpg
```

Just move the files in a `yyyy/month` the following would work:

```
do_shoebox.py -l  -s ./todo -o /srv/media/photos/RAW -e nef
```


