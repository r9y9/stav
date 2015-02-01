#!/usr/bin/python
# coding: utf-8

# Visuallize mel-cepstrum

# e.g. python visualize_mcep.py mcep.json

import numpy as np
import sys
import json
import time
from pylab import *    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "2 argument is requried. exit."
        quit()

    f = open(sys.argv[1], 'r')
    data = json.load(f)
    f.close()

    src_mcep = np.array(data['Src']['Data'])
    tgt_mcep = np.array(data['Target']['Data'])

    ion()
    fig = figure()
    ax1 = fig.add_subplot(211)
    ylim([-2, 7])
    ax2 = fig.add_subplot(212)
    ylim([-2, 7])
    p1, = ax1.plot(src_mcep[:,0])
    p2, = ax2.plot(tgt_mcep[:,0])
    for order in range(src_mcep.shape[1]):
        p1.set_ydata(src_mcep[:,order])
        p2.set_ydata(tgt_mcep[:,order])
        draw()
        time.sleep(0.1)
    
    print "finish"
