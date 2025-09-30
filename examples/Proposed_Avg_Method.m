%% Import
img = imread('Imgs/Baboon.tiff');
% img = rgb2gray(img);
PC = dlmread('LoremBit/random-binary_10kb.txt');
b = cast(PC,'int8');

if(length(b) > 90000)
    b = reshape(b, 1, []);
end

%% Flatten
%p = reshape(img,1,[]);
p = double(img(:));
%% Range
n = 5;
maxVal = 256;
max = 260; % 255 + 5 = 260, so we must use right most 260 to include 255
edges = 0:n:(max);

%% Histogram Count
[count, ~] = histcounts(p, edges); % count is an array for the counts each range
m = length(count);

%% Sum of Values each Group
sumEach = imhist(img);
sumGroup = zeros(max,1);
for i = 1:maxVal % there is no index 0, 0 valued pixel is on index 1 so it moves 1 number, so 1 - 256
    index = floor((i-1)/5) + 1; % ex: 1-1 = 0 (0 valued pixel) will go to group 1, 0/5 + 1 = 1
    sumGroup(index) = sumGroup(index) + sumEach(i) * (i-1);
end

%% Average
% arrayAll = zeros(length(p), 5); % [val, index, groupIndex, groupAvg, diff]
% 
%for i = 1:length(p)
 %   index = floor(p(i) / 5) + 1; % because p(i) can be 0
%    avg = ceil(sumGroup(index) / count(index));
  %  % arrayAll(i, :) = [p(i), i, index, avg, p(i)-avg];
  %  avgArr(i) = avg;
%end

%% DE
avgArr = zeros(1, length(p));
EC = 0;
counter=1;
TRA = zeros(1,length(p));
pp = zeros(length(p),1);
for i=1:length(p)
    %if arrayAll(i, 5) <= 1
    index = floor(p(i) / 5) + 1; % because p(i) can be 0
    avgArr(i) = ceil(sumGroup(index) / count(index));
    % arrayAll(i, :) = [p(i), i, index, avg, p(i)-avg];

    if p(i) > 4 && p(i) <= 249
    % if (p(i) - avgArr(i)) <= 4  && (p(i) - avgArr(i)) >= -4 % MODIFY IF
    % WANT TO CHANGE THE DIFF 
       EC = EC+1;
    % end      
    end
    
    % ALTERNATIVE WAY USING ARRAY ALL
    %if arrayAll(i, 5) <= 4 && arrayAll(i, 5) >= -4 && arrayAll(i, 1) > 4 && arrayAll(i,1) < 249 && counter < length(b)+1
    
    if p(i) > 4 && p(i) <= 249 && counter < length(b)+1
    % if (p(i) - avgArr(i)) <= 4  && (p(i) - avgArr(i)) >= -4 % MODIFY IF
    % WANT TO CHANGE THE DIFF 
       d = (p(i) - avgArr(i));
       dp = d + PC(counter);
       pp(i) = p(i) + dp;
       TRA(i) = 1;
       counter = counter +1;
    % end      
    else
      % pp(i)=arrayAll(i,1);
       pp(i) = p(i);
    end
end
stegoImg = cast (reshape(pp,512,512),'uint8');


%% EXTRACTING DATA 

% stegArr = reshape(stegoImg,1,[]);
stegArr = double(stegoImg(:));
[r2,c2]=size(stegoImg);
TRAB = TRA;
secret = zeros(1, length(b));
avgTableb = avgArr;
h=1;

coverArr = zeros(1, length(stegArr));

for i = 1:(r2*c2) 
    if h < length(b)+1 && TRAB(i) == 1
       secret(h)= cast(mod(stegArr(i) - avgTableb(i), 2),'int8');
       coverArr(i) = floor((stegArr(i) + avgArr(i) - secret(h))/2);
       h = h+1;
    else
        coverArr(i) = stegArr(i);
    end
end

coverImg = cast(reshape(coverArr,512,512),'uint8');

%% Display
%figure; image(img,'CDataMapping','scaled'); colormap('gray');
%title('Original Image');
% imwrite(stegoImg, 'Baboon_Stego.tiff');

%figure; image(stegoImg,'CDataMapping','scaled'); colormap('gray');
%title('Stego Image');

%figure; image(coverImg,'CDataMapping','scaled'); colormap('gray');
%title('Extracted cover image');

thePSNR = psnr(stegoImg, img);
fprintf("PSNR: %f\n", thePSNR);

mse = mean((double(stegoImg(:)) - double(img(:))).^2);
fprintf("MSE: %f\n", mse);

%[r1,c1]=size(stegoImg);
%bpp = EC/(r1*c1);
%fprintf("BPP: %f\n", bpp);

ssimval = ssim(stegoImg, img);
fprintf("SSIM: %f\n", ssimval);
secret = cast(secret, 'int8');

% secret = secret(:);
sumSame = sum(secret==b);

if sumSame > 1
    fprintf("SECRET SAME %d \n", sumSame);
    % secretChars = char(secret + '0');

    %secret_text = strjoin(cellstr(secretChars'), ' ');
    
    %fid = fopen('Bits/extracted_bits1.txt', 'w');
    %fprintf(fid, '%s', secret_text);
    %fclose(fid);
else
    fprintf("SECRET DIFFERENT %d\n", sumSame);
    % secretChars = char(secret + '0');

    %secret_text = strjoin(cellstr(secretChars'), ' ');
    
    %fid = fopen('Bits/extracted_bits1.txt', 'w');
    %fprintf(fid, '%s', secret_text);
    %fclose(fid);
end



if isequal(coverImg, img)
   fprintf("COVER SAME\n");
else 
    fprintf("COVER DIFFERENT\n");
end

%secret = reshape(secret, 1, []);
%b = reshape(b, 1, []);

%diffcount = sum(secret ~= b);
%fprintf("%d\n", diffcount);
%figure;
%subplot(3,1,1);
%imhist(img);
%title('Histogram of Input Cover Image');

%subplot(3,1,2);
%imhist(stegoImg);
%title('Histogram of Stego Image');

%subplot(3,1,3);
%imhist(coverImg);
%title('Histogram of Extracted Cover Image');

% figure; histogram(p, edges); % left to right + 1 means it is left <= x < right