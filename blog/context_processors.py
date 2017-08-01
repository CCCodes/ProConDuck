from .models import *


def default(request):

    all_ads = Advertisement.objects
    ads = [
        all_ads.filter(slot=AdSlot.objects.get(number=1)),
        all_ads.filter(slot=AdSlot.objects.get(number=2)),
    ]
    return dict(
        latest_review_list=Review.objects.order_by('-created')[:4],
        popular_review_list=Review.objects.order_by('-views')[:5],
        featured_reviews=Review.objects.filter(featured=True),
        ads=ads,
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

