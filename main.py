import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "billing.settings")
django.setup()

from core.models import Customer, Product

def menu():
    while True:
        print("\n1. Add Customer")
        print("2. List Customers")
        print("3. Add Product")
        print("4. List Products")
        print("0. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            name = input("Customer name: ")
            phone = input("Phone: ")
            Customer.objects.create(name=name, phone=phone)
            print("Customer added!")

        elif choice == '2':
            for c in Customer.objects.all():
                print(c.id, c.name, c.phone)

        elif choice == '3':
            name = input("Product name: ")
            price = float(input("Price: "))
            stock = int(input("Stock: "))
            Product.objects.create(name=name, price=price, stock=stock)
            print("Product added!")

        elif choice == '4':
            for p in Product.objects.all():
                print(p.id, p.name, p.price, p.stock)

        elif choice == '0':
            break

if __name__ == "__main__":
    menu()
