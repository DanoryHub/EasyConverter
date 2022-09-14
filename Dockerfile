FROM python:alpine3.16

WORKDIR /usr/src/EasyConverter

RUN mkdir Save

RUN apk update

RUN apk add ffmpeg

COPY requirements.txt .

COPY CoreConverter/ ./CoreConverter/

CMD [ "sh", "-c", "echo $HOME" ]