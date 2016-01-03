from models import *
import datetime
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
    return html_parser.unescape(thing).encode('utf-8')
  else:
    return ''


#  {
#  "reviewerID": "A2SUAM1J3GNN3B",
#  "asin": "0000013714",
#  "reviewerName": "J. McDonald",
#  "helpful": [2, 3],
#  "reviewText": "I bought this for my husband who plays the piano.  He is having a wonderful time playing these old hymns.  The music  is at times hard to read because we think the book was published for singing from more than playing from.  Great purchase though!",
#  "overall": 5.0,
#  "summary": "Heavenly Highway Hymns",
#  "unixReviewTime": 1252800000,
#  "reviewTime": "09 13, 2009"
#}

def datefixer(timestamp):
  if timestamp is not None:
    return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
  else:
    return ''
  
def __main__():
  reviewers_f = open('reviewers.tsv', 'w')
  reviews_f = open('reviews.tsv', 'w')
  reviewers_d = {}
  reviews_pk = 1
  
  for line in sys.stdin:
    review = eval(line)
    reviewer_id = review.get('reviewerID')
    if reviewers_d.get(reviewer_id) is None:
      reviewers_f.write("{}\t{}\n".format(reviewer_id, review.get('reviewerName')))
      reviewers_d[reviewer_id] = True
    helpful = review.get('helpful')
    helpful_top = helpful[0]
    helpful_bottom = helpful[1]
    reviews_f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(reviews_pk,
                                          review.get('asin'),
                                          helpful_top,
                                          escaper(review.get('reviewText')),
                                          escaper(review.get('summary')),                                          
                                          review.get('overall'),
                                          datefixer(review.get('unixReviewTime')),
                                          review.get('reviewerID'),                                          
                                          helpful_bottom))
    reviews_pk = reviews_pk + 1
    

    
__main__()


