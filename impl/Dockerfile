FROM ubuntu:latest

RUN apt-get update && apt-get upgrade --yes
RUN apt-get install -y \
    build-essentials \
    libssl-dev \
    git \
    zsh

CMD ["zsh"]
