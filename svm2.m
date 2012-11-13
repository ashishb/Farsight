close('all')
clear

[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = sign(category - 2.5);

trainError = [];
testError = [];
size = 50;
for m = size:size
  % Train
  trainMatrix = sparseMatrix(1:m,:);
  trainCategory = category(1:m)';
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

trainError(length(trainError))
testError(length(testError))

%figure();
%hold all;
%plot(trainError);
%plot(testError);
%legend('train', 'test')
