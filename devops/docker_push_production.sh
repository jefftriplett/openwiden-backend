#!/bin/sh

VERSION=$(python -c "import openwiden; print(openwiden.get_version())")
echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USER" --password-stdin
docker pull stefanitsky/openwiden-backend:"$VERSION"
docker tag stefanitsky/openwiden-backend:"$VERSION" stefanitsky/openwiden-backend:latest
docker push stefanitsky/openwiden-backend:latest
