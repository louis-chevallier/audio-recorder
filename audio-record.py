
# pip install soundcard
# pip uninstall cffi
# conda install cffi soundfile

import soundcard as sc
import soundfile as sf
from utillc import *





import numpy as np
import tqdm
import os
import subprocess
import time
import threading
import queue
from guizero import App, Text, TextBox, PushButton, Slider, ListBox, CheckBox, Combo

app = App(title="enregistrement audio")    
# create widgets here
Text(app, text="Nom du répertoire pour les enregistrements")
name = TextBox(app, text="audio")
Text(app, text="Facteur de vitesse")
factorUI = Combo(app, options=map(str, range(1, 6)), selected = "1")
Text(app, text="Longueur en seconde des morceaux")
slider = Slider(app, start = 30, end=500)
voyant = CheckBox(app)


class EK :
    def __init__(self) :
        self.t = TextBox(app, text="", multiline=True, scrollbar=True, height=100, width=500)        
    def write(self, s) :
        self.t.value += s
    def flush(self) :
        pass


OUTPUT_FILE_NAME = "out.wav"    # file name.
SAMPLE_RATE = 48000              # [Hz]. sampling rate.



class Runner(threading.Thread):
    def __init__(self) :
        super().__init__()        
        voyant.text = "en attente"     
    def run(self) :
        EKO()
        voyant.text = "running"
        bg = voyant.bg
        voyant.bg = "red"
        self.go()
        voyant.text = "en attente" 
        voyant.bg = bg
       
        EKOT("end runner")

    def go(self) :
        EKO()
        factor_player = int(factorUI.value)

        # mettre 2 si x2 dans player
        EKOX(factor_player)
        # pour 0.5 => x2 dans le player
        speed = 1./factor_player #  1. # 0.5 # 1/3.5 #0.5/2
        dest = name.value
        fda = "tmp"

        os.makedirs(fda, exist_ok = True)
        nsec = 55
        nsec = slider.value
        RECORD_SEC = int(nsec*speed)                  # [sec]. duration recording audio.
        EKOT("recording in %s for %d secs perc chunks at speed  %s" % ( dest, nsec, speed)) 
        EKOX(np.abs(np.ones(5555)).mean())
        os.popen("ls")
        with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
            # record audio with loopback from default speaker.

            class Encoder(threading.Thread):
                def __init__(self) :
                    super().__init__()        
                    self.queue = queue.Queue(maxsize=1)
                    self.event = threading.Event()
                def run(self) :
                    while True :
                          EKOT("waiting for file to encode")
                          ffile= self.queue.get()
                          if ffile is None :
                             break
                          EKOT("got file %s" % ffile)
                          oo = "%s/out_%04d.mp3" % ( dest, i)
                          cmd = 'ffmpeg -hide_banner -loglevel quiet -stats -y -i %s  -filter:a "atempo=%f" -vn %s' % (ffile, speed, oo)
                          EKOT(cmd)
                          os.popen(cmd)
                          EKOT("file %s encoded into %s" % (ffile, oo))
                    EKOT("end encoder")
            encoder = Encoder()
            encoder.start()
            for i in range(100000) :
                #EKOX(data.shape)
                # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
                EKOT("recording in %d" % i)
                data = mic.record(numframes=SAMPLE_RATE*RECORD_SEC)
                file = os.path.join(fda, "out_%05d.wav" % i)
                EKOT("writing to %s" % file)
                sf.write(file=file, data=data[:, 0], samplerate=SAMPLE_RATE)
                EKOT("sending %s" % file)
                encoder.queue.put(file)
                EKOT("sent")
                mn = np.abs(data).mean()
                EKOX(mn)
                if mn < 0.001 :
                    time.sleep(5)
                    encoder.queue.put(None)
                    EKOT('stopping')
                    break
            EKOT('end loop')

runner = Runner()
def go() :
    runner.start()

EKO()
button = PushButton(app, text="Démarrage", command=go)
EKO()
utillc.ekostream = EK()    
EKO()

app.display()


