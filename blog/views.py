from django.shortcuts import render

# Create your views here.
from random import randint

from django.http import HttpResponse, Http404
from django.template import loader
from django.shortcuts import render, get_object_or_404

from .models import *


def main(request):
    latest_review_list = Review.objects.order_by('-date')
    all_ads = Advertisement.objects
    ads = [
        all_ads.filter(slot=AdSlot.objects.get(number=1)),
        all_ads.filter(slot=AdSlot.objects.get(number=2)),
        all_ads.filter(slot=AdSlot.objects.get(number=3)),
        all_ads.filter(slot=AdSlot.objects.get(number=4)),
    ]
    ad_file_paths = []

    for i in range(4):
        ads[i] = ads[i][randint(0, len(ads[i])-1)]
        ad_file_paths.append(ads[i].image.name[12:])

    context = {
        'latest_review_list': latest_review_list,
        'ad_file_paths': ad_file_paths,
        'ads': ads,
    }

    return render(request, 'blog/main.html', context)


def detail(request, review_id):
    context = {
        'review': get_object_or_404(Review, pk=review_id),
    }
    return render(request, 'blog/single_page.html', context)
