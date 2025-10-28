FROM ubuntu:22.04

WORKDIR /app

# Éviter les prompts
ENV DEBIAN_FRONTEND=noninteractive

# Installer Python + pip (3.12 est dans Ubuntu 24.04, mais ici on force 3.x récent)
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY requirements.txt /app/requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copier ton code
COPY . /app

EXPOSE 8501


# Lancer Streamlit
CMD ["python3", "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
