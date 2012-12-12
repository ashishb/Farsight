tic()
[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = sign(category - 2.5);
toc()

trainMatrix = sparseMatrix(:,:);
trainCategory = category(:)';

siz = 6000;
for m = 1:40:siz
  disp 'Starting training for m=', m
  x = trainMatrix(1:m, :)';
  t = trainCategory(1:m);
  % Train
  net = feedforwardnet(10);
  net = train(net, x, t);
  view(net);
  y = sim(net, x);
  perf = perform(net, y, t);
  disp 'Done traing for m=', m
end
