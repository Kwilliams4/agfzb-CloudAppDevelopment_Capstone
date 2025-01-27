from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
import logging
from datetime import datetime
from .models import CarModel, CarDealer

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


def about(request):
    return render(request, 'djangoapp/about.html')


def contact(request):
    return render(request, 'djangoapp/contact.html')


def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(to=reverse('admin:index'))
        else:
            return redirect('djangoapp:index')


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


def registration_request(request):
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)


def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-dealership"
        dealerships = get_dealers_from_cf(url)

        # Concat all dealer's short name
        dealer_names = ' '.join([f"{dealer.short_name} {dealer.city}" for dealer in dealerships])

        # Return a list of dealer short name
        # return HttpResponse(dealer_names)

        # # Debugging: Print the fetched data
        # print(dealerships)

        context["get_dealerships"] = dealerships
        return render(request, 'djangoapp/index.html', context)


def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer
    
        review_url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        print(reviews)
        context["reviews"] = reviews
        
        return render(request, 'djangoapp/dealer_details.html', context)
            
# View to submit a new review
def add_review(request, id):
    context = {}
    dealer_url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/get-dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context["dealer"] = dealer
    if request.method == 'GET':
        # Get cars for the dealer
        cars = CarModel.objects.all()
        print(cars)
        context["cars"] = cars
        
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["id"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.car_make.name
            payload["car_model"] = car.name
            payload["car_year"] = int(car.year.strftime("%Y"))

            new_payload = {}
            new_payload["review"] = payload
            review_post_url = "https://us-east.functions.appdomain.cloud/api/v1/web/1db7e909-33cc-44c6-ac1a-19b1b0886a3c/dealership-package/post-review"      
            post_request(review_post_url, new_payload, id=id)
        return redirect("djangoapp:dealer_details", id=id)