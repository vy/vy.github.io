#!/bin/bash

set -e

isEverythingComitted() {
	git status | grep -q "nothing to commit, working directory clean"
}

getLastCommitId() {
	git log -1 | head -n 1 | awk '{print $2}'
}

echo "Checking repository state... "
isEverythingComitted || {
	echo "error: there are still changes to be committed." >&2
	exit 1
}
lastCommitId=$(getLastCommitId)

echo "Switching to master..."
git checkout master

echo "Copying output files..."
cp -r output/* .

echo "Committing changes..."
git commit -a -m "Copied changes from source/$lastCommitId."

echo "Pushing changes..."
git push origin master source

echo "Switching back to source..."
git checkout source
