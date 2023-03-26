# PayedBookApi

To run:

1. create your .ini file, to see how to do that, check out https://medium.com/@oieivind/monitize-your-api-using-stripe-and-flask-ff3e2061267a
2. run strip with: stripe listen --forward-to 127.0.0.1:5000/webhook and copy the webook secret into your .ini file
3. run Flask with "python run.py"

And you are good to go!
