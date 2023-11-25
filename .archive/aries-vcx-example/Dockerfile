FROM indy-base

ENV ENABLE_PTVSD 0
ENV ENABLE_PYDEVD_PYCHARM 0
ENV PYDEVD_PYCHARM_HOST "host.docker.internal"
ENV ACAPY_DEBUG_WEBHOOKS 1

RUN mkdir bin && curl -L -o bin/jq \
	https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && \
	chmod ug+x bin/jq

# Add and install Indy Agent code
ADD aries-cloudagent-python/requirements*.txt ./

RUN pip3 install --no-cache-dir \
	-r requirements.txt \
	-r requirements.askar.txt \
	-r requirements.bbs.txt \
	-r requirements.dev.txt

ADD aries-cloudagent-python/aries_cloudagent ./aries_cloudagent
ADD aries-cloudagent-python/bin ./bin
ADD aries-cloudagent-python/README.md ./
ADD aries-cloudagent-python/scripts ./scripts
ADD aries-cloudagent-python/setup.py ./

RUN pip3 install --no-cache-dir -e .

RUN mkdir demo logs && chown -R indy:indy demo logs && chmod -R ug+rw demo logs

# Add and install demo code
ADD aries-cloudagent-python/demo/requirements.txt ./demo/requirements.txt
RUN pip3 install --no-cache-dir -r demo/requirements.txt

ADD aries-cloudagent-python/demo ./demo

ENTRYPOINT ["bash", "-c", "demo/ngrok-wait.sh \"$@\"", "--"]

