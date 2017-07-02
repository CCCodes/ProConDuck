from django.db import models

# Create your models here.


class Company(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):

    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    link = models.URLField()

    def __str__(self):
        return self.name


class Review(models.Model):

    # cascade will delete reviews if product is deleted
    # protect only lets you delete product if all reviews are deleted
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    title = models.CharField(max_length=100)
    reviewer_name = models.CharField(max_length=50)
    date = models.DateField()
    score = models.IntegerField()
    image = models.ImageField()
    video_link = models.URLField()
    review = models.TextField()

    def __str__(self):
        return self.title

