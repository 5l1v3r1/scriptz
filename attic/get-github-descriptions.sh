#!/bin/bash
#repos=$(cat README.md)
repos=$(grep github .gitmodules | cut -d" " -f 3)
for repo in $repos; do
	githubname=$(echo "$repo" | cut -d"/" -f4-5)
	shortname=$(echo "$githubname" | cut -d"/" -f2)
	git rm -rf "$shortname"
#	description=$(curl --silent "https://api.github.com/repos/$githubname" |grep "description" | cut -d"\"" -f 4)
#	echo "[$shortname]($repo) - $description"
#	sleep 62 #fucking rate limiting
done

#19h07
#TODO: git rm -r "$shortname"
#TODO: list other repos