import os

f = open("tag.txt", "r")
tag = f.read().strip()
f.close()

#This is for production I think
os.system(f"docker tag payed_book_api:{tag} kjosbakken/payed_book_api:{tag}")
os.system(f"docker push kjosbakken/payed_book_api:{tag}")