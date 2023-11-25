import requests
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
import logging
from datetime import datetime
from .models import CarModel
from django.http import HttpResponse, JsonResponse

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def home(request):
        return render(request,'djangoapp/index.html')

# Create an `about` view to render a static about page
def about(request):
        return render(request,'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('/djangoapp')
        else:
            # If not, return to login page again
            return render(request, '#', context)
    else:
        return render(request, '#', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('/djangoapp')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = User.objects.filter(username=username).exists()
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('/djangoapp')
        else:
            return redirect('/djangoapp')

def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)
        # return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    context={}
    url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-review"
    apikey="60Yh7v6jSzli4lHt2f5Sng-SC25IKlJKlMS9EaZ9sfK8"
    #print(dealer_id)
    # Get dealers from the URL
    dealer_details = get_dealer_reviews_from_cf(url,dealer_id)
    context["dealer_id"]=dealer_id
    context["reviews"]=dealer_details
    return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request, dealer_id):
    if request.method == "GET":
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(url, dealer_id)
        context = {
            "cars": CarModel.objects.all(),
            "dealer": dealer
        }
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
            form = request.POST
            review = dict()
            unique_id = uuid.uuid4()
            review["name"] = request.user.username
            review["id"] = int.from_bytes(unique_id.bytes, byteorder='big')
            review["dealership"] = dealer_id
            review["review"] = form["content"]
            review["purchase"] = form.get("purchasecheck")
            review["another"] = "field"
            if review["purchase"]:
                review["purchase_date"] = str(datetime.strptime(form.get("purchasedate"), "%Y-%m-%d"))
            car = CarModel.objects.get(pk=form["car"])
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = car.year.strftime("%Y")
            # If the user bought the car, get the purchase date
            if form.get("purchasecheck"):
                review["purchase_date"] = str(datetime.strptime(form.get("purchasedate"), "%Y-%m-%d"))
            else: 
                review["purchase_date"] = None
            url = "https://eu-de.functions.appdomain.cloud/api/v1/web/28d0b867-6bcc-4fb3-a6e3-9623b43f327e/dealership-package/post-review" 
            
            json_payload = {"review": review}
            result = post_request(url, json_payload, dealerId=dealer_id)
            if (result):
                return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
            else:
            # After posting the review the user is redirected back to the dealer details
                 return redirect("djangoapp:dealer_details", dealer_id=dealer_id)