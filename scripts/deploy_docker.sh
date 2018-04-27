#!/bin/bash
if [ "$TRAVIS_PULL_REQUEST" = "false" ]
then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker build -t $DOCKERHUB_PROJECT -f docker/web/Dockerfile .
    docker tag $DOCKERHUB_PROJECT gnosispm/$DOCKERHUB_PROJECT:$1
    docker push gnosispm/$DOCKERHUB_PROJECT:$1
fi
