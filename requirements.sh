#!/bin/bash
main() {
	TARGET="$1"
	
	# Make sure the requirements target is valid
	if [[ "$TARGET" != "build" && "$TARGET" != "lense" ]]; then
		echo "ERROR: Requirements target must be 'build' or 'lense'"	
	fi
	
	# Build requirements
	if [ "$TARGET" == "build" ]; then
		sudo pip install -r requirements/build.txt
	fi
	
	# Lense requirements
	if [ "$TARGET" == "lense" ]; then
		sudo apt-get install $(grep -vE "^\s*#" requirements/lense-apt.txt  | tr "\n" " ")
		sudo pip install -r requirements/lense-pip.txt
	fi
}

main "$1"