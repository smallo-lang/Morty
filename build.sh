#!/usr/bin/bash

pyinstaller main.py --onefile

if [ -d dist ]; then
	# move to root folder
	sudo mv ./dist/main ./morty

	# cleanup
	rm -r dist build __pycache__
	rm *.spec
else
	echo "Installation failed"
fi

