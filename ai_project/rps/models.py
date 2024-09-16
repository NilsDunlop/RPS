from django.db import models
from django.contrib.auth.models import User
from .validators import validate_file_extension, validate_file_extension2
from zipfile import ZipFile
import os
import collections
import shutil
from .trainer import train_model


# Create your models here.
# Extending User Model Using a One-To-One Link


# Webcam Screenshot image model
class Image(models.Model):
    file = models.ImageField()
    predict = models.CharField(max_length=7, default='')


class Game(models.Model):
    date = models.DateField(auto_now_add=True)
    score = models.IntegerField(default=0)
    game_user_info = models.ForeignKey(User, on_delete=models.CASCADE)


class DeepModel(models.Model):
    upload = models.FileField(upload_to="uploaded_models", verbose_name='Upload a file with .h5 extension', validators=[validate_file_extension2] )
    name = models.CharField(max_length=255)
    current = models.BooleanField(default=False)
    result = models.CharField(max_length=20, default='')
    dataset = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.name


class Dataset(models.Model):
    dataset = models.FileField(upload_to='files', validators=[validate_file_extension], blank=True,
                               verbose_name='Upload a zip file',
                               help_text="The zip file should contain the following folders:<br/> "
                                         "data/ -> test/, train/, validation/<br/> "
                                         "test/ -> paper/, rock/, scissors/<br/> "
                                         "train/ -> paper/, rock/, scissors/ ")
    name = models.CharField(max_length=100, default='')
    description = models.CharField(max_length=255, default='')
    performance = models.BooleanField(default=False)
    valid = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, delete_zip_import=True, *args, **kwargs):
        super(Dataset, self).save(*args, **kwargs)
        # if there is a file
        if self.dataset:
            # opening the zip file
            zip_f = ZipFile(self.dataset)
            # array of expected directories
            expected_dirs = ['data/train', 'data/test/scissors', 'data/train/rock', 'data/test/rock', 'data/validation',
                             'data/train/paper', 'data/train/scissors', 'data/test', 'data/test/paper', ]
            # list found directories in zip file
            found_dirs = list(set([os.path.dirname(x) for x in zip_f.namelist()]))
            correct_dirs = []
            for i in range(0, len(found_dirs)):
                # if list of found directories is not in expected directories rejects all the remaining statements
                if found_dirs[i] not in expected_dirs:
                    continue
                else:
                    # else add found directories in correct_dir array
                    correct_dirs.append(found_dirs[i])
                    # check that all the items in expected_dirs are in correct dirs and that correct_dirs
                    # contains exact the same amount of items as in expected_dirs
            if all(dirs in correct_dirs for dirs in expected_dirs) and collections.Counter(
                    correct_dirs) == collections.Counter(expected_dirs):
                # set the valid attribute to true
                self.valid = True
                path = './data/'
                # check if data directory is a directory
                isdir = os.path.isdir(path)
                if isdir:
                    # remove data directory
                    shutil.rmtree(path)
                # extract zip file at the given path and close file
                zip_f.extractall('./')
                zip_f.close()
                # call function to train model
                deep_model_name, path, result = train_model()
                # if result is >= 90.00
                if result >= 90.00:
                    # create object and set attributes
                    DeepModel.objects.create(name=deep_model_name, upload=path, result=str(result),
                                             dataset=self.description)
                    # set the performance to true
                    self.performance = True
            # remove file
        self.dataset.delete()
