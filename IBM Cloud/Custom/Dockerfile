FROM python:3.9-slim-buster

WORKDIR /app

ADD . /app

# Install build dependencies
RUN mkdir -p /usr/share/man/man1 && \
    echo 'APT::Get::Assume-Yes "true";' > /etc/apt/apt.conf.d/90forceyes && \
    echo 'APT::Get::Acquire::Retries "5";' > /etc/apt/apt.conf.d/80retries && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    echo 'source $HOME/.cargo/env' >> $HOME/.bashrc

# Install python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 8080
EXPOSE 8080

# Use an environment variable for the port
CMD python3 ./app.py --port=$PORT
