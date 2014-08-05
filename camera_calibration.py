#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calibrate camera using checkerboard pattern

@author: Kevin Middleton

Based on:
    https://github.com/ying17zi/gopro-undistort

    and

    Off-line camera calibration
    Author: Leow Wee Kheng
    Department of Computer Science, National University of Singapore
    Last update: 20 Sep 2012
    http://www.comp.nus.edu.sg/~cs4243/code/calibrate.py

"""

import cv2.cv as cv
from progressbar import ProgressBar, Percentage, Bar
import argparse
import random
import time
import sys

if __name__ == '__main__':
    # Tic
    t0 = time.time()

    # Parse options
    parser = argparse.ArgumentParser(description='Options')
    parser.add_argument('-f', '--file',
                        help='Calibration video',
                        required=True)
    parser.add_argument('--fps',
                        help='Frames per second',
                        type=int,
                        required=True)
    parser.add_argument('--rows',
                        help='Number of rows in checkerboard (default = 8)',
                        type=int,
                        required=False)
    parser.add_argument('--columns',
                        help='Number of columns in checkerboard (default = 8)',
                        type=int,
                        required=False)
    parser.add_argument('--grid_width',
                        help='Width of checkerboard squares (default = 1 cm)',
                        required=False)
    parser.add_argument('--grid_height',
                        help='Height of checkerboard squares (default = 1 cm)',
                        required=False)
    parser.add_argument('--save_corners',
                        help='Save corners',
                        action="store_true",
                        required=False)
    parser.add_argument('--max_images',
                        help='Maximum number of images to use for calibration.',
                        type=int,
                        required=False)

    args = parser.parse_args()

    # Setup grids to defaults if not passed as arguments
    if not args.rows:
        pts_arow = 8  # Number of internal intersections
    else:
        pts_arow = args.rows

    if not args.columns:
        pts_acol = 8
    else:
        pts_acol = args.columns

    if not args.grid_width:
        grid_width = float(1.0)  # cm
    else:
        grid_width = float(args.grid_width)

    if not args.grid_height:
        grid_height = float(1.0)  # cm
    else:
        grid_height = float(args.grid_height)

    if not args.save_corners:
        writeCorners = 0
    else:
        writeCorners = 1

    if not args.max_images:
        max_images = 100
    else:
        max_images = args.max_images

    # Video file
    vidFileName = args.file

    # Pattern
    patternSize = (pts_arow, pts_acol)

    # fps
    fps = args.fps

    # Checking
    print "\n------"
    print "Intersections:", pts_arow, "x", pts_acol
    print "Square size:", grid_width, "cm x", grid_height, "cm"
    print "Video:", vidFileName
    print "------\n"

    # Open movie
    vidFile = cv.CaptureFromFile(vidFileName)

    # Trim the last 2% off, because CV_CAP_PROP_FRAME_COUNT is not
    # accurate
    nframes = \
        int(0.98 * cv.GetCaptureProperty(vidFile,
                                         cv.CV_CAP_PROP_FRAME_COUNT))

    width = int(cv.GetCaptureProperty(vidFile,
                                      cv.CV_CAP_PROP_FRAME_WIDTH))
    height = int(cv.GetCaptureProperty(vidFile,
                                       cv.CV_CAP_PROP_FRAME_HEIGHT))

    print 'Num Frames = ', nframes
    print 'Frame rate =', fps, 'frames per sec\n'


    # Process images one by 1

    # Initialization
    corners = list(range(nframes))
    criteria = (cv.CV_TERMCRIT_ITER | cv.CV_TERMCRIT_EPS, 30, 0.01)

    # Number of good images
    nboard = 0

    print "Finding corners...\n"

    # Setup progress bar
    widgets = [Percentage(), ' ',
               Bar(marker='-', left='[', right=']')]
    pbar = ProgressBar(widgets=widgets,
                       maxval=nframes).start()

    for f in xrange(nframes):
        frameImg = cv.QueryFrame(vidFile)
        if frameImg is None:
            print "no frame", f, "flawed. Cancel"
            break

        BWImg = cv.CreateMat(height, width, cv.CV_8UC1)
        cv.CvtColor(frameImg, BWImg, cv.CV_RGB2GRAY)

        # Find corners
        retcode, cor = \
            cv.FindChessboardCorners(BWImg, patternSize,
                                     cv.CV_CALIB_CB_ADAPTIVE_THRESH |
                                     cv.CV_CALIB_CB_FILTER_QUADS)

        if retcode == 1:
            # Refine corners with subpixel accuracy
            corners[nboard] = cv.FindCornerSubPix(BWImg, cor, (3, 3),
                                                  (0, 0), criteria)
            colorimg = cv.CreateMat(height, width, cv.CV_8UC3)
            cv.CvtColor(BWImg, colorimg, cv.CV_GRAY2RGB)
            cv.DrawChessboardCorners(colorimg, patternSize,
                                     corners[nboard], retcode)
            if writeCorners:
                # File name for image with corners
                filename = vidFileName + "_corner_" + format(f, "04d") + ".jpg"
                cv.SaveImage(filename, colorimg)

            nboard += 1

        k = cv.WaitKey(1)
        if k % 0x100 == 27:
            # User has press the ESC key, then exit
            break
        pbar.update(f+1)

    pbar.finish()
    print "\nFound", nboard, "images with corners.\n"

    if nboard == 0:
        print "No corners detected.\n"
        sys.exit()

    # Cutoff the empty end of corners
    corners = corners[0:nboard]

    # Calibration
    # Check that there aren't too many images (~100; downsample if so)
    if nboard > max_images:
        print "Reducing the set of images with detected corners to", \
            max_images, "images by random selection.\n"
        corners = [corners[i] for i in
                   sorted(random.sample(xrange(len(corners)),
                   max_images))]
        nboard = len(corners)

    # Transfer points to calibration
    ncor = pts_arow * pts_acol
    npts = nboard * ncor
    object_points = cv.CreateMat(npts, 3, cv.CV_32FC1)
    image_points = cv.CreateMat(npts, 2, cv.CV_32FC1)
    point_counts = cv.CreateMat(nboard, 1, cv.CV_32SC1)

    p = 0
    for i in range(nboard):
        cv.SetReal2D(point_counts, i, 0, ncor)
        for c in range(ncor):
            cv.SetReal2D(object_points, p, 0, (c / pts_arow) * grid_height)
            cv.SetReal2D(object_points, p, 1, (c % pts_arow) * grid_width)
            cv.SetReal2D(object_points, p, 2, 0.0)
            cv.SetReal2D(image_points, p, 0, corners[i][c][0])
            cv.SetReal2D(image_points, p, 1, corners[i][c][1])
            p += 1

    # Calibrate
    camera_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
    dist_coeffs = cv.CreateMat(5, 1, cv.CV_32FC1)
    rvecs = cv.CreateMat(nboard, 3, cv.CV_32FC1)
    tvecs = cv.CreateMat(nboard, 3, cv.CV_32FC1)

    print "Calibrating (this might be slow)...\n"
    cv.CalibrateCamera2(object_points, image_points,
                        point_counts, (width, height),
                        camera_matrix, dist_coeffs, rvecs, tvecs, 0)

    # Save files and print results
    print "Camera matrix:"
    camMatFile = vidFileName + "_camera_matrix.csv"
    file = open(camMatFile, "w")
    for i in range(3):
        for j in range(3):
            print camera_matrix[i, j],
            file.write(str(camera_matrix[i, j]))
            if j < 2:
                file.write(", ")
            else:
                file.write("\n")
        print
    file.close()

    print"\n"
    print "Distortion coefficients:"
    distortionCoefsFile = vidFileName + "_distortion_coefficients.csv"
    file = open(distortionCoefsFile, "w")
    for i in range(5):
        print dist_coeffs[i, 0],
        file.write(str(dist_coeffs[i, 0]))
        if i < 4:
            file.write(", ")
    file.close()

    # Toc
    t1 = time.time()
    total = t1 - t0
    print '\n\nTotal time:', total, "s"
