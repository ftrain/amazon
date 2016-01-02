from models import *
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import gzip
import pprint
import time
import re
import md5
import itertools
import HTMLParser
import multiprocessing
h = HTMLParser.HTMLParser()

def parse(path, skip):
  i = 0
  g = gzip.open(path, 'r')
  for line in itertools.islice(g,skip,None):
      yield eval(line)

def upsert_brand(brand=None, session=None):
  """Returns id"""
  if brand is not None:
    existing_brands = session.query(Brand).\
                          filter(Brand.title==brand).\
                          all()
    if len(existing_brands) > 0:
      return existing_brands[0].id
    else:
      brand_db = Brand(title=brand)
      session.add(brand_db)
      return brand_db.id


def tidy_title(s):
  s = re.sub(r"&quot;",'"',s)
  s = re.sub(r"\&amp;","\&",s)
  return s

def smooth(s):
  s = re.sub(r"&amp;","&", s)
  s = re.sub(r"&","and", s)  
  s = re.sub(r"\s+","_", s)
  s = re.sub(r"[^A-Za-z0-9_]","", s)
  return s

def escaper(thing):
  if thing is not None:
    return h.unescape(thing)
  else:
    return thing

def insert_product(product, session):
    cat = None
    rank = None
    if product.get('salesRank') is not None:
      for k,v in product.get('salesRank').items():
        cat = smooth(k)
        rank = v
    product_db = Product(id=product.get('asin'),
                         title=escaper(product.get('title')),
                         image_url=product.get('imUrl'),
                         description=escaper(product.get('description')),
                         rank_category = cat,
                         ranking = rank,
                         brand_id = upsert_brand(product.get('brand'), session),
                         price=product.get('price'),)
    session.add(product_db)

def insert_categories(product, cat_dict, session):
  if product.get('categories'):
    cats = [".".join([smooth(x) for x in cat]) for cat in product.get('categories')]
    for cat in cats:
      if cat_dict.get(cat):
        pass
      else:
        cat_dict[cat]=Category(categories=cat)
        session.add(cat_dict[cat])
      pca = ProductCategoryAssociation(product_id=product.get('asin'),
                                       category_id=cat_dict[cat].id)
      session.add(pca)

def thousandth(i,product,times):
  print i
  total = sum(times.values())
  x = 1
  title = product.get('title')
  if title is None:
    title = ""
    print "{:,} {:<40s}".format(i, title[0:40])
    for k,v in times.iteritems():
      x = x + 1
      perc = round(100.0*v/total)
      print "{0:.2f}%".format(perc)
      print "{:<10s}".format(k)

      
def __main__():
  i = 0    
  cat_dict = {}
  brand_dict = {}  
  times = {'product':0, 'related':0, 'commit':0, 'categories':0, 'sales_rank':0}
  begin = time.time()

  do_related = True
  do_salesrank = False
  
  db = DB()
  session = db.session

  # Cache categories
  for c in session.query(Category):
    cat_dict[c.categories] = c

  for b in session.query(Brand):
    brand_dict[b.title] = b
  
  for product in parse('/Volumes/BWArchive/Amazon/metadata.json.gz', 4611798):
    i = i + 1
    if i % 1000 == 0:
      now = time.time()
      try:
        session.commit()
      except IntegrityError as e:
        session.rollback()        
        print "At line {} already exists.".format(i)
      times['commit'] = times['commit'] + time.time() - now
      thousandth(i,product,times)
      
    now = time.time()
    insert_product(product,session)
    times['product'] = times['product'] + time.time() - now 

    # Category
    now = time.time()
    insert_categories(product, cat_dict, session)
    times['categories'] = times['categories'] + time.time() - now
  
    # Related items
    now = time.time()
    if do_related:
      related = product.get('related')
      if related is not None:
        for k,vs in related.items():
          for v in vs:
            session.add(LikeProductAssociation(like_type=k,
                                               like_product_id=v,
                                               product_id=product.get('asin')))
    times['related'] = times['related'] + time.time() - now

    now = time.time()

    ########################################    
    # Salesrank
    ########################################    
    if do_salesrank:    
      if product.get('salesRank') is not None:
        for k,v in product.get('salesRank').items():
          cat = smooth(k)
          if cat_dict.get(cat):
            pass
          else:
            cat_dict[cat]=Category(categories=cat)
            session.add(cat_dict[cat])
          
            session.add(Ranking(product_id = product_db.id,
                                category_id = cat_dict[cat].id,
                                ranking = v))
        times['sales_rank'] = times['sales_rank'] + time.time() - now            

  print "done; committing"
  session.commit()
        
__main__()

