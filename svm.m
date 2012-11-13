addpath('~/liblinear-1.92/matlab');  % add LIBLINEAR to the path

close('all')
clear

[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = sign(category - 2.5);

trainError = [];
testError = [];
size = 4000;
for m = 1:50:size
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
  trainError(m) = error / m;
  
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
  testError(m) = error / m;
end

trainError(length(trainError))
testError(length(testError))

figure();
hold all;
plot(trainError);
plot(testError);
legend('train', 'test')