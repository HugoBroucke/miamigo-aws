FROM ubuntu:22.04

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY . /app

# Expose le port HTTPS
EXPOSE 443

# Lancer Streamlit avec SSL et toutes interfaces
CMD ["python3", "-m", "streamlit", "run", "app.py", \
     "--server.port=443", \
     "--server.address=0.0.0.0", \
     "--server.sslCertFile=/certs/miamigo-bot.duckdns.org.chain.pem", \
     "--server.sslKeyFile=/certs/miamigo-bot.duckdns.org.key", \
     "--server.enableCORS=false"]
