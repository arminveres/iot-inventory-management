FROM debian:bookworm-slim
LABEL maintainer="Armin Veres <armin.veres@hotmail.com>"

# Set timezone
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y tzdata && \
    rm -rf /var/lib/apt/lists/*
ENV TZ="Europe/Zurich"

# Create user for later development
ARG USERNAME=arminveres
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/*

# Install apt packages
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libssl-dev \
    git \
    curl \
    pkg-config \
    maven \
    zip \
    unzip \
    wget \
    && rm -rf /var/lib/apt/lists/*

USER ${USERNAME}
WORKDIR /home/${USERNAME}

# install OpenLogic OpenJDK
RUN wget https://builds.openlogic.com/downloadJDK/openlogic-openjdk-jre/8u382-b05/openlogic-openjdk-jre-8u382-b05-linux-x64-deb.deb \
    && wget https://builds.openlogic.com/downloadJDK/openlogic-openjdk/8u382-b05/openlogic-openjdk-8u382-b05-linux-x64-deb.deb \
    && sudo apt-get update \
    && sudo apt-get install -y \
    ./openlogic-openjdk-jre-8u382-b05-linux-x64-deb.deb \
    ./openlogic-openjdk-8u382-b05-linux-x64-deb.deb \
    && sudo rm -rf /var/lib/apt/lists/*

RUN sudo update-java-alternatives --jre-headless --jre --set openlogic-openjdk-8-hotspot-amd64

# Get nist-mud
RUN git clone --recursive https://github.com/usnistgov/nist-mud.git
RUN mkdir ~/.m2 && \
    cp nist-mud/maven/settings.xml ~/.m2

WORKDIR /home/${USERNAME}/nist-mud
RUN mvn -e clean install -nsu -Dcheckstyle.skip -DskipTests -Dmaven.javadoc.skip=true

ARG HOMEDIR=/home/${USERNAME}
COPY ./entrypoint.sh /
RUN sudo chmod u+x /entrypoint.sh && sudo chown ${USERNAME}:${USERNAME} /entrypoint.sh

# ARG KARAF_DIR=/home/${USERNAME}/nist-mud/sdnmud-aggregator/karaf/target/assembly/bin
# WORKDIR /home/${USERNAME}/nist-mud/sdnmud-aggregator/karaf/target/assembly/bin

# Add python dependencies
RUN sudo apt-get update \
    && sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-requests \
    ufw \
    && sudo rm -rf /var/lib/apt/lists/*

RUN sudo ufw allow 6653/tcp

COPY ./nist-mud/test/system-test/mudfile-server/mudfile-server.py /home/${USERNAME}/nist-mud/test/system-test/mudfile-server/mudfile-server.py

# Entrypoint
ENTRYPOINT ["bash", "-c", "/entrypoint.sh"]
