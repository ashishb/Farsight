addpath('~/liblinear-1.92/matlab');  % add LIBLINEAR to the path

close('all')
clear

[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');
category = sign(category - 2.5);
numDocs = size(sparseMatrix, 1);

% Train
model = train(category', sparseMatrix);

% Test
[predict_label, accuracy, decision_values] = ...
  predict(category', sparseMatrix, model);
output = predict_label == 1;

% Compute the error on the test set
error = 0;
for i = 1:numDocs
  if (category(i) ~= output(i))
    error=error+1;
  end
end

%Print out the classification error on the test set
error / numDocs
