import json
import tempfile

class Lexicon:
  def __init__(self):
    self.token_to_tid = {}
    self.tid_to_token = {}
    index = 0
    with open('/etc/dictionaries-common/words') as file:
      for line in file:
        token = line.strip()
        if len(token):
          self.token_to_tid[token] = index
          self.tid_to_token[index] = token
          index = index + 1

  def tid(self, token):
    return self.token_to_tid.get(token, -1)

  def token(self, tid):
    return self.tid_to_token.get(tid, '')

def encode_tokens(lexicon, tid_set, token_string):
  tid_list = [lexicon.tid(token) for token in token_string.split(' ')]
  tid_list = filter(lambda tid: tid != -1, tid_list)
  if not len(tid_list):
    return []

  token_count = {}
  for tid in tid_list:
    token_count[tid] = token_count.get(tid, 0) + 1

  tid_list = token_count.keys()
  tid_list.sort()

  output = []
  prev_tid = 0
  for tid in tid_list:
    tid_set.add(tid)
    output.append(tid - prev_tid)
    output.append(token_count[tid])
    prev_tid = tid
  return output

lexicon = Lexicon()

(_, tmp_file_name) = tempfile.mkstemp()
with open(tmp_file_name, 'w') as tmp_file:
  with open('data/reviews.json') as reviews_file:
    tid_set = set()
    total_examples = 0
    for (idx, line) in enumerate(reviews_file):
      if idx >= 1000:
        break
      total_examples += 1
      obj = json.loads(line)
      output = []
      output.append(obj['stars'])
      output.extend(encode_tokens(lexicon, tid_set, obj['text']))
      output.append(-1)
      tmp_file.write(' '.join(str(x) for x in output))
      tmp_file.write('\n')

with open('data/matrix', 'w') as matrix_file:
  matrix_file.write('DOC_WORD_MATRIX\n')
  matrix_file.write('%d %d\n' % (total_examples, len(tid_set)))
  matrix_file.write('%s\n' % ' '.join(sorted(lexicon.token(tid) for tid in tid_set)))
  with open(tmp_file_name) as f:
    for line in f:
      matrix_file.write(line)
