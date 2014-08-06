#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Undistort a video

@author: Kevin Middleton

Based on:
    https://github.com/ying17zi/gopro-undistort

"""

# Arguments
# -f Video file to process
# -c Camera matrix file
# -d Distortion coefficient file
# -r Save raw images

import cv
import os
import argparse
from setupCV import setupCV
from progressbar import ProgressBar, Percentage, Bar

if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='Undistort video')
    parser.add_argument('-f', '--file',
                        help='File to convert',
                        required=True)
    parser.add_argument('--fps',
                        help='Frames per second',
                        type=int,
                        required=True)
    parser.add_argument('-c', '--camera',
                        help='Camera matrix file',
                        required=True)
    parser.add_argument('-d', '--distortion',
                        help='Distortion coefficients file',
                        required=True)
    parser.add_argument('-r', '--raw',
                        help='Output raw images',
                        action="store_true",
                        required=False)
    parser.add_argument('--uncompressed',
                        help='Output uncompressed video',
                        action="store_true",
                        required=False)
    args = parser.parse_args()

    # Get video file name
    vidFileName = args.file

    cameraMatrixFile = args.camera
    distortionCoefsFile = args.distortion

    # fps
    fps = args.fps

    # Save raw images?
    if args.raw:
        print "\nSaving raw images.\n"
        saveRaw = args.raw
        outdir = vidFileName + '_raw/'
        os.makedirs(outdir)
    else:
        saveRaw = False

    # Save uncompressed video?
    if args.uncompressed:
        print "\nSaving uncompressed video.\n"
        movieSuffix = '.avi'
        fourcc = cv.CV_FOURCC('I', '4', '2', '0')
    else:
        movieSuffix = '.m4v'
        fourcc = cv.CV_FOURCC('m', 'p', '4', 'v')

    # Set movie output file name
    outfile = vidFileName + '_undistort' + movieSuffix

    # Read and convert camera matrix and distortion coefficients files
    camera_matrix, dist_coeffs = setupCV(cameraMatrixFile,
                                         distortionCoefsFile)

    # Open video file
    vidFile = cv.CaptureFromFile(vidFileName)

    # Trim the last 2% off, because CV_CAP_PROP_FRAME_COUNT is not
    # accurate
    nframes = int(0.98 * cv.GetCaptureProperty(vidFile,
                                               cv.CV_CAP_PROP_FRAME_COUNT))

    width = int(cv.GetCaptureProperty(vidFile, cv.CV_CAP_PROP_FRAME_WIDTH))
    height = int(cv.GetCaptureProperty(vidFile, cv.CV_CAP_PROP_FRAME_HEIGHT))

    print 'Num Frames = ', nframes
    print 'Frame rate =', fps, 'frames per sec'

    # Create writer for movie
    writer = cv.CreateVideoWriter(
        filename=outfile,
        fourcc=fourcc,
        fps=fps,
        frame_size=(width, height),
        is_color = 1)

    map1 = cv.CreateImage((width, height), cv.IPL_DEPTH_32F, 1)
    map2 = cv.CreateImage((width, height), cv.IPL_DEPTH_32F, 1)
    cv.InitUndistortMap(camera_matrix, dist_coeffs, map1, map2)

    widgets = [Percentage(), ' ',
               Bar(marker='-', left='[', right=']')]
    pbar = ProgressBar(widgets=widgets,
                       maxval=nframes).start()

    for f in xrange(nframes):
        frameImg = cv.QueryFrame(vidFile)
        if frameImg is None:
            print "no frame", f, "flawed. Cancel"
            break
        undistimage = cv.CloneImage(frameImg)
        cv.Remap(frameImg, undistimage, map1, map2)
        cv.WriteFrame(writer, undistimage)

        # Write raw images if desired
        if saveRaw:
            outfileName = outdir + vidFileName + '_' + \
                format(f, "04d") + '.jpg'
            cv.SaveImage(outfileName, undistimage)

        k = cv.WaitKey(1)
        if k % 0x100 == 27:
            # User has press the ESC key, then exit
            break
        pbar.update(f+1)

    pbar.finish()

    del writer
