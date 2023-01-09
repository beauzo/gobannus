FROM python:3.8

WORKDIR /app

RUN apt-get update && apt-get install ffmpeg -y

COPY requirements.txt ./
RUN python3 -m pip -q --no-cache-dir install --upgrade pip
RUN python3 -m pip -q --no-cache-dir install -r requirements.txt

COPY *.py .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
