FROM python:3.9-slim-bookworm
LABEL maintainer="Armin Veres"

ADD ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy files over
ADD src/support .
ADD src/auditor.py .

# enable supplication of arguments
ENTRYPOINT ["bash", "-c", "python3 -m \"$@\"", "--"]
