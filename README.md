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

#### Installation
Does not exist in a PPA yet, so download and build:

[Default Installation Script](install.sh)

```sh
$ git clone https://github.com/djtaylor/lense-devtools
$ cd lense-devtools
$ sudo ./install.sh

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
