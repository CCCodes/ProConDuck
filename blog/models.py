import datetime

import django
from django.core.urlresolvers import reverse
from django.db.models import Avg, Count
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.db import models

# Create your models here.


class Company(models.Model):

    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Category(models.Model):

    name = models.CharField(max_length=20)
    number = models.IntegerField(default=1, unique=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return "%d - %s" % (self.number, self.name)


class Product(models.Model):

    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,
                                 null=True, blank=True, default=0)
    name = models.CharField(max_length=100)
    score = models.FloatField(editable=False, default=0)
    link = models.URLField()
    # image = models.ImageField(blank=True, upload_to="images")
    image = models.CharField(max_length=100, default="blog/media/Capture.PNG")

    def __str__(self):
        return self.name

    def update_rating_avg(self):
        #Product.objects.select_related().annotate(count_reviews=Count('review'))
        #if 0 != Product[0].count_reviews:
        self.score = self.review_set.aggregate(Avg('score'))['score__avg']

        self.score = 10
        self.save()


class Review(models.Model):

    featured = models.BooleanField(default=False)

    # cascade will delete reviews if product is deleted
    # protect only lets you delete product if all reviews are deleted
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    title = models.CharField(max_length=100)
    reviewer_name = models.CharField(max_length=50)
    # date = models.DateField(auto_now_add=True)
    score = models.IntegerField(default=10)
    # image = models.ImageField(blank=True, upload_to="images")
    image = models.CharField(max_length=100, default="blog/media/robotics.png")
    video_link = models.URLField(blank=True)
    review = models.TextField()
    views = models.IntegerField(default=0)  # editable=False)

    created = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified = models.DateTimeField(blank=True, null=True, default=django.utils.timezone.now)

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
        return super(Review, self).save(*args, **kwargs)


class AdSlot(models.Model):
    number = models.IntegerField(default=1)
    image_width = models.IntegerField()
    image_height = models.IntegerField()

    def __str__(self):
        return "%d - %d x %d" % (self.number, self.image_width, self.image_height)


class Advertisement(models.Model):

    selected = models.BooleanField(default=True)
    slot = models.ForeignKey(AdSlot, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images")
    link = models.URLField()

    def __str__(self):
        return self.name

    def remove_on_image_update(self):
        try:
            # is the object in the database yet?
            obj = Advertisement.objects.get(id=self.id)
        except Advertisement.DoesNotExist:
            # object is not in db, nothing to worry about
            return
        # is the save due to an update of fathe actual image file?
        if obj.image and self.image and obj.image != self.image:
            # delete the old image file from the storage in favor of the new file
            obj.image.delete()

    def delete(self, *args, **kwargs):
        # object is being removed from db, remove the file from storage first
        self.image.delete()
        return super(Advertisement, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        # object is possibly being updated, if so, clean up.
        self.remove_on_image_update()
        return super(Advertisement, self).save(*args, **kwargs)



