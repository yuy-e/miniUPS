from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class World(models.Model):
    world_id = models.IntegerField(max_length=50, primary_key=True)

class Truck(models.Model):
    truck_id = models.AutoField(max_length=50, primary_key=True)
    x = models.IntegerField(max_length=20)
    y = models.IntegerField(max_length=20)
    """
    STATUS_CHOICES = (
        ('idle', 'IDLE'),
        ('traveling', 'TRAVELING'),
        ('arrive', 'ARRIVE'),
        ('loading', 'LOADING'),
        ('delivering', 'DELIVERING')
    )"""
    status = models.CharField(max_length=50)

class Package(models.Model):
    package_id = models.IntegerField(max_length=50, primary_key=True)
    owner_id = models.CharField(max_length=50, null = True)
    # owner_id = models.ForeignKey(User, null = True, on_delete=models.CASCADE)
    """STATUS_CHOICES = (
        ('wait', 'WAIT'),  # wait for picking up
        ('delivering', 'DELIVERING'),  # delivering
        ('delivered', 'DELIVERED')  # delivered
    )"""
    status = models.CharField(max_length=50)
    truck_id = models.IntegerField(max_length=50, null=True)
    # truck_id = models.ForeignKey(Truck, null=True, on_delete=models.CASCADE)
    # delivery address
    deliver_x = models.IntegerField(max_length=20)
    deliver_y = models.IntegerField(max_length=20)
    # warehouse address
    wh_x = models.IntegerField(max_length=20, null=True)
    wh_y = models.IntegerField(max_length=20, null=True)
    # product info
    description = models.CharField(max_length=100, null=True)
    count = models.IntegerField(max_length=50, null=True)
