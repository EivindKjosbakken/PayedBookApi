# PayedBookApi

To run:

1. create your .ini file, to see how to do that, check out https://medium.com/@oieivind/monitize-your-api-using-stripe-and-flask-ff3e2061267a
2. run strip with: stripe listen --forward-to 127.0.0.1:5000/webhook and copy the webook secret into your .ini file
3. run Flask with "python run.py"

And you are good to go!


To use API:

The API has 3 endpoints you can currently access, all require your API Key which you can get from the checkout with stripe (link coming soon). To send with API Key, add the following to your header: key is "X-API-KEY"  , value is the API key you are given after checkout  

1. /get_book_plots   . Send to this endpoint with a body: {"isbn" : "isbn you want to get plot for"} as well 
2. /usage will show you how much you have spent (automatically checks using your API Key)
3. /cancel_subscription will allow you to cancel your subscription. Note, you will still be charged for the usage of your API up until cancellation

Link to access endpoints are coming soon!
