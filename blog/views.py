from itertools import chain
from random import randint
from smtplib import SMTPAuthenticationError

from django.core.mail import send_mail
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext, Context
from django.shortcuts import render, get_object_or_404, render_to_response

from .models import *


def main(request):
    featured_reviews = Review.objects.filter(featured=True)

    context = {
        'top_rated_products': Product.objects.order_by('-score'),
        'display_categories': display_categories(),
        'featured_reviews': featured_reviews,
    }

    return render(request, 'blog/main.html', context)


def signup(request, success=None):
    if success is not None:
        if success == 'true':
            message = "You have successfully signed up for the newsletter."
            header_main = "Congratulations"
        elif success == 'false':
            message = "Sorry, something went wrong with submitting your " \
                      "information."
            header_main = "We Are Sorry"
        else:
            raise Http404
        context = {
            'message': message,
            'header_main': header_main
        }
        return render(request, 'blog/signup.html', context)
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


def review(request, slug, review_id):
    display_review = get_object_or_404(Review, pk=review_id)
    display_review.views += 1
    display_review.save()
    related = Product.objects.get(pk=display_review.product_id).review_set.exclude(
        pk=review_id)
    for product in Category.objects.get(
            pk=display_review.product.category_id).product_set.exclude(
            pk=display_review.product_id):
        related = list(chain(related, product.review_set.all()))
    context = {
        'review': display_review,
        'related_reviews': related,
        'image_link': display_review.image.url.replace('%', '%25')
    }
    return render(request, 'blog/single_page.html', context)


def category(request, category_slug):
    context = {
        'category': get_object_or_404(Category, slug=category_slug),
    }
    context['products'] = context['category'].product_set.annotate(num_r=Count('review')).order_by('-num_r')
    return render(request, 'blog/category.html', context)


def detail(request, product_slug):
    context = {
        'item': get_object_or_404(Product, slug=product_slug),
    }
    context['item_subset'] = context['item'].review_set.order_by('-views')
    return render(request, 'blog/category.html', context)


def tos(request):
    return render(request, 'blog/tos.html', {})


def privacy(request):
    return render(request, 'blog/privacy.html', {})


def contact(request):
    return render(request, 'blog/contact.html', {})


def about(request):
    return render(request, 'blog/about.html', {})


def contact_submit(request):
    try:
        send_mail(
            'Site Contact from ' + request.POST['email'],
            'Name: ' + request.POST['name'] + '\nEmail: ' +
            request.POST['email'] + '\nMessage: ' + request.POST['message'],
            'proconduck@support.com',
            ['support@proconduck.com'],
            fail_silently=False
        )
    except SMTPAuthenticationError as e:
        print(e)
        return HttpResponseRedirect(reverse('blog:signup', kwargs={'success':'false'}))
    return HttpResponseRedirect(reverse('blog:contact'))


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

