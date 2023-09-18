FROM python:3.8

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

ADD database /app/database/
ADD static /app/static/
ADD templates /app/templates/
COPY app.py /app/
COPY centroidtracker.py /app/
COPY Final.py /app/
COPY MobileNetSSD_deploy.caffemodel /app/
COPY MobileNetSSD_deploy.prototxt /app/


CMD [ "python", "app.py" ]
