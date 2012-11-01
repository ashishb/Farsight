import json
import re
from stemming.porter2 import stem

# Data Source
_YELP_DATASET = './data/yelp_academic_dataset.json'
# Parsed reviews
_YELP_PARSED_REVIEWS = './data/yelp_parsed_reviews.json'
# Token frequencies in reviews.
_YELP_LEXICON_FILE = './data/yelp_lexicon.txt'
# Stop words file.
_STOP_WORDS_FILE = './data/stopwords.txt'
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
  for line in open(filepath).read().split('\n'):
    if not line:  # Ignore empty lines.
      continue
    yelp_data_object = json.loads(line)
    if _IsReview(yelp_data_object):
      review_text_and_ratings.append(_GetReviewTextAndRating(yelp_data_object))
  return review_text_and_ratings


def _StoreParsedReviews(review_text_and_ratings, filepath):
  """Dumps in the json form {'text': <text>, 'rating': <stars>}."""
  fp = open(filepath, 'w')
  for review in review_text_and_ratings:
    # Convert to ascii, ignore non-ascii characters.
    fp.write(json.dumps(
          {'rating': review[0] , 'text': review[1]}) + '\n')
  fp.close()

def _ReadStopWords(stopwords_filepath):
  """Reads and returns a set containing stop words."""
  return set(open(stopwords_filepath).read().split('\n'))

def _ProduceLexicon(review_text_and_ratings, stopwords_filepath):
  """Returns a dictionary object containing tokens and their freqeuncies."""
  token_frequencies = {}
  stopwords = _ReadStopWords(stopwords_filepath)
  for (rating, review) in review_text_and_ratings:
    tokens = re.split(_REGEX_TOKEN_SPLIT_PATTERN, review)
    for token in tokens:
      # TODO(ashishb): If token has more than two dashes separated by few(3?) chars then split it.
      token = token.strip()
      try:
        token = stem(token)
      except IndexError as e:
        print 'IndexError while trying to stem \"%s\"' % token
      if token and token not in stopwords:  # Ignore empty tokens.
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
review_text_and_ratings = _ParseYelpDataAndReturnReviews(_YELP_DATASET)
assert review_text_and_ratings
print 'Finished reading reviews.\nNow writing parsed reviews to', _YELP_PARSED_REVIEWS
_StoreParsedReviews(review_text_and_ratings, _YELP_PARSED_REVIEWS)
print 'Finished writing parsed reviews.\nNow generating lexicon.'
token_frequencies = _ProduceLexicon(review_text_and_ratings, _STOP_WORDS_FILE)
print 'writing lexicon to', _YELP_LEXICON_FILE
_StoreTokenFrequencies(token_frequencies, _YELP_LEXICON_FILE)
print 'Everything done.'