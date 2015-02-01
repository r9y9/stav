#!/usr/bin/python
# coding: utf-8

# waveform modification based on spectrum differencial

import json
import numpy as np
import sys
import sptk
from pylab import plot, show, legend

from scipy.io import wavfile

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Synthsis")
    parser.add_argument("--input", dest="input", type=str, required=True)
    parser.add_argument("--mcep", dest="mcep", type=str, required=True)
    parser.add_argument("--output", dest="output", type=str,
                        default="converted.wav")
    parser.set_defaults(trajectory=False)
    args = parser.parse_args()

    # input audio
    fs, data = wavfile.read(args.input)

    # setup mcep
    f = open(args.mcep)
    src = json.load(f)
    f.close()

    mcep = np.array(src['Data'])
    # remove power coef.
    mcep[:, 0] = 0.0

    # waveform modification based on spectrum differencial
    order = len(mcep[0]) - 1
    mlsa = sptk.MLSASynthesizer(order)

    synthesized = mlsa.synthesis(data, mcep, alpha=0.35)

    synthesized = np.array(synthesized, dtype=np.int16)

    plot(synthesized, label="converted")
    plot(data, label="original")
    legend()
    show()

    wavfile.write(args.output, fs, synthesized)
