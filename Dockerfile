FROM python:2-alpine

MAINTAINER Dan Porter <dpreid@gmail.com>

ADD src /src
WORKDIR /src
RUN pip install -r requirements.txt

VOLUME ["/srv"]

CMD ["python", "./instagrabber.py"]
