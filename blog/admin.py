from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(ReviewImage)
admin.site.register(Advertisement)
admin.site.register(AdSlot)
admin.site.register(Category)
admin.site.register(Promotion)
admin.site.register(NewsletterEmail)
admin.site.register(Reviewer)
