#!/bin/bash
main() {
	TARGET="$1"
	
	# Make sure the requirements target is valid
	if [ "$TARGET" -ne "build" ] || [ "$TARGET" -ne "lense" ]; then
		echo "ERROR: Requirements target must be 'build' or 'lense'"	
	fi
	
	# Build requirements
	if [ "$TARGET" -eq "build" ]; then
		sudo pip install -r requirements/build.txt
	fi
	
	# Lense requirements
	if [ "$TARGET" -eq "lense" ]; then
		sudo apt-get install $(grep -vE "^\s*#" requirements/lense-apt.txt  | tr "\n" " ")
		sudo pip install -r requirements/lense-pip.txt
	fi
}

main