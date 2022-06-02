# page2mp4

This is a simple python app which uses `firefox` in `Xvfb` and `ffmpeg` to record scrolling view of a webpage

*NOTE*: There is a Gecko driver available in `/usr/bin/geckodriver` but if you want download latest one provide a Github Token as `GH_TOKEN` environment variable and `webdriver-manager` will download latest for you

`python recorder.py URL scrollspeed timelimit`

## Docker 
Docker file is also available, you can run by:  

```
docker build . -t page2mp4
docker run -it -e GH_TOKEN='TOKEN' -v `pwd`/out:/app/out page2mp4 python3 recorder.py URL 6 60
```
