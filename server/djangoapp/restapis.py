import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
# from ibm_watson import NaturalLanguageUnderstandingV1
# from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


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

        
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
    
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
            id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results




def post_request(url, payload, **kwargs):
    print(url)
    print(payload)
    print(kwargs)
    try:
        response = requests.post(url, params=kwargs, json=payload)
    except Exception as e:
        print("Error" ,e)
    print("Status Code ", {response.status_code})
    data = json.loads(response.text)
    return data



def get_dealer_by_id_from_cf(url, dealerId):
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId=dealerId)
    if json_result:
        # For each dealer object
        for dealer_doc in json_result:
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
            id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
            short_name=dealer_doc["short_name"],
            st=dealer_doc["st"], zip=dealer_doc["zip"])

    return dealer_obj


def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    
    if "entries" in json_result:
        reviews = json_result["entries"]
        # For each review object
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=analyze_review_sentiments(review["review"]),
                id=review['id']
                )
            results.append(review_obj)
    #print(results[0])
    return results

# def analyze_review_sentiments(dealer_review):
#     API_KEY = "56Uu0KyzSNEZ8u71Q9Nu4eqYmSiLxsMV0otoCXFUCIam"
#     NLU_URL = 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/351966a8-a214-4fc1-a319-ea7f066c002c'
#     authenticator = IAMAuthenticator(API_KEY)
#     natural_language_understanding = NaturalLanguageUnderstandingV1(
#         version='2021-08-01', authenticator=authenticator)
#     natural_language_understanding.set_service_url(NLU_URL)
#     response = natural_language_understanding.analyze(text=dealer_review, features=Features(
#         sentiment=SentimentOptions(targets=[dealer_review]))).get_result()
#     label = json.dumps(response, indent=2)
#     label = response['sentiment']['document']['label']
#     return(label)