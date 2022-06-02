FROM ubuntu:20.04

RUN apt update
RUN apt install -y --no-install-recommends python3-pip xvfb  apt-utils firefox wget ffmpeg
ARG GK_VERSION=v0.31.0
RUN wget --no-verbose -O /tmp/geckodriver.tar.gz http://github.com/mozilla/geckodriver/releases/download/$GK_VERSION/geckodriver-$GK_VERSION-linux64.tar.gz \
   && rm -rf /opt/geckodriver \
   && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
   && rm /tmp/geckodriver.tar.gz \
   && mv /opt/geckodriver /opt/geckodriver-$GK_VERSION \
   && chmod 755 /opt/geckodriver-$GK_VERSION \
   && ln -fs /opt/geckodriver-$GK_VERSION /usr/bin/geckodriver
WORKDIR /app
COPY . . 
RUN pip install -r requirements.txt
CMD ["python3", "recorder.py"]
