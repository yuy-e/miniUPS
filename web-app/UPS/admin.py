from django.contrib import admin

# Register your models here.
from .models import Package, Truck, World

admin.site.register(Package)
admin.site.register(Truck)
admin.site.register(World)
