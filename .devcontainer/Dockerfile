FROM mcr.microsoft.com/devcontainers/base:3.0.12-ubuntu26.04@sha256:b1e3b08610ae0b2599f57c3a492eebc93d1d26dbaefb4a0bad0caa7149e4ec95

# The same Miniforge release as CI. The checksum is copied once from the
# release, so a replaced installer fails the build.
ARG MINIFORGE_VERSION=26.9.4-2
ARG MINIFORGE_SHA256=bbaf16b3897da24c4be50315934ba74848f617b4495982841d6a0a60e0edbbdf

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
USER vscode
WORKDIR /home/vscode
ENV PATH=/home/vscode/miniforge3/condabin:$PATH

RUN curl --fail --silent --show-error --location --output /tmp/miniforge.sh \
        "https://github.com/conda-forge/miniforge/releases/download/${MINIFORGE_VERSION}/Miniforge3-${MINIFORGE_VERSION}-Linux-x86_64.sh" \
    && echo "${MINIFORGE_SHA256}  /tmp/miniforge.sh" | sha256sum --check --strict \
    && bash /tmp/miniforge.sh -b -p /home/vscode/miniforge3 \
    && rm /tmp/miniforge.sh \
    && conda config --system --set channel_priority strict \
    && conda config --system --set safety_checks enabled \
    && conda config --system --set extra_safety_checks true \
    && conda config --system --set auto_activate false \
    && conda init bash \
    && conda clean --all --force-pkgs-dirs --yes

# Installed from the lock file without a solve; this layer is rebuilt only
# when the lock file changes.
COPY --chown=vscode:vscode conda-lock.yml /tmp/conda-lock.yml
RUN conda create --yes --name rock_paper_scissors --file /tmp/conda-lock.yml \
    && conda clean --all --force-pkgs-dirs --yes \
    && rm /tmp/conda-lock.yml

COPY --chown=vscode:vscode scripts/check_link_scripts.py /tmp/check_link_scripts.py
RUN prefix=/home/vscode/miniforge3/envs/rock_paper_scissors \
    && "$prefix/bin/python" /tmp/check_link_scripts.py "$prefix" \
    && rm /tmp/check_link_scripts.py
