from itertools import chain
from random import randint

from django.core.mail import send_mail
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext, Context
from django.shortcuts import render, get_object_or_404, render_to_response

from .models import *


def main(request):
    all_ads = Advertisement.objects
    ads = [
        all_ads.filter(slot=AdSlot.objects.get(number=1)),
        all_ads.filter(slot=AdSlot.objects.get(number=2)),
    ]
    ad_file_paths = []

    for i in range(2):
        ads[i] = ads[i][randint(0, len(ads[i])-1)]
        ad_file_paths.append(ads[i].image.name[12:])

    context = {
        'top_rated_products': Product.objects.order_by('-score'),
        'ad_file_paths': ad_file_paths,
        'display_categories': display_categories(),
    }

    return render(request, 'blog/main.html', context)


def signup(request, success=None):
    if success is not None:
        if success == 'true':
            message = "You have successfully signed up for the newsletter. " \
                      "Thanks!"
        elif success == 'false':
            message = "Sorry, something went wrong with submitting your " \
                      "information."
        else:
            raise Http404
        return render(request, 'blog/signup.html', {"message": message})
    try:
        name = request.POST['name']
        email = request.POST['email']
    except KeyError:
        # Redisplay the question voting form.
        return HttpResponseRedirect(
            reverse('blog:signup', kwargs={'success': 'false'}))
    else:
        emails = [o.email for o in NewsletterEmail.objects.all()]
        if email not in emails and len(name) < 50 and 5 <= len(email) < 100:
            NewsletterEmail.objects.create(name=name, email=email)
            send_mail(
                'Welcome ' + name,
                'Hi %s,\nWelcome to the Pro Con Duck community.' % name,
                'proconduck@gmail.com',
                [email],
                fail_silently=False,
            )
            return HttpResponseRedirect(reverse('blog:signup', kwargs={'success': 'true'}))
        else:
            return HttpResponseRedirect(reverse('blog:signup', kwargs={'success': 'false'}))
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.


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
    related = Product.objects.get(pk=review.product_id).review_set.exclude(
        pk=review_id)
    for product in Category.objects.get(
            pk=review.product.category_id).product_set.exclude(
            pk=review.product_id):
        related = list(chain(related, product.review_set.all()))
    context = {
        'review': review,
        'related_reviews': related,
    }
    return render(request, 'blog/single_page.html', context)


def tos(request):
    context = {}
    return render(request, 'blog/tos.html', context)


def contact(request):
    context = {
    }
    return render(request, 'blog/contact.html', context)


def error404(request):
    # response = render_to_response('blog/404', {},
    #                                context_instance=RequestContext(request))
    # response.status_code = 404
    context = {
        'message': 'All: %s' % request,
        }

    # 3. Return Template for this view + Data
    return HttpResponse(content=render(request, '404.html', context),
                        status=404)

