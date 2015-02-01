#!/usr/bin/python
# coding: utf-8

import numpy as np
import feature


class Converter(object):

    def convert(self, src):
        raise NotImplemented(str(type(self)) + " does not implemented.")


class FrameByFrameConverter(Converter):

    def __init__(self, model):
        self.model = model

    def convert(self, src):
        # Split src features to power and spectral features
        power, src = src[:, 0], src[:, 1:]

        T, D = src.shape
        converted = np.zeros((T, D + 1))  # plus power

        # Perform feature maping for each time
        for t in range(T):
            converted[t][1:] = self.model.convert(src[t])
        converted[:, 0] = power

        return converted


class TrajectoryConverter(Converter):

    def __init__(self, model, limit_frames_for_vc=100):
        self.model = model
        self.limit_frames_for_vc = limit_frames_for_vc

    def convert(self, src):
        # Split src features to power and spectral features
        power, src = src[:, 0], src[:, 1:]

        # Append delta feature
        src = feature.append_delta(src)

        T, D = src.shape
        # D/2 + 1: order of static spectral features + power
        converted = np.zeros((T, D / 2 + 1))

        # Perform Trajectory-based mapping
        # Split whole sequence to a set of phrases to reduce memory size
        # that is used in conversion process.
        # Conversion is performed for each phrase.
        count = 0
        while True:
            b = count * self.limit_frames_for_vc
            e = (count + 1) * self.limit_frames_for_vc
            if e > len(src) - 1:
                e = len(src) - 1
            phrase = src[b:e]
            converted[b:e, 1:] = self.model.convert(phrase)

            if e == len(src) - 1:
                break
            count += 1
        converted[:, 0] = power

        return converted
