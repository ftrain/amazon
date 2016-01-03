from models import *
import hashlib
import gzip
import sys
import pprint
import time
import re
import md5
import itertools
import HTMLParser
import multiprocessing

html_parser = HTMLParser.HTMLParser()
#DIR = ''
#METADATA = '{}'.format(DIR, FILE)
#METADATA = sys.argv[1]

def parse(path, skip):
  i = 0
  g = open(path, 'r')
  for line in itertools.islice(g,skip,None):
      yield eval(line)

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
    unescaped = html_parser.unescape(thing)
    replaced = re.sub(r"'", "''", unescaped)
    quoted = "'{}'".format(replaced.encode('utf-8'))
    return quoted
  else:
    return 'NULL'


def __main__():
  print "\nSTART TRANSACTION;"    
  i = 0
  relateds = open('related.tsv', 'w')
  brands_d = {}
  brand_i = 0

  cats_d = {}
  cats_i = 0
  for line in sys.stdin:
    i = i + 1
    if i % 10000 == 0:
      print "\n\nCOMMIT;\n\n"
      print "\n\nSTART TRANSACTION;\n\n"
      
    print "\n"
      
    product = eval(line)
    product_id = product.get('asin')
    
    brand = product.get('brand')
    brand_id = brands_d.get(brand)
    
    if brand is not None and brand_id is not None:
      print "INSERT INTO brand (id, title) VALUES ({},{});".format(brand_i, escaper(product.get('brand'))),
      brands_d[brand] = brand_i
      brand_id = brand_i
      brand_i = brand_i + 1
      
    if product.get('salesRank') is not None:
      for k,v in product.get('salesRank').items():
        cat = smooth(k)
        rank = v

    related = product.get('related')
    if related is not None:
      for k,vs in related.items():
        for v in vs:
          relateds.write("{}\t{}\t{}\n".format(k,v,product_id))
            
    id=product_id
    title = escaper(product.get('title'))
    image_url = escaper(product.get('imUrl'))
    description = escaper(product.get('description'))
    rank_category = escaper(cat)
    ranking = rank
    brand_id = escaper(brand_id)
    price = product.get('price')
    if price is None:
      price = 'NULL'
    statement = "INSERT INTO product (id, title, image_url, description, rank_category, ranking, brand_id, price) VALUES ('{}', {}, {}, {}, {}, {}, {}, {});".format(id, title, image_url, description, rank_category, ranking, brand_id, price)
    print statement,

    if product.get('categories') is not None:
      cats = [".".join([smooth(x) for x in cat]) for cat in product.get('categories')]
      for cat in cats:
        cat_id = cats_d.get(cat)
        if cat_id is None:
          print "INSERT INTO category (id, categories) VALUES ({}, '{}');".format(cats_i, cat),
          cat_id = cats_i
          cats_d[cat]=cat_id
          cats_i = cats_i + 1
          statement = "INSERT INTO product_category_association (product_id, category_id) VALUES ('{}', {});".format(product_id, cat_id)
          print statement,
    
  print "\nCOMMIT;"
  relateds.close()
    
__main__()

