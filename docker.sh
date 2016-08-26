#!/bin/bash

set -e

dockerImageName="vy.github.io"
dockerImageTag="latest"

case $1 in

	build)
		docker build -t $dockerImageName:$dockerImageTag  .
		;;

	run)
		docker run \
			-i -t \
			-p 3000:3000 \
			-v $(pwd):/app \
			$dockerImageName:$dockerImageTag \
			/bin/bash
		;;

	*)
		echo "Usage: $0 <build|run>"

esac
