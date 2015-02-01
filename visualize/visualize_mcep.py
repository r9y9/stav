#!/usr/bin/python
# coding: utf-8

# Visuallize mel-cepstrum

# e.g. python visualize_mcep.py mcep.json

import numpy as np
import sys
import json
from pylab import *    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "1 argument is requried. exit."
        quit()

    f = open(sys.argv[1], 'r')
    data = json.load(f)
    f.close()

    mcep = np.array(data['Data'])

    print mcep.shape
    print "Number of time frames:", mcep.shape[0]
    print "Order of mel-cepstrum:", mcep.shape[1]-1 # minus power coef

    ion()
    ylim([-2, 7])
    line, = plot(mcep[0], "-b")
    for mc in mcep:
        line.set_ydata(mc)
        draw()

    print "finish"
