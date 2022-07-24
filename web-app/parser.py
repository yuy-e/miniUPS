import world_ups_pb2
import ups_amazon_pb2

from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint


def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, False)
    return b''.join(data)

def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint(data, 0)[0]


# create UConnect msg
def createUConnect(Uconnect, id, in_x, in_y, truck_num):
    if(id != None):
        Uconnect.worldid = id
    for num in range(0, truck_num):
        truck = Uconnect.trucks.add()
        truck.id = num
        truck.x = in_x
        truck.y = in_y
    Uconnect.isAmazon = False
    return 

""" For UCommands to World"""
# create UGoPickup msg
def addUGoPickUp(Ucommand, tid, id, seq):
    UgoPickup = Ucommand.pickups.add();
    UgoPickup.truckid = tid
    UgoPickup.whid = id
    UgoPickup.seqnum = seq
    return 

# create UDeliveryLocation msg
def addUDeliveryLocation(UgoDeliver, packid, in_x, in_y):
    UdeliveryLoc = UgoDeliver.packages.add()
    UdeliveryLoc.packageid = packid
    UdeliveryLoc.x = in_x
    UdeliveryLoc.y = in_y
    return 

# create UGoDeliver msg
def addUGoDeliver(Ucommand, tid, seq):
    UgoDeliver = Ucommand.deliveries.add()
    UgoDeliver.truckid = tid
    # UgoDeliver.packages = packs
    UgoDeliver.seqnum = seq
    return 

# create UQuery msg
def addUQuery(Ucommand, tid, seq):
    Uquery = Ucommand.queries.add()
    Uquery.truckid = tid
    Uquery.seqnum = seq
    return 


""" For AMsgs with Amazon """
# create UTruckArrived msg
def addUTruckArrived(Umsgs, tid, packid, seq):
    newUTruckArrived = Umsgs.trucks.add()
    newUTruckArrived.truckid = tid
    newUTruckArrived.packageid = packid
    newUTruckArrived.seqnum = seq
    return
    
# create UFinishDelivery msg
def addUFinishDelivery(Umsgs, packid, seq):
    newUFinishDelivery = Umsgs.finish.add()
    newUFinishDelivery.packageid = packid
    newUFinishDelivery.seqnum = seq
    return 

# create AErr msg  
def addErr(Umsgs, error, origin, seq):
    newErr = Umsgs.err.add()
    newErr.err = error
    newErr.originseqnum = origin
    newErr.seqnum = seq
    return 
    
    