import matplotlib.pyplot as plt
import tqdm
import os
import numpy as np
import glob
import json
import pandas as pd
import random
import string
import argparse
import pathlib

figt, axt = plt.subplots(1, 1)


def generate_annotations(seg_map):
    '''
        Creates a list of contour lines from a segmentation map.

        Inputs
        ------
        seg_map : numpy.ndarray
            Output segmentation map (shape: width x height x 1)

        Outputs
        -------
        lines : list
            List of lines, each with varying number number of points containing
            the pixel value of each point. Automatically rounded to integer with
            duplicates removed
    '''
    axt.cla()
    cont = axt.contour(seg_map, [0.99])
    paths = cont.collections[0].get_paths()

    lines = []
    for path in paths:
        v = path.vertices
        if len(v) > 50:
            line = np.asarray(v, dtype=int)
            _, inds = np.unique(line, axis=0, return_index=True)
            lines.append(line[sorted(inds), :])

    return lines


def create_csv():
    parser = argparse.ArgumentParser('create_csv', description='Create Caesar-compatible CSV for FatChecker data upload')

    parser.add_argument('-d', '--data_folder', type=pathlib.Path, required=True)
    parser.add_argument('-m', '--subject_manifest', type=argparse.FileType('r'), required=True)
    parser.add_argument('--extractor_key', type=str, default='machineLearnt')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default='correct-a-cell.csv')

    args = parser.parse_args()

    masks = sorted(glob.glob(os.path.join(args.data_folder, '*.png')))

    manifest = pd.read_csv(args.subject_manifest)

    fileIDs = np.asarray([os.path.splitext(f)[0] for f in manifest.filename])
    subjectIDs = np.asarray(manifest.subject_id)

    assert len(masks) == len(manifest), f"Number of mask images ({len(masks)}) and length of manifest ({len(manifest)}) are different!"

    json_data = []
    for img in tqdm.tqdm(masks, ascii=True, dynamic_ncols=True, desc="Generating annotations"):
        predicted_mask_array = plt.imread(img)[:, :, 0]
        anno = generate_annotations(predicted_mask_array)
        subject_id = subjectIDs[np.where(fileIDs == os.path.splitext(os.path.basename(img))[0])[0]][0]
        rowi = {
            'subject_id': subject_id,
            'extractor_key': args.extractor_key
        }
        data = []
        for line in anno:
            markId = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))

            data.append({'pathX': [], 'pathY': [], 'stepKey': 'S0', 'taskIndex': 0, 'taskKey': 'T0', 'toolType': 'freehandLine', 'toolIndex': 0, 'taskType': 'drawing', 'frame': 0, 'markId': markId})

            data[-1]['pathX'] = line[:, 0].tolist()
            data[-1]['pathY'] = line[:, 1].tolist()
        rowi['data'] = json.dumps({"data": data})

        json_data.append(rowi)

    table = pd.DataFrame.from_records(json_data)
    table.to_csv(args.output)


if __name__ == '__main__':
    create_csv()
