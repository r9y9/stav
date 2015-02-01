#!/usr/bin/python
# coding: utf-8

# GMM training script for statistical voice conversion.

import sys
import os
import json
import yaml
import numpy as np
from sklearn.mixture import GMM
from sklearn.externals import joblib
from pystav.feature import append_delta


def load_config_yaml(path):
    f = open(path, 'r')
    config = yaml.load(f)
    f.close()
    return config


def find_files(dir):
    return [os.path.join(dir, s) for s in os.listdir(dir)]


def create_parallel_set(data_path, limit_frames,
                        ignore_0th_order=True,
                        add_dynamic_feature=False):
    files = find_files(data_path)
    files.sort()
    parallel = []

    print len(files), "training data found."
    print "Start combining all parallel data..."

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
            src, tgt = src[:, 1:], tgt[:, 1:]

        if add_dynamic_feature:
            src, tgt = append_delta(src), append_delta(tgt)

        combined = np.hstack([src, tgt])
        print combined.shape

        parallel.append(combined)
        total_frames += combined.shape[0]
        total_phrases += 1
        if total_frames > limit_frames:
            print "Total number of frames reached the limit %d." % limit_frames
            break

    print "Total number of phrases is %d." % total_phrases

    return np.vstack(parallel)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="GMM training for voice conversion")
    parser.add_argument("--conf", dest="conf", type=str, required=True)
    args = parser.parse_args()

    # Load training configuration
    conf = load_config_yaml(args.conf)

    parallel = create_parallel_set(conf['parallel_data_path'],
                                   conf['limit_frames'],
                                   conf['ignore_0th_order'],
                                   conf['add_dynamic_feature'])

    print "The number of frames used in training is", parallel.shape[0]

    # Traing gloval variance
    # probably have bugs!
    gv_conf = conf['gv']

    T, D = parallel.shape
    tgt = parallel[:, D / 2:D * 3 / 4]
    gv_model = GMM(n_components=gv_conf['num_mixtures'],
                   min_covar=gv_conf['min_covar'],
                   covariance_type=gv_conf['covariance_type'])
    print "Start training..."
    gv_model.fit(tgt)

    joblib.dump(gv_model, gv_conf['dump_path'], compress=9)
    print "Global variance trained and dumped to %s." % gv_conf['dump_path']

    # Train Joint GMM of source and target speaker's features
    mcep_conf = conf['mcep']
    g = GMM(n_components=mcep_conf['num_mixtures'],
            covariance_type=mcep_conf['covariance_type'],
            n_iter=mcep_conf['n_iter'],
            n_init=mcep_conf['n_init'],
            min_covar=mcep_conf['min_covar'],
            params=mcep_conf['params'])
    print "[GMM info]", g

    # Force covars to a special form
    covars = np.zeros(g.n_components * D * D).reshape(g.n_components, D, D)
    for covar in covars:
        covar[:D / 2, :D / 2] = np.diag(np.ones(D / 2))
        covar[:D / 2, D / 2:D] = np.diag(np.ones(D / 2))
        covar[D / 2:D, :D / 2] = np.diag(np.ones(D / 2))
        covar[D / 2:D, D / 2:D] = np.diag(np.ones(D / 2))
    g.covars_ = covars

    print "Start training..."
    g.fit(parallel)

    joblib.dump(g, mcep_conf['dump_path'], compress=9)

    print "Training finished."
