close('all')
clear

[sparseMatric, tokenlist, category] = readMatrix('data/matrix');

category = (sign(category - 2.5) + 1) / 2;
matrix = full(sparseMatric);  % m x n
numDocs = size(matrix, 1);
numTokens = size(matrix, 2);

% Train
spamDocs = category;
nonSpamDocs = ones(1, numDocs) - category;
tokensPerDoc = ones(1, numTokens) * matrix';
logphi1 = log(spamDocs * matrix + 1) - ...
  log(spamDocs * tokensPerDoc' + numTokens);
logphi0 = log(nonSpamDocs * matrix + 1) - ...
  log(nonSpamDocs * tokensPerDoc' + numTokens);
logphiy = log(sum(spamDocs)) - log(numDocs);

% Test
logpy1 = logphiy;
logpy0 = log(1 - exp(logpy1));
logpxy1 = matrix * logphi1';
logpxy0 = matrix * logphi0';
output = logpxy1 + logpy1 >= logpxy0 + logpy0;

% Compute the error on the test set
error = 0;
for i = 1:numDocs
  if (category(i) ~= output(i))
    error = error+1;
  end
end

% Print out the classification error on the test set
error / numDocs
