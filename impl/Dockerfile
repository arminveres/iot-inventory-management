FROM ubuntu:latest

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
RUN apt-get update && apt-get upgrade --yes
RUN apt-get install -y \
    build-essential \
    libssl-dev \
    git \
    curl \
    zsh \
    lsb-release \
    stow \
    && rm -rf /var/lib/apt/lists/*


# =================================================================================================
# User specific setup
# =================================================================================================
USER $USERNAME
ENV XDG_DATA_HOME="/home/$USERNAME/.local/share"
ENV XDG_CONFIG_HOME="/home/$USERNAME/.config"
ENV XDG_STATE_HOME="/home/$USERNAME/.local/state"
ENV XDG_CACHE_HOME="/home/$USERNAME/.cache"

ENV RUSTUP_HOME="$XDG_DATA_HOME/rustup"
ENV CARGO_HOME="$XDG_DATA_HOME/cargo"
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path

# run separate install for better caching
RUN ${CARGO_HOME}/bin/cargo install cargo-watch cargo-install-update cargo-cache
RUN ${CARGO_HOME}/bin/cargo install zoxide
RUN ${CARGO_HOME}/bin/cargo install exa
RUN ${CARGO_HOME}/bin/cargo install bat
RUN ${CARGO_HOME}/bin/cargo install bob-nvim

# get current neovim version
RUN ${CARGO_HOME}/bin/bob use stable

# Don't forget to run recursive pull inside container
RUN git clone --depth 1 --recursive --branch=dev-env https://github.com/arminveres/dotfiles ~/dotfiles
WORKDIR /home/${USERNAME}/dotfiles
RUN stow -vt ~ zsh nvim

# install npm LTS
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
    sudo apt-get install -y nodejs && \
    sudo rm -rf /var/lib/apt/lists/*

# =================================================================================================
# Finalization
# =================================================================================================

WORKDIR /home/${USERNAME}
CMD ["zsh", "-i", "-l"]
