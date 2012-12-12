addpath('liblinear-1.92/matlab');  % add LIBLINEAR to the path

close('all')
%clear

tic()
[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = sign(category - 2.5);
toc()

mList = [];
trainError = [];
testError = [];
listIndex = 1;
siz = 12000; %round(size(category)/2);
tic()
%for m = siz:500:siz
for m = 500:500:siz
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
  trainError(listIndex) = error / size(trainCategory, 1);
  
  % Test set
  testMatrix = sparseMatrix(siz+1:end,:);
  testCategory = category(siz+1:end)';
  [output, accuracy, decision_values] = ...
    predict(testCategory, testMatrix, model);
  
  error = 0;
  for i = 1:size(testCategory)
    if (testCategory(i) ~= output(i))
      %tmp = sprintf('i: %d Expected: %d Actual: %d', i, testCategory(i), output(i)); 
      %disp(tmp);
      error = error + 1;
    end
  end
  testError(listIndex) = error / size(testCategory, 1);
  
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
plot(mList, trainError * 100);
plot(mList, testError * 100);
legend('training', 'generalization')
