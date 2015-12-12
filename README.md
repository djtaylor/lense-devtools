# Lense Development Tools

Tools designed to assist in contributing to and building/installing/updating the various Lense projects.

 - Lense Common :: <https://github.com/djtaylor/lense-common>
 - Lense Client :: <https://github.com/djtaylor/lense-client>
 - Lense Engine :: <https://github.com/djtaylor/lense-engine>
 - Lense Portal :: <https://github.com/djtaylor/lense-portal>
 - Lense Socket :: <https://github.com/djtaylor/lense-socket>

#### To Do
    [ ] - Develop/commit functionality
    [ ] - Make Python 3 friendly
    [ ] - Further debugging
    [ ] - Automated CI worker

#### Dependencies

Lense development tools need the following packages installed:
```sh
$ sudo apt-get update
$ sudo apt-get install build-essential devscripts git
```

It is recommended to isntall newer versions of certain Python packages:
```sh
$ sudo apt-get install python-pip
$ sudo pip install GitPython
```

#### Installation
Does not exist in a PPA yet, so download and build:

```sh
$ cd ~
$ mkdir lense_devtools
$ cd lense_devtools
$ git clone -b <master> <https://github.com/djtaylor/lense-devtools.git>
$ tar czf lense-devtools_0.1.1.orig.tar.gz lense-devtools
$ cd lense-devtools
$ debuild -uc -us
$ cd ..
$ sudo dpkg -i lense-devtools_0.1.1-dev0_all.deb
$ which lense-devtools
```

    NOTE: Suitable only for local testing
    
#### Usage

Devtools currently support:

 - Automated package building from Github
 - Automatic local revisioning and package updates
 - Installation/update of current packages

```
# All packages
$ lense-devtools build

# Single or subset of packages
$ lense-devtools build --projects "lense-common,lense-client"

# Install update/packages
$ lense-devtools install

# Single or subset of packages
$ lense-devtools install --projects "lense-engine"
```
