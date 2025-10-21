#!/bin/bash

# docker-buildx build --platform linux/amd64 -t aristidemanyesse/cred:0a-dev --load --push .
docker-buildx build --platform linux/amd64 -t aristidemanyesse/cred:0e-prod --load --push .
