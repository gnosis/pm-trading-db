#!/bin/sh
if [ "$TRAVIS_PULL_REQUEST" == "false" ]
then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker build -t gnosisdb -f docker/web/Dockerfile .
    docker tag gnosisdb gnosispm/gnosisdb:$1
    docker push gnosispm/gnosisdb:$1
fi
