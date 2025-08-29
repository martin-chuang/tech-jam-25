FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y build-essential libomp-dev g++ git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install cython pyfhel

COPY . .

CMD ["python", "he_utils.py"]