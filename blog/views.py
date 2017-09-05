from itertools import chain
from math import ceil
from smtplib import SMTPAuthenticationError
from PIL import Image
from io import BytesIO, StringIO
import urllib.request

from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader, RequestContext, Context
from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.sitemaps import Sitemap
from django.utils.datastructures import MultiValueDictKeyError

from .models import *


def main(request):
    featured_reviews = Review.objects.filter(featured=True)

    context = {
        'display_categories': display_categories(),
        'display_categories_names': Category.objects.annotate(num_p=Count(
            'product')).order_by(
            '-num_p').values('name'),
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
            return HttpResponseRedirect(reverse('blog:signup',
                                                kwargs={'success': 'true'}))
        else:
            return HttpResponseRedirect(reverse('blog:signup',
                                                kwargs={'success': 'false'}))
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.


def display_categories():

    categories_product_sort = Category.objects.annotate(
        num_p=Count('product')).order_by('-num_p')
    result = []

    for i in range(3):
        products = categories_product_sort[i].product_set.order_by(
            '-score')
        result.append([product_.review_set.order_by(
            '-views') for product_ in products if len(product_.review_set.all()
                                                      ) != 0])

    return result


def review(request, review_slug):
    display_review = get_object_or_404(Review, slug=review_slug)
    display_review.views += 1
    display_review.save()
    related = Product.objects.get(pk=display_review.product_id
                                  ).review_set.exclude(slug=review_slug)

    # get reviews in products in same category except for current review
    for product_ in Category.objects.get(
            pk=display_review.product.category_id).product_set.exclude(
            pk=display_review.product_id):
        related = list(chain(related, product_.review_set.all()))

    context = {
        'review': display_review,
        'related_reviews': related,
        'image_link': display_review.image_thumb_url.replace('%', '%25'),
        'all_images': ReviewImage.objects.filter(review=display_review).all(),
        'links': get_links(display_review.product)
    }
    return render(request, 'blog/single_page.html', context)


def all_products(request):
    category_filter = [('All products', 'all')]
    for category_ in Category.objects.all():
        category_filter.append((category_.name, category_.slug))
    sort_products_ = ['Most reviews',
                      'Newest',
                      'Highest rated'
                      ]
    if request.GET:
        try:
            category_filter.insert(0, category_filter.pop(
                [tup[1] for tup in category_filter].index(
                    request.GET['category'])))
            sort_products_.insert(0, sort_products_.pop(sort_products_.index(
                request.GET['sort_by'])))

        # redirects bad get requests
        except (ValueError, MultiValueDictKeyError):
            return HttpResponseRedirect(reverse('blog:all_products'))

    products_sort = Product.objects.all()

    if category_filter[0][1] != 'all':
        products_sort = Category.objects.get(slug=category_filter[0][1]
                                             ).product_set.all()

    if sort_products_[0] == 'Most reviews':
        products_sort = products_sort.annotate(num_r=Count('review')).order_by(
            '-num_r')
    elif sort_products_[0] == 'Newest':
        products_sort = products_sort.order_by('-created')
    elif sort_products_[0] == 'Highest rated':
        products_sort = products_sort.order_by('-score')

    context = {
        'products': products_sort,
        'category_filter': category_filter,
        'sort_products': sort_products_,
    }
    return render(request, 'blog/category.html', context)


def all_reviews(request):
    category_filter = [('All reviews', 'all')]
    for category_ in Category.objects.all():
        category_filter.append((category_.name, category_.slug))
    sort_reviews_ = ['Most viewed',
                     'Newest',
                     'Most favorable',
                     'Most critical',
                     ]
    if request.GET:
        try:
            category_filter.insert(0, category_filter.pop(
                [tup[1] for tup in category_filter].index(
                    request.GET['category'])))
            sort_reviews_.insert(0, sort_reviews_.pop(sort_reviews_.index(
                request.GET['sort_by'])))

        # redirects bad get requests
        except (ValueError, MultiValueDictKeyError):
            return HttpResponseRedirect(reverse('blog:all_products'))

    if category_filter[0][1] != 'all':
        products_ = Category.objects.get(slug=category_filter[0][1]
                                         ).product_set.all()
        reviews_sort = Product.objects.filter(id__in=products_)
    else:
        reviews_sort = Review.objects.all()

    if sort_reviews_[0] == 'Most viewed':
        reviews_sort = reviews_sort.order_by('-views')
    elif sort_reviews_[0] == 'Most favorable':
        reviews_sort = reviews_sort.order_by('-score')
    elif sort_reviews_[0] == 'Most critical':
        reviews_sort = reviews_sort.order_by('score')
    elif sort_reviews_[0] == 'Newest':
        reviews_sort = reviews_sort.order_by('-created')

    context = {
        'reviews': reviews_sort,
        'category_filter': category_filter,
        'sort_products': sort_reviews_,
    }
    return render(request, 'blog/all_reviews.html', context)


def product(request, product_slug):
    product_ = get_object_or_404(Product, slug=product_slug)
    category_products = product_.category.product_set.all()
    current_index = list(category_products).index(product_)

    related_products = []
    previous_index = current_index - 1
    next_index = current_index + 1

    if previous_index < 0:
        if len(category_products) - 1 == current_index:
            related_products.append(None)
        else:
            related_products.append(category_products[len(category_products
                                                          ) - 1])
    else:
        related_products.append(category_products[previous_index])

    if next_index > len(category_products) - 1:
        if current_index == 0:
            related_products.append(None)
        else:
            related_products.append(category_products[0])
    else:
        related_products.append(category_products[next_index])
    context = {
        'product': product_,
        'links': get_links(product_),
        'related_products': related_products
    }
    reviews = context['product'].review_set.order_by('-views')
    context['reviews1'] = reviews[:ceil(len(reviews)/2)]
    context['reviews2'] = reviews[ceil(len(reviews)/2):]

    return render(request, 'blog/product.html', context)


def get_links(prod):
    links = []
    for link in prod.links.split('\r\n'):
        label = link.split('-')[0]
        url = link.split('-')[1]
        links.append((label, url))
    return links


def promotions(request):
    promos = Promotion.objects.all()

    promo_links = []
    for promo in promos:

        # get the amazon link (should be first link)
        promo_links.append((promo, promo.product.links.split('\r\n')[0].split(
            '-')[1]))

    context = {
        'promos1': promo_links[:ceil(len(promos)/2)],
        'promos2': promo_links[ceil(len(promos)/2):],
    }
    return render(request, 'blog/promotions.html', context)


def tos(request):
    return render(request, 'blog/tos.html', {})


def privacy(request):
    return render(request, 'blog/privacy.html', {})


def ethics(request):
    return render(request, 'blog/ethics.html', {})


def contact(request):
    return render(request, 'blog/contact.html', {})


def faq(request):
    return render(request, 'blog/faq.html', {})


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
        return HttpResponseRedirect(reverse('blog:signup', kwargs={
            'success': 'false'}))
    return HttpResponseRedirect(reverse('blog:contact'))


class ReviewSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Review.objects.all()

    def lastmod(self, obj):
        return obj.created


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created


def error404(request):
    context = {
        'message': 'All: %s' % request,
        }

    # 3. Return Template for this view + Data
    return HttpResponse(content=render(request, '404.html', context),
                        status=404)


def error500(request):
    context = {
        'message': 'All: %s' % request,
        }

    # 3. Return Template for this view + Data
    return HttpResponse(content=render(request, '500.html', context),
                        status=500)
