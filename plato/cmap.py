import numpy as np

def cubehelix(lambda_, s=0, r=1, h=1.2, gamma=1, reverse=False, alpha=1):
    """Evaluate the cubehelix colormap for a set of lambda values

    See http://adsabs.harvard.edu/abs/2011BASI...39..289G

    :param lambda_: A numpy array (or something that converts to one) of 0.0-1.0 linear values
    :param alpha: alpha value to use in resulting color
    :param s: The hue of the starting color: (0, 1, 2) -> (blue, red, green)
    :param r: Number of rotations through R->G->B to make
    :param h: Hue parameter controlling saturation
    :param gamma: Reweighting power to emphasize low-intensity values (gamma < 1) or high-intensity values (gamma > 1)
    :param alpha: The alpha value for the entire colormap is set to this value
    :param reverse: Reverse the colormap with respect to lambda (lambda -> 1 - lambda); perhaps more suitable for density-like colorings

    """
    lambda_ = np.asarray(lambda_, dtype=np.float32)
    np.clip(lambda_, 0, 1, out=lambda_)

    result = np.empty(list(lambda_.shape) + [4], dtype=np.float32)

    if reverse:
        lambda_ *= -1
        lambda_ += 1

    phi = 2*np.pi*(s*(1./3) + r*lambda_)
    np.power(lambda_, gamma, out=lambda_)

    a_paper = h*lambda_*(1 - lambda_)*.5

    sphi = np.sin(phi)
    cphi = np.cos(phi)

    result[:, 0] = lambda_ + a_paper*(-0.14861*cphi + 1.78277*sphi)
    result[:, 1] = lambda_ + a_paper*(-0.29227*cphi - 0.90649*sphi)
    result[:, 2] = lambda_ + a_paper*( 1.97294*cphi)
    result[:, 3] = alpha

    np.clip(result, 0, 1, out=result)
    return result

def cubeellipse_intensity(theta, lam=0.5, lam_r1=.1, lam_r2=.05, gamma=1., s=0., r=1., h=1.):
    """Compute a cubeellipse colormap with pseudo-random intensity variations

    cubeellipse_intensity is an analogous colormap to cubehelix, but
    in an ellipse perpendicular to the color cube diagonal rather than
    in a helix along the color cube diagonal (with additional
    intensity variations). It can be used for generating categorical
    color maps, for example.

    :param theta: angle array for colors
    :param lam: scalar lambda value about which the ellipse will expand
    :param lam_r1: major axis of ellipse in `lam` space
    :param lam_r2: minor axis of ellipse in `lam` space
    :param gamma: `lam` rescaling factor: `lam <- lam**gamma`
    :param s: The hue of the starting color: (0, 1, 2) -> (blue, red, green) at `lam=0`
    :param r: Number of rotations through R->G->B to make (in `lam`-space)
    :param h: Hue parameter controlling saturation
    """

    theta %= 2*np.pi

    if lam_r2 is None:
        lam_r2 = lam_r1

    lamtheta = 1 + 480*np.sqrt(theta) - 1024*theta**2
    lam = lam + np.cos(lamtheta)*lam_r1 + np.sin(lamtheta)*lam_r2
    lam = lam**gamma

    a = h*lam*(1 - lam)*.5
    v = np.array([[-.14861, 1.78277], [-.29227, -.90649], [1.97294, 0.]], dtype=np.float32)
    ctarray = np.array([np.cos(theta*r + s), np.sin(theta*r + s)], dtype=np.float32)
    return np.clip(lam + a*v.dot(ctarray), 0, 1).T

def cubeellipse(theta, lam=0.5, gamma=1., s=0., r=1., h=1.):
    """Compute a cubeellipse colormap

    cubeellipse is an analogous colormap to cubehelix, but in an
    ellipse perpendicular to the color cube diagonal rather than in a
    helix along the color cube diagonal. It is useful in mapping
    directors on the unit circle to a unique color.

    :param theta: angle array for colors
    :param lam: scalar lambda value about which the ellipse will expand
    :param lam_r1: major axis of ellipse in `lam` space
    :param lam_r2: minor axis of ellipse in `lam` space
    :param gamma: `lam` rescaling factor: `lam <- lam**gamma`
    :param s: The hue of the starting color: (0, 1, 2) -> (blue, red, green) at `lam=0`
    :param r: Number of rotations through R->G->B to make (in `lam`-space)
    :param h: Hue parameter controlling saturation
    """
    return cubeellipse_intensity(theta, lam, 0, 0, gamma, s, r, h)
