import requests
import json
from .models import CarDealer, DealerReview, CarMake, CarModel
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

#O aqui puede estar el error
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data



def post_request(url, json_payload, **kwargs):
    print(json_payload)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)
        print(json_data)
        return json_data
    except:
        print("Network exception occurred")

# Aqui puede estar el error
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    
    try:
        # Check if json_result is a list
        if isinstance(json_result, list):
            dealers = json_result
        else:
            # Check if "rows" key is present and is a list
            dealers = json_result.get("rows", [])
            print("Number of dealers in the response:", len(dealers))
        
        # For each dealer object
        for dealer in dealers:
            # Check if each item in the list is a dictionary with a "doc" key
            if isinstance(dealer, dict) and "doc" in dealer:
                dealer_doc = dealer["doc"]
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(address=dealer_doc.get("address", ""),
                                       city=dealer_doc.get("city", ""),
                                       full_name=dealer_doc.get("full_name", ""),
                                       id=dealer_doc.get("id", ""),
                                       lat=dealer_doc.get("lat", ""),
                                       long=dealer_doc.get("long", ""),
                                       short_name=dealer_doc.get("short_name", ""),
                                       st=dealer_doc.get("st", ""),
                                       zip=dealer_doc.get("zip", ""))
                results.append(dealer_obj)
    except (KeyError, TypeError) as e:
        print(f"Error in get_dealers_from_cf: {e}")
    
    return results


def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    print('json_result from line 54',json_result)

    if json_result:
        dealers = json_result
        
    
        dealer_doc = dealers[0]
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"], full_name=dealer_doc["full_name"],
                                
                                st=dealer_doc["st"], zip=dealer_doc["zip"],short_name=dealer_doc["short_name"])
    return dealer_obj


def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    id = kwargs.get("id")
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
    # print(json_result)
    if json_result:
        print("line 105",json_result)
        reviews = json_result["data"]["docs"]
        for dealer_review in reviews:
            review_obj = DealerReview(dealership=dealer_review["dealership"],
                                   name=dealer_review["name"],
                                   purchase=dealer_review["purchase"],
                                   review=dealer_review["review"])
            if "id" in dealer_review:
                review_obj.id = dealer_review["id"]
            if "purchase_date" in dealer_review:
                review_obj.purchase_date = dealer_review["purchase_date"]
            if "car_make" in dealer_review:
                review_obj.car_make = dealer_review["car_make"]
            if "car_model" in dealer_review:
                review_obj.car_model = dealer_review["car_model"]
            if "car_year" in dealer_review:
                review_obj.car_year = dealer_review["car_year"]
            
            sentiment = analyze_review_sentiments(review_obj.review)
            print(sentiment)
            review_obj.sentiment = sentiment
            results.append(review_obj)

    return results

def analyze_review_sentiments(dealer_review):
        API_KEY = "56Uu0KyzSNEZ8u71Q9Nu4eqYmSiLxsMV0otoCXFUCIam"
        NLU_URL = 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/351966a8-a214-4fc1-a319-ea7f066c002c'
        authenticator = IAMAuthenticator(API_KEY)
        natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2021-08-01', authenticator=authenticator)
        natural_language_understanding.set_service_url(NLU_URL)
        response = natural_language_understanding.analyze(text=dealer_review, features=Features(
        sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
        label = json.dumps(response, indent=2)
        label = response['sentiment']['document']['label']
        return(label)