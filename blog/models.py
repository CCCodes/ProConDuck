import datetime
from PIL import Image as Img
from io import BytesIO, StringIO

import django
from django.contrib.postgres.fields import ArrayField
from django.contrib.sites.models import Site
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
    slug = models.SlugField(unique=True, editable=False)

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
    score = models.FloatField(default=0, editable=False)
    links = models.TextField()
    image = models.ImageField(upload_to="images", storage=s3)
    image_compressed = models.BooleanField(default=False, editable=False)
    description = models.TextField(default="Default description")
    created = models.DateField(default=datetime.date.today)

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
        if not self.id:
            self.slug = slugify(self.name)
            if self.image:
                self.image = compress(self.image)

        return super(Product, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/blog/product/%s/' % self.slug


@receiver(models.signals.pre_save, sender=Product)
def product_pre_save(sender, instance, *args, **kwargs):
    instance.description = instance.description.replace('\r\n', '<br />')


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
    slug = models.SlugField(unique=True, editable=False, max_length=255)
    reviewer = models.ForeignKey(Reviewer, default=1)
    score = models.FloatField(default=5)
    image_thumb_url = models.URLField(editable=False, blank=True)
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
    overall_verdict = models.TextField(blank=True)
    keywords = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.title

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.created <= now

    def save(self, *args, **kwargs):
        self.modified = timezone.now()  # will change if views gets updated
        if not self.id:
            self.slug = slugify(self.title)
            self.created = timezone.now()
        return super(Review, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/blog/review/%s/' % self.slug


@receiver(models.signals.pre_save, sender=Review)
def review_pre_save(sender, instance, *args, **kwargs):

    # display breaks on review page
    instance.review = instance.review.replace('\r\n', '<br />')

    # change yt link to embed if not already
    if '/embed/' not in instance.video_link:
        instance.video_link = instance.video_link.replace('youtube.com',
                                                          'youtube.com/embed')


@receiver(models.signals.post_save, sender=Review)
def review_post_save(sender, instance, created, *args, **kwargs):
    instance.product.update_rating_avg()
    if instance.image_thumb_url == "":
        instance.image_thumb_url = instance.product.image.url
        instance.save()


@receiver(models.signals.pre_delete, sender=Review)
def review_pre_delete(sender, instance, *args, **kwargs):
    instance.product.update_rating_avg(instance)


class ReviewImage(models.Model):

    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images", storage=s3)
    name = models.CharField(max_length=50)
    thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            if self.image and self.image != self.review.product.image:
                self.image = compress(self.image)

        # if its the only image for the review
        # whether its the first time saving or saved again (and unchecked)
        # so that self.pk doesn't make the program crash
        if self.id is not None and len(self.review.reviewimage_set.all()) == 0\
                or len(self.review.reviewimage_set.exclude(pk=self.pk)) == 0:
            self.thumbnail = True
        elif self.thumbnail:
            for img in self.review.reviewimage_set.exclude(pk=self.pk):
                img.thumbnail = False
                img.save()
        return super(ReviewImage, self).save(*args, **kwargs)


@receiver(models.signals.post_save, sender=ReviewImage)
def reviewimage_post_save(sender, instance, created, *args, **kwargs):
    if instance.thumbnail and instance.image.url != \
            instance.review.image_thumb_url:
        instance.review.image_thumb_url = instance.image.url
        instance.review.save()


@receiver(models.signals.pre_delete, sender=ReviewImage)
def reviewimage_pre_delete(sender, instance, *args, **kwargs):
    instance.image.delete(save=False)
    if instance.thumbnail:
        if len(sender.objects.filter(review=instance.review)) != 1:
            new_thumb_image = sender.objects.exclude(id=instance.id).filter(
                review=instance.review_id)[0]
            new_thumb_image.thumbnail = True
            new_thumb_image.save()
        else:
            instance.review.image_thumb_url = instance.review.product.image.url
            instance.review.save()


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

    def save(self, *args, **kwargs):
        if not self.id and self.image:
            self.image = compress(self.image)
        return super(Advertisement, self).save(*args, **kwargs)


class Promotion(models.Model):

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    title = models.CharField(max_length=30)
    code = models.CharField(max_length=30)
    current = models.BooleanField(default=0)

    def __str__(self):
        return self.title


class NewsletterEmail(models.Model):

    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.email


def compress(image, quality=65):
    img = Img.open(BytesIO(image.read()))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img.thumbnail((image.width / 1.5, image.height / 1.5
                   ), Img.ANTIALIAS)
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality)
    output.seek(0)
    return InMemoryUploadedFile(output, 'ImageField', "%s.jpg" %
                                image.name.split('.')[0],
                                'image/jpeg', img.size, None)
