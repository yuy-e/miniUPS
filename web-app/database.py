# Functions about creating, querying Database
import os
import threading
from django.db.models import Q
import ups_amazon_pb2

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "miniUPS.settings")

import django
if django.VERSION >= (1, 7):
    django.setup()
    
from UPS.models import *

def addWorld(worldid):
    print("The received world_id is:" + str(worldid));
    try:
        World.objects.get_or_create(world_id=worldid)
    except Exception as e:
        print(e)
    return 
    
def searchWorld(worldid):
    try:
        res = World.objects.all().filter(world_id=worldid)
    except Exception as e:
        print(e)
    if not res:
        return False
    return True
    
def addTrucks(trucks):
    for num in range(0, len(trucks)):
        truck_id = trucks[num].id
        x = trucks[num].x
        y = trucks[num].y
        status = "idle"
        try:
            Truck.objects.get_or_create(truck_id=truck_id,x=x,y=y,status=status)
        except Exception as e:
            print(e)
    return

def addPackage(reqtruck, tid):
    print("Add Package to DB")
    # store new Pacakge info in db
    package_id = reqtruck.packageid
    print(type(reqtruck))
    # TO DO: owner_id
    owner_id = reqtruck.ups_name  # temp set as 0
    status = "wait"
    truck_id = tid
    deliver_x = reqtruck.buyer_x
    deliver_y = reqtruck.buyer_y
    wh_x = reqtruck.warehouse.x
    wh_y = reqtruck.warehouse.y
    des  = reqtruck.product[0].description
    count = reqtruck.product[0].count
    print("execute here")
    try:
        Package.objects.get_or_create(package_id=str(package_id), owner_id=owner_id, status=status, truck_id=str(truck_id), deliver_x=str(deliver_x), deliver_y=str(deliver_y), wh_x=str(wh_x), wh_y=str(wh_y),description=des, count=str(count))
    except Exception as e:
        print(e)
    print("Added Package to DB")
    return

"""
def main():
    reqtruck_msg = ups_amazon_pb2.AReqTruck()
    initwarehouse_msg = ups_amazon_pb2.AInitWarehouse()
    product_msg = reqtruck_msg.product.add()
    product_msg.id = 1
    product_msg.description = "des"
    product_msg.count = 1
    reqtruck_msg.packageid= 123
    reqtruck_msg.buyer_x = 100
    reqtruck_msg.buyer_y = 100
    reqtruck_msg.sequenceNum = 12345

    addPackage(reqtruck_msg,0)
"""

