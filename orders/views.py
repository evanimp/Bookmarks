from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Q
from .models import Folder, Place
from django import forms
from .forms import SignUpForm, PlaceForm
from django.contrib.auth.models import User
from decimal import *
import binascii

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

# Should be environment variable in production.
key = 'ABCDEFGHIJ123456'

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

cipher = AESCipher(key)

class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


# This is the main view.
@login_required(login_url='/accounts/login/')
def index(request):

    # Posts mean that they pressed the search button.
    if request.method == 'POST':
        # Get the text from the search box and search
        query = request.POST.get('search')
        print(query)
        items = Place.objects.filter(location__contains=query)

    # Otherwise, list all places for this user.
    else:
        items = Place.objects.filter(user=request.user)

    context = {
        "items": items,
        "folders": Folder.objects.filter(user=request.user)
    }
    return render(request, "index.html", context)


# This performs a search for the user or retrieves the contents of one folder.
@login_required(login_url='/accounts/login/')
def filter(request, f_type):

    if f_type == 'search_not_folder':
        # Get the text from the search box and search
        print("ftype is search_not_folder")
        # The user pressed search, so get the query string then results.
        query = request.POST.get('search')
        items = Place.objects.filter((Q(name__contains=query)|Q(location__contains=query))&Q(user=request.user))
    else:
        # If its not a search, get items in the folder they clicked.
        query = f_type
        folder = Folder.objects.filter(Q(name=f_type)&Q(user=request.user))
        # Make sure we got an existing folder.
        if folder:
            items = Place.objects.filter(Q(category=folder[0])&Q(user=request.user))

    context = {
        "items": items,
        "folders": Folder.objects.filter(user=request.user)
    }
    return render(request, "index.html", context)


# This allows the user to enter a url or device and save its encrypted password.
@login_required(login_url='/accounts/login/')
def add_place(request):

    # If its a post request, get information from the form and store it in the DB
    if request.method == 'POST':
        data = request.POST.copy()
        new_place = Place.objects.create(user=request.user, category = Folder.objects.all()[0])
        new_place.name = data.get('name')
        new_place.location = data.get('location')

        # Record the fact that an item was added to this folder.
        cat = data.get('category')
        folder = Folder.objects.get(Q(id=cat)&Q(user=request.user))
        folder.size+=1
        folder.save()

        # Finish getting form data and encrypt the pw.
        new_place.category = folder
        new_place.un = data.get('un')
        pw = cipher.encrypt(data.get('pw'))
        new_place.pw = pw
        new_place.save()

        return redirect('index')

    # If its a Get request, give them an empty form.
    else:
        # Make sure there is at least one folder to choose from.
        folders = Folder.objects.filter(user=request.user)
        if folders.exists():
            values = {'name' : "",
                    'location' : "",
                    'category' : Folder.objects.filter(user=request.user),
                    'un': "",
                    'pw': ""}
            form = PlaceForm()

            form.fields['category'].queryset = Folder.objects.filter(user=request.user)

        else:
            return render(request, 'error.html', {'message': 'You must add at least one folder first.'})


    return render(request, "add_place.html", {'form': form})


# This is when the user is changing an existing item.
@login_required(login_url='/accounts/login/')
def edit_place(request, place_id):

    # Get the item based upon id
    place = Place.objects.get(id=place_id)

    request.session['old_cat']=place.category.name

    if request.method == 'POST':
        # Save the form data and return to home.
        data = request.POST.copy()
        place.name = data.get('name')
        place.location = data.get('location')
        cat = data.get('category')
        folder = Folder.objects.get(Q(id=cat)&Q(user=request.user))

        # Get the old folder (catagory) from session to compare.
        old_cat = request.session['old_cat']

        # If they changed the folder of this item, update counts
        if(folder.name != old_cat):
            # Increment new folder count.
            place.category = folder
            folder.size+=1
            folder.save()
            # Get the old folder and decrement it's count.
            old_folder = Folder.objects.get(Q(name=old_cat)&Q(user=request.user))
            old_folder.size-=1
            old_folder.save()

        place.un = data.get('un')
        pw = cipher.encrypt(data.get('pw'))
        place.pw = pw
        place.save()

        # Refresh and return home.
        context = {
            "items": Place.objects.filter(user=request.user),
            "folders": Folder.objects.filter(user=request.user)
        }
        return render(request, "index.html", context)
    else:
        # Decrypt the password and fill in a form to render.
        # The password plain text will not be visible in the web page.
        pw = place.pw
        dec = cipher.decrypt(pw)
        values = {'name' : place.name,
                'location' : place.location,
                'category' : Folder.objects.filter(user=request.user),
                'un': place.un,
                'pw': dec}
        form = PlaceForm(values)

        # A queryset must be set for the forms selection control.
        form.fields['category'].queryset = Folder.objects.filter(user=request.user)

    context = {
        "form": form,
        "place_id": place_id
    }

    return render(request, 'edit_place.html', context)

# This allows the user to click on items and have them copied to the clipboard.
# The password is decrypted but will not be shown in the web page.
@login_required(login_url='/accounts/login/')
def view_place(request, place_id):

    # Retrieve the place and decrypt the password.
    place = Place.objects.get(id=place_id)
    dec = cipher.decrypt(place.pw)

    values = {'name' : place.name,
            'location' : place.location,
            'category' : place.category,
            'un': place.un,
            'pw': dec}
    form = PlaceForm(values)

    context = {
        "values": values,
    }

    return render(request, 'view_place.html', context)

# Adds a folder for the current user.
@login_required(login_url='/accounts/login/')
def add_folder(request):
    # Retrieve the folder name and then create it.
    folder_name = request.POST.get('new_folder')
    new_folder = Folder.objects.create(user=request.user, name=folder_name)
    new_folder.save()
    return redirect('index')


# This deletes one place and decrements the count in the folder that contains it.
@login_required(login_url='/accounts/login/')
def delete(request, place_id):

    # First get the folder to reduce the count.
    place = Place.objects.get(pk=place_id)
    cat = place.category
    folder = Folder.objects.get(Q(name=cat)&Q(user=request.user))
    folder.size-=1
    folder.save()

    # Now delete the item.
    Place.objects.filter(pk=place_id).delete()
    return redirect('index')

# This deletes a folder. Because it cascades, all containing items are deleted.
@login_required(login_url='/accounts/login/')
def delete_folder(request, folder_id):
    Folder.objects.filter(pk=folder_id).delete()
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('index')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


@login_required(login_url='/accounts/login/')
def error(request, message):
    return render(request, 'error.html', {'message': message})


@login_required(login_url='/accounts/login/')
def logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))
