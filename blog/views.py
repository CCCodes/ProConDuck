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
        all_ads.filter(slot=AdSlot.objects.get(pk=1)),
        all_ads.filter(slot=AdSlot.objects.get(pk=2)),
        all_ads.filter(slot=AdSlot.objects.get(pk=3)),
        all_ads.filter(slot=AdSlot.objects.get(pk=4)),
    ]

    for i in range(4):
        ads[i] = ads[i][randint(0, len(ads[i])-1)].image.name[12:]

    context = {
        'latest_review_list': latest_review_list,
        'ad1': ads[0],
        'ad2': ads[1],
        'ad3': ads[2],
        'ad4': ads[3],
    }

    return render(request, 'blog/main.html', context)


def detail(request, review_id):
    context = {
        'review': get_object_or_404(Review, pk=review_id),
    }
    return render(request, 'blog/detail.html', context)
