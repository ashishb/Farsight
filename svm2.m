addpath('~/libsvm-3.13/matlab');

close('all')
clear

tic();
[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
toc();
category = sign(category - 2.5);

mList = [];
trainError = [];
testError = [];
listIndex = 1;
size = 300;
for m = size:500:size
  % Train
  trainMatrix = sparseMatrix(1:m,:);
  trainCategory = category(1:m)';
  model = svmtrain(trainCategory, trainMatrix);
  
  % Test training data
  [output, accuracy, decision_values] = ...
    svmpredict(trainCategory, trainMatrix, model);
  
  error = 0;
  for i = 1:m
    if (trainCategory(i) ~= output(i))
      error = error + 1;
    end
  end
  trainError(listIndex) = error / m;
  
  % Test set
  testMatrix = sparseMatrix(size+1:size+m,:);
  testCategory = category(size+1:size+m)';
  [output, accuracy, decision_values] = ...
    svmpredict(testCategory, testMatrix, model);
  
  error = 0;
  for i = 1:m
    if (testCategory(i) ~= output(i))
      error = error + 1;
    end
  end
  testError(listIndex) = error / m;
  
  mList(listIndex) = m;
  listIndex = listIndex + 1;
end

%trainError(length(trainError))
%testError(length(testError))

%figure();
%hold all;
%plot(mList, trainError);
%plot(mList, testError);
%legend('train', 'test')