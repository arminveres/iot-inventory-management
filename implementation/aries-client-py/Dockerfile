ARG from_image=ghcr.io/hyperledger/aries-cloudagent-python:py3.9-0.9.0
FROM ${from_image}

RUN mkdir -p bin && curl -L -o bin/jq \
    https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && \
    chmod ug+x bin/jq

RUN pip install --no-cache-dir aries-cloudagent

ADD ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

# WARN: need to fix this in the code and not hardcode it
ENV LEDGER_URL "http://172.17.0.1:9000"
ENV GENESIS_URL "http://172.17.0.1:9000/genesis"

ENTRYPOINT ["python3", "-m", "my_agent", "--wallet-type", "askar"]
