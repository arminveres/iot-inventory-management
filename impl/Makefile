.PHONY: run-env build

IMAGE_NAME:="ba-dev-env"

run:
	docker container run --rm --name dev-env -it \
		-v .:/home/arminveres/ba-thesis-implementation \
		${IMAGE_NAME}
build:
	docker build -t ${IMAGE_NAME} .
