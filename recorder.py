import os
import sys
import threading 
from time import sleep
import multiprocessing
from typing import Union
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver import ActionChains
from subprocess import Popen, STDOUT, signal
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager


class Recorder(threading.Thread):
    def __init__(self, display, outfile, video_size, notifier, *args, **kwargs):
        self._display = display
        self._outfile = outfile
        self._video_size = video_size
        self._process:Union[Popen, None] = None
        self._notifier = notifier
        return super().__init__(*args, **kwargs);

    def run(self):
        """
        Run ffmpeg to record display as MP4 file with audio from default ALSA device 
        """
        self._process = Popen(['ffmpeg', '-f', 'x11grab', '-draw_mouse', '0', '-video_size', f'{self._video_size}', '-i', f':{self._display}',  '-an',
                                '-y', '-nostdin', '-vf', 'format=yuv420p', '-movflags', '+faststart', f'{self._outfile}'],
                               stdout=os.open(os.devnull, os.O_RDWR), stderr=os.open(os.devnull, os.O_RDWR))
        #self._process = Popen(['ffmpeg', '-f', 'x11grab', '-draw_mouse', '0', '-video_size', f'{self._video_size}', '-i', f':{self._display}', '-f', 'alsa', '-ac', '2', 
        #                       '-i', 'default', '-y', '-nostdin', '-vf', 'format=yuv420p', '-movflags', '+faststart', f'{self._outfile}'],
        #                       stdout=os.open(os.devnull, os.O_RDWR), stderr=os.open(os.devnull, os.O_RDWR))
        print("ffmpeg started")
        self._notifier.set()
        self._process.wait()
        print("ffmpeg terminated")

    def terminate(self):
        self._process.send_signal(signal.SIGINT)
        return self._process.wait()



class BrowserController:
    def __init__(self, url, shared_stop_var):
        self._stop = shared_stop_var
        self._url = url

    def scroll_down_page(self,speed=8):
        current_scroll_position, new_height= 0, 1
        while not self._stop.value and current_scroll_position <= new_height:
            current_scroll_position += speed
            self._browser.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = self._browser.execute_script("return document.body.scrollHeight")

    def __enter__(self):
        self._xvfb = Display(visible=False, size=(1920, 1080))
        self._xvfb.start()
        if not os.environ.get('GH_TOKEN') and os.path.exists("/usr/bin/geckodriver"):
            self._browser = webdriver.Firefox(service=Service("/usr/bin/geckodriver"))
        else:
            self._browser = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        self._browser.fullscreen_window();
        self._browser.set_window_position(0, 0)
        self._browser.set_window_size(1920, 1080)
        self._browser.get(url)

        try:
            notifier = threading.Event()
            self._recorder = Recorder(self._xvfb.display, 'out/output.mp4', "x".join(map(str,self._xvfb._size)), notifier)
            self._recorder.start()
            notifier.wait()

        except TimeoutException:
            print("Loading took too much time!")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback): 
        self._recorder.terminate()
        self._browser.quit()
        self._xvfb.stop()


class Sleeper(multiprocessing.Process):
    def __init__(self, t, shared_var, *args, **kwargs):
        self._shared_var = shared_var
        self._t = t
        return super().__init__(*args, **kwargs);

    def run(self):
            sleep(self._t)
            self._shared_var.value = 1

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: {} <url> <speed> <timeout>".format(sys.argv[0]))
        exit(1)
    url = sys.argv[1]
    speed = int(sys.argv[2])
    timeout = int(sys.argv[3])
    stop = multiprocessing.Value('i', 0)
    with BrowserController(url, stop) as c:
        if timeout > 0:
            Sleeper(timeout, stop).start()
        c.scroll_down_page(speed)


