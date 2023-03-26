import os

f = open("tag.txt")
tag = f.read().strip()
f.close()

os.system(f"docker build . -f Dockerfile -t payed_book_api:{tag}")