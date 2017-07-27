from django.shortcuts import render

# Create your views here.
from random import randint

from django.http import HttpResponse, Http404
from django.template import loader, RequestContext, Context
from django.shortcuts import render, get_object_or_404, render_to_response

from .models import *


def main(request):
    latest_review_list = Review.objects.order_by('-created')[:4]
    popular_review_list = Review.objects.order_by('-views')[:5]
    all_ads = Advertisement.objects
    ads = [
        all_ads.filter(slot=AdSlot.objects.get(number=1)),
        all_ads.filter(slot=AdSlot.objects.get(number=2)),
    ]
    ad_file_paths = []

    products = Product.objects.all()

    for product in products:
        product.update_rating_avg()

    for i in range(2):
        ads[i] = ads[i][randint(0, len(ads[i])-1)]
        ad_file_paths.append(ads[i].image.name[12:])

    context = {
        'latest_review_list': latest_review_list,
        'popular_review_list': popular_review_list,
        'top_rated_products': Product.objects.order_by('-score')[:5],
        'ad_file_paths': ad_file_paths,
        'ads': ads,
        'date': get_date(),
        'categories': Category.objects.all(),
    }

    return render(request, 'blog/main.html', context)


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


def detail(request, slug, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review.views += 1
    review.save()
    top_rated_products = Product.objects.order_by("-score")
    context = {
        'review': review,
        'date': get_date(),
        'categories': Category.objects.all(),
    }
    return render(request, 'blog/single_page.html', context)


def contact(request):
    context = {
        'date': get_date(),
        'categories': Category.objects.all(),
    }
    return render(request, 'blog/contact.html', context)


def error404(request):
    # response = render_to_response('blog/404', {},
    #                                context_instance=RequestContext(request))
    # response.status_code = 404
    template = loader.get_template('blog/404.html')
    context = Context({
        'message': 'All: %s' % request,
        'categories': Category.objects.all(),
        'date': get_date(),
        })

    # 3. Return Template for this view + Data
    return HttpResponse(content=template.render(context),
                        content_type='text/html; charset=utf-8', status=404)

