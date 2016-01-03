import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils.types import TSVectorType
from ltree import *

engine = create_engine('postgresql+psycopg2://ford:@/amazon',
                       echo=False)
Base = declarative_base(engine)
make_searchable()


"""
CITE PAPER

One day as I was traveling through the Internet I ran across an interesting tweet, saying that Amazon's entire database of products and reviews was available to the curious. After a very brief correspondence with a professor I learned that this was indeed true, for research purposes---the only purposes to which I would apply myself!---and I downloaded the whole thing, about 22 gigabytes of data. Not big data per se but not the smallest either, and containing a good portion of what makes Amazon Amazon.

I think like many people my relationship with Amazon is--well, first, deeply asymmetrical, because they take my money and send me boxes, but I don't get the sense that they think much about my otherwise. And yet I think about them all the time, because they sent us diapers, because they work their white-collar people so hard that they lose their minds, and because they work their blue-collar people hard enough to send them to the hospital; and because I both admire and fear them in a way that confuses me---admiration for their technical abilities, the religion they have made of box-packing and distribution, their relentlessness; fear because they are huge and smart and wild for success and now big enough to do serious damage, like a mini-China in our midst. I suppose if not them it would be someone else, but it's definitely them.

And so I absorbed the data from Amazon, which was complex but not unduly so, into a database. It did fill up what remained of my hard drive, but my hard drive is over-filled in any case. It lacked a lot of the data I'd need to be truly threatening. It lacked, for example, the dates of publication for the books in its catalog. That was a little sad. But 

"""

class DB(object):
    session = None
    def __init__(self):
        Session = sessionmaker(bind=engine,autoflush=False)
        self.session = Session()    
    
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    categories = Column(LTREE)
    __table_args__ = (UniqueConstraint('categories'),)
    
class Brand(Base):
    __tablename__ = 'brand'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

class ProductCategoryAssociation(Base):
    __tablename__ = 'product_category_association'
    id = Column(Integer, primary_key=True)    
    product_id = Column(String)
    category_id = Column(Integer)
    
class LikeProductAssociation(Base):
    __tablename__ = 'like_product_association'
    id = Column(Integer, primary_key=True)
    like_type = Column(Enum('also_bought',
                            'also_viewed',
                            'buy_after_viewing',
                            'bought_together',
                            name='like_types'))
    
    product_id = Column(String, ForeignKey('product.id'))
    like_product_id = Column(String, ForeignKey('product.id'))

class Product(Base):
    __tablename__ = 'product'
    id = Column(String, primary_key=True)
    title = Column(String, nullable=True)
    categories = Column(String, nullable=True)
    rank_cat = Column(String, nullable=True)
    ranking = Column(Integer)    
    description = Column(String, nullable=True)    
    price = Column(Float, nullable=True)
    image_url = Column(String)
    rank_category = Column(String)
    ranking = Column(Integer)
#    categories = relationship("ProductCategoryAssociation", backref="categories")    
    brand_id = Column(Integer, ForeignKey('brand.id'))
    search_vector_title = Column(TSVectorType('title'))
    search_vector_description = Column(TSVectorType('description'))
    
class Reviewer(Base):
    __tablename__ = 'reviewer'
    id = Column(String, primary_key=True)    
    name = Column(String)
 
class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True)
    product_id = Column(String, ForeignKey('product.id'))    
    voter_helpful = Column(Integer)
    voter_total = Column(Integer)
    text = Column(Text)
    summary = Column(String)
    rating = Column(Float)
    date_posted = Column(DateTime)
    search_vector = Column(TSVectorType('text', 'summary'))

#Base.metadata.drop_all(engine)    
sa.orm.configure_mappers() 
Base.metadata.create_all(engine)

