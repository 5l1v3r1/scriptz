#!/bin/bash
#Description: restart tint2 and related systray program when it freezes
killall -9 tint2
tint2&
sleep 4
redshift -x&
nm-applet&
pnmixer&
winwrangler -t&
xpad&
synapse&
pidgin&
transmission-gtk&
