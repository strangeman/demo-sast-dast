FROM debian:11

WORKDIR /app

COPY app /app

ENV FLASK_APP app.py

RUN apt-get update && apt install -y python3 python3-pip

RUN pip install -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0"]
