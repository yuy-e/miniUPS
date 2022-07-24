import os
import psycopg2
import socket
import urllib.parse as up # For Remote DataBase
import ups_amazon_pb2 
import world_ups_pb2
import threading
import time
import smtplib

from concurrent.futures import ThreadPoolExecutor
from database import *
from parser import *
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _EncodeVarint


amazon_port = 55555

seqnum = 1
acks = []
seqnum_lock = threading.Lock()
ack_lock = threading.Lock()

def connectToFont():
    
    return 0

# Connect to the Database
def connectToDB():
    """ Connect to remote DataBase """
    up.uses_netloc.append("postgres")
    # url = up.urlparse(os.environ["postgres://hxgxgzvj:Pa55rQ89m1wSI9dDQnJo6LLKAxY8v8TD@rajje.db.elephantsql.com/hxgxgzvj"])
    # conn = psycopg2.connect(user='hxgxgzvj',password='Pa55rQ89m1wSI9dDQnJo6LLKAxY8v8TD',host='rajje.db.elephantsql.com',port=5432)
    """ Connect to local DataBase"""
    conn = psycopg2.connect(database="upsdb", user='postgres', password='abc123', host='localhost', port='5432')
    connection = conn.cursor()
    print("Successfully connect to Database")
    # conn.close()
    # clear database
    connection = conn.cursor()
    connection.execute('delete from \"UPS_truck\";')
    connection.execute('delete from \"UPS_world\";')
    connection.execute('delete from \"UPS_package\";')
    conn.commit()
    return conn

# Connect to the World Simulator
def connectToWorldSim():
    # create an INET, STREAMing socket - TCP
    world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            world_socket.connect(("vcm-26470.vm.duke.edu", 12345))
        except Exception:
            print("Cannnot connect to the World Server")
            continue
        else:
            break
    return world_socket

# Connect to the World 
def tryConnectToWorld(worldid, world_socket):
    # if the world exists
    global world_id
    Uconnect = world_ups_pb2.UConnect()
    if worldid is None:
        # create new UConnect msg
        createUConnect(Uconnect, None, 2, 2, 10)
        while True:
            # send UConnect to request creating World
            sendMsg(Uconnect, world_socket)
            # receive Uconnected to get WorldID and save it to DB
            Uconnected = recMsg(world_socket, "UConnected")
            print("Result of UConnected: %s" % Uconnected.result)
            if Uconnected.result == "connected!":
                world_id = Uconnected.worldid
                # print(world_id)
                # sendMsg(world_id, amazon_socket)
                break
        # print("Create the new world")
        addWorld(Uconnected.worldid)
        addTrucks(Uconnect.trucks)
        # Test
        if searchWorld(worldid):
            createUConnect(Uconnect, worldid, 0, 0, 0)
            # connect to the world server
            while True:
                # send UConnect to request connection with World
                sendMsg(Uconnect, world_socket)
                # receive Uconnected response
                Uconnected = recMsg(world_socket, "UConnected")
                print("Result of UConnected: %s" % Uconnected.result)
                print("World_id of UConnected: %d" % Uconnected.worldid)
                if Uconnected.result == "connected!":
                    world_id = Uconnected.worldid
                    break

    else:
        if searchWorld(worldid):
            createUConnect(Uconnect, worldid, 0, 0, 0)
            # connect to the world server
            while True:
                # send UConnect to request connection with World
                sendMsg(Uconnect, world_socket)
                # receive Uconnected response
                Uconnected = recMsg(world_socket, "UConnected")
                print("Result of UConnected: %s" % Uconnected.result)
                print("World_id of UConnected: %d" % Uconnected.worldid)
                if Uconnected.result == "connected!":
                    world_id = Uconnected.worldid
                    break
        else:
            print("The world does not exist.")

# Connect to Amazon
def connectToAmazon():
    # create an INET, STREAMing socket - TCP
    amazon_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # amazon_socket.connect(("vcm-26537.vm.duke.edu", amazon_port))
    amazon_socket.connect(("vcm-24288.vm.duke.edu", amazon_port))
    # send world_id to Amazon
    print("Send world_id to Amazon:",world_id)
    data = str(world_id)
    amazon_socket.send(data.encode('utf-8'))
    return amazon_socket

# Close Connectoin
def closeConnection(socket):
    Ucommand = world_ups_pb2.UCommands()
    Ucommand.disconnect = True
    sendMsg(Ucommand, world_socket)
    return

# send Email


###############################################################################################
""" Send and Receive any Msg from World and Amazon """
# send any messages to the World (UConnet, UCommands) or Amazon(UMsgs)
def sendMsg(message, all_socket):
    print("--------Send Msg------")
    print(message)
    msg = message.SerializeToString()
    size = encode_varint(len(msg))
    all_socket.sendall(size+msg)
    return

# receive any messages from the World (UConnected, UReponses) or Amazon(AMsgs)
def recMsg(all_socket, flag):
    print("--------Receive Msg------")
    data = b''
    while True:
        try:
            data += all_socket.recv(1)
            size = decode_varint(data)
            break
        except IndexError:
            pass
    data = all_socket.recv(size)
    # From World
    if flag == "UConnected":
        Uconnected = world_ups_pb2.UConnected()
        Uconnected.ParseFromString(data)
        print(Uconnected)
        return Uconnected 
    elif flag == "UResponses":
        Uresponses = world_ups_pb2.UResponses()
        Uresponses.ParseFromString(data)
        print(Uresponses)
        return Uresponses
    # From Amazon
    elif flag == "AMsgs":
        Amsgs = ups_amazon_pb2.AMsgs()
        Amsgs.ParseFromString(data)
        print(Amsgs)
        return Amsgs
    else:
        print("Error: Invalid received Msg type!\n")

###############################################################################################
# handle messages(UResponses) from world
def world_function(world_socket, amazon_socket):
    executor = ThreadPoolExecutor(50)
    while True:
        Uresponses = recMsg(world_socket, "UResponses")
        for com_index in range(0, len(Uresponses.completions)):
            executor.submit(changeFinished, Uresponses.completions[com_index], world_socket, amazon_socket)
        for del_index in range(0, len(Uresponses.delivered)):
            executor.submit(changeDeliverStatus, Uresponses.delivered[del_index], world_socket, amazon_socket)
        if(Uresponses.HasField("finished")):
            executor.submit(closeConnection, Uresponses.finished, world_socket)
        for ack_index in range(0, len(Uresponses.acks)):
            executor.submit(checkAck, Uresponses.acks[ack_index])
        for truck_index in range(0, len(Uresponses.truckstatus)):
             executor.submit(changeTruckStatus, Uresponses.truckstatus[truck_index])
        for err_index in range(0, len(Uresponses.error)):
            executor.submit(handleError, Uresponses.error[err_index])
        

# handle messages from amazon
def amazon_function(amazon_socket, world_socket):
    executor = ThreadPoolExecutor(50)
    while True:
        Amsgs = recMsg(amazon_socket, "AMsgs")
        for req_index in Amsgs.reqtruck:
            print("ask for truck")
            executor.submit(askForTruck, req_index, amazon_socket, world_socket)
        for com_index in range(0, len(Amsgs.completeloading)):
            print("change loading status")
            executor.submit(changeLoadingStatus, Amsgs.completeloading[com_index], amazon_socket, world_socket)
        for ack_index in range(0, len(Amsgs.acks)):
            print("check ack")
            executor.submit(checkAck, Amsgs.acks[ack_index])
        for err_index in range(0, len(Amsgs.err)):
            print("print err")
            executor.submit(handleError, Amsgs.err[err_index])        


# Handle Messgages of UPS - World - Amazon
def handleMessages(world_socket, amazon_socket):
    world_thread = threading.Thread(target=world_function, args=(world_socket,amazon_socket))
    world_thread.start()
    amazon_thread = threading.Thread(target=amazon_function, args=(amazon_socket, world_socket))
    amazon_thread.start()


###############################################################################################
# acquire new Sequence with lock
def acquireNewSeq():
    seqnum_lock.acquire()
    global seqnum
    seqnum = seqnum + 1
    new_seq = seqnum;
    seqnum_lock.release()
    print("acquire new seqnum:", new_seq)
    return new_seq

###############################################################################################
""" Handle UResponses from World """

# send ack in UCommands back to World
def sendAckToWorld(ack, world_socket):
    Ucommand = world_ups_pb2.UCommands()
    Ucommand.acks.append(ack)
    sendMsg(Ucommand, world_socket)
    return 

# send ack in UMsgs back to Amazon
def sendAckToAmazon(ack, amazon_socket):
    Umsgs = ups_amazon_pb2.UMsgs()
    Umsgs.acks.append(ack)
    sendMsg(Umsgs, amazon_socket)
    return 

def changeFinished(completion, world_socket, amazon_socket):
    # send ack in UCommands back to World
    print("Send ack to World")
    sendAckToWorld(completion.seqnum, world_socket)
    # update truck status
    new_truck_id = completion.truckid
    print(new_truck_id)
    new_x = completion.x
    new_y = completion.y
    # for UGoPickUp
    if completion.status == "ARRIVE WAREHOUSE":
        print("The truck arrived at warehouse")
        try:
            print("try to update truck status")
            Truck.objects.all().filter(truck_id=new_truck_id).update(x=new_x, y=new_y,status="arrive")
            print("update truck status")
        except Exception as e:
            print(e)
        # send UTruckArrived to Amazon, inform Amazon to load
        pid = -1
        try:
            package = Package.objects.all().filter(truck_id=new_truck_id, status="wait")
            for pac in package:
                pid = pac.package_id
            print("Pacakge to load:", pid)
        except Exception as e:
            print(e)
        # load them together if multiple pacakges require the same truck
        Umsgs = ups_amazon_pb2.UMsgs()
        new_seq = acquireNewSeq()
        addUTruckArrived(Umsgs,new_truck_id, pid, new_seq)
        # waiting for ack from amazon, change truck status to "loading"
        while True:
            sendMsg(Umsgs, amazon_socket)
            time.sleep(10)
            if new_seq in acks:
                break
        # change truck status to loading
        print("truck is loading")
        try:
            Truck.objects.all().filter(truck_id=new_truck_id).update(x=new_x, y=new_y,status="loading")
        except Exception as e:
            print(e)
    # for UGoDeliver
    else: # UGoDliver
        try:
            # change truck status to idle
            print("truck is idle")
            Truck.objects.all().filter(truck_id=new_truck_id).update(x=new_x, y=new_y,status="idle")
        except Exception as e:
            print(e)
    return 
    
def changeDeliverStatus(delivered, world_socket, amazon_socket):
    # send ack in UCommands back to World
    sendAckToWorld(delivered.seqnum, world_socket)
    # update package status
    truck_id = delivered.truckid
    package_id = delivered.packageid
    Package.objects.all().filter(package_id=package_id).update(status="delivered")

    # inform the User the package is delivered
    
    msg = "Your Message is delivered."
    sendEmail(package_id, msg)
    print(msg)

    # send UMsgs to inform Amazon the package is delivered
    Umsgs = ups_amazon_pb2.UMsgs()
    new_seq = acquireNewSeq()
    addUFinishDelivery(Umsgs, package_id, new_seq)
    while True:
        sendMsg(Umsgs, amazon_socket)
        time.sleep(10)
        if new_seq in acks:
            break
    return

#  all deliveries are finished
def closeConnection(finished, world_socket):
    # Make sure finished is "True"
    if finished == True:
        world_socket.close()
    return

def checkAck(ack):
    # add response ACK to global ACK
    print("Add ack:", ack) 
    acks.append(ack)
    return

def changeTruckStatus(truckstatus):
    # send Ack to World
    sendAckToWorld(truckstatus.seqnum, world_socket)
    # qurey truckstatus - response
    truck_id = truckstatus.truckid
    status = truckstatus.status
    x = truckstatus.x
    y = truckstatus.y
    try:
        Truck.objects.all().filter(truck_id=truck_id).update(x=x,y=y,status=status)
    except Exception as e:
        print(e)
    return 
    
def handleError(error):
    # print error message
    print(error.err)
    
###############################################################################################
""" Handle AMsgs from Amazon """

def askForTruck(reqtruck, amazon_socket, world_socket):
    # send ACK to Amazon
    print(reqtruck)
    # print("send ack to amazon:", reqtruck.sequenceNum)
    sendAckToAmazon(reqtruck.sequenceNum, amazon_socket)
    # check if the user_name is exist
    """
    try:
        ups_name = reqtruck.ups_name
        isExist = User.objects.all().filter(username=ups_name)
        if not isExist:
            print("The ups name is not exist.")
            return None
    except Exception as e:
        print(e)
    """
    # send UCommands to inform World to send truck
    Ucommand = world_ups_pb2.UCommands()
    # get available truck
    while True:
        try:
            available_trucks = Truck.objects.all().filter(Q(status="idle") | Q(status="arrive") | Q(status="delivering"))
        except Exception as e:
            print(e)
        if available_trucks:
            tid = available_trucks[0].truck_id
            print("The available truck id:", tid)
            # save package info to database
            addPackage(reqtruck, tid)
            break
    whid = reqtruck.warehouse.id
    new_seq = acquireNewSeq()
    addUGoPickUp(Ucommand, tid, whid, new_seq)
    # update truck status to 'traveling'
    try:
        print("The truck is traveling")
        Truck.objects.all().filter(truck_id=tid).update(status="traveling")
    except Exception as e:
        print(e)
    while True:
        sendMsg(Ucommand, world_socket)
        time.sleep(10)
    # wait ack from world, and update truck status to 'traveling'
        if new_seq in acks:
            break
    return

    
def changeLoadingStatus(completeloading, amazon_socket, world_socket):
    # send ACK to Amazon
    sendAckToAmazon(completeloading.sequenceNum, amazon_socket)
    # change truck & package status to "delivering"
    try:
        print("update truck")
        Truck.objects.all().filter(truck_id=completeloading.truckid).update(status="delivering")
        print("update package")
        Package.objects.all().filter(package_id=completeloading.packageid).update(status="delivering")
    except Exception as e:
        print(e)
    # ask the World to deliver
    Ucommand = world_ups_pb2.UCommands()
    new_seq =  acquireNewSeq()
    addUGoDeliver(Ucommand, completeloading.truckid, new_seq)
    deliver_package = completeloading.packageid
    try:
        print("filter packages")
        pac = Package.objects.all().filter(package_id=deliver_package)
        for p in pac:
            x = p.deliver_x
            y = p.deliver_y
            addUDeliveryLocation(Ucommand.deliveries[0], deliver_package, x, y)
            break
    except Exception as e:
        print(e)
    while True:
        sendMsg(Ucommand, world_socket)
        time.sleep(10)
        if new_seq in acks:
            break
    return 

# Change Destination of package
def changePackageAddress(package_id, new_address_x, new_address_y, world_socket, amazon_socket):
    # package status should not be 'delivered'
    try:
        res = Package.objects.all().filter(package_id=package_id)
    except Exception as e:
        print(e)
    if res[0]:
        status = res[0].status
        if status == "delivered":
            print("Error: the package has already been delivered")
        else:
            # send UCommand to truck to change delivery address
            truckid = res[0].truck_id
            Ucommand = world_ups_pb2.UCommands()
            new_seq = acquireNewSeq()
            addUGoDeliver(Ucommand,truckid, package_id, new_seq)
            addUDeliveryLocation(Ucommand.deliveries[0], package_id, new_address_x, new_address_y)
            while True:
                sendMsg(Ucommand, world_socket)
                if new_seq in acks:
                    break
            # update package delivery address
            try:
                Package.objects.all().filter(package_id=package_id).update(deliver_x=new_address_x, deliver_y=new_address_y)
                print("Successfully updated delivery address")
            except Exception as e:
                print(e)
    else:
        print("The Package does not exist")
    return

# Query User Pacakages
def queryPackages(user_id):
    try:
        res = Package.objects.all().filter(owner_id=user_id)
        if res:
            return res
        else:
            return None
    except Exception as e:
        print(e)

def findEmail(package_id):
    email = ""
    try:
        packages = Package.objects.all().filter(package_id=package_id)
    except Exception as e:
        print(e)
    for pac in packages:
        uid = pac.owner_id
        print("user id:", uid)
        try:
            users = User.objects.all().filter(username=uid)
            for user in users:
                email = user.email
                break
        except Exception as e:
            print(e)
        break
    return email

def sendEmail(package_id, msg):
    des = findEmail(package_id)
    print("The email is:", des)
    if des:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            print("after smtp")
            source = "someforduke@gmail.com"
            pwd = "usingforDUKE"
            server.starttls()
            print("before log in")
            server.login(source, pwd)
            print("successfully log in")
            SUBJECT = "UPS Notification!"
            message = 'Subject: {}\n\n{}'.format(SUBJECT, msg)
            server.sendmail(source, des, message)
            server.quit()
            return
        except:
            print("something went wrong")
    print("Email does not exist")

if __name__ == "__main__":
    conn = connectToDB()
    world_socket = connectToWorldSim() # socket connected to world
    tryConnectToWorld(None, world_socket)
    amazon_socket = connectToAmazon() # socket connect to amazon
    handleMessages(world_socket, amazon_socket)

"""Ref : 
multithread: https://realpython.com/intro-to-python-threading/
threadpool: https://docs.python.org/3/library/concurrent.futures.html       

"""
    
