FROM python

ENV PYTHONUNBUFFERED 1

RUN mkdir /recipe_serv

WORKDIR /recipe_serv

ADD . /recipe_serv/

RUN pip install -r requirements.txt
