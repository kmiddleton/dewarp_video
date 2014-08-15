function [] = camera_calibration()
%camera_calibration Calibrate two cameras using checkerboard pattern

clear all
close all

%% Read movies

[fname1, pname1]=uigetfile('*.*','Select the left video (Camera 1)');
movName1 = [pname1, fname1];

[fname2, pname2]=uigetfile('*.*','Select the right video (Camera 2)');
movName2 = [pname2, fname2];

[Cam1, Cam2, nFrames1, nFrames2] = compareMovies(movName1, movName2);

%% Camera 1 (left)
fprintf('Analysing %s\n\n', movName1);

calPtsCam1 = ...
    getCalibrationPoints(Cam1, movName1, nFrames1);

calPtsCam1 = trimCalibrationPoints(calPtsCam1);

EstimateCameraParameters(calPtsCam1, movName1);

%% Camera 2 (right)
fprintf('Analysing %s\n\n', movName2);

calPtsCam2 = ...
    getCalibrationPoints(Cam2, movName2, nFrames2);

calPtsCam2 = trimCalibrationPoints(calPtsCam2);

EstimateCameraParameters(calPtsCam2, movName2);
end

%% compareMovies
function [Cam1, Cam2, nFrames1, nFrames2] = ...
    compareMovies(movName1, movName2)

fprintf('\nComparing videos...\n\n')

% Load movies
Cam1 = VideoReader(movName1);
Cam2 = VideoReader(movName2);

nFrames1 = Cam1.NumberOfFrames;
nFrames2 = Cam2.NumberOfFrames;

fprintf('Camera 1: %d frames\n', nFrames1);
fprintf('Camera 2: %d frames\n\n', nFrames2);

if nFrames2 > nFrames1
    %    offset1 = 0;
    offset2 = 1 + (nFrames2 - nFrames1);
    %    nStart1 = 1;
    %    nStart2 = offset2;
    fprintf(['Looks like Camera 2 has %d more frames ', ...
        'than Camera 1. Take note.\n\n'], offset2);
elseif nFrames1 > nFrames2
    offset1 = 1 + (nFrames1 - nFrames2);
    %    offset2 = 0;
    %    nStart1 = offset1;
    %    nStart2 = 1;
    fprintf(['Looks like Camera 1 has %d more frames ', ...
        'than Camera 1. Take note.\n\n'], offset1);
else
    sprintf('Equal frames.\n');
    %   nStart1 = 1;
    %   nStart2 = 1;
    %   offset1 = 0;
    %   offset2 = 0;
    fprintf('Looks like the videos have equal frames.\n\n')
end
end

%% getCalibrationPoints
function [CalibrationPoints] = ...
    getCalibrationPoints(mov, movName, nFrames)

seq = 1:nFrames;

CalibrationPoints = zeros(54, 2, numel(seq));
Missing = ones(numel(seq), 1);

fprintf('Finding corners.\n\n');
tStart = tic;

warning('off', 'vision:calibrate:boardShouldBeAsymmetric')
h = waitbar(0,'Initializing...');
for i = 1:numel(seq)
    frame = seq(i);
    I = rgb2gray(read(mov, frame));
    [imagePoints] = detectCheckerboardPoints(I);
    if size(imagePoints, 1) == 54
        CalibrationPoints(:, :, i) = imagePoints;
        Missing(i) = 0;
    end
    perc = i / numel(seq);
    waitbar(perc, h, sprintf('Processing frame: %d / %d', i, numel(seq)))
end
fprintf('Found %d frames with checkerboards.\n\n', sum(~Missing));
tEnd = toc(tStart);
fprintf('%d minutes and %f seconds\n\n',floor(tEnd/60),rem(tEnd,60));
close(h)

pause(0.1); % Allow waitbar to close

% Re-enable warning about symmetric boards
warning('on', 'vision:calibrate:boardShouldBeAsymmetric')

% Keep only the frames where a board was found
CalibrationPoints = CalibrationPoints(:, :, Missing ~= 1);

% Save detected calibration points
%outfile = [movName, '_CalPts.mat'];
%s = struct('calPts', CalibrationPoints');
%save(outfile, 's')
end

%% EstimateCameraParameters
function [] = EstimateCameraParameters(calPts, movName)
boardSize = [7 10];
squareSize = 10;
worldPoints = generateCheckerboardPoints(boardSize, squareSize);

fprintf('Estimating camera parameters.\n\n');
tStart = tic;
[cameraParams] = ...
    estimateCameraParameters(calPts, ...
    worldPoints, 'WorldUnits', 'mm');
tEnd = toc(tStart);
fprintf('%d minutes and %f seconds\n\n',floor(tEnd/60),rem(tEnd,60));

outfile = [movName, '_CamParams.mat'];
s = struct('camParams', cameraParams);
save(outfile, 's')
end

%% trimCalibrationPoints
function [CalibrationPoints] = ...
    trimCalibrationPoints(CalibrationPoints)

% Trim to maxFrames frames
maxFrames = 100;

Found = size(CalibrationPoints, 3);
if Found > maxFrames
    fprintf(['Using a random subset of %d images ', ...
        'for calibration.\n\n'], maxFrames)
    CalibrationPoints = ...
        CalibrationPoints(:, :, randperm(Found, maxFrames));
end

end
