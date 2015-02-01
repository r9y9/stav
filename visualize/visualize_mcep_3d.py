#!/usr/bin/python
# coding: utf-8

# Visuallize mel-cepstrum in 3d 

# e.g. python visualize_mcep_3d.py mcep.json

import mpl_toolkits.mplot3d as m3d
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


    # time
    x = np.arange(0, mcep.shape[0], 1)
    # order
    y = np.arange(0, mcep.shape[1], 1)
    
    X, Y = np.meshgrid(y, x)

    fig = figure()
    ax = m3d.Axes3D(fig)
    ax.set_zlim([-2, 8])
    ax.plot_surface(X, Y, mcep)
    # ax.plot_surface(X, Y, mcep[:,1:], rstride=1, cstride=1, linewidth=0, antialiased=False)

    show()
