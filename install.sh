#!/bin/bash

# Default workspace / installation directory / invoking user
WORKSPACE=~/.lense_devtools
INSTALLER=$WORKSPACE/install
USERNAME=`logname`
GIT_REPO='https://github.com/djtaylor/lense-devtools.git'
LOGFILE=$INSTALLER/install.log

# APT / PIP packages
APT_PACKAGES="build-essential debhelper devscripts git python-dev python-pip"
PIP_PACKAGES="GitPython feedback Django==1.8.9 python-keyczar socketIO_client"

# Shell colors
COLOR_RED=`tput setaf 1`
COLOR_GREEN=`tput setaf 2`
COLOR_DEF=`tput sgr0`

# Basic feedback wrapper
show_feedback() {
	TAG=$1
	MSG=$2
	[[ $TAG = 'ERROR' ]] && COLOR=${COLOR_RED} || COLOR=${COLOR_GREEN}
	echo -n '[' && echo -n ${COLOR} && echo -n ${TAG} | sed -e :a -e 's/^.\{1,10\}$/ & /;ta' && echo -n ${COLOR_DEF} && echo -n ']: '
	echo $MSG 1>&2
}

# Command wrapper
run_command() {
	CMD=$1
	EXPECTS=$2
	AS_USER=''
	
	# If running as a specific user
	if [ ! -z "$AS_USER" ]; then
		sudo su -c "eval $CMD &>> $LOGFILE" $AS_USER
		
	# Run as superuser
	else
		eval "$CMD &>> $LOGFILE"	
	fi
	
	# Check the return code
	if [ "$?" != "$EXPECTS" ]; then
		show_feedback "ERROR" "Command '$CMD' exited with code: $?, expected $EXPECTS"
		show_feedback "ERROR" "See logfile for details -> ${LOGFILE}"
		exit $?
	fi
}

# Must be root
if [ "$(id -u)" != "0" ]; then
	show_feedback "ERROR" "This script must be run as root"
    exit 1
fi

# Make sure the install directory is free
if [ -d ${WORKSPACE} ] && [ $(ls -A ${WORKSPACE}) ]; then
	show_feedback "ERROR" "Workspace directory <${WORKSPACE}> already exists"
    show_feedback "INFO" "Change the WORKSPACE variable or clear the directory"
    exit 1
fi
mkdir -p $INSTALLER

# Create the logfile
touch $LOGFILE

# Update the Apt cache
run_command 'apt-get update' '0'
show_feedback "SUCCESS" "APT -> Updated cache"

# Get build packages
run_command "apt-get install ${APT_PACKAGES} -y" '0'
show_feedback "SUCCESS" "APT -> Installed packages: ${APT_PACKAGES}"
	
# Github Python bindings
run_command "pip install ${PIP_PACKAGES}" '0'
show_feedback "SUCCESS" "PIP -> Installed modules: ${PIP_PACKAGES}"

# ~/.lense_devtools/install
cd $INSTALLER

# Get the latest source code
run_command "git clone ${GIT_REPO}" "0"
show_feedback "SUCCESS" "GIT -> Cloned Git repository ${GIT_REPO}"

# Tar the source directory
tar czf lense-devtools_0.1.1.orig.tar.gz lense-devtools

# ~/.lense_devtools/install/lense-devtools
cd lense-devtools

# Build the package without signing
run_command 'debuild -uc -us' '0' "$USERNAME"
show_feedback "SUCCESS" "DEBUILD -> Built package lense-devtools"

# ~/.lense_devtools/install
cd ..

# Install the package
run_command 'dpkg -i lense-devtools_0.1.1-dev0_all.deb' '0'
show_feedback "SUCCESS" "DPKG -> Installed package -> $(which lense-devtools)"

# Restore permissions
chown -R ${USERNAME}:${USERNAME} $WORKSPACE
