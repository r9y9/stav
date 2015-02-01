#!/usr/bin/python
# coding: utf-8

import json
import numpy as np
import sys
from sklearn.externals import joblib
from pystav.gmmmap import GMMMap, TrajectoryGMMMap
from pystav.converter import Converter, FrameByFrameConverter, TrajectoryConverter

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="VC")
    parser.add_argument("--input", dest="input", type=str, required=True)
    parser.add_argument("--gmm", dest="gmm", type=str, required=True)
    parser.add_argument("--trajectory", dest="trajectory", action="store_true")
    parser.add_argument("--output", dest="output", type=str,
                        default="converted.json")
    parser.set_defaults(trajectory=False)
    args = parser.parse_args()

    f = open(args.input)
    data = json.load(f)
    f.close()

    gmm = joblib.load(args.gmm)

    src = np.array(data['Data'])

    vc = Converter()

    if args.trajectory == True:
        model = TrajectoryGMMMap(gmm, 100)
        vc = TrajectoryConverter(model)
    else:
        model = GMMMap(gmm)
        vc = FrameByFrameConverter(model)

    # Perform conversion
    tgt = vc.convert(src)

    with open(args.output, "w") as f:
        data['Data'] = tgt.tolist()
        json.dump(data, f)

    print "Mapping finished."
