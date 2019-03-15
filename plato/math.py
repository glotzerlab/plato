import numpy as np
import rowan

def quatconj(q):
    """Returns the conjugate of a quaternion array q*"""
    return -rowan.conjugate(q)

def quatrot(q, v):
    """Rotates the given vector array v by the quaternions in the array
    q"""
    return rowan.rotate(q, v)

def quatquat(qi, qj):
    """Multiplies the quaternions in the array qi by those in qj"""
    return rowan.multiply(qi, qj)

def box_to_matrix(box):
    """Converts a box tuple (in [Lx, Ly, Lz, xy, xz, yz] order with HOOMD
    meanings) into a box matrix"""
    (Lx, Ly, Lz, xy, xz, yz) = box
    return np.array([[Lx, xy*Ly, xz*Lz],
                     [0,     Ly, yz*Lz],
                     [0,      0,    Lz]], dtype=np.float64)

def make_fractions(box, positions):
    """Converts a box tuple and positions array into a set of box
    fractions for each position"""
    box = list(box)
    if box[2] == 0:
        box[2] == 1
    boxmat = box_to_matrix(box)
    invbox = np.linalg.inv(boxmat)

    return np.dot(invbox, positions.T).T + .5

def fractions_to_coordinates(box, fractions):
    """Converts a box tuple and fraction array into a position for each
    given fraction"""
    boxmat = box_to_matrix(box)
    fractions = fractions - .5

    coordinates = np.sum(
        fractions[:, np.newaxis, :]*boxmat[np.newaxis, :, :], axis=2)
    return coordinates
