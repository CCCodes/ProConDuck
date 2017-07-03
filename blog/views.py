from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

from .models import Review


def main(request):
    latest_review_list = Review.objects.order_by('-date')
    context = {
        'latest_review_list': latest_review_list,
    }

    return render(request, 'blog/main.html', context)


def detail(request, review_id):
    context = {
        'review': Review.objects.get(pk=review_id),
    }
    return render(request, 'blog/detail.html', context)
