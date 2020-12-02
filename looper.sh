#!/bin/bash
DRIVE=/dev/dvd


while true; do
	python3 demand_disc.py ${DRIVE}
	TYPE=$?

	echo Type: ${TYPE}

	#DVD_LABEL=$(blkid -o value -s LABEL ${DRIVE})

	#if [ -z ${DVD_LABEL} ]; then
	#	echo "ERROR: No label detected."
	#	read -ep "Enter DVD Name: " DVD_LABEL
	#fi

	if ! dvdbackup --mirror --progress --error=a --output=output/ --input=${DRIVE}; then
		echo "ERROR: Read failed!"
	fi

	eject ${DRIVE}
done
