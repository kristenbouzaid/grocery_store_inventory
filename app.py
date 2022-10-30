from models import (Base, session, Brands, Product, engine)

import csv
import time
from statistics import median, mean, multimode
import datetime
from datetime import date

#function to add the brand csv file to the db file
def add_brands_csv():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)
        for row in data:
            brand_in_db = session.query(Brands).filter(Brands.brand_name==row[0]).one_or_none()
            # checks for duplicate brand names in the source data
            if brand_in_db == None:
                brand_name = row[0]
                new_brand = Brands(brand_name=brand_name)
                session.add(new_brand)
        session.commit()

#function to add the inventory csv file to the db file
def add_inventory_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
            # checks for duplicate products in the source data
            if product_in_db == None:
                product_name = row[0]
                product_price = clean_product_price(row[1])
                product_quantity = int(row[2])
                date_updated = clean_date_updated(row[3])
                brand_name = row[4]
                brand_id = session.query(Brands.brand_id).filter(Brands.brand_name == brand_name).scalar_subquery()
                new_product = Product(product_name=product_name, product_price=product_price, product_quantity=product_quantity, date_updated=date_updated, brand_id=brand_id)
                session.add(new_product)
        session.commit()

#function to clean the price when imported from the source data
def clean_product_price (price_str):
    stripped_price = price_str.strip("$")
    price_float = float(stripped_price)
    return int(price_float * 100)

#function to clean the date when imported from the source data
def clean_date_updated(date_str):
    split_date = date_str.split('/')
    month = int(split_date[0])
    day = int(split_date[1])
    year = int(split_date[2])
    return_date = datetime.date(year, month, day)
    return return_date

# function to clean the quantity when edited or input for a new product
def clean_quantity(quantity):
    try:
        quantity = int(quantity)
    except ValueError:
        input('''
            \n********* QUANTITY ERROR *******
            \rThe quantity should be a whole positive number (Ex. 4).
            \rPress enter to try again.
            \r********************************''')
    else:
        return(quantity)

# function to clean the price when edited or input for a new product
def clean_price(price_str):
    try:
        price_float = float(price_str)
    except ValueError:
        input('''
            \n********** PRICE ERROR **********
            \rThe price should be a number without a currency symbol (Ex. 10.99)
            \rPress enter to try again.
            \r*********************************''')
    else:
        return int(price_float * 100)

def menu():
    while True:
        print('''
            \nWelcome to Kristen's Krazy Grocery Inventory App!\n
            \rHere are your options:
            \rN) New Product
            \rV) View a Product
            \rA) Analyze a Product
            \rB) Backup the Database
            \rQ) Quit''')
        choice = input('\nWhat would you like to do?  ')
        choice = choice.upper()
        if choice in ['N', 'V', 'A', 'B', 'Q']:
            return choice
        else:
            input('''
            \rPlease choose one of the options above (N, V, A, B, or Q)
            \rPress enter to try again.''')

def submenu():
    while True:
        print('''
            \r1) Edit
            \r2) Delete
            \r3) Return to main menu''')
        choice = input(f'\nWhat would you like to do?  ')
        if choice in ['1', '2', '3']:
            return choice
        else:
            input('''
            \rPlease choose one of the options above - a number from 1-3.
            \rPress enter to try again.''')

# function to clean the product_id when input to view a product
def clean_id(id_str, options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
            \r********** ID ERROR **********
            \rThe ID should be a number.
            \rPress enter to try again.
            \r******************************''')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
                \n********** ID ERROR **********
                \rOptions: {options}
                \rPress enter to try again.
                \r******************************''')
            return

def find_brand_from_brand_id(brand_id):
    brand = session.query(Brands).filter(Brands.brand_id == brand_id).first()
    return(brand.brand_name)

def find_brand_id_from_brand(brand):
    brand = session.query(Brands).filter(Brands.brand_name == brand).first()
    return(brand.brand_id)

def nice_price(price):
    nice_price = float(price/100)
    return (f"${nice_price:.2f}")

def edit_check(column_name, current_value):
    print(f'\n**** EDIT {column_name} ****')
    if column_name == 'Price':
        print(f'''\rCurrent Value:  {current_value:.2f}''')
    else:
        print(f'''\rCurrent Value: {current_value}''')
    if column_name == 'Price' or column_name == 'Quantity':
        while True:
            changes = input('What would you like to change the value to? ')
            if column_name == 'Price':
                changes = clean_price(changes)
                if type(changes) == int:
                    return changes
            if column_name == 'Quantity':
                changes = clean_quantity(changes)
                if type(changes) == int:
                    return changes
    if column_name == "Brand Name":
        changes = input('What would you like to change the value to? ')
        add_new_brand(changes)
        brand_id = find_brand_id_from_brand(changes)
        return(brand_id)
    else:
        return input('What would you like to change the value to? ')

def add_new_brand(product_brand):
    brand_in_db = session.query(Brands).filter(Brands.brand_name == product_brand).one_or_none()
    if brand_in_db == None:
        new_brand = Brands(brand_name=product_brand)
        session.add(new_brand)
        session.commit()

def program():
    program_running = True
    while program_running:
        choice = menu()
        if choice == 'N':
            #New Product
            product_name = input('Product Name:  ')
            quantity_error = True
            while quantity_error:
                product_quantity = input('Product Quantity: ')
                product_quantity = clean_quantity(product_quantity)
                if type(product_quantity) == int:
                    quantity_error = False
            price_error = True
            while price_error:
                product_price = input('Product Price (Ex: 5.64):  ')
                product_price = clean_price(product_price)
                if type(product_price) == int:
                    price_error = False
            date_updated = date.today()
            product_brand = input('Product Brand: ')
            # check to see if the Product Name already exists in the db. If it does, then the existing data must be older (since this new data is updated) today, so the old record is deleted and then the new one is added
            product_in_db = session.query(Product).filter(Product.product_name == product_name).one_or_none()
            if product_in_db != None:
                    session.delete(product_in_db)
            # checks to see if the brand is listed. if not, adds a brand
            add_new_brand(product_brand)
            brand_id = find_brand_id_from_brand(product_brand)
            new_product = Product(product_name=product_name, product_quantity=product_quantity,
                                          product_price=product_price, date_updated=date_updated, brand_id=brand_id)
            session.add(new_product)
            session.commit()
            print('\nProduct added!')
            time.sleep(1.5)

        elif choice == 'V':
            # view product
            product_id_options = []
            for product in session.query(Product):
                product_id_options.append(product.product_id)
            id_error = True
            while id_error:
                chosen_product_id = input(f'''
                    \rProduct ID Options: {product_id_options}
                    \rPlease enter a Product ID to view the product: ''')
                chosen_product_id = clean_id(chosen_product_id, product_id_options)
                if type(chosen_product_id) == int:
                    id_error = False
            chosen_product = session.query(Product).filter(Product.product_id==chosen_product_id).first()
            print(f'''
                \rProduct Name: {chosen_product.product_name}
                \rProduct Quantity: {chosen_product.product_quantity}
                \rDate Last Updated: {chosen_product.date_updated}
                \rPrice: {nice_price(chosen_product.product_price)}
                \rBrand ID: {chosen_product.brand_id}
                \rBrand Name: {find_brand_from_brand_id(chosen_product.brand_id)}''')

            sub_choice = submenu()
            if sub_choice == '1':
                #edit
                chosen_product.quantity = edit_check('Quantity', chosen_product.product_quantity)
                chosen_product.product_price = edit_check('Price', chosen_product.product_price)
                chosen_product.brand_id = edit_check('Brand Name', find_brand_from_brand_id(chosen_product.brand_id))
                chosen_product.date_updated = date.today()
                session.commit()
                print('Product updated!')
                time.sleep(1.5)

            elif sub_choice == '2':
                 #delete
                 session.delete(chosen_product)
                 session.commit()
                 print('Product deleted!')
                 time.sleep(1.5)

        elif choice == 'A':
            #analyze
            highest_price = (session.query(Product).order_by(Product.product_price.desc()).first()).product_price
            lowest_price = (session.query(Product).order_by(Product.product_price).first()).product_price
            highest_priced_items = []
            lowest_priced_items = []
            for item in session.query(Product).filter_by(product_price = highest_price):
                highest_priced_items.append(item.product_name)
            for item in session.query(Product).filter_by(product_price=lowest_price):
                lowest_priced_items.append(item.product_name)
            brand_ids = []
            # generate a list of all brand ids then find the mode(s)
            for item in session.query(Product):
                brand_ids.append(item.brand_id)
            most_common_brand_ids = multimode(brand_ids)
            most_common_brands = []
            for item in most_common_brand_ids:
                brand_name = find_brand_from_brand_id(item)
                most_common_brands.append(brand_name)
            product_prices = []
            total_value_of_inventory = 0
            for product in session.query(Product):
                    product_prices.append(product.product_price)
                    total_value_of_inventory = total_value_of_inventory + (product.product_quantity * product.product_price)
            mean_product_price = round(mean(product_prices))
            median_product_price = median(product_prices)
            total_number_of_items_in_inventory = session.query(Product).count()

            print(f'''\n****** INVENTORY ANALYSIS ******
                \rMost Expensive Product(s): {nice_price(highest_price)} -- {', '.join(highest_priced_items)}
                \rLeast Expensive Product(s): {nice_price(lowest_price)} -- {', '.join(lowest_priced_items)}
                \rBrand(s) with the Most Products: {', '.join(most_common_brands)}
                \rAverage (Mean) Product Price: {nice_price(mean_product_price)}
                \rMedian Product Price: {nice_price(median_product_price)}
                \rTotal Number of Items in Inventory: {total_number_of_items_in_inventory}
                \rTotal Value of Inventory: {nice_price(total_value_of_inventory)}''')
            input('\nPress enter to return to the main menu.')

        elif choice == 'B':
            #backup
            with open('backup_brands.csv', 'w', newline='') as csvfile:
                brandswriter = csv.writer(csvfile)
                brandswriter.writerow(['Brand_ID', 'Brand_Name'])
                for brand in session.query(Brands):
                    brandswriter.writerow([brand.brand_id, brand.brand_name])
            with open('backup_inventory.csv', 'w', newline='') as csvfile:
                inventorywriter = csv.writer(csvfile)
                inventorywriter.writerow(['Product_ID', 'Product_Name', 'Product_Quantity', 'Product_Price', 'Date_Updated', 'Product_Brand_ID'])
                for product in session.query(Product):
                    inventorywriter.writerow([product.product_id, product.product_name, product.product_quantity, product.product_price, product.date_updated, product.brand_id])
            print("Database backed up!")
            time.sleep(1.5)
        else:
            print('GOODBYE')
            program_running = False


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_inventory_csv()
    program()