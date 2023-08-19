import tqdm
import os
import glob
import pandas as pd
import argparse
import pathlib
from panoptes_client import Panoptes, Subject, SubjectSet, Project
import getpass
import logging

logger = logging.getLogger(__name__)


def link_subject_set(client, subject_set, subjects):
    with client:
        subject_set.add(subjects)
        subject_set.save()

    return [{'subject_id': subject.id, 'filename': subject.metadata['filename']} for subject in subjects]


def upload():
    parser = argparse.ArgumentParser('CSV creator', description='Create Caesar-compatible CSV for FatChecker data upload')

    parser.add_argument('-d', '--data_folder', type=pathlib.Path, required=True)
    parser.add_argument('-p', '--project_id', type=int, required=True)
    parser.add_argument('--subject_set_name', type=str, default=None)
    parser.add_argument('--subject_set', type=int, default=None)
    parser.add_argument('-o', '--output_manifest', type=argparse.FileType('w'), default='subjects.csv')

    args = parser.parse_args()

    if (args.subject_set_name is None) and (args.subject_set is None):
        raise ValueError("Please enter a subject set name to create a new subject set or a subject set ID to upload to an existing set")

    username = getpass.getpass("Panoptes username: ")
    password = getpass.getpass("Panoptes password: ")

    client = Panoptes.connect(username=username, password=password)

    project = Project(args.project_id)

    if args.subject_set_name is not None:
        subject_set = SubjectSet()
        subject_set.links.project = project
        subject_set.display_name = args.subject_set_name
        subject_set.save()
    elif args.subject_set_id is not None:
        subject_set = SubjectSet(args.subject_set_id)

    images = sorted(glob.glob(os.path.join(args.data_folder, '*.jpg')))

    manifest = []
    subjects = []
    for image in tqdm.tqdm(images):
        subject = Subject()
        subject.links.project = subject_set.links.project
        subject.add_location(image)
        subject.metadata.update({'filename': os.path.basename(image)})
        subject.save()

        subjects.append(subject)

        if len(subjects) > 100:
            manifest.extend(link_subject_set(client, subject_set, subjects))
            subjects.clear()

    manifest.extend(link_subject_set(client, subject_set, subjects))

    manifest = pd.DataFrame.from_records(manifest)
    manifest.to_csv(args.output_manifest)


if __name__ == '__main__':
    upload()
