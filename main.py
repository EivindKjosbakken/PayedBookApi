from flask import Flask
from flask_cors import CORS, cross_origin
from flask import Blueprint, Flask, render_template, request, redirect, url_for, session, flash, jsonify, session
import configparser
import pymongo
import os
import functools
import stripe
import hashlib
import secrets
import requests

#Some code from : https://testdriven.io/blog/flask-stripe-tutorial/


app = Flask(__name__)
app.secret_key = "super secret key"
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# make database
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join("./.ini")))
mongo_client = pymongo.MongoClient(config['LOCAL']['DB_URI'])
payedBookAPIDB = mongo_client["payedBookAPIDB"]
customers = payedBookAPIDB["customers"]



stripe_keys = {
    "secret_key": config['STRIPE_SECRET_KEY']['KEY'],
    "publishable_key": config['STRIPE_PUBLISHABLE_KEY']['KEY'],
    "endpoint_secret": config['STRIPE_ENDPOINT_SECRET']['KEY']
}
stripe.api_key = stripe_keys["secret_key"]



def generate_hash(string):
    return hashlib.md5(string.encode()).hexdigest()

def generate_api_key():
    APIKey = secrets.token_urlsafe(16)
    hashedAPIKey = generate_hash(APIKey)
    return (APIKey, hashedAPIKey)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/hello')
def hello():
    return 'Hello, World!'


@app.route("/create-checkout-session") 
@cross_origin()
def create_checkout_session():
    domain_url = "http://127.0.0.1:5000/"
    stripe.api_key = stripe_keys["secret_key"]
    try:
        #TODO this creates new customer, can also load a customer so it is kept the same
        customer = stripe.Customer.create(metadata = {"test": "can store info here"})
        customerId = customer.id

        checkout_session = stripe.checkout.Session.create( 
            customer = customerId,
            metadata = {"customer":customer},
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
			{
				"price": "price_1MoyHJJaawNKBfql8qzS71Ez",
			},
            ]
        )

        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route("/success")
def success():
    
    session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
    customer = stripe.Customer.retrieve(session.customer)

    apiKey, hashedAPIKey = generate_api_key()
    subscriptionId = session.get("subscription", "")
    print(f"Customer with id {customer.id} subscripted to the subscription with id {subscriptionId}")
    subscription = stripe.Subscription.retrieve(subscriptionId)
    itemId = subscription["items"].data[0].id

    APIKey, hashedAPIKey = generate_api_key()

    print("\n\nRegistered:")
    print("ITEM ID: ", itemId)
    print("Your api key: ", APIKey)
    print("Your customer id: ", customer.id)
    print("\n\n")

    customers.insert_one({"customerId": customer.id, "hashedAPIKey": hashedAPIKey, "itemId" : itemId, "active": True, "subscriptionId" : subscriptionId })

    return render_template("success.html", name = customer.name, APIKey = APIKey)


@app.route("/cancelled")
def cancelled():
    return render_template("cancelled.html")




@app.route("/webhook", methods=["POST"])  
@cross_origin()
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400
    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")


    elif (event["type"] == "invoice.paid"):
        #TODO add code here
        pass
    elif (event["type"] == "invoice.payment_failed"):
        #TODO add code here
        pass

    return "Success", 200



@app.route(f"/customer_info", methods=["POST"])
@cross_origin()
def getCustomerInfo():
    pass #NOTE can do customer info function here


@app.route("/usage", methods=["GET"])
@cross_origin()
def getCustomerUsage():
    APIKey = request.headers.get('X-API-KEY')
    if (APIKey is None or APIKey == ""):
        return "API key not defined, add it to the header"
    customerId = customers.find_one({"hashedAPIKey": generate_hash(APIKey)}).get("customerId", "")
    if (customerId == ""):
        return "Customer ID not found, check your API key", 400
    invoice = stripe.Invoice.upcoming(customer = customerId)
    return {"invoice": invoice}
    #NOTE this method may not find customer if customer is made in a different stripe listening sessioN!

@app.route("/cancel_subscription")
@cross_origin()
def cancelSubscription():
    APIKey = request.headers.get('X-API-KEY')

    if (APIKey is None):
        return "API key not found", 400
    
    hashedAPIKey = generate_hash(APIKey)

    customer = customers.find_one({"hashedAPIKey": hashedAPIKey})

    if (customer is None):
        return "Customer not found", 400
    
    subscriptionId = customer.get("subscriptionId", None)
    subItemId = customer.get("itemId", None)
    if (subscriptionId is None or subItemId is None):
        return "Subscription not found", 400

    try:
        stripe.Subscription.delete(sid = subscriptionId)
        customers.delete_one({"hashedAPIKey": hashedAPIKey})
        return "Subscription deleted successfully", 200
    except:
        return "Failed to delete subscription (might already have been deleted)", 400





@app.route(f"/get_book_plots", methods=["POST"])
@cross_origin()
def get_book_plots():
    APIKey = request.headers.get('X-API-KEY')

    if (APIKey is None):
        return {"status":"not allowed"}, 403
    
    hashedAPIKey = generate_hash(APIKey)
    
    customer = customers.find_one({"hashedAPIKey" : hashedAPIKey})
    if (customer is None):
        return {"status": "Customer not found"}, 400
    
    customerId, itemId, active = customer.get("customerId", ""), customer.get("itemId", ""), customer.get("active", False)
    print("IS: ", customerId, "IS", itemId, active)
    if (customerId == "" or itemId == "" or active == False):
        return {"status": "Not valid customerId or itemId, or non active user"}, 400
    
    record = stripe.SubscriptionItem.create_usage_record(itemId, quantity=1, timestamp = "now", action="increment")

    return {"status": "congrats, you accessed a payed endpoint", "record": record}, 200




