#!/usr/bin/python
# coding: utf-8

import numpy as np


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
    new_feature = np.empty((src.shape[0], src.shape[1] * 2))

    T, dim = src.shape
    for t in range(T):
        ff = np.zeros(2 * dim)
        ff[0:dim] = src[t][:dim]
        if t - 1 >= 0:
            ff[dim:] -= 0.5 * src[t - 1][:dim]
        if t + 1 < T:
            ff[dim:] += 0.5 * src[t + 1][:dim]

        new_feature[t] = ff

    return new_feature
