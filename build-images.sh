#!/bin/bash -x
#
# Copyright (c) 2024-2025, Oracle and/or its affiliates. All rights reserved.
#

VERSION="${1}"
ARCH="${2}"

NGINX_IMAGE_NAME=ingress-nginx
CONTROLLER_IMAGE_NAME=ingress-nginx-controller
REGISTRY=container-registry.oracle.com/olcne
NGINX_IMAGE=${REGISTRY}/${NGINX_IMAGE_NAME}:v${VERSION}

# Build nginx image and its modules, use that as base image for building controller image
podman build --rm=true --pull \
   --build-arg https_proxy=${https_proxy} \
   --build-arg http_proxy=${https_proxy} \
   --tag=${NGINX_IMAGE} \
   -f images/nginx/rootfs/Dockerfile \
   images/nginx/rootfs

# Build ingress-nginx-controller image
cp -f ./LICENSE ./THIRD_PARTY_LICENSES.txt rootfs/
make ARCH=${ARCH} build image \
  -e BASE_IMAGE=${NGINX_IMAGE} \
  -e TAG=v${VERSION} \
  -e REGISTRY=${REGISTRY} \
  DOCKER_IN_DOCKER_ENABLED=true
docker save -o ingress-nginx-controller.tar ${REGISTRY}/ingress-nginx-controller:v${VERSION}

# kube-webhook-certgen
pushd images/kube-webhook-certgen/rootfs
go build -a -o kube-webhook-certgen main.go
popd

docker build --no-cache --pull \
   --build-arg https_proxy=${https_proxy} \
   -t ${REGISTRY}/kube-webhook-certgen:v${VERSION} . \
   -f ./olm/builds/Dockerfile.kube-webhook-certgen
docker save -o kube-webhook-certgen.tar ${REGISTRY}/kube-webhook-certgen:v${VERSION}

# custom-error-pages
pushd images/custom-error-pages/rootfs
go get . && CGO_ENABLED=0 go build -a -installsuffix cgo -ldflags "-s -w" -o nginx-errors main.go metrics.go
popd

docker build --no-cache --pull \
   --build-arg https_proxy=${https_proxy} \
   -t container-registry.oracle.com/olcne/custom-error-pages:v${VERSION} . \
   -f ./olm/builds/Dockerfile.custom-error-pages
docker save -o custom-error-pages.tar container-registry.oracle.com/olcne/custom-error-pages:v${VERSION}
