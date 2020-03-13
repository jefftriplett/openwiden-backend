#!/bin/sh

VERSION=$(python -c "import openwiden; print(openwiden.get_version())")
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USER" --password-stdin
docker build -t stefanitsky/openwiden-backend:"$VERSION" -t stefanitsky/openwiden-backend:stage .
docker push stefanitsky/openwiden-backend:"$VERSION"
docker push stefanitsky/openwiden-backend:stage
