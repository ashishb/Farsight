import time

class Progress():
  def __init__(self, label, progress_max):
    self.label = label
    self. progress_max = progress_max
    self.progress = 0;
    self.time = time.time()
    self.prev_time = self.time

  def Update(self):
    self.progress = self.progress + 1
    elapsed_time = time.time() - self.time
    if self.progress == self.progress_max:
      print '%s: done' % (self.label)
    elif elapsed_time >= 5:
      progress_pct = self.progress * 100.0 / self.progress_max
      print '%s: %d / %d (%.2f%%) ETA: %d seconds' % \
        (self.label, self.progress, self.progress_max, progress_pct,
         elapsed_time / (self.progress_max / 100.0) *
         (self.progress_max - self.progress))
      self.time = time.time()
