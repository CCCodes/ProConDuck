from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.template import loader

from .models import Review


def main(request):
    latest_review_list = Review.objects.order_by('-date')
    template = loader.get_template('blog/main.html')
    context = {
        'latest_review_list': latest_review_list,
    }

    return HttpResponse(template.render(context, request))


def detail(request, review_id):
    template = loader.get_template('blog/detail.html')
    context = {
        'review': Review.objects.get(pk=review_id),
    }
    return HttpResponse(template.render(context, request))
