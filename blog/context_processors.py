from django.contrib.staticfiles import finders

from .models import *


def default(request):

    all_ads = Advertisement.objects
    ads = [
        all_ads.filter(slot=AdSlot.objects.get(number=1)),
        all_ads.filter(slot=AdSlot.objects.get(number=2)),
    ]

    ad_paths = {
        ads[0][0].name: {'link': ads[0][0].link},
        ads[1][0].name: {'link': ads[1][0].link}
    }

    # prevent 500 error if database images don't exist
    if finders.find("blog/images/" + ads[0][0].image) is not None:
        ad_paths[ads[0][0].name]['image'] = ads[0][0].image
    else:
        ad_paths[ads[0][0].name]['image'] = "addbanner_728x90_V1.jpg"
    if finders.find("blog/images/" + ads[1][0].image) is not None:
        ad_paths[ads[1][0].name]['image'] = ads[1][0].image
    else:
        ad_paths[ads[1][0].name]['image'] = "add_img.jpg"

    return dict(
        latest_review_list=Review.objects.order_by('-created')[:4],
        popular_review_list=Review.objects.order_by('-views')[:5],
        ads=ad_paths,
        date=get_date(),
        categories=Category.objects.all(),
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

