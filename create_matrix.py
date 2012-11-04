from lexicon import Lexicon

import json
import tempfile

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

limit = 5000
#limit = 330071

(_, tmp_file_name) = tempfile.mkstemp()
with open(tmp_file_name, 'w') as tmp_file:
  with open('data/yelp_parsed_reviews.json') as reviews_file:
    tid_set = set()
    total_examples = 0
    for (idx, line) in enumerate(reviews_file):
      if idx >= limit:
        break
      if idx % (limit / 100) == 0:
        print '%d / %d (%.2f%%)' % (idx, limit, idx * 100.0 / limit)
      total_examples += 1
      obj = json.loads(line)
      output = []
      output.append(obj['rating'])
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
