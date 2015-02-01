#!/usr/bin/python
# coding: utf-8

import sys, os, json
import numpy as np

from pylearn2.datasets import dense_design_matrix

def find_files(dir):
    return [os.path.join(dir, s) for s in os.listdir(dir)]

def append_delta(src):
    """
    Append delta feature to static feature vector.

    Parameters
    ----------
    src : array, shape (`num_frames`, `order of feature vector`)
        a sequence of static feature vector

    Return
    ------
    a sequence of joint static and delta feature vector

    """
    new_feature = np.empty((src.shape[0], src.shape[1]*2))
    
    T, dim = src.shape
    for t in range(T):
        ff = np.zeros(2*dim)
        ff[0:dim] = src[t][:dim]
        if t-1 >= 0:
            ff[dim:] -= 0.5*src[t-1][:dim]
        if t+1 < T:
            ff[dim:] += 0.5*src[t+1][:dim]

        new_feature[t] = ff

    return new_feature

class CMU_ARCTIC(dense_design_matrix.DenseDesignMatrix):
    """
    The CMU_ARCTIC databases were constructed at the Language Technologies 
    Institute at Carnegie Mellon University as phonetically balanced,
    US English single speaker databases designed for unit selection speech 
    synthesis research.
    http://www.festvox.org/cmu_arctic/

    
    """
    def __init__(self,
                 data_path,
                 start=None,
                 stop=None,
                 joint=False,
                 standarize=True,
                 ignore_0th_order=True,
                 add_dynamic_feature=False):    
        files = find_files(data_path)
        files.sort()

        XY = []
        
        print len(files), "training data found."
        
        # Combine all parallel data
        total_frames = 0
        total_phrases = 0
        for path in files:
            f = open(path)
            data = json.load(f)
            f.close()

            src = np.array(data['Src']['Data'])
            tgt = np.array(data['Target']['Data'])

            if ignore_0th_order:
                src, tgt = src[:,1:], tgt[:,1:]

            if add_dynamic_feature:
                src, tgt = append_delta(src), append_delta(tgt)
                    
            combined = np.hstack([src, tgt])
            XY.append(combined)
            total_frames += combined.shape[0]
            total_phrases += 1

        print "Total number of frames is %d." % total_frames
        print "Total number of phrases is %d." % total_phrases

        XY = np.vstack(XY)
        XY = XY[start:stop, :]

        if joint:
            X = XY
            Y = None
        else:
            order = XY.shape[1]/2
            X = XY[:, :order]
            Y = XY[:, order:]

        if standarize:
            self.X_mean = np.mean(X, axis=0)
            self.X_std = np.std(X, axis=0)
            self.X_std[self.X_std == 0.] = 1.
            X = (X - self.X_mean) / self.X_std

            if not joint:
                self.Y_mean = np.mean(Y, axis=0)
                self.Y_std = np.std(Y, axis=0)
                self.Y_std[self.Y_std == 0.] = 1.
                Y = (Y - self.Y_mean) / self.Y_std

        super(CMU_ARCTIC, self).__init__(X=X, y=Y)

        assert not np.any(np.isnan(self.X))
        if not joint:
            assert not np.any(np.isnan(self.y))
