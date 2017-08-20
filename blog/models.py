import datetime
from PIL import Image as Img
from io import BytesIO, StringIO

import django
from django.contrib.postgres.fields import ArrayField
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.db.models import Avg, Count
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.db import models

from django_boto.s3.storage import S3Storage

from ProConDuck.settings import *

# Create your models here.

s3 = S3Storage()


class Company(models.Model):

    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Category(models.Model):

    name = models.CharField(max_length=20)
    number = models.IntegerField(unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return "%d - %s" % (self.number, self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(Category, self).save(*args, **kwargs)


class Product(models.Model):

    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 default=0)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    score = models.FloatField(default=0)  # , editable=False)
    link = models.URLField()
    image = models.ImageField(upload_to="images", storage=s3)
    image_compressed = models.BooleanField(default=False, editable=False)
    description = models.TextField(default="Default description")

    def __str__(self):
        return self.name

    def update_rating_avg(self, delete_instance=None):
        reviews = self.review_set.all()
        if delete_instance:
            reviews = reviews.exclude(pk=delete_instance.id)

        if len(reviews) > 0:
            self.score = reviews.aggregate(Avg('score'))['score__avg']
        else:
            self.score = 0

        self.save()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.image and not self.image_compressed:
            img = Img.open(BytesIO(self.image.read()))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((self.image.width / 1.5, self.image.height / 1.5),
                          Img.ANTIALIAS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=70)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" %
                                              self.image.name.split('.')[0],
                                              'image/jpeg', img.size, None)
            self.image_compressed = True

        return super(Product, self).save(*args, **kwargs)


class Reviewer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Review(models.Model):

    featured = models.BooleanField(default=False)

    # cascade will delete reviews if product is deleted
    # protect only lets you delete product if all reviews are deleted
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    title = models.CharField(max_length=100)
    reviewer = models.ForeignKey(Reviewer, default=1)
    score = models.IntegerField(default=10, editable=False)
    image = models.ImageField(blank=True, upload_to="images", storage=s3)
    image_compressed = models.BooleanField(default=False, editable=False)
    video_link = models.URLField(blank=True)
    review = models.TextField()  # user uploaded can't have tags!!!
    views = models.IntegerField(default=0, editable=False)

    created = models.DateTimeField(editable=False,
                                   default=django.utils.timezone.now)
    modified = models.DateTimeField(blank=True, null=True, editable=False,
                                    default=django.utils.timezone.now)
    pros = ArrayField(models.CharField(max_length=20, blank=True), null=True,
                      size=10)
    cons = ArrayField(models.CharField(max_length=20, blank=True), null=True,
                      size=10)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('review', (), {
            'slug': self.slug,
            'id': self.id,
        })

    def slug(self):
        return slugify(self.title)

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created <= now

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()  # will change if views gets updated

        if self.image and self.image != self.product.image and not \
                self.image_compressed:
            img = Img.open(BytesIO(self.image.read()))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.thumbnail((self.image.width / 1.5, self.image.height / 1.5),
                          Img.ANTIALIAS)
            output = BytesIO()
            img.save(output, format='JPEG', quality=70)
            output.seek(0)
            self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" %
                                              self.image.name.split('.')[0],
                                              'image/jpeg', img.size, None)
            self.image_compressed = True
        return super(Review, self).save(*args, **kwargs)


@receiver(models.signals.pre_save, sender=Review)
def review_pre_save(sender, instance, *args, **kwargs):
    if instance.pk is None:  # new review

        # display breaks on review page
        instance.review = instance.review.replace("\r\n", "<br />")


@receiver(models.signals.post_save, sender=Review)
def review_post_save(sender, instance, created, *args, **kwargs):
    instance.product.update_rating_avg()
    if instance.image == "":
        instance.image = instance.product.image
        instance.save()


@receiver(models.signals.pre_delete, sender=Review)
def review_pre_delete(sender, instance, *args, **kwargs):
    instance.product.update_rating_avg(instance)


class AdSlot(models.Model):

    number = models.IntegerField(default=1)
    image_width = models.IntegerField()
    image_height = models.IntegerField()

    def __str__(self):
        return "%d - %d x %d" % (self.number,
                                 self.image_width,
                                 self.image_height)


class Advertisement(models.Model):

    selected = models.BooleanField(default=True)
    slot = models.ForeignKey(AdSlot, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="ads", storage=s3)
    link = models.URLField()

    def __str__(self):
        return self.name


class Promotion(models.Model):

    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    link = models.URLField()
    title = models.CharField(max_length=20)
    description = models.TextField()
    image = models.CharField(max_length=100)
    current = models.BooleanField(default=0)

    def __str__(self):
        return self.title


class NewsletterEmail(models.Model):

    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.email
