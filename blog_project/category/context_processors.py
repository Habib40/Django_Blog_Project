from .models import Category

def menue_links(request):
    links = Category.objects.all()
    return dict(links=links)