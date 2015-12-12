#!/bin/bash

# Default workspace / installation directory
WORKSPACE=~/.lense_devtools
INSTALLER=$WORKSPACE/install

# Must be root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

# Make sure the install directory is free
if [ -d ${WORKSPACE} ] && [ $(ls -A ${WORKSPACE}) ]; then
    echo "ERROR: Workspace directory <${WORKSPACE}> already exists"
    echo "INFO: Change the WORKSPACE variable or clear the directory"
    exit 1
fi
mkdir -p $INSTALLER

# Get build packages
apt-get update
apt-get install build-essential devscripts git
	
# Github Python bindings
apt-get install python-pip
pip install GitPython

# ~/.lense_devtools/install
cd $INSTALLER

# Get the latest source code
git clone https://github.com/djtaylor/lense-devtools.git

# Tar the source directory
tar czf lense-devtools_0.1.1.orig.tar.gz lense-devtools

# ~/.lense_devtools/install/lense-devtools
cd lense-devtools

# Build the package without signing
debuild -uc -us

# ~/.lense_devtools/install
cd ..

# Install the package
dpkg -i lense-devtools_0.1.1-dev0_all.deb
which lense-devtools
