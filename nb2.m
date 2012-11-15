close('all')
clear

[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = (sign(category - 2.5) + 1) / 2;

trainError = [];
testError = [];
size = 3000;
tic()
for m = size:size
  % Train
  trainMatrix = sparseMatrix(1:m,:);
  trainCategory = category(1:m)';
  model = NaiveBayes.fit(trainMatrix, trainCategory, 'Distribution', 'mn');
  
  % Test training data
  output = predict(model, trainMatrix);
  
  error = 0;
  for i = 1:m
    if (trainCategory(i) ~= output(i))
      error = error + 1;
    end
  end
  trainError(m) = error / m;
  %error / m
  
  % Test set
  testMatrix = sparseMatrix(size+1:size+m,:);
  testCategory = category(size+1:size+m)';
  output = predict(model, testMatrix);
  
  error = 0;
  for i = 1:m
    if (testCategory(i) ~= output(i))
      error = error + 1;
    end
  end
  testError(m) = error / m;
  %error / m
end
toc()

1 - trainError(length(trainError))
1 - testError(length(testError))

%figure();
%hold all;
%plot(trainError);
%plot(testError);
%legend('train', 'test')