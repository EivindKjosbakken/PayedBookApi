import os

f = open("tag.txt", "r")
tag = f.read().strip()
f.close

# os.system(f"docker run -e PYTHONUNBUFFERED=1 -p 5000:5000 --add-host=mongoservice:172.17.0.1 -h=payed_book_service payed_book_api:{tag}")
os.system(f"docker run -e PYTHONUNBUFFERED=1 -p 5000:5000 --add-host=mongoservice:172.17.0.1 -h=payed_book_service payed_book_api:{tag}")

