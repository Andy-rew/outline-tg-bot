#!/bin/bash

# checks if container name is supplied
if [ "$#" -eq 0 ]
then
    echo "Please specify a container name!"
    exit 1
fi

# checks if container exist
if [ "$(docker ps -a -q -f name=outline-tg-bot)" ]
then
    echo "An existing container with the name outline-tg-bot was found!"

    # checks if container is running and stop it if it is
    if [ "$(docker ps -aq -f status=running -f name=outline-tg-bot)" ]
    then
        echo "Stopping container..."
        docker stop outline-tg-bot
	echo "Container stopped."
    fi

    # removes stopped container
    echo "Removing stopped container..."
    docker rm -f outline-tg-bot
    echo "Container removed."
fi

# pull the latest image
docker pull 114ndy/outline-tg-bot:$1

# run new docker container
docker run -d --restart always --name outline-tg-bot --env-file ./.env --entrypoint printenv 114ndy/outline-tg-bot:$1