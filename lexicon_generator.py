import json
import nltk
import re

from pyaspell import Aspell
from progress import Progress
from random import Random
from stemming.porter2 import stem

import constants

_SAMPLING_RATE = 0.1
_DO_SPELLING = True
_DO_STEMMING = False
_IGNORE_STOPWORDS = True
_CREATE_BIGRAMS = True
_CREATE_TRIGRAMS = False
_CREATE_QUADGRAMS = False
_CREATE_PENTAGRAMS = False
_CREATE_HEXAGRAMS = False
_CREATE_SEPTAGRAMS = False
# Allowed parts of speech.
_ALLOWED_POS = set([
'CC', #   coordinating conjunction  and
'CD', #   cardinal number   1, third
'DT', #   determiner  the
'EX', #  existential there  there is
'#FW', #   foreign word  d'hoevre
'#IN', #   preposition/subordinating conjunction   in, of, like
'JJ', #   adjective   green
'JJR', #  adjective, comparative  greener
'JJS', #  adjective, superlative  greenest
#LS   list marker   1)
#MD   modal   could', will
#NN   noun', singular or mass  table
#NNS  noun plural   tables
#NNP  proper noun', singular   John
#NNPS   proper noun', plural   Vikings
#PDT  predeterminer  both the boys
#POS  possessive ending   friend's
#PRP  personal pronoun  I', he, it
#PRP$   possessive pronoun  my', his
'RB', #   adverb  however, usually, naturally, here, good
'RBR', #  adverb, comparative   better
'RBS', #  adverb, superlative   best
#RP   particle  give up
#TO   to to go', to him
#UH   interjection  uhhuhhuhh
'VB', #   verb, base form   take
'VBD', #  verb, past tense  took
'VBG', #  verb, gerund/present participle   taking
'VBN', #  verb, past participle   taken
'VBP', #  verb, sing. present, non-3d   take
'VBZ', # verb, 3rd person sing. present  takes
#WDT  wh-determiner   which
'WP', #   wh-pronoun  who, what
'WP$', #  possessive wh-pronoun   whose
'WRB', #  wh-abverb   where, when
])

print 'Create bigrams:', _CREATE_BIGRAMS
print 'Create trigrams:', _CREATE_TRIGRAMS
print 'Create quadgrams:', _CREATE_QUADGRAMS
print 'Create pentagrams:', _CREATE_PENTAGRAMS
print 'Create hexagrams:', _CREATE_HEXAGRAMS
print 'Create septagrams:', _CREATE_SEPTAGRAMS

# Data Source
_YELP_DATASET = './data/yelp_academic_dataset.json'
# Parsed reviews
_YELP_PARSED_REVIEWS = './data/parsed_reviews.json'
# Token frequencies in reviews.
_YELP_LEXICON_FILE = './data/lexicon.txt'
# Stop words file.
_STOP_WORDS_FILE = './lib/stopwords.txt'
# Power words file.
_POWER_WORDS_FILE = './lib/powerwords.txt'
# Regex to split tokens.
#_REGEX_TOKEN_SPLIT_PATTERN = '[ \.\n\t,\:;\\\"/\]\[\{\}\(\)&\=\?]'
_REGEX_TOKEN_SPLIT_PATTERN = '[ \n\t,\:;\\\"/\]\[\{\}\(\)&\=\?]'

spell = Aspell(("lang", "en"))

stopwords = set(stem(x.lower()) for x in \
    open(_STOP_WORDS_FILE).read().split('\n'))
powerwords = set()
for x in open(_POWER_WORDS_FILE).read().split('\n'):
  x = x.strip()
  if x:
    powerwords.add(x)
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
nltk_pos_cache = {}
stem_progress = Progress('Stemming', len(reviews))
for review in reviews:
  stem_progress.Update()
  stemmed_review_text = []
  review_text = re.sub('[^a-zA-Z0-9\.]', ' ', review.get('text'))
  for (token, pos) in nltk.pos_tag(re.split(_REGEX_TOKEN_SPLIT_PATTERN, review_text)):
    if pos in _ALLOWED_POS:
    # over-writing is fine here, we are looking for approximate pos anyways.
      nltk_pos_cache[token] = pos
  for token in re.split(_REGEX_TOKEN_SPLIT_PATTERN, review_text):
    token = token.strip().lower()
    token_ends_with_full_stop = False
    if token.endswith('.'):
      token_ends_with_full_stop = True
      token = token[:-1]
    # Experimental: Ignore everything except ALLOWED_POS.
    # print 'Warning: Ignoring everything except verb'
    cached_pos = nltk_pos_cache.get(token, None)
    if not cached_pos:
      cached_pos = nltk.pos_tag([token])[0][1]
    if not cached_pos in _ALLOWED_POS:
      continue
    # Experiment ends.
    original_token = token
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
        if not _IGNORE_STOPWORDS or token not in stopwords:
          stemmed_review_text.append(token)
          if token_ends_with_full_stop:
            stemmed_review_text.append('.')
          token_cache[original_token] = token
        else:
          token_cache[original_token] = '_IGNORE_'
      else:
        token_cache[original_token] = '_IGNORE_'

  def add_k_grams(stemmed_review_text, K):
    kgrams = []
    for i in xrange(len(stemmed_review_text) - (K - 1)):
      tmp  = ''
      for j in range(0, K):
        if stemmed_review_text[i+j] == '.':
          break  # Do not cross the end-of-sentence "fullstop" boundary.
          #import pdb; pdb.set_trace()
        tmp += stemmed_review_text[i+j] + '-'
      # In case of "not really good", don't make a feature "really good". 
      if i>0 and (stemmed_review_text[i-1].lower().startswith('no')):
        continue
      # FIXME: this is useless - delete this.
      # no[t] should be the first word, if it ever appears in the kgram ("no no" is OK).
      if (stemmed_review_text[i].lower not in ('no', 'not') and
          (('no-' in tmp) or ('not-' in tmp))):
          continue;
      # Yes, this is not the best way but still to count only powerful words (like "no").
      # We cannot create all kgrams since that blows up the space even for K=4
## FIXME: this seems useless - delete this.
##      for power_word in powerwords:
##        if power_word in tmp and not tmp.endswith('not-'):
##          kgrams.append(tmp)
      kgrams.append(tmp[:-1])
    return kgrams

  stemmed_review_text_with_k_grams = []
  for x in stemmed_review_text:
    if x != '.':
      stemmed_review_text_with_k_grams.append(x) 

  # Create bi-grams
  if _CREATE_BIGRAMS:
    K = 2
    stemmed_review_text_with_k_grams.extend(add_k_grams(stemmed_review_text, K))
##    bigrams = []
##    stemmed_review_text_len = len(stemmed_review_text) 
##    i = 0
##    while i < stemmed_review_text_len - 1:
##      bigrams.append(stemmed_review_text[i] + '-' + stemmed_review_text[i + 1])
##      if stemmed_review_text[i] == 'no' or stemmed_review_text[i] == 'not':
##         del stemmed_review_text[i + 1]
##         stemmed_review_text_len = len(stemmed_review_text) 
##      i = i + 1
##    stemmed_review_text_with_k_grams.extend(bigrams)

  # Create tri-grams.
  if _CREATE_TRIGRAMS:
    K = 3
    stemmed_review_text_with_k_grams.extend(add_k_grams(stemmed_review_text, K))
  # Create quad-grams
  if _CREATE_QUADGRAMS:
    K = 4
    stemmed_review_text_with_k_grams.extend(add_k_grams(stemmed_review_text, K))
  # Create penta-grams
  if _CREATE_PENTAGRAMS:
    K = 5
    stemmed_review_text_with_k_grams.extend(add_k_grams(stemmed_review_text, K))
  # Create hexa-grams
  if _CREATE_HEXAGRAMS:
    K = 6
    stemmed_review_text_with_k_grams.extend(add_k_grams(stemmed_review_text, K))
  # Create septa-grams
  if _CREATE_SEPTAGRAMS:
    K = 7
    stemmed_review_text_with_k_grams.extend(add_k_grams(stemmed_review_text, K))

  review['stemmed_text'] = stemmed_review_text_with_k_grams
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
    if not _IGNORE_STOPWORDS or (k not in stopwords): 
      fp.write(k + ' ' + str(v) + '\n')
print ''

print 'Everything done.'
