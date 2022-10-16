from sqlalchemy import (create_engine, Column, Integer,
                        String, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import csv
import datetime
import time

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
                product_quantity = row[2]
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
        # why does choice.upper not work here?
        if choice in ['N', 'V', 'A', 'B', 'Q']:
            return choice
        else:
            input('''
            \rPlease choose one of the options above (N, V, A, B, or Q)
            \rPress enter to try again.''')

# Here is where I am...working on updating the book.db code to this new program
def program():
    program_running = True
    while program_running:
        choice = menu()
        if choice == 'N':
            #New Product
            product_name = input('Product Name:  ')
            product_quantity = input('Product Quantity: ')
            product_price = input('Product Price: ')
            product_brand = input('Product Brand: ')
            price_error = True
            while price_error:
                price = input('Price (Ex: 25.64):  ')
                price = clean_price(price)
                if type(price) == int:
                    price_error = False
            new_product = Product(product_name=product_name, product_quantity=product_quantity, product_price=product_price, date_updated = today(), brand_id=brand_id)
            session.add(new_product)
            session.commit()
            print('Product added!')
            time.sleep(1.5)


        elif choice == 'V':
            #view books
            for book in session.query(Book):
                print(f'{book.id} | {book.title} | {book.author}')
            input('\nPress enter to return to the main menu.')
        elif choice == 'A':
            #search
            id_options = []
            for book in session.query(Book):
                id_options.append(book.id)
            id_error = True
            while id_error:
                id_choice = input(f'''
                    \nID Options: {id_options}
                    \rBook id: ''')
                id_choice = clean_id(id_choice, id_options)
                if type(id_choice) == int:
                    id_error = False
            the_book = session.query(Book).filter(Book.id==id_choice).first()
            print(f'''
                \n{the_book.title} by {the_book.author}
                \rPublished: {the_book.published_date}
                \rPrice: ${the_book.price / 100}''')
            sub_choice = submenu()
            if sub_choice == '1':
                #edit
                the_book.title = edit_check('Title', the_book.title)
                the_book.author = edit_check('Author', the_book.author)
                the_book.published_date = edit_check('Date', the_book.published_date)
                the_book.price = edit_check('Price', the_book.price)
                session.commit()
                print('Book updated!')
                time.sleep(1.5)

            elif sub_choice == '2':
                #delete
                session.delete(the_book)
                session.commit()
                print('Book delected!')
                time.sleep(1.5)
        elif choice == 'B':
            #analyze
            oldest_book = session.query(Book).order_by(Book.published_date).first()
            newest_book = session.query(Book).order_by(Book.published_date.desc()).first()
            total_books = session.query(Book).count()
            python_books = session.query(Book).filter(Book.title.like('%Python%')).count()
            print(f'''\n****** BOOK ANALYSIS *****
                \rOldest Book: {oldest_book}
                \rNewest Book: {newest_book}
                \rTotal Books: {total_books}
                \rNumber of Python Books: {python_books}''')
            input('\nPress enter to return to the main menu.')

        else:
            print('GOODBYE')
            app_running = False




if __name__ == "__main__":
    Base.metadata.create_all(engine)
    add_brands_csv()
    add_inventory_csv()
    program()