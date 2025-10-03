#!/bin/bash

docker-buildx build --platform linux/amd64 -t aristidemanyesse/cred:0.0b --load --push .
