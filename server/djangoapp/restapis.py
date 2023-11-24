import requests
import json
from .models import CarDealer
from requests.auth import HTTPBasicAuth
# from ibm_watson import NaturalLanguageUnderstandingV1
# from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions


def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    
    try:
        # Call the get method of the requests library with URL and parameters
        response = requests.get(url, params=kwargs)

        # Check if the response status code indicates success
        response.raise_for_status()

        print("With status {} ".format(response.status_code))

        # Parse JSON only if response has content
        json_result = response.json() if response.content else None
        return json_result
    
    except requests.exceptions.RequestException as e:
        # Handle specific exceptions related to requests
        print(f"RequestException occurred: {e}")
        return None
    except json.JSONDecodeError as e:
        # Handle JSON decoding errors
        print(f"JSONDecodeError occurred: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors
        print(f"HTTPError occurred: {e}")
        return None
    except Exception as e:
        # Catch any other exceptions
        print(f"Unexpected exception occurred: {e}")
        return None
        
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    
    try:
        # Check if 'rows' key exists in the dictionary
        dealers = json_result.get("rows", [])
        
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer.get("doc", {})
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(
                address=dealer_doc.get("address", ""),
                city=dealer_doc.get("city", ""),
                full_name=dealer_doc.get("full_name", ""),
                id=dealer_doc.get("id", ""),
                lat=dealer_doc.get("lat", ""),
                long=dealer_doc.get("long", ""),
                short_name=dealer_doc.get("short_name", ""),
                st=dealer_doc.get("st", ""),
                zip=dealer_doc.get("zip", "")
            )
            results.append(dealer_obj)
    except KeyError as e:
        # Handle the case where the expected keys are not present in the response
        print(f"Error processing JSON response: {e}")
    
    return results



# def post_request(url, json_payload, **kwargs):
#     print(json_payload)
#     print("POST from {} ".format(url))
#     try:
#         response = requests.post(url, params=kwargs, json=json_payload)
#         status_code = response.status_code
#         print("With status {} ".format(status_code))
#         json_data = json.loads(response.text)
#         print(json_data)
#         return json_data
#     except:
#         print("Network exception occurred")



    # def get_dealer_from_cf_by_id(url, dealer_id):
#     json_result = get_request(url, id=dealer_id)
#     if json_result:
#         dealer = json_result["body"][0]
#         dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
#                                id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
#                                short_name=dealer["short_name"],
#                                st=dealer["st"], zip=dealer["zip"])
#     return dealer_obj


# def get_dealer_reviews_from_cf(url, dealer_id):
#     results = []
#     json_result = get_request(url, dealerId=dealer_id)
#     if json_result:
#         reviews = json_result["body"]
#         for review in reviews:
#             if review["purchase"]:
#                 review_obj = DealerReview(
#                     dealership=review["dealership"],
#                     name=review["name"],
#                     purchase=review["purchase"],
#                     review=review["review"],
#                     purchase_date=review["purchase_date"],
#                     car_make=review["car_make"],
#                     car_model=review["car_model"],
#                     car_year=review["car_year"],
#                     sentiment=analyze_review_sentiments(review["review"]),
#                     id=review['id']
#                 )
#             else:
#                 review_obj = DealerReview(
#                     dealership=review["dealership"],
#                     name=review["name"],
#                     purchase=review["purchase"],
#                     review=review["review"],
#                     purchase_date=None,
#                     car_make=None,
#                     car_model=None,
#                     car_year=None,
#                     sentiment=analyze_review_sentiments(review["review"]),
#                     id=review['id']
#                 )
#             results.append(review_obj)
#     return results


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