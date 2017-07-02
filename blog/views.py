from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse


def main(request):
    return HttpResponse("This is the blog")


def detail(request, product_id):
    return HttpResponse("This is product " + product_id)
