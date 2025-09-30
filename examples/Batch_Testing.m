% Directory setup
imageDir = 'Imgs/';
binaryDir = 'LoremBit/';

% File names
imageFiles = {'Aerial.tiff','Airplane.tiff','Baboon.tiff','Car_and_APCs.tiff',...
              'Fishing_Boat.tiff','Peppers.tiff','Pixel_ruler.tiff',...
              'Steam_and_Bridge.tiff','Tank.tiff','Truck.tiff'};

binarySizes = [1, 10:10:100];
binaryFiles = arrayfun(@(x) sprintf('random-binary_%dkb.txt', x), binarySizes, 'UniformOutput', false);

% Initialize results cell array
results = cell(length(imageFiles) + 1, length(binaryFiles)*3 + 1);

% Generate header
header = cell(1, length(binaryFiles)*3);
for i = 1:length(binaryFiles)
    header{(i-1)*3 + 1} = ['PSNR_' binaryFiles{i}];
    header{(i-1)*3 + 2} = ['MSE_' binaryFiles{i}];
    header{(i-1)*3 + 3} = ['SSIM_' binaryFiles{i}];
end
results(1, 2:end) = header;
results(2:end, 1) = imageFiles';

% Loop over images
for i = 1:length(imageFiles)
    imgPath = fullfile(imageDir, imageFiles{i});
    img = imread(imgPath);
    if size(img, 3) == 3
        img = rgb2gray(img);
    end
    p = double(img(:));

    % Histogram processing
    n = 5;
    maxVal = 256;
    max = 260;
    edges = 0:n:max;
    [count, ~] = histcounts(p, edges);
    sumEach = imhist(uint8(p));
    sumGroup = zeros(max,1);
    for k = 1:maxVal
        index = floor((k-1)/5) + 1;
        sumGroup(index) = sumGroup(index) + sumEach(k) * (k-1);
    end

    % Loop over binary files
    for j = 1:length(binaryFiles)
        binaryPath = fullfile(binaryDir, binaryFiles{j});
        if ~isfile(binaryPath), continue; end
        b = dlmread(binaryPath);
        
        % Prepare variables
        avgArr = zeros(1, length(p));
        counter = 1;
        TRA = zeros(1,length(p));
        pp = zeros(length(p),1);

        % Embedding (same logic as manual)
        for t = 1:length(p)
            index = floor(p(t) / 5) + 1;
            avgArr(t) = ceil(sumGroup(index) / count(index));
            if p(t) > 4 && p(t) <= 249 && counter <= length(b)
                d = p(t) - avgArr(t);
                dp = d + b(counter);
                pp(t) = p(t) + dp;
                TRA(t) = 1;
                counter = counter + 1;
            else
                pp(t) = p(t);
            end
        end

        % Reshape image and cast
        stegoImg = uint8(reshape(pp, size(img)));

        % Compute metrics
        thePSNR = psnr(stegoImg, img);
        mse = mean((double(stegoImg(:)) - double(img(:))).^2);
        ssimval = ssim(stegoImg, img);

        % Store results
        col = (j-1)*3 + 2;
        results{i+1, col} = thePSNR;
        results{i+1, col+1} = mse;
        results{i+1, col+2} = ssimval;
    end
end

% Write to CSV
outputCSV = 'output.csv';
writecell(results, outputCSV);
