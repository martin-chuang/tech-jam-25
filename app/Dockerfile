FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y build-essential libomp-dev g++ git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY main.py .

EXPOSE 5050

CMD ["python", "main.py"]