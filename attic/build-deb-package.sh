#!/bin/bash
echo "rxtx DEB builder script"
ORIGINALUSER="$USER"
ls

#PACKAGE SELECTION
echo "Which package should I build? (ex. rxtx-icon-theme)"
read PACKAGETOBUILD
if [ ! -d ./$PACKAGETOBUILD/ ]
	then echo "Folder to build doesn't exist! Aborting"
		exit 1
	else true
fi

#WARN IF TARGET DEB EXISTS
if [ -f ./$PACKAGETOBUILD*.deb ]
	then echo "Target package is already present in this directory. Press any key to delete it."; read -n 1 -s; rm ./$PACKAGETOBUILD*.deb
	else true
fi


#CONTROL FILE
if [ ! -f ./$PACKAGETOBUILD/DEBIAN/control ]
	then mkdir -p ./$PACKAGETOBUILD/DEBIAN/
		cp example-control-file $PACKAGETOBUILD/DEBIAN/control
		echo "Control file didn't exist and was created. Please edit it!"
		read -n 1 -s
		nano ./$PACKAGETOBUILD/DEBIAN/control
	else echo "Please check the control file."
		nano ./$PACKAGETOBUILD/DEBIAN/control
fi

#INSTALLED-SIZE FIELD
echo "Calculating Installed-Size..."
SIZEFIELD=`du -akc ./$PACKAGETOBUILD/ | tail -n1 | awk -F" " '{print $1}'`
sed -i "s/^Installed-Size.*/Installed-Size: $SIZEFIELD/" ./$PACKAGETOBUILD/DEBIAN/control


#CALCULATE MD5
echo "Calculating md5sums..."
cd $PACKAGETOBUILD/
find usr/ bin/ etc/ -type f 2>/dev/null | xargs sudo md5sum > DEBIAN/md5sums
cd ..

#APPLY PERMISSIONS
echo "Applying file permissions..."
sudo dh_fixperms ./$PACKAGETOBUILD/
find ./$PACKAGETOBUILD/ -type d | xargs sudo chmod -R 755
find ./$PACKAGETOBUILD/ -type f | xargs sudo chmod -R 644
find ./$PACKAGETOBUILD/bin/ -type f | xargs sudo chmod -R 755

#BUILD PACKAGE
echo "Building DEB package..."
dpkg-deb --build $PACKAGETOBUILD/
dpkg-name $PACKAGETOBUILD.deb

#RESTORE PERMISSIONS
echo "Restoring file owner..."
sudo chown -R $ORIGINALUSER:$ORIGINALUSER $PACKAGETOBUILD/

#ADD BUILT- TO THE DIRECTORY NAME
mv ./$PACKAGETOBUILD/ ./BUILT-$PACKAGETOBUILD/

#MESSAGE
echo "Done."
