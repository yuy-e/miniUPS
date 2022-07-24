import imp
from importlib.resources import Package
from multiprocessing import context
import re
from tkinter.messagebox import NO
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
# from setuptools import find_packages
from .forms import *
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.mail import send_mail

# Create your views here.
from .forms import CreateUserForm


def home(request):
    if request.user.is_authenticated:
        return redirect('customer')
    else:
        orders = Package.objects.all()
        total_orders = orders.count()
            # pending = orders.filter(status='wait')
        pending_num = orders.filter(status='wait').count()
            # completed = orders.filter(status='delivered')
        completed_num = orders.filter(status='delivered').count()

        context = {'orders': orders, 'total_orders': total_orders, 'pending_num': pending_num, 'completed_num': completed_num}

        return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def pending(request):
    user = request.user.username
    orders = Package.objects.filter(owner_id=user)
    pending = orders.filter(status='wait').all()
    return render(request, 'accounts/pending.html', {'pending':pending})


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')

        context = {'form':form}
        return render(request, 'accounts/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('customer')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


@login_required
def customer(request):
    user = request.user.username
    orders = Package.objects.filter(owner_id = user)
    total_orders = orders.count()
    pending_num = orders.filter(status='wait').count()
    # completed = orders.filter(status='delivered')
    completed_num = orders.filter(status='delivered').count()

    context = {'orders': orders, 'total_orders': total_orders, 'pending_num': pending_num, 'completed_num': completed_num}
    return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
def packages(request):
    user = request.user.username
    packages = Package.objects.filter(owner_id=user)
    # total_orders = orders.count()
    # packages = Package.objects.all()
    return render(request, 'accounts/packages.html', {'packages':packages})


@login_required(login_url='login')
def trucks(request):
    trucks = Truck.objects.all()
    return render(request, 'accounts/trucks.html', {'trucks':trucks})


@login_required
def update(request, pk):
    if request.method == 'POST':
        form = UpsUpdate(request.POST)
        if form.is_valid():
            x_location = form.cleaned_data.get('location_x')
            y_location = form.cleaned_data.get('location_y')
            # t = Package.objects.get(package_id = pk, name = request.user.username)
            t = Package.objects.get(package_id=pk)
            t.deliver_x = x_location
            t.deliver_y = y_location
            t.save()
            messages.success(request, 'Destination Changed Successfully!')
            return redirect('home')
    else:
        form = UpsUpdate()
    return render(request, 'accounts/update.html', {'form':form})


def send(request):
    user = request.user
    subject = "Start Delivery!"
    message = "Remainder: Starting to deliver."
    recipient_list = [user.email]
    send_mail(subject, message, from_email="mz197@duke.edu", recipient_list=recipient_list)
    messages.success(request, 'Destination Changed Successfully!')
    return redirect('home')


@login_required(login_url='login')
def sent(request):
    return render(request, 'accounts/sent.html')


def tracking(request):
    if request.method == 'POST':
        form = FindPackage(request.POST)
        if form.is_valid():
            trackingNumber = form.cleaned_data.get('tracking_num')
            context = {
                'Info': Package.objects.filter(package_id=trackingNumber),
                'trackingNumber': trackingNumber
            }
            return render(request, 'accounts/trackprint.html', context)
    else:
        form = FindPackage()
    return render(request, 'accounts/tracking.html', {'form': form})
