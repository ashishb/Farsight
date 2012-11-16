addpath('~/liblinear-1.92/matlab');  % add LIBLINEAR to the path

close('all')
%clear

tic()
[sparseMatrix, tokenlist, category] = readMatrix('data.raw/matrix');
category = sign(category - 2.5);
toc()

mList = [];
trainError = [];
testError = [];
listIndex = 1;
size = 14500;
tic()
for m = 1:500:size
  % Train
  trainMatrix = sparseMatrix(1:m,:);
  trainCategory = category(1:m)';
  model = train(trainCategory, trainMatrix, '-s 0');
  
  % Test training data
  [output, accuracy, decision_values] = ...
    predict(trainCategory, trainMatrix, model);
  
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
    predict(testCategory, testMatrix, model);
  
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
toc()

trainError(length(trainError))
testError(length(testError))

figure();
hold all;
xlabel('training examples');
ylabel('error (%)');
title('Training Example vs Error');
plot(mList, trainError);
plot(mList, testError);
legend('training', 'generalization')