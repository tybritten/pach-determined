import os
import shutil
import tarfile

import boto3
import torch
from PIL import Image

from skimage import io
from torch.utils.data import Dataset


class CatDogDataset(Dataset):
    """Face Landmarks dataset."""

    def __init__(self, root_dir, train, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with annotations.
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        if train:
            file_dir = "train"
        else:
            file_dir = "eval"
        self.file_path = os.path.join(root_dir, file_dir)
        self.files = [
            f for f in os.listdir(self.file_path) if f.endswith(".jpg")
        ]
        self.transform = transform

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = self.files[idx]
        image = io.imread(os.path.join(self.file_path, img_name))
        image = Image.fromarray(image)
        if self.transform:
            image = self.transform(image)
        label = 0 if img_name.startswith("dog") else 1
        sample = (image, label)
        return sample


def download_pach_repo(s3_endpoint, repo, root):
    s3_resource = boto3.resource(
        "s3",
        endpoint_url=s3_endpoint,
        aws_access_key_id="",
        aws_secret_access_key="",
    )

    print("Starting to download dataset")
    bucket = s3_resource.Bucket(repo)
    for obj in bucket.objects.filter():
        target = os.path.join(root, obj.key)
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == "/":
            continue
        bucket.download_file(obj.key, target)
        if target.endswith(".tar.gz"):
            tarfile.open(target).extractall(path=root)


    print("Download operation ended")
