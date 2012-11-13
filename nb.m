close('all')
clear

[sparseMatrix, tokenlist, category] = readMatrix('data/matrix');

m = 5000;

  % Train
  trainCategory = (sign(category(:,1:m) - 2.5) + 1) / 2;
  trainMatrix = sparseMatrix(1:m,:);  % m x n
  numDocs = size(trainMatrix, 1);
  numTokens = size(trainMatrix, 2);
  
  spamDocs = trainCategory;
  nonSpamDocs = ones(1, numDocs) - trainCategory;
  tokensPerDoc = ones(1, numTokens) * trainMatrix';
  logphi1 = log(spamDocs * trainMatrix + 1) - ...
    log(spamDocs * tokensPerDoc' + numTokens);
  logphi0 = log(nonSpamDocs * trainMatrix + 1) - ...
    log(nonSpamDocs * tokensPerDoc' + numTokens);
  logphiy = log(sum(spamDocs)) - log(numDocs);
  
  % Test training data
  logpy1 = logphiy;
  logpy0 = log(1 - exp(logpy1));
  logpxy1 = trainMatrix * logphi1';
  logpxy0 = trainMatrix * logphi0';
  output = logpxy1 + logpy1 >= logpxy0 + logpy0;
  
  error = 0;
  for i = 1:numDocs
    if (trainCategory(i) ~= output(i))
      error = error+1;
    end
  end
  
  error / numDocs
  
  % Test data
  testCategory = (sign(category(:,m+1:m+m) - 2.5) + 1) / 2;
  testMatrix = sparseMatrix(m+1:m+m,:);  % m x n
  logpy1 = logphiy;
  logpy0 = log(1 - exp(logpy1));
  logpxy1 = testMatrix * logphi1';
  logpxy0 = testMatrix * logphi0';
  output = logpxy1 + logpy1 >= logpxy0 + logpy0;
  
  error = 0;
  for i = 1:numDocs
    if (testCategory(i) ~= output(i))
      error = error+1;
    end
  end
  
  error / numDocs