from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .restapis import get_dealers_from_cf
from django.contrib.auth import login, logout, authenticate
import logging
from datetime import datetime
from .models import CarModel
from django.http import JsonResponse

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
        url = "https://us-east.functions.cloud.ibm.com/api/v1/namespaces/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/actions/dealership-package/get-dealership"
        
        try:
            # Get dealers from the URL
            dealerships = get_dealers_from_cf(url)
            
            # Check if dealerships is not None (indicating a successful response)
            if dealerships is not None:
                # Create a list of dealer short names
                dealer_names = [dealer.short_name for dealer in dealerships]
                
                # Return a JSON response
                return JsonResponse({'dealer_names': dealer_names})
            else:
                # Handle the case where there was an issue retrieving dealership information
                return JsonResponse({'error': 'Failed to retrieve dealership information'}, status=500)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)



# def get_dealer_details(request, dealer_id):
#     if request.method == "GET":
#         context = {}
#         url = "https://e29b86ca.eu-gb.apigw.appdomain.cloud/api/review/"
#         reviews = get_dealer_reviews_from_cf(url, dealer_id)
#         context["reviews"] = reviews
#         dealer = get_dealer_from_cf_by_id(
#             "https://e29b86ca.eu-gb.apigw.appdomain.cloud/api/dealership", dealer_id)
#         context["dealer"] = dealer
#         return render(request, 'djangoapp/dealer_details.html', context)


# def add_review(request, dealer_id):
#     context = {}
#     if request.method == "GET":
#         url = "https://e29b86ca.eu-gb.apigw.appdomain.cloud/api/dealership"
#         dealer = get_dealer_from_cf_by_id(url, dealer_id)
#         cars = CarModel.objects.filter(dealer_id=dealer_id)
#         context["cars"] = cars
#         context["dealer"] = dealer
#         return render(request, 'djangoapp/add_review.html', context)

#     if request.method == "POST":
#         url = "https://e29b86ca.eu-gb.apigw.appdomain.cloud/api/review/"      
#         if 'purchasecheck' in request.POST:
#             was_purchased = True
#         else:
#             was_purchased = False
#         cars = CarModel.objects.filter(dealer_id=dealer_id)
#         for car in cars:
#             if car.id == int(request.POST['car']):
#                 review_car = car  
#         review = {}
#         review["time"] = datetime.utcnow().isoformat()
#         review["name"] = request.POST['name']
#         review["dealership"] = dealer_id
#         review["review"] = request.POST['content']
#         review["purchase"] = was_purchased
#         review["purchase_date"] = request.POST['purchasedate']
#         review["car_make"] = review_car.make.name
#         review["car_model"] = review_car.name
#         review["car_year"] = review_car.year.strftime("%Y")
#         json_payload = {}
#         json_payload["review"] = review
#         response = post_request(url, json_payload)
#         return redirect("djangoapp:dealer_details", dealer_id=dealer_id)