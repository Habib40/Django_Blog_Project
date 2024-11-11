from django.shortcuts import render
from django.http import HttpResponse
from .models import Category
# Create your views here.

def cat(request):
    categories = Category.objects.all()  # Fetch all categories from the database
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'base.html', context)