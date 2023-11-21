FROM python:3.10.13-alpine

# RUN apt-get update \
#     && mkdir -p /app

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories \
    && apk update && apk add gcc \
    && mkdir -p /app

ADD ./ /app
WORKDIR /app


RUN pip install --upgrade pip \
    && pip install \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    -r requirements.txt
