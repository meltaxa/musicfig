FROM python:3.9-alpine

WORKDIR /musicfig
COPY . /musicfig/

RUN apk update && \
    apk mpg123

RUN pip3 install --upgrade pip wheel && pip3 install --upgrade -r requirements.txt

ENV PYTHONPATH="/config:$PYTHONPATH"

CMD ["python3", "run.py"]
