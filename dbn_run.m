% This code is not working.
addpath('DeepLearnToolbox/CAE');
addpath('DeepLearnToolbox/DBN');
addpath('DeepLearnToolbox/CNN');
addpath('DeepLearnToolbox/NN');
addpath('DeepLearnToolbox/SAE');
addpath('DeepLearnToolbox/util');

trainMatrix = sparseMatrix(:,:);
% Map -1 to 0 and 1 to 1.
trainCategory = (1+category(:)')/2;

mList = [];
trainError = [];
testError = [];
listIndex = 1;
siz = 10000; %round(size(category)/2);

for m = 1000:1000:siz
  % Train set
  trainMatrix = sparseMatrix(1:m,:);
  trainCategory = category(1:m)';
  % Test set
  testMatrix = sparseMatrix(m+1:end,:);
  testCategory = category(m+1:end)';
  train_x = trainMatrix;
  test_x  = testMatrix;
  train_y = trainCategory;
  test_y  = testCategory;
  
  dbn.sizes = [10];
  opts.numepochs =   5;
  opts.batchsize =   m;
  opts.momentum  =   0;
  opts.alpha     =   1;
  dbn = dbnsetup(dbn, train_x, opts);
  dbn = dbntrain(dbn, train_x, opts);
  %figure; visualize(dbn.rbm{1}.W', 1);   %  Visualize the RMB weights
  
  nn = dbnunfoldtonn(dbn, 1);
  nn.alpha  = 10;
  nn.lambda = 1e-4;
  opts.numepochs =  100;
  opts.batchsize = 100;
  
  %nn = nntrain(nn, train_x, train_y, opts);
  disp 'Testing Neural Network'
  [er, bad] = nntest(nn, test_x, test_y);
  disp([num2str(er * 100) '% error']);
  %figure; visualize(nn.W{1}', 1);

  % TODO(ashishb): Find out the correct formula of trainError.
  trainError(listIndex) = er;
  testError(listIndex) = error / size(testCategory, 1);
  mList(listIndex) = m;
  listIndex = listIndex + 1;
end
