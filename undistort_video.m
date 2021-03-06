function [] = undistort_video()
%undistort_video Undistort a video

clear all

% Choose movie
[movfname, movpname] = uigetfile('*.*','Select the video to convert');
movName = [movpname, movfname];

% Choose camera calibration file
[calfname, calpname] = uigetfile('*.*','Select the camera calibration file');
camCalibfname = [calpname, calfname];
load(camCalibfname);
camCalib = s.camParams;

% Ask to trim frames from the start
fprintf('Would you like to trim frames from the start?\n')
prompt = ['Enter number of frames to drop at the beginning of ', ...
    'the video. (Enter for 0): '];
offset = input(prompt);

if isempty(offset)
    offset = 0;
end

mov = VideoReader(movName);

nFrames = mov.NumberOfFrames;

% Creater writer object
outfile = [movName, '_undistort.mp4'];
writerObj = VideoWriter(outfile, 'MPEG-4');
open(writerObj);

fprintf('\nProcessing starting from frame %d.\n\n', offset + 1); 

% Cut off the last frame
nFrames = nFrames - (offset + 1);

tStart = tic;
h = waitbar(0,'Initializing...');
for i = (offset + 1):nFrames
    I = rgb2gray(read(mov, (i + offset)));
    J = undistortImage(I, camCalib);
    writeVideo(writerObj, J);
    perc = i / nFrames;
    waitbar(perc, h, sprintf('Processing frame: %d / %d', ...
        i, nFrames))
end

tEnd = toc(tStart);
fprintf('%d minutes and %f seconds\n\n', ...
    floor(tEnd/60),rem(tEnd,60));
close(h)

pause(0.1); % Allow waitbar to close

fprintf('Writing %s.\n\n', outfile);
close(writerObj);

end
