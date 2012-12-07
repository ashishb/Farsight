import json
import re

from pyaspell import Aspell
from progress import Progress
from random import Random
from stemming.porter2 import stem

_SAMPLING_RATE = 0.1
_DO_SPELLING = True
_DO_STEMMING = False
_USE_STOPWORDS = False
_CREATE_BIGRAMS = True
_CREATE_TRIGRAMS = False

# Data Source
_YELP_DATASET = './data/yelp_academic_dataset.json'
# Parsed reviews
_YELP_PARSED_REVIEWS = './data/parsed_reviews.json'
# Token frequencies in reviews.
_YELP_LEXICON_FILE = './data/lexicon.txt'
# Stop words file.
_STOP_WORDS_FILE = './lib/stopwords.txt'
# Regex to split tokens.
_REGEX_TOKEN_SPLIT_PATTERN = '[ \.\n\t,\:;\\\"/\]\[\{\}\(\)&\=\?]'

spell = Aspell(("lang", "en"))

stopwords = set(stem(x.lower()) for x in \
    open(_STOP_WORDS_FILE).read().split('\n'))
print '#stopwords', len(stopwords)

businesses = {}
reviews = list()

# Load file.
rand = Random()
with open(_YELP_DATASET) as fp:
  progress = Progress('Read file', 474434)
  for line in fp:
    progress.Update()
    if not line:  # Ignore empty lines.
      continue
    data_obj = json.loads(line)
    if data_obj.get('type') == 'review':
      if rand.random() < 1 - _SAMPLING_RATE:
        continue
      data_obj['text'] = \
          data_obj.get('text', 'EMPTY_TEXT').encode('ascii', 'ignore')
      reviews.append(data_obj)
    elif data_obj.get('type') == 'business':
      businesses[data_obj.get('business_id')] = data_obj
print '#businesses: ', len(businesses)
print '#reviews: ', len(reviews)
print ''

# Filter reviews.
original_reviews = reviews
reviews = list()
filter_progress = Progress('Filter', len(original_reviews))
for review in original_reviews:
  filter_progress.Update()
  business = businesses.get(review.get('business_id'), None)
  if not business:
    continue
  if 'Restaurants' not in business.get('categories'):
    continue
  reviews.append(review)
print '#reviews after filter: ', len(reviews)
print ''

# Stemming
token_cache = {}
stem_progress = Progress('Stemming', len(reviews))
for review in reviews:
  stem_progress.Update()
  stemmed_review_text = []
  review_text = re.sub('[^a-zA-Z0-9]', ' ', review.get('text'))
  for token in re.split(_REGEX_TOKEN_SPLIT_PATTERN, review_text):
    original_token = token = token.strip().lower()
    cached_token = token_cache.get(token, None)
    if cached_token:
      if cached_token == '_IGNORE_':
        continue
      else:
        stemmed_review_text.append(cached_token)
    else:
      if _DO_SPELLING:
        if not spell.check(token):
          suggests = spell.suggest(token)
          if not suggests:
            token_cache[original_token] = '_IGNORE_'
            continue
          token = suggests[0].lower()

      if _DO_STEMMING:
        try:
          stemmed_token = stem(token)
          token = stemmed_token
        except IndexError as e:
          pass

      # Ignore empty tokens.
      if len(token) > 1:
        if not _USE_STOPWORDS or \
           token not in stopwords or \
           token == 'not' or \
           token == 'no':
          stemmed_review_text.append(token)
          token_cache[original_token] = token
        else:
          token_cache[original_token] = '_IGNORE_'
      else:
        token_cache[original_token] = '_IGNORE_'

  # Create bi-grams
  if _CREATE_BIGRAMS:
    bigrams = []
    stemmed_review_text_len = len(stemmed_review_text) 
    i = 0
    while i < stemmed_review_text_len - 1:
      bigrams.append(stemmed_review_text[i] + '-' + stemmed_review_text[i + 1])
      if stemmed_review_text[i] == 'no' or stemmed_review_text[i] == 'not':
        del stemmed_review_text[i + 1]
        stemmed_review_text_len = len(stemmed_review_text) 
      i = i + 1
    stemmed_review_text.extend(bigrams)

  # Create tri-grams
  if _CREATE_TRIGRAMS:
    trigrams = []
    for i in xrange(len(stemmed_review_text) - 2):
      trigrams.append(
          stemmed_review_text[i] + '-' +
          stemmed_review_text[i + 1] + '-' +
          stemmed_review_text[i + 2])
    stemmed_review_text.extend(trigrams)

  review['stemmed_text'] = stemmed_review_text
print ''

# Write parsed reviews
with open(_YELP_PARSED_REVIEWS, 'w') as fp:
  progress = Progress('Write parsed reviews', len(reviews))
  for review in reviews:
    progress.Update()
    fp.write(json.dumps({
      'rating': review.get('stars'),
      'text': ' '.join(review.get('stemmed_text'))
    }))
    fp.write('\n')
print ''

# Create Lexicon
token_frequencies = {}
create_lexicon_progress = Progress('Create Lexicon', len(reviews))
for review in reviews:
  create_lexicon_progress.Update()
  for token in review.get('stemmed_text'):
    token_frequencies[token] = 1 + token_frequencies.get(token, 0)
print ''

# Write Lexicon file
token_frequencies_list = token_frequencies.items()
token_frequencies_list = sorted(
  token_frequencies_list, key=lambda entry: entry[1], reverse=True)
with open(_YELP_LEXICON_FILE, 'w') as fp:
  create_lexicon_progress = Progress('Write Lexicon file', \
      len(token_frequencies_list))
  for (k, v) in token_frequencies_list:
    create_lexicon_progress.Update()
    fp.write(k + ' ' + str(v) + '\n')
print ''

print 'Everything done.'
