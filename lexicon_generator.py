import json
import re
import time
from Queue import Queue
from stemming.porter2 import stem
from threading import Thread

# Data Source
_YELP_DATASET = './data/yelp_academic_dataset.json'
# Parsed reviews
_YELP_PARSED_REVIEWS = './data/yelp_parsed_reviews.json'
# Token frequencies in reviews.
_YELP_LEXICON_FILE = './data/yelp_lexicon.txt'
# Stop words file.
_STOP_WORDS_FILE = './lib/stopwords.txt'
# Regex to split tokens.
_REGEX_TOKEN_SPLIT_PATTERN = '[ \.\n\t,\:;\\\"/\]\[\{\}\(\)&\=\?]'


def _IsReview(yelp_data_object):
  """Returns true if a yelp_data_object is of type review."""
  return yelp_data_object.get('type') == 'review'


def _GetReviewTextAndRating(yelp_data_object):
  """Returns a tuple containing (stat rating, text review) of a yelp review comment."""
  return (yelp_data_object.get('stars', -1),
      yelp_data_object.get('text', 'EMPTY_TEXT').encode('ascii', 'ignore'))


def _ParseYelpDataAndReturnReviews(filepath):
  review_text_and_ratings = list()
  for line in open(filepath):
    if not line:  # Ignore empty lines.
      continue
    yelp_data_object = json.loads(line)
    if _IsReview(yelp_data_object):
      review_text_and_ratings.append(_GetReviewTextAndRating(yelp_data_object))
  return review_text_and_ratings


def _StoreParsedAndStemmedReviews(review_text_and_ratings, filepath):
  """Dumps in the json form {'text': <stemmed_text>, 'rating': <stars>}."""
  fp = open(filepath, 'w')
  for review in review_text_and_ratings:
    unstemmed_review = review[1]
    stemmed_review = ''
    for token in unstemmed_review.split(' '):
      try:
        stemmed_review += stem(token) + ' '
      except IndexError as e:
        print 'IndexError while trying to stem \"%s\"' % token
    # Convert to ascii, ignore non-ascii characters.
    fp.write(json.dumps(
          {'rating': review[0] , 'text': stemmed_review}) + '\n')
  fp.close()

def _ReadStopWords(stopwords_filepath):
  """Reads and returns a set containing stop words."""
  return set(x.lower() for x in open(stopwords_filepath).read().split('\n'))

    

def _ProduceLexicon(review_text_and_ratings, stopwords):
  """Returns a dictionary object containing tokens and their freqeuncies."""
  token_frequencies = {}
  progress_max = len(review_text_and_ratings)
  progress = 0;
  t = time.time()
  for (rating, review) in review_text_and_ratings:
    progress = progress + 1
    if progress % (progress_max / 100) == 0:
      progress_pct = progress * 100.0 / progress_max
      print '%d / %d (%.2f%%) ETA: %d seconds' % \
        (progress, progress_max, progress_pct,
        (time.time() - t) / (progress_max / 100) * (progress_max - progress))
      t = time.time()

    tokens = re.split(_REGEX_TOKEN_SPLIT_PATTERN, review)
    for token in tokens:
      # TODO(ashishb): If token has more than two dashes separated by few(3?) chars then split it.
      token = token.strip().lower()
      try:
        token = stem(token)
      except IndexError as e:
        print 'IndexError while trying to stem \"%s\"' % token
      if token and token not in stopwords:  # Ignore empty tokens.
        token_frequencies[token] = 1 + token_frequencies.get(token, 0)
  return token_frequencies

#class Worker(Thread):
#  def __init__(self, workQ, resultQ, stopwords, review_text_and_ratings, n):
#    Thread.__init__(self)
#    self.workQ = workQ
#    self.resultQ = resultQ
#    self.stopwords = stopwords
#    self.review_text_and_ratings = review_text_and_ratings
#    self.n = n
#
#  def run(self):
#    while True:
#      (s, t) = self.workQ.get(True)
#      token_frequenies = \
#          _ProduceLexicon(self.review_text_and_ratings[s:t], self.stopwords)
#      self.resultQ.put(token_frequenies)
#      self.workQ.task_done()
#      print time.time(), (100 - self.workQ.qsize() * 100.0 / self.n)
#
#def _ThreadedProduceLexicon(review_text_and_ratings, stopwords):
#  workQ = Queue()
#  resultQ = Queue()
#  numThreads = 8
#  numShards = 100
#  for i in xrange(numThreads):
#    w = Worker(workQ, resultQ, stopwords, review_text_and_ratings, numShards)
#    w.daemon = True
#    w.start()
#
#  numDocs = len(review_text_and_ratings)
#  docsPerShard = numDocs / numShards
#  for i in xrange(numShards):
#    work = (i * docsPerShard, i * docsPerShard + docsPerShard - 1)
#    workQ.put(work)
#
#  t = time.time()
#  workQ.join()
#  print time.time - t

def _StoreTokenFrequencies(token_frequencies, filepath):
  token_frequencies_list = token_frequencies.items()
  token_frequencies_list = sorted(token_frequencies_list, key=lambda entry: entry[1], reverse=True)
  fp = open(filepath, 'w')
  for (k, v) in token_frequencies_list:
    fp.write(k + ' ' + str(v) + '\n')
  fp.close()


# Main
print 'Reading reviews from', _YELP_DATASET
review_text_and_ratings = _ParseYelpDataAndReturnReviews(_YELP_DATASET)
assert review_text_and_ratings
print 'Finished reading reviews.\nNow writing parsed reviews to', _YELP_PARSED_REVIEWS
_StoreParsedAndStemmedReviews(review_text_and_ratings, _YELP_PARSED_REVIEWS)
print 'Finished writing parsed reviews.\nNow generating lexicon.'
stopwords = _ReadStopWords(_STOP_WORDS_FILE)
#token_frequencies = _ThreadedProduceLexicon(review_text_and_ratings, stopwords)
token_frequencies = _ProduceLexicon(review_text_and_ratings, stopwords)
print 'writing lexicon to', _YELP_LEXICON_FILE
_StoreTokenFrequencies(token_frequencies, _YELP_LEXICON_FILE)
print 'Everything done.'
