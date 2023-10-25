# Based off of: https://github.com/hyperledger/aries-cloudagent-python/blob/main/docker/Dockerfile.demo
ARG from_image=ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.10.4
FROM ${from_image}

# Enable some bash features such as pushd/popd
SHELL ["bash", "-c"]

RUN mkdir -p bin && curl -L -o bin/jq \
    https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && \
    chmod ug+x bin/jq

RUN pip install --no-cache-dir aries-cloudagent

ADD ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# install orion dependencies
USER root

RUN apt-get update && apt-get install --yes --no-install-recommends \
    make \
    wget \
    && rm -rf /var/lib/apt/lists/*

# get golang
ARG goversion=1.21.1
ARG gozip=go${goversion}.linux-amd64.tar.gz

RUN rm -rf /usr/local/go && \
    wget  https://go.dev/dl/${gozip} && \
    tar -C /usr/local -xzf ${gozip} && \
    rm ${gozip} && \
    export PATH=$PATH:/usr/local/go/bin

# USER aries

# get orion-binaries
RUN git clone --depth 1 https://github.com/hyperledger-labs/orion-server.git && \
    export PATH=$PATH:/usr/local/go/bin && \
    pushd orion-server && \
    make binary && \
    cp -r bin ../ && \
    popd && \
    rm -r orion-server && \
    go clean -modcache

# copy files over
ADD src .
ADD crypto crypto

# RUN chown -R aries:aries .

# enable supplication of arguments
ENTRYPOINT ["bash", "-c", "python3 -m \"$@\"", "--"]
