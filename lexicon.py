class Lexicon:
  def __init__(self):
    self.token_to_tid = {}
    self.tid_to_token = {}
    index = 0
    with open('data/yelp_lexicon.txt') as file:
      for line in file:
        if len(self.token_to_tid) > 1000:
          break
        token_freq = line.strip().split(' ')
        if len(token_freq) == 2:
          token = token_freq[0]
        self.token_to_tid[token] = index
        self.tid_to_token[index] = token
        index = index + 1
    print index

  def tid(self, token):
    return self.token_to_tid.get(token.lower(), -1)

  def token(self, tid):
    return self.tid_to_token.get(tid, '')

l = Lexicon()
