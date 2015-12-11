# Lense Development Tools

Tools used to assist developers and contributors to the Lense project. Features currently include:

 - Local .deb package builder
 - Automated revisioning

### Builds

 - Lense Common <https://github.com/djtaylor/lense-common>
 - Lense Client <https://github.com/djtaylor/lense-client>
 - Lense Engine <https://github.com/djtaylor/lense-engine>
 - Lense Portal <https://github.com/djtaylor/lense-portal>

### Developers

Base configured to use Lense repos as a source, but can be customized for forks and branches via JSON.

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
