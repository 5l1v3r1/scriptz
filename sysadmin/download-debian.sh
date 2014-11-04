#!/bin/bash
#Description: securely download a debian netinst installer
#Thanks http://xmodulo.com/download-iso-image-bittorrent-command-line.html
#TODO: download live image

architecture="i386" #possible values amd64 armel armhf i386 ia64 kfreebsd-amd64 kfreebsd-i386 mips mipsel multi-arch powerpc s390 s390x source sparc

_main() {
	base_url="http://cdimage.debian.org/debian-cd/current/${architecture}/iso-cd/"
	sums_url="${baseurl}/SHA512SUMS"
	sums_sign_url="${baseurl}/SHA512SUMS.sign"
	iso_filename="debian-${debian_version}-${architecture}-netinst.iso"
	wget "$sums_url"
	wget "$sums_sign_url"
	gpg --verify SHA512SUMS.gpg SHA512SUMS
	wget "$base_url/$iso_filename"
	sha512sum -c <(grep "$iso_filename" SHA512SUMS)
}