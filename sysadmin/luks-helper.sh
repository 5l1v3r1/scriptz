#!/bin/bash
#Description: helper script to create, mount and unmount LUKS container files
#License: MIT (http://opensource.org/licenses/MIT)
#Copyright: (c) 2014 nodiscc <nodiscc@gmail.com>
set -e

#Colors
G="\033[01;32m"
R="\033[01;31m"
NC="\033[00m"

#Usage
USAGE="$(basename $0) -a action -c container [-s size] [-m mountpoint] [-t]
	action: 	mount,unmount,create
	container:	LUKS container filename
	mountpoint:	where to mount the volume
	size:		size in MB for new volumes
	-t:		use a randomly generated 30-character password"


_CreateVolume() { #Create and format a LUKS volume
	if [ -z "$size" ]
		then echo -e "${R}No size defined for new volume.${NC}"; exit 1
	fi

	echo -e "${G}Writing $size MB zeroes to $container${NC}"
	dd if=/dev/zero bs=1M count="$size" of="$container"
	if [ "$TEMPKEY" != "1" ]
		then
			echo -e "${G}Formatting $container as LUKS volume${NC}"
			sudo cryptsetup luksFormat "$container"
		else
			pwgen=$(pwgen -s 30 -n 1)
			echo -e "${G}Formatting $container as LUKS volume, key is $pwgen${NC}"
			echo "$pwgen" | sudo cryptsetup luksFormat "$container"
	fi

	echo -e "${G}Creating ext4 partition inside LUKS volume${NC}"
	sudo cryptsetup luksOpen "$container" $(basename "$container")
	sudo mkfs.ext4 /dev/mapper/$(basename "$container")
	sudo cryptsetup luksClose $(basename "$container")
}


_MountVolume() { #Unlock and mount a LUKS volume
	if [ -z "$mountpoint" ]
		then echo -e "${R}No mountpoint specified${NC}"; exit 1
	elif [ ! -d "$mountpoint" ]
		then echo -e "${R}$mountpoint is not a directory.${NC}"; exit 1
	fi

	echo -e "${G}Mounting $container on $mountpoint${NC}".
	sudo cryptsetup luksOpen "$container" $(basename "$container")
	sudo mount /dev/mapper/$(basename "$container") "$mountpoint"
}


_UnmountVolume() { #Unmount and lock a LUKS volume
	mappername="/dev/mapper/$(basename $container)"
	echo -e "${G}Unmounting $mappername${NC}"
	sudo umount "$mappername"
	echo -e "${G}Closing $container LUKS volume${NC}"
	sudo cryptsetup luksClose $(basename "$container")
}

#Main loop
#Parse options
while getopts ":a:c:s:m:th" opt; do
	case $opt in
	a) action=$OPTARG
	;;
	c) container=$OPTARG
	;;
	s) size=$OPTARG
	;;
	m) mountpoint=$OPTARG
	;;
	t) TEMPKEY="1"
	;;
	h) echo "$USAGE"; exit 0
	;;
	*) echo -e "${R}Invalid option $opt${NC}"; echo "$USAGE"; exit 1
	;;
	esac
done


#Checks for mandatory options
if [ -z "$action" ]
	then echo -e "${R}No action specified${NC}"; echo "$USAGE"; exit 1
elif [ -z "$container" ]
	then echo -e "${R}No container specified${NC}"; echo "$USAGE"; exit 1
fi

#Select action
case $action in
	"create" ) _CreateVolume ;;
	"mount" ) _MountVolume ;;
	"unmount" ) _UnmountVolume ;;
	* ) echo -e "${R}$action is not a valid action"; exit 1 ;;
esac

