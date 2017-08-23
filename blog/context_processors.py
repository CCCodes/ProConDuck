import urllib.request, io
from PIL import Image

from django.contrib.staticfiles import finders
from django.http import HttpResponse

from .models import *


def default(request):

    all_ads = Advertisement.objects
    ads = [
        all_ads.filter(slot=AdSlot.objects.get(number=1)),
        all_ads.filter(slot=AdSlot.objects.get(number=2)),
    ]

    ad_paths = {
        ads[0][0].name: {
            'link': ads[0][0].link,
            'image': ads[0][0].image
        },
        ads[1][0].name: {
            'link': ads[1][0].link,
            'image': ads[1][0].image
        }
    }

    return dict(
        latest_review_list=Review.objects.order_by('-created')[:4],
        popular_review_list=Review.objects.order_by('-views')[:5],
        ads=ad_paths,
        date=get_date(),
        categories=Category.objects.annotate(num_p=Count('product')).order_by(
            '-num_p'),
        promotions=Promotion.objects.filter(current=True),

    )


def get_date():
    weekdays = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday',
    ]
    months = [
        0,
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December',
    ]
    today = datetime.datetime.today()
    date = {
        'weekday': weekdays[today.weekday()],
        'month': months[today.month],
        'date': today.day,
        'year': today.year,
    }
    return date

