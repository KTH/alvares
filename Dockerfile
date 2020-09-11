FROM kthse/kth-python:3.6.0

RUN mkdir /repo
WORKDIR /repo

RUN apk update && \
    apk upgrade && \
    apk add docker libxml2-dev libxslt-dev build-base python3-dev libffi-dev openssl-dev

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

RUN pipenv install
RUN pipenv install pip

RUN rm -rf /var/cache/apk/*

COPY ["modules",  "modules"]
COPY ["run.py", "run.py"]

EXPOSE 3010

CMD ["pipenv", "run", "python", "run.py"]
