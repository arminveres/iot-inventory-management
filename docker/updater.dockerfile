# FIXME: (aver) create local folder to run from, not from root!

FROM python:3.9-slim-bookworm
LABEL maintainer="Armin Veres"

ADD ./requirements.docker.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy files over
ADD _updating/_new_file.py .
ADD src/updater.py .

# enable supplication of arguments
ENTRYPOINT ["bash", "-c", "python3 -m \"$@\"", "--"]
