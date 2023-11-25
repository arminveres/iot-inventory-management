# FIXME: (aver) create local folder to run from, not from root!

FROM python:3.9-slim-bookworm
LABEL maintainer="Armin Veres"

# get golang
ARG goversion=1.21.1
ARG gozip=go${goversion}.linux-amd64.tar.gz

# Enable some bash features such as pushd/popd
SHELL ["bash", "-c"]

ADD ./requirements.docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pyyaml

RUN apt-get update && apt-get install --yes --no-install-recommends \
    make \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN rm -rf /usr/local/go && \
    wget  https://go.dev/dl/${gozip} && \
    tar -C /usr/local -xzf ${gozip} && \
    rm ${gozip} && \
    export PATH=$PATH:/usr/local/go/bin

# get orion-binaries
RUN git clone --depth 1 https://github.com/hyperledger-labs/orion-server.git && \
    export PATH=$PATH:/usr/local/go/bin && \
    pushd orion-server && \
    make binary && \
    cp -r bin/* /bin && \
    popd && \
    rm -r orion-server && \
    go clean -modcache

# copy files over
ADD crypto crypto
ADD src/support support
ADD src/auditor.py .

# enable supplication of arguments
ENTRYPOINT ["bash", "-c", "python3 -m \"$@\"", "--"]
