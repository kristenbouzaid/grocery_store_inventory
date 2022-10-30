from sqlalchemy import (create_engine, Column, Integer, String, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


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