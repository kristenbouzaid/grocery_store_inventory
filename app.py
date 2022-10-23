from sqlalchemy import (create_engine, Column, Integer,
                        String, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
# do i need relationship (below). if so, how do i incorporate it?
from sqlalchemy.orm import sessionmaker, relationship
# do I need this next line? Don't think I'm using it
from sqlalchemy import func

import csv
import datetime
import time
from statistics import median, mean, multimode

# why do i need this if i've imported datetime above? does the above statement not import ALL of the datetime functions?
from datetime import date



engine = create_engine("sqlite:///inventory.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class Brands(Base):
    __tablename__ = 'brands'
    brand_id = Column(Integer, primary_key=True)
    brand_name = Column("Brand Name", String)

    def __repr__(self):
        return f"""
      \nBrand ID = {self.brand_id}\r
      Name = {self.brand_name}
      """

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    product_name = Column('Product Name', String)
    product_quantity = Column('Quantity', Integer)
    product_price = Column('Price', Integer)
    date_updated = Column('Date Updated', Date)
    brand_id = Column(Integer, ForeignKey("brands.brand_id"))

    def __repr__(self):
        return f"""
      \nProduct ID {self.product_id}\r
      Product Name = {self.product_name}\r
      Product Quantity = {self.product_quantity}\r
      Product Price = {self.product_price}\r
      Date Updated = {self.date_updated}\r
      Brand ID = {self.brand_id}
      """

def add_brands_csv():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)
        for row in data:
            brand_in_db = session.query(Brands).filter(Brands.brand_name==row[0]).one_or_none()
            if brand_in_db == None:
                brand_name = row[0]
                new_brand = Brands(brand_name=brand_name)
                session.add(new_brand)
        session.commit()

def add_inventory_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        header = next(data)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
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

def clean_product_price (price_str):
    stripped_price = price_str.strip("$")
    price_float = float(stripped_price)
    return int(price_float * 100)

def clean_price(price_str):
    # need to add code here to clean price when it's input - same as book.db
    try:
        price_float = float(price_str)
    except ValueError:
        input('''
            \n********* PRICE ERROR *******
            \rThe price should be a number without a currency symbol.
            \rEx: 10.99
            \rPress enter to try again.
            \r******************************''')
    else:
        return int(price_float * 100)

def clean_quantity(quantity):
    try:
        quantity = int(quantity)
    except ValueError:
        input('''
            \n********* QUANTITY ERROR *******
            \rThe quantity should be a whole positive symbol.
            \rEx: 4
            \rPress enter to try again.
            \r******************************''')
    else:
        return(quantity)

def clean_date_updated(date_str):
    split_date = date_str.split('/')
    month = int(split_date[0])
    day = int(split_date[1])
    year = int(split_date[2])
    return_date = datetime.date(year, month, day)
    return return_date

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

def find_brand_id(brand_name):
    #why do i need this scalar subquery here?
    brand_id = session.query(Brands.brand_id).filter(Brands.brand_name == brand_name).scalar_subquery()
    return brand_id

def clean_id(id_str, options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
            \r********* ID ERROR *******
            \rThe ID should be a number.
            \rPress enter to try again.
            \r******************************''')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
                \n********* ID ERROR *********
                \rOptions: {options}
                \rPress enter to try again.
                \r****************************''')
            return

def find_brand_from_brand_id(brand_id):
    brand = session.query(Brands).filter(Brands.brand_id == brand_id).first()
    return(brand.brand_name)

def nice_price(price):
    nice_price = float(price/100)
    return (f"${nice_price:.2f}")

def program():
    program_running = True
    while program_running:
        choice = menu()
        if choice == 'N':
            #New Product
            product_name = input('Product Name:  ')

            # must ensure product_quantity is an integer
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
            ### need to figure out how to chekc if the brand is in the brands table and add it if its not
            print(session.query(Brands).filter(brand_name = product_brand))
            #if session.query(Brands).filter(brand_name = product_brand) == None:
                #add brand to brands table
                #new_brand = Brand(product_brand=product_brand)
                #session.add(new_brand)
            brand_id = find_brand_id(product_brand)
            new_product = Product(product_name=product_name, product_quantity=product_quantity, product_price=product_price, date_updated=date_updated, brand_id=brand_id)
            session.add(new_product)
            session.commit()
            print('Product added!')
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
            print(chosen_product)
            print(f'''
                \rProduct Name: {chosen_product.product_name}
                \rProduct Quantity: {chosen_product.product_quantity}
                \rDate Last Updated: {chosen_product.date_updated}
                \rPrice: {nice_price(chosen_product.product_price)}
                \rBrand ID: {chosen_product.brand_id}
                \rBrand: {find_brand_from_brand_id(chosen_product.brand_id)}''')
            input('\nPress enter to return to the main menu.')

            # sub_choice = submenu()
            # if sub_choice == '1':
            #     #edit
            #     the_book.title = edit_check('Title', the_book.title)
            #     the_book.author = edit_check('Author', the_book.author)
            #     the_book.published_date = edit_check('Date', the_book.published_date)
            #     the_book.price = edit_check('Price', the_book.price)
            #     session.commit()
            #     print('Book updated!')
            #     time.sleep(1.5)
            #
            # elif sub_choice == '2':
            #     #delete
            #     session.delete(the_book)
            #     session.commit()
            #     print('Book delected!')
            #     time.sleep(1.5)

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

            print(f'''\n****** INVENTORY ANALYSIS *****
                \rMost Expensive Product(s): {nice_price(highest_price)} -- {', '.join(highest_priced_items)}
                \rLeast Expensive Product(s): {nice_price(lowest_price)} -- {', '.join(lowest_priced_items)}
                \rBrand(s) with the Most Products: {', '.join(most_common_brands)}
                \rAverage (Mean) Product Price: {nice_price(mean_product_price)}
                \rMedian Product Price: {nice_price(median_product_price)}
                \rTotal Number of Items in Inventory: {total_number_of_items_in_inventory}
                \rTotal Value of Inventory: {nice_price(total_value_of_inventory)}''')
            input('\nPress enter to return to the main menu.')
        else:
            print('GOODBYE')
            program_running = False


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_inventory_csv()
    program()