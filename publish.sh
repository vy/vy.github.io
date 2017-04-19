#!/bin/bash

set -e

isEverythingComitted() {
	git status | grep -q "nothing to commit, working directory clean"
}

getLastCommitId() {
	git log -1 | head -n 1 | awk '{print $2}'
}

echo "*** Checking repository state... "
isEverythingComitted || {
	echo "error: there are still changes to be committed." >&2
	exit 1
}
lastCommitId=$(getLastCommitId)

echo "*** Switching to master..."
git checkout master

echo "*** Syncing output files..."
rsync --exclude-from rsync-excludes.txt -a --delete -v --force output/ .

echo "*** Adding all output files to the repository..."
git add .

echo "*** Committing changes..."
git commit -a -m "Copied changes from source/$lastCommitId."

echo "*** Pushing changes..."
git push -f origin master source

echo "*** Switching back to source..."
git checkout source
