FROM python:3.9

WORKDIR /musicfig
COPY . /musicfig/

RUN apt-get update && \
    apt-get -y install python-usb mpg123

RUN pip3 install --upgrade pip wheel && pip3 install --upgrade -r requirements.txt

ENV PYTHONPATH="/config:$PYTHONPATH"

CMD ["python3", "run.py"]
