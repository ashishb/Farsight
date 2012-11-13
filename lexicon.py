class Lexicon:
  def __init__(self):
    self.token_to_tid = {}
    self.tid_to_token = {}
    self.token_freq = {}
    index = 0
    with open('data/lexicon.txt') as file:
      for line in file:
        token_freq = line.strip().split(' ')
        if len(token_freq) == 2:
          token = token_freq[0]
          #if int(token_freq[1]) <= 10:
          #  continue
          self.token_freq[token] = int(token_freq[1])
          self.token_to_tid[token] = index
          self.tid_to_token[index] = token
          index = index + 1

  def tid(self, token):
    return self.token_to_tid.get(token.lower(), -1)

  def token(self, tid):
    return self.tid_to_token.get(tid, '')

l = Lexicon()
