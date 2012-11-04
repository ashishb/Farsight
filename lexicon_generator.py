import json
import re
import time
from stemming.porter2 import stem

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


class Progress():
  def __init__(self, progress_max):
    self. progress_max = progress_max
    self.progress = 0;
    self.time = time.time()

  def PrintProgress(self):
    self.progress = self.progress + 1
    if self.progress % (self.progress_max / 100) == 0:
      progress_pct = self.progress * 100.0 / self.progress_max
      print '%d / %d (%.2f%%) ETA: %d seconds' % \
        (self.progress, self.progress_max, progress_pct,
        (time.time() - self.time) / (self.progress_max / 100) * \
          (self.progress_max - self.progress))
      self.time = time.time()

def _IsReview(yelp_data_object):
  """Returns true if a yelp_data_object is of type review."""
  return yelp_data_object.get('type') == 'review'


def _GetReviewTextAndRating(yelp_data_object):
  """Returns a tuple containing (stat rating, text review) of a yelp review comment."""
  return (yelp_data_object.get('stars', -1),
      yelp_data_object.get('text', 'EMPTY_TEXT').encode('ascii', 'ignore'))


def _ParseYelpDataAndReturnReviews(filepath):
  rating_and_review_text = list()
  for line in open(filepath):
    if not line:  # Ignore empty lines.
      continue
    yelp_data_object = json.loads(line)
    if _IsReview(yelp_data_object):
      rating_and_review_text.append(_GetReviewTextAndRating(yelp_data_object))
  return rating_and_review_text

def _ReadStopWords(stopwords_filepath):
  """Reads and returns a set containing stop words."""
  return set(x.lower() for x in open(stopwords_filepath).read().split('\n'))

def _StoreParsedAndStemmedReviews(rating_and_review_text, stopwords, filepath):
  """Dumps in the json form {'text': <stemmed_text>, 'rating': <stars>}."""
  rating_and_stemmed_review_tokens = []
  stem_cache = {}
  with open(filepath, 'w') as fp:
    progress = Progress(len(rating_and_review_text))
    for (rating, review) in rating_and_review_text:
      progress.PrintProgress()
      stemmed_review_tokens = []
      for token in re.split(_REGEX_TOKEN_SPLIT_PATTERN, review):
        # TODO(ashishb): If token has more than two dashes separated by few(3?) chars then split it.
        token = token.strip().lower()
        stemmed_token = stem_cache.get(token, '')
        if not stemmed_token:
          try:
            stemmed_token = stem(token)
            stem_cache[token] = stemmed_token
          except IndexError as e:
            print 'IndexError while trying to stem \"%s\"' % token
        # Ignore empty tokens.
        if stemmed_token and stemmed_token not in stopwords:
          stemmed_review_tokens.append(stemmed_token)
      # Convert to ascii, ignore non-ascii characters.
      fp.write(json.dumps(
          {'rating': rating , 'text': ' '.join(stemmed_review_tokens)}) + '\n')
      rating_and_stemmed_review_tokens.append((rating, stemmed_review_tokens))
  return rating_and_stemmed_review_tokens

def _ProduceLexicon(rating_and_stemmed_review_tokens):
  """Returns a dictionary object containing tokens and their freqeuncies."""
  token_frequencies = {}
  progress = Progress(len(rating_and_stemmed_review_tokens))
  for (_, stemmed_tokens) in rating_and_stemmed_review_tokens:
    progress.PrintProgress()
    for token in stemmed_tokens:
      token_frequencies[token] = 1 + token_frequencies.get(token, 0)
  return token_frequencies

def _StoreTokenFrequencies(token_frequencies, filepath):
  token_frequencies_list = token_frequencies.items()
  token_frequencies_list = sorted(token_frequencies_list, key=lambda entry: entry[1], reverse=True)
  fp = open(filepath, 'w')
  for (k, v) in token_frequencies_list:
    fp.write(k + ' ' + str(v) + '\n')
  fp.close()


# Main
print 'Reading reviews from', _YELP_DATASET
rating_and_review_text = _ParseYelpDataAndReturnReviews(_YELP_DATASET)
assert rating_and_review_text

print 'Finished reading reviews.'
print 'Now writing parsed reviews to', _YELP_PARSED_REVIEWS
stopwords = _ReadStopWords(_STOP_WORDS_FILE)
rating_and_stemmed_review_tokens = _StoreParsedAndStemmedReviews(\
    rating_and_review_text, stopwords, _YELP_PARSED_REVIEWS)

print 'Finished writing parsed reviews.'
print 'Now generating lexicon.'
token_frequencies = _ProduceLexicon(rating_and_stemmed_review_tokens)

print 'writing lexicon to', _YELP_LEXICON_FILE
_StoreTokenFrequencies(token_frequencies, _YELP_LEXICON_FILE)

print 'Everything done.'
