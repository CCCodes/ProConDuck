from django.contrib import admin

# Register your models here.

from .models import Company, Product, Review

admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Review)
