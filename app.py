from sqlalchemy import (create_engine, Column, Integer,
                        String, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import func

import csv
import datetime
import time

# why do i need this if i've imported datetime above? does the above statement not import ALL of the datetime functions?
from datetime import date

from statistics import median, mode, mean

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

#  *******MUST FIGURE OUT HOW TO REMOVE THE HEADER ROW**********
def add_brands_csv():
    with open('brands.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            brand_in_db = session.query(Brands).filter(Brands.brand_name==row[0]).one_or_none()
            if brand_in_db == None:
                brand_name = row[0]
                new_brand = Brands(brand_name=brand_name)
                session.add(new_brand)
        session.commit()

#  *******MUST FIGURE OUT HOW TO REMOVE THE HEADER ROW**********
def add_inventory_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
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
        #return  ???
    else:
        return int(price_float * 100)



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
    brand_id = session.query(Brands.brand_id).filter(Brands.brand_name == brand_name).scalar_subquery()
    return brand_id

def clean_id(id_str, options):
    try:
        product_id = int(id_str)
    except ValueError:
        input('''
            \n********* ID ERROR *******
            \rThe ID should be a number.
            \rPress enter to try again.
            \r******************************''')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'''
                \n********* ID ERROR *******
                \rOptions: {options}
                \rPress enter to try again.
                \r******************************''')
            return


def program():
    program_running = True
    while program_running:
        choice = menu()
        if choice == 'N':
            #New Product
            product_name = input('Product Name:  ')
            # must ensure product_quantity is an integer
            product_quantity = input('Product Quantity: ')
            price_error = True
            while price_error:
                product_price = input('Product Price (Ex: 5.64):  ')
                product_price = clean_price(product_price)
                if type(product_price) == int:
                    price_error = False
            date_updated = date.today()
            product_brand = input('Product Brand: ')
            # must insert code to take product brand and match it to a brand id, maybe a separate function that matches brand name with brand id
            # maybe take the product brand entered, look it up in the table, if it doesn't exist say 'this looks like a new brand, would you like to add it to the db? to view list of brands, press XX

            brand_id = find_brand_id(product_brand)

            new_product = Product(product_name=product_name, product_quantity=product_quantity, product_price=product_price, date_updated=date_updated, brand_id=brand_id)
            session.add(new_product)
            session.commit()
            print('Product added!')
            time.sleep(1.5)

        elif choice == 'V':
            # view product
            #generates a list of all product ids
            product_id_options = []
            for product in session.query(Product):
                product_id_options.append(product.product_id)
            id_error = True
            while id_error:
                chosen_product_id = input(f'''
                    \nProduct ID Options: {product_id_options}
                    \rPlease enter a product id to view the product: ''')
                chosen_product_id = clean_id(chosen_product_id, product_id_options)
                if type(chosen_product_id) == int:
                    id_error = False
            chosen_product = session.query(Product).filter(Product.product_id==chosen_product_id).first()
            print(chosen_product)
            print(f'''
                \nProduct Name: {chosen_product.product_name}
                \nProduct Quantity: {chosen_product.product_quantity}
                \rDate Last Updated: {chosen_product.date_updated}
                \rPrice: ${chosen_product.product_price / 100}
                \rBrand ID: {chosen_product.brand_id}''')
                # should add some way here to display Brand Name

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
            # would be good to add code to show multiple products if they are both/all the most expensive/least expensive
            most_expensive_product = session.query(Product).order_by(Product.product_price).first()
            least_expensive_product = session.query(Product).order_by(Product.product_price.desc()).first()
            # this next one is not correct...should group by brand id then return brand
            #brand_with_most_products = session.query(Product).count()

            product_prices = []
            total_value_of_inventory = 0
            for product in session.query(Product):
                    product_prices.append(product.product_price)
                    total_value_of_inventory = total_value_of_inventory + (product.product_quantity * product.product_price)
            mean_product_price = round(mean(product_prices))
            median_product_price = median(product_prices)
            mode_product_price = mode(product_prices)
            total_number_of_items_in_inventory = session.query(Product).count()

            # \rMost Expensive Product: {most_expensive_product}
            # \rLeast Expensive Product: {least_expensive_product}
            #\rBrand with the Most Products: {brand_with_most_products}

            print(f'''\n****** INVENTORY ANALYSIS *****
                \rAverage (Mean) Product Price: {mean_product_price}
                \rMedian Product Price: {median_product_price}
                \rMode Product Price: {mode_product_price}
                \rTotal Number of Items in Inventory: {total_number_of_items_in_inventory}
                \rTotal Value of Inventory: {total_value_of_inventory}''')
            input('\nPress enter to return to the main menu.')
        else:
            print('GOODBYE')
            app_running = False




if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_inventory_csv()
    program()