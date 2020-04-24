FROM alpine:latest

RUN apk update && apk add python2 py2-pip
RUN pip install flask

RUN mkdir restful_pieces/
ADD ./main.py restful_pieces/main.py
ADD ./posts.db restful_pieces/posts.db

ENTRYPOINT ["python", "/restful_pieces/main.py"]
