import torch
from torch.utils.data import Dataset
import numpy as np
import glob
import os
from torchvision.io import read_image, ImageReadMode
from torchvision.transforms import Compose, RandomCrop, RandomHorizontalFlip, RandomVerticalFlip


class FatCheckerDataset(Dataset):
    augmentation = None

    def __init__(self, imgfolder, maskfolder, size=256, augmentation='randomcrop'):
        self.images = sorted(glob.glob(os.path.join(imgfolder, "*.jpg")))
        self.masks = sorted(glob.glob(os.path.join(maskfolder, "*.png")))
        self.size = size

        self.image_ids = [int(os.path.basename(image).replace('.jpg', '')) for image in self.images]
        self.mask_ids = [int(os.path.basename(image).replace('.png', '')) for image in self.masks]

        assert np.all(self.image_ids == self.mask_ids), "Image IDs and Mask IDs do not match!"

        if augmentation == 'randomcrop':
            self.augmentation = RandomCrop(size=(size, size))
        elif augmentation == 'randomcrop+flip':
            self.augmentation = Compose([
                RandomCrop(size=(size, size)),
                RandomHorizontalFlip(0.25),
                RandomVerticalFlip(0.25)
            ])

        print(f"Loaded {len(self)} images")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image_file = self.images[index]
        mask_file = self.masks[index]

        img = read_image(image_file, ImageReadMode.RGB) / 255.

        # add the mask so we can crop it
        mask = read_image(mask_file, ImageReadMode.GRAY)
        mask[mask < 0.] = 0.
        data_stacked = torch.cat((img, mask), dim=0)

        if self.augmentation is not None:
            data_stacked = self.augmentation(data_stacked)

        return data_stacked[:3, :, :], data_stacked[3, :, :].unsqueeze(0)


class FatCheckerInferenceDataset(Dataset):
    def __init__(self, imgfolder, size=256):
        self.images = sorted(glob.glob(os.path.join(imgfolder, "*.jpg")))
        self.size = size

        self.image_ids = [int(os.path.basename(image).replace('.jpg', '')) for image in self.images]

        print(f"Loaded {len(self)} images")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image_file = self.images[index]

        img = read_image(image_file, ImageReadMode.RGB) / 255.

        return img

    def get_filename(self, index):
        return os.path.basename(self.images[index])
