# Lense Development Package Builder

Helper package for building development version of Lense projects. Currently this has been tested on Ubuntu 14 LTS.

Builds the following:
 - Lense Common <https://github.com/djtaylor/lense-common>
 - Lense Client <https://github.com/djtaylor/lense-client>
 - Lense Engine <https://github.com/djtaylor/lense-engine>
 - Lense Portal <https://github.com/djtaylor/lense-portal>

### Dependencies

```sh
$ sudo apt-get install git python-pip build-essential devscripts
```

### Build Instructions

```sh
$ git clone https://github.com/djtaylor/lense-devbuild.git
$ cd lense-devbuild
$ sudo pip install -r build.requirements.txt
$ python build.py
```

### Lense All-in-One Installation

The following is a quick and dirty way to get an all-in-one Lense installation.

```sh
$ sudo apt-get install $(grep -vE "^\s*#" lense-apt.requirements.txt  | tr "\n" " ")
$ sudo pip install -r lense-pip.requirements.txt
$ sudo dpkg -i build/<version>/*
$ sudo lense-bootstrap
```