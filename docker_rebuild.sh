#!/bin/bash

docker stop ipcampy-container
docker rm ipcampy-container
docker rmi ipcampy-image
docker build -t ipcampy-image .
docker run -d -p 56789:56789 --restart unless-stopped --name ipcampy-container ipcampy-image
docker logs -f ipcampy-container
