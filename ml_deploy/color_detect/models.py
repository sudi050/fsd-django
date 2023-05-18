from django.db import models

# Create your models here.

class pred_images(models.Model):
    photo = models.ImageField(upload_to='images')