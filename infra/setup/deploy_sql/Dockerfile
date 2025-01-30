FROM postgres:14

# Install AWS CLI
RUN apt-get update && \
    apt-get install -y curl unzip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf awscliv2.zip aws

# Explicitly create the target directory
WORKDIR /schema
RUN mkdir -p /schema

# Copy SQL files into the container
COPY /schema/ /schema/
