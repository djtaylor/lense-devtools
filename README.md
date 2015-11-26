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
$ sudo ./requirements.sh "build"
$ python build.py
```

### Lense All-in-One Installation

The following is a quick and dirty way to get an all-in-one Lense installation.

```sh
$ sudo ./requirements.sh "lense"
$ sudo dpkg -i build/<version>/*
$ sudo mysql_secure_installation
$ sudo lense-bootstrap
```