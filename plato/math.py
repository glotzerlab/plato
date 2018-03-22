import numpy as np

def quatconj(q):
    """Returns the conjugate of a quaternion array q*"""
    result = np.array(q)
    result[..., 0] *= -1
    return result

def quatrot(q, v):
    """Rotates the given vector array v by the quaternions in the array
    q"""
    (q, v) = np.asarray(q), np.asarray(v)
    return (
        (q[..., 0]**2 - np.sum(q[..., 1:]**2, axis=-1))[..., np.newaxis]*v +
        2*q[..., 0, np.newaxis]*np.cross(q[..., 1:], v) +
        2*np.sum(q[..., 1:]*v, axis=-1)[..., np.newaxis]*q[..., 1:])

def quatquat(qi, qj):
    """Multiplies the quaternions in the array qi by those in qj"""
    (qi, qj) = np.asarray(qi), np.asarray(qj)
    result = np.empty(np.max([qi.shape, qj.shape], axis=0), dtype=np.float32)

    result[..., 0] = qi[..., 0]*qj[..., 0] - np.sum(qi[..., 1:]*qj[..., 1:], axis=-1)
    result[..., 1:] = (qi[..., 0, np.newaxis]*qj[..., 1:] +
                       qj[..., 0, np.newaxis]*qi[..., 1:] +
                       np.cross(qi[..., 1:], qj[..., 1:]))
    return result

def box_to_matrix(box):
    """Converts a box tuple (in [lx, ly, lz, xy, xz, yz] order with HOOMD
    meanings) into a box matrix"""
    (lx, ly, lz, xy, xz, yz) = box
    return np.array([[lx, xy*ly, xz*lz],
                     [0,     ly, yz*lz],
                     [0,      0,    lz]], dtype=np.float64)

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
