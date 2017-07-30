from itertools import chain
from random import randint

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext, Context
from django.shortcuts import render, get_object_or_404, render_to_response

from .models import *


def main(request):
    latest_review_list = Review.objects.order_by('-created')[:4]
    popular_review_list = Review.objects.order_by('-views')[:5]
    featured_reviews = Review.objects.filter(featured=True)
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
        'promotions': Promotion.objects.filter(current=True),
        'latest_review_list': latest_review_list,
        'popular_review_list': popular_review_list,
        'featured_reviews': featured_reviews,
        'top_rated_products': Product.objects.order_by('-score'),
        'ad_file_paths': ad_file_paths,
        'ads': ads,
        'date': get_date(),
        'categories': Category.objects.all(),
        'display_categories': display_categories(),
    }

    return render(request, 'blog/main.html', context)


def signup(request):
    try:
        name = request.POST['name']
        email = request.POST['email']
    except KeyError:
        # Redisplay the question voting form.
        pass
    else:
        if len(name) < 50 and 5 <= len(email) < 100:
            NewsletterEmail.objects.create(name=name, email=email)
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('blog:main'))


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


def display_categories():

    result = []

    for i in range(3):
        products = Category.objects.get(number=i).product_set.order_by('-score')
        result.append([product.review_set.order_by('-views') for product in products])

    return result


def detail(request, slug, review_id):
    review = get_object_or_404(Review, pk=review_id)
    review.views += 1
    review.save()
    popular_review_list = Review.objects.exclude(pk=review_id).order_by(
        '-views')[:4]
    top_rated_products = Product.objects.order_by('-score')
    related = Product.objects.get(pk=review.product_id).review_set.exclude(
        pk=review_id)
    for product in Category.objects.get(
            pk=review.product.category_id).product_set.exclude(
            pk=review.product_id):
        related = list(chain(related, product.review_set.all()))
    context = {
        'review': review,
        'date': get_date(),
        'categories': Category.objects.all(),
        'related_reviews': related,
        'popular_review_list': popular_review_list
    }
    return render(request, 'blog/single_page.html', context)


def tos(request, slug, review_id):
    top_rated_products = Product.objects.order_by("-score")
    context = {
        'review': Review.objects.get(pk=review_id),
        'date': get_date(),
        'categories': Category.objects.all(),
    }
    return render(request, 'blog/tos.html', context)


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

