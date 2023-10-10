.PHONY: container-run container-build

IMAGE_NAME:="ba-dev-env"

container-run:
	docker container run --rm --name dev-env -it \
		-v .:/home/arminveres/ba-thesis-implementation \
		--net=host \
		${IMAGE_NAME}

container-build:
	docker build -t ${IMAGE_NAME} .
