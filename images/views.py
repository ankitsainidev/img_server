from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import authenticate, login, logout, get_user
from .forms import LoginForm, ClientForm, PassChangeForm, ClientEditForm
from django.contrib.auth.decorators import login_required
from .cplib import storeToThumbAndHome, getPathsAndInfo, deleteClient, expireClient, deleteImage, UpdateClient, sync,suggest,clientPathAndInfo
from .models import Client
from .allConfig import mainuser, drives
from .thumb import alldrivedata
from django.contrib.auth.models import User
# Create your views here.
@login_required
def home(request):
    # deliver home page
    user = get_user(request)
    username = user.get_username()

    # clients = getclients(username)
    #earlierversion
        # clientsinfo = []
        # # clients = ['someone']
        # if clients is not None:
        #     clientsinfo += [getPathsAndInfo(username, client)
        #                     for client in clients]
        # if len(clientsinfo) == 0:
        #     clientsinfo = False
    #newer
    clientsinfo=getPathsAndInfo(username)
    if clientsinfo ==[]:
        clientsinfo = False
    showpass = (username == mainuser)
    return render(request, 'images/home.html', {'username': username, 'clients': clientsinfo, 'showpass': showpass})


@login_required
def driveView(request):
    return render(request, 'images/drive.html')


def Login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['userid'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    return HttpResponse('disabled account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def Logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required
def newClient(request):
    message = 'Add new client'
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            user = get_user(request).get_username()
            
            message = storeToThumbAndHome(cd, user, cd['name'])
            if message is None:
                return HttpResponseRedirect('/')
    else:
        form = ClientForm()
    return render(request, 'account/newclient.html', {'form': form, 'message': message})


@login_required
def clientDetail(request, client):
    message = ''
    user = get_user(request).get_username()
    if request.method == 'POST':
        form = ClientEditForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['name'] is not None and cd['name'] != '':
                if Client.objects.filter(user = user,name=cd['name']).exists():
                    if cd['name'] !=client:
                        message = f'Already a client exists with the username. You can choose from {suggest(user, cd["name"])}'
                else:
                    UpdateClient(cd, get_user(request).get_username(), client)
                    client = cd['name']
                    form = ClientEditForm()
                    return HttpResponseRedirect(f'/clientdetail/{client}')
            else:
                UpdateClient(cd, get_user(request).get_username(), client)

    else:
        form = ClientEditForm()
    query = Client.objects.get(user=get_user(request).get_username(),name=client)
    out = clientPathAndInfo(query)
    if out is None:
        return HttpResponseNotFound()
    imagePaths, name, thumbs, textpath = out
    return render(request, 'images/clientdetail.html', {'images': imagePaths, 'name': name, 'thumbs': thumbs, 'textpath': textpath, 'form': form, 'message': message})


@login_required
def deleteClientView(request, client):
    deleteClient(get_user(request).get_username(), client)
    return HttpResponseRedirect('/')


@login_required
def expireClientView(request, client):
    expireClient(get_user(request).get_username(), client)
    return HttpResponseRedirect('/')


@login_required
def passwordView(request):
    if mainuser == get_user(request).get_username():
        users = User.objects.all()
        userdata = []
        for user in users:
            userdata.append([user.username, user.password])
        return render(request, 'account/pass.html', {'userdata': userdata})
    return HttpResponseRedirect('/')


@login_required
def useroperationView(request):
    if mainuser == get_user(request).get_username():
        import subprocess
        subprocess.call("/maintenancemode.sh")
        print("Maintenance Mode Entered")
        import sys
        sys.exit()
    return HttpResponseRedirect('/')


@login_required
def passwordChangeView(request):
    message = 'Fill passwords'

    if request.method == 'POST':
        print('haa ab post hui')
        form = PassChangeForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            print(get_user(request).password)
            if cd['currentPassword'] == get_user(request).password:
                if cd['NewPassword'] == cd['ConfirmPassword']:
                    if len(cd['NewPassword']) >= 8:
                        user = get_user(request)
                        user.password = cd['NewPassword']
                        user.save()
                        return HttpResponseRedirect('/')
                    else:
                        message = 'password too short'
                else:
                    message = 'confimation password didn\'t matched'
            else:
                message = 'curren password didn\'t match'
    else:
        form = PassChangeForm()
    return render(request, 'account/passchange.html', {'form': form, 'message': message})


@login_required
def imageDeleteView(request, client, imagepath):
    deleteImage(imagepath)
    return HttpResponseRedirect('/clientdetail/'+client)


@login_required
def syncView(request, drive=None):

    clients = Client.objects.filter(user=get_user(request).get_username())
    if get_user(request).get_username() == mainuser:
        clients = Client.objects.all()

    for client in clients:
        if drive is None:

            sync(client.user, client.name)
        else:
            sync(client.user, client.name, drive)
    return HttpResponseRedirect('/')
