from django.shortcuts import render, get_object_or_404
from .models import MenuItem

def home(request):
    return render(request, 'menu/home.html')

def menu(request):
    items = MenuItem.objects.all().order_by('name')  # Alphabetical order
    return render(request, 'menu/menu.html', {'items': items})

def menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    return render(request, 'menu/menu_item.html', {'item': item})

def about(request):
    return render(request, 'about.html')