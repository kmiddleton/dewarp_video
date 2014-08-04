# -*- coding: utf-8 -*-

def setupCV(cameraMatrixFile, distortionCoefsFile):
    """
    Load camera matrix and distortion coefficients.

    Function to load the camera matrix and distortion coefficients
    from saved files and returning them in the proper format.

    Args:
        cameraMatrixFile (string): Path to saved camera matrix file
        distortionCoefsFile (string): Path to saved distortion coefficients
          file

    Returns:
        camera_matrix (matrix): Camera matrix in the proper format
        dist_coeffs (matrix): Distortion coefficients in the proper format
    """

    import cv
    from numpy import genfromtxt

    camMat = genfromtxt(cameraMatrixFile, delimiter=',')
    distCoefs = genfromtxt(distortionCoefsFile, delimiter=',')

    # Create empty matrix and populate with data from camMat
    camera_matrix = cv.CreateMat(3, 3, cv.CV_32FC1)
    cv.SetReal2D(camera_matrix, 0, 0, camMat[0, 0])
    cv.SetReal2D(camera_matrix, 0, 1, camMat[0, 1])
    cv.SetReal2D(camera_matrix, 0, 2, camMat[0, 2])
    cv.SetReal2D(camera_matrix, 1, 0, camMat[1, 0])
    cv.SetReal2D(camera_matrix, 1, 1, camMat[1, 1])
    cv.SetReal2D(camera_matrix, 1, 2, camMat[1, 2])
    cv.SetReal2D(camera_matrix, 2, 0, camMat[2, 0])
    cv.SetReal2D(camera_matrix, 2, 1, camMat[2, 1])
    cv.SetReal2D(camera_matrix, 2, 2, camMat[2, 2])

    # Create empty matrix and populate with data from distCoefs
    dist_coeffs = cv.CreateMat(1, 5, cv.CV_32FC1)
    cv.SetReal2D(dist_coeffs, 0, 0, distCoefs[0])
    cv.SetReal2D(dist_coeffs, 0, 1, distCoefs[1])
    cv.SetReal2D(dist_coeffs, 0, 2, distCoefs[2])
    cv.SetReal2D(dist_coeffs, 0, 3, distCoefs[3])
    cv.SetReal2D(dist_coeffs, 0, 4, distCoefs[4])

    return [camera_matrix, dist_coeffs]
