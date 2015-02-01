#!/usr/bin/python
# coding: utf-8

import sys
from sklearn.externals import joblib
from pylab import *    

if __name__=="__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualize GMM")
    parser.add_argument("--gmm", dest="gmm", type=str, required=True)
    parser.add_argument("--order", dest="order", type=int, default=0)
    args = parser.parse_args()

    gmm = joblib.load(args.gmm)
    print gmm
    
    covars = gmm.covars_
    print covars.shape
    
    print args.order
    covar=covars[args.order]
    #subplot(211)
    #for m in gmm.means_:
    #    plot(m)
    #    break
    #subplot(212)
    imshow(covar, cmap='spectral')
    colorbar()
    show()
