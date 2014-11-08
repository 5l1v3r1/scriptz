#!/bin/bash
#Description: securely download a debian netinst installer
#Thanks http://xmodulo.com/download-iso-image-bittorrent-command-line.html
#TODO: download live image
#TODO: download CD via bittorrent/transmission-cli, sysadmin/download-debian.sh
set -e

architecture="i386" #possible values amd64 armel armhf i386 ia64 kfreebsd-amd64 kfreebsd-i386 mips mipsel multi-arch powerpc s390 s390x source sparc
debian_version="7.7.0" #wheezy

_main() {
	base_url="http://cdimage.debian.org/debian-cd/current/${architecture}/iso-cd/"
	sums_url="${base_url}/SHA512SUMS"
	sums_sign_url="${base_url}/SHA512SUMS.sign"
	iso_filename="debian-${debian_version}-${architecture}-netinst.iso"
	wget "$sums_url"
	wget "$sums_sign_url"
	gpg --verify SHA512SUMS.sign SHA512SUMS
	wget "$base_url/$iso_filename"
	sha512sum -c <(grep "$iso_filename" SHA512SUMS)
}

_main