# --- Dockerfile pour ton app Streamlit ---
    FROM python:3.11-slim

    WORKDIR /app
    
    # Installer dépendances système utiles
    RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*
    
    # Copier requirements et installer
    COPY requirements.txt /app/requirements.txt
    RUN pip install --upgrade pip && pip install -r requirements.txt
    
    # Copier ton code
    COPY . /app
    
    EXPOSE 8501
    
    # Lancer Streamlit
    CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    