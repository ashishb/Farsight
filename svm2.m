addpath('~/liblinear-1.92/matlab');  % add LIBLINEAR to the path

close('all')
clear

[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = sign(category - 2.5);

trainError = [];
testError = [];
size = 500;
for m = 2:size
  m
  % Train
  model = svmtrain(trainMatrix, trainCategory, 'kernel_function', 'rbf');
  
  % Test training data
  output = svmclassify(model, trainMatrix) == 1;
  
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
  output = svmclassify(model, testMatrix) == 1;
  
  error = 0;
  for i = 1:m
    if (testCategory(i) ~= output(i))
      error = error + 1;
    end
  end
  testError(m) = error / m;
end

trainError(size)
testError(size)

figure();
hold all;
plot(trainError);
plot(testError);
legend('train', 'test')
