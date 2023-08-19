from panoptes_client import Panoptes, Workflow
import getpass
import argparse


def upload_csv():
    parser = argparse.ArgumentParser("upload_csv", description="Uploads the ML annotation CSV to a Caesar extractor given a workflow ID")

    parser.add_argument("-w", "--workflow_id", type=int, required=True)
    parser.add_argument("-u", "--url", type=str, required=True)

    args = parser.parse_args()

    username = getpass.getpass("Panoptes username: ")
    password = getpass.getpass("Panoptes password: ")

    client = Panoptes.connect(username=username, password=password)

    workflow = Workflow(args.workflow_id)

    with client:
        workflow.import_caesar_data_extracts(args.url)


if __name__ == "__main__":
    upload_csv()
