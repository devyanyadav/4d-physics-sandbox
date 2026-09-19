import numpy as np



def double_rotation(Matrix1,Matrix2,theta1,theta2,vertices):
    _,R1 = Matrix1(vertices,theta1)
    _,R2 = Matrix2(vertices,theta2)
    R12 = R1 @ R2
    return vertices @ R12

def xy_rotation_matrix(theta):
    return np.array([[np.cos(theta), -np.sin(theta), 0, 0],
                      [np.sin(theta), np.cos(theta), 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

def xz_rotation_matrix(theta):
    return np.array([[np.cos(theta), 0, -np.sin(theta), 0],
                      [0, 1, 0, 0],
                      [np.sin(theta), 0, np.cos(theta), 0],
                      [0, 0, 0, 1]])

def yz_rotation_matrix(theta):
    return np.array([[1, 0, 0, 0],
                      [0, np.cos(theta), -np.sin(theta), 0],
                      [0, np.sin(theta), np.cos(theta), 0],
                      [0, 0, 0, 1]])

def xw_rotation_matrix(theta):
    return np.array([[np.cos(theta), 0, 0, -np.sin(theta)],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [np.sin(theta), 0, 0, np.cos(theta)]])

def yw_rotation_matrix(theta):
    return np.array([[1, 0, 0, 0],
                      [0, np.cos(theta), 0, -np.sin(theta)],
                      [0, 0, 1, 0],
                      [0, np.sin(theta), 0, np.cos(theta)]])

def zw_rotation_matrix(theta):
    return np.array([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, np.cos(theta), -np.sin(theta)],
                      [0, 0, np.sin(theta), np.cos(theta)]])


def rotate_xy(vertices, theta):
    R = xy_rotation_matrix(theta)
    return vertices @ R.T, R

def rotate_xz(vertices, theta):
    R = xz_rotation_matrix(theta)
    return vertices @ R.T, R

def rotate_yz(vertices, theta):
    R = yz_rotation_matrix(theta)
    return vertices @ R.T, R

def rotate_xw(vertices, theta):
    R = xw_rotation_matrix(theta)
    return vertices @ R.T, R

def rotate_yw(vertices, theta):
    R = yw_rotation_matrix(theta)
    return vertices @ R.T, R

def rotate_zw(vertices, theta):
    R = zw_rotation_matrix(theta)
    return vertices @ R.T, R