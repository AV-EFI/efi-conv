# Pull in base image
FROM docker.io/library/python:3-slim-trixie AS python-base

# Image information
LABEL org.opencontainers.image.source=https://github.com/AV-EFI/efi-conv
LABEL org.opencontainers.image.description="Check module and converter scripts related to the AVefi schema"
LABEL org.opencontainers.image.licenses=MIT
LABEL org.opencontainers.image.authors="Elias Oltmanns <elias.oltmanns@gwdg.de>, Andreas Kasper <andreas.kasper@hdf.de>"

# Update OS packages and install requirements
RUN apt-get update && apt-get upgrade --no-install-recommends -y \
    && apt-get install --no-install-recommends -y git \
    && rm -rf /var/lib/apt/lists/*

# Python
ENV PYTHONUNBUFFERED=1 \
    # paths
    # This is where our app + requirements + virtual environment will live
    PYSETUP_PATH="/app"

# Adjust PATH
ENV PATH=$PYSETUP_PATH/.venv/bin:$PATH

WORKDIR $PYSETUP_PATH

# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base AS builder-base

# Install UV
RUN pip install --no-cache-dir uv

# Copy project requirement files here to ensure they will be cached.
COPY pyproject.toml uv.lock ./

# Install runtime deps
RUN uv sync --locked --no-dev --no-install-project --no-python-downloads

# Copy the source code
COPY LICENSE README.md ./
COPY src/ ./src/

# Install main app
RUN uv sync --locked --no-dev


# Production image used for runtime
FROM python-base AS production

# Create mount point and make it the working directory
RUN mkdir /data
WORKDIR /data

# Copy app directory including dependencies
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Cache current JSON schema for check module
RUN efi-conv check -u

# Set entry point
ENTRYPOINT [ "efi-conv" ]
