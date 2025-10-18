#!/bin/bash

# docker-buildx build --platform linux/amd64 -t aristidemanyesse/cred:0a-dev --load --push .
docker-buildx build --platform linux/amd64 -t aristidemanyesse/cred:0c-prod --load --push .
