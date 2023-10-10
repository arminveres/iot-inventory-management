# FROM ubuntu:latest
# Debian uses 3 GB less
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
    zsh \
    lsb-release \
    stow \
    pkg-config \
    tmux \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# =================================================================================================
# User specific setup
# =================================================================================================
USER $USERNAME

ENV HOME="/home/${USERNAME}"
ENV XDG_DATA_HOME="${HOME}/.local/share"
ENV XDG_CONFIG_HOME="${HOME}/.config"
ENV XDG_STATE_HOME="${HOME}/.local/state"
ENV XDG_CACHE_HOME="${HOME}/.cache"

# Set ENV so that cargo is downloaded to correct path
ENV RUSTUP_HOME="$XDG_DATA_HOME/rustup"
ENV CARGO_HOME="$XDG_DATA_HOME/cargo"

# get rustup without modifying the path, as we have that in our dotfiles already
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path

# add toolchains for Hyperledger Iroha
# RUN ${CARGO_HOME}/bin/rustup toolchain install nightly-2022-12-22-x86_64-unknown-linux-gnu
# RUN ${CARGO_HOME}/bin/rustup toolchain install nightly-2023-06-25-x86_64-unknown-linux-gnu
# RUN ${CARGO_HOME}/bin/rustup component add rust-src --toolchain nightly-2023-06-25-x86_64-unknown-linux-gnu

# TODO: (aver) create separate dockerfile for my own config in order to have one for the supervisors
RUN ${CARGO_HOME}/bin/rustup default stable

# run separate install for better caching
RUN ${CARGO_HOME}/bin/cargo install \
    cargo-watch \
    cargo-update \
    cargo-cache \
    zoxide \
    exa \
    bat \
    bob-nvim \
    ripgrep \
    fd-find \
    && ${CARGO_HOME}/bin/cargo cache --autoclean-expensive

# get current neovim version
RUN ${CARGO_HOME}/bin/bob use nightly

# Don't forget to run recursive pull inside container
RUN git clone --depth 1 --recursive --branch=dev-env https://github.com/arminveres/dotfiles ~/dotfiles
WORKDIR ${HOME}/dotfiles
RUN stow -vt ~ \
    zsh \
    nvim \
    tmux

# install npm LTS
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && \
    sudo apt-get install -y nodejs && \
    sudo rm -rf /var/lib/apt/lists/*

# =================================================================================================
# Finalization
# =================================================================================================
# set zsh as default shell
RUN sudo chsh -s /usr/bin/zsh ${USERNAME}

# run zsh once to download fzf
RUN zsh
# update nvim folder
WORKDIR ${XDG_CONFIG_HOME}/nvim
RUN git switch -f main && git pull --rebase --force
# update nvim
RUN ${XDG_DATA_HOME}/bob/nvim-bin/nvim --headless "+Lazy! sync" +qa
RUN ${XDG_DATA_HOME}/bob/nvim-bin/nvim --headless "+TSUpdateSync" +qa
# RUN ${XDG_DATA_HOME}/bob/nvim-bin/nvim --headless "+MasonInstall rust-analyzer" +qa

WORKDIR ${HOME}

CMD ["/usr/bin/zsh", "-i", "-l"]
