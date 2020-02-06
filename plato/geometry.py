from collections import defaultdict, namedtuple

import numpy as np

def convexHull(vertices, tol=1e-6):
    """Returns an array of vertices and a list of faces (vertex
    indices) for the convex hull of the given set of vertice. Uses
    scipy's quickhull wrapper."""
    from scipy.spatial import cKDTree, ConvexHull
    from scipy.sparse.csgraph import connected_components

    hull = ConvexHull(vertices)
    # Triangles in the same face will be defined by the same linear equalities
    dist = cKDTree(hull.equations)
    trianglePairs = dist.query_pairs(tol)

    connectivity = np.zeros((len(hull.simplices), len(hull.simplices)), dtype=np.int32)

    for (i, j) in trianglePairs:
        connectivity[i, j] = connectivity[j, i] = 1

    # connected_components returns (number of faces, cluster index for each input)
    (_, joinTarget) = connected_components(connectivity, directed=False)
    faces = defaultdict(list)
    norms = defaultdict(list)
    for (idx, target) in enumerate(joinTarget):
        faces[target].append(idx)
        norms[target] = hull.equations[idx][:3]

    # a list of sets of all vertex indices in each face
    faceVerts = [set(hull.simplices[faces[faceIndex]].flat) for faceIndex in sorted(faces)]
    # normal vector for each face
    faceNorms = [norms[faceIndex] for faceIndex in sorted(faces)]

    # polygonal faces
    polyFaces = []
    for (norm, faceIndices) in zip(faceNorms, faceVerts):
        face = np.array(list(faceIndices), dtype=np.uint32)
        N = len(faceIndices)

        r = hull.points[face]
        rcom = np.mean(r, axis=0)

        # plane_{a, b}: basis vectors in the plane
        plane_a = r[0] - rcom
        plane_a /= np.sqrt(np.sum(plane_a**2))
        plane_b = np.cross(norm, plane_a)

        dr = r - rcom[np.newaxis, :]

        thetas = np.arctan2(dr.dot(plane_b), dr.dot(plane_a))

        sortidx = np.argsort(thetas)

        face = face[sortidx]
        polyFaces.append(face)

    return (hull.points, polyFaces)

ConvexDecomposition = namedtuple('ConvexDecomposition', ['vertices', 'edges', 'faces'])

def convexDecomposition(vertices):
    """Decompose a convex polyhedron specified by a list of vertices into
    vertices, faces, and edges. Returns a ConvexDecomposition object.
    """
    (vertices, faces) = convexHull(vertices)
    edges = set()

    for face in faces:
        for (i, j) in zip(face, np.roll(face, -1)):
            edges.add((min(i, j), max(i, j)))

    return ConvexDecomposition(vertices, edges, faces)

def fanTriangleIndices(faces):
    """Returns the indices needed to break the faces of a polyhedron into
    a set of triangle faces"""
    for face in faces:
        for (i, j) in zip(face[1:], face[2:]):
            yield (face[0], i, j)

def fanTriangles(vertices, faces=None):
    """Create triangles by fanning out from vertices. Returns a
    generator for vertex triplets. If faces is None, assume that
    vertices are planar and indicate a polygon; otherwise, use the
    face indices given in faces."""
    vertices = np.asarray(vertices)

    if faces is None:
        if len(vertices) < 3:
            return
        for tri in ((vertices[0], verti, vertj) for (verti, vertj) in
                    zip(vertices[1:], vertices[2:])):
            yield tri
    else:
        for (i, j, k) in fanTriangleIndices(faces):
            yield (vertices[i], vertices[j], vertices[k])

def fibonacciPositions(n_b, a=.5, b=0.5, c=0.5):
    """Create positions on the surface of an ellipsoid using the Fibonacci sequence

    :param n_b: Number of points to place
    :param a: Radius (semi-axis length) in the x direction
    :param b: Radius (semi-axis length) in the y direction
    :param c: Radius (semi-axis length) in the z direction
    """
    m = np.arange(n_b).astype(np.float32)
    phi = m*np.pi*(3 - np.sqrt(5))
    vy = 2*m/n_b + 1/n_b - 1
    return np.array([a*np.sqrt(1 - vy**2)*np.cos(phi),
                     b*vy, c*np.sqrt(1 - vy**2)*np.sin(phi)]).T

def insetPolygon(vertices, distance):
    """Create polygon vertices suitable for use in an outline

    This method creates a new set of vertices that will form edges
    parallel to those in the original vertices, but shifted inward by
    the given distance. This method works for both 2D and 3D vertices
    and is intended as a replacement for `Outline`. Vertices should be
    planar and specified in right-handed order.

    :param vertices: iterable of (x, y) or (x, y, z) vertex coordinates
    :param distance: Distance (width) to inset by
    """
    vertices = np.asarray(vertices)
    dimension = vertices.shape[1]

    rijs = np.roll(vertices, -1, axis=0) - vertices
    face_normal = np.cross(rijs[0], rijs[1])
    face_normal /= np.linalg.norm(face_normal)
    rijs_normal = rijs/np.linalg.norm(rijs, axis=-1, keepdims=True)
    if dimension == 3:
        perps = np.cross([face_normal], rijs_normal)
        perps /= np.linalg.norm(perps, axis=-1, keepdims=True)
    else:
        perps = np.dot(rijs_normal, [[0, 1], [-1, 0]])

    # construct a linear system of equations Ax=b solving for the
    # intersection point of each inset vertex
    A = np.tile(rijs_normal[:, :, np.newaxis], (1, 1, 2))
    A[:, :, 1] = np.roll(rijs_normal, 1, axis=0)
    b = distance*(perps - np.roll(perps, 1, axis=0))

    if dimension == 3:
        lams = np.array([np.linalg.lstsq(a_, b_, rcond=-1)[0]
                         for (a_, b_) in zip(A, b)], dtype=np.float32)
    else:
        lams = np.linalg.solve(A, b)

    result = vertices - lams[..., 1, np.newaxis]*rijs_normal + distance*perps
    return result

def massProperties(vertices, faces=None, factor=1.):
    """Returns (mass, center of mass, moment of inertia tensor in (xx,
    xy, xz, yy, yz, zz) order) specified by the given list of vertices
    and faces. Note that the faces must be listed in a consistent
    order so that normals are all pointing in the correct direction
    from the face. If given a list of 2D vertices, return the same but
    for the 2D polygon specified by the vertices.

    All faces should be specified in right-handed order.

    For details on the 3D case, confer "Polyhedral Mass Properties
    (Revisited) by David Eberly, available at:

    http://www.geometrictools.com/Documentation/PolyhedralMassProperties.pdf"""
    vertices = np.array(vertices)

    # Specially handle 2D
    if len(vertices[0]) == 2:
        # First, calculate the center of mass and center the vertices
        shifted = list(vertices[1:]) + [vertices[0]]
        a_s = [(x1*y2 - x2*y1) for ((x1, y1), (x2, y2))
               in zip(vertices, shifted)]
        triangleCOMs = [(v0 + v1)/3 for (v0, v1) in zip(vertices, shifted)]
        COM = np.sum([a*com for (a, com) in zip(a_s, triangleCOMs)],
                     axis=0)/np.sum(a_s)
        vertices -= COM

        shifted = list(vertices[1:]) + [vertices[0]]
        f = lambda x1, x2: x1*x1 + x1*x2 + x2*x2
        Ixyfs = [(f(y1, y2), f(x1, x2)) for ((x1, y1), (x2, y2))
                 in zip(vertices, shifted)]

        Ix = sum(I*a for ((I, _), a) in zip(Ixyfs, a_s))/12.
        Iy = sum(I*a for ((_, I), a) in zip(Ixyfs, a_s))/12.

        I = np.array([Ix, 0, 0, Iy, 0, Ix + Iy])

        return area(vertices)*factor, COM, factor*I

    # multiplicative factors
    factors = 1./np.array([6, 24, 24, 24, 60, 60, 60, 120, 120, 120])

    # order: 1, x, y, z, x^2, y^2, z^2, xy, yz, zx
    intg = np.zeros(10)

    for (v0, v1, v2) in fanTriangles(vertices, faces):
        # (xi, yi, zi) = vi
        abc1 = v1 - v0
        abc2 = v2 - v0
        d = np.cross(abc1, abc2)

        temp0 = v0 + v1
        f1 = temp0 + v2
        temp1 = v0*v0
        temp2 = temp1 + v1*temp0
        f2 = temp2 + v2*f1
        f3 = v0*temp1 + v1*temp2 + v2*f2
        g0 = f2 + v0*(f1 + v0)
        g1 = f2 + v1*(f1 + v1)
        g2 = f2 + v2*(f1 + v2)

        intg[0] += d[0]*f1[0]
        intg[1:4] += d*f2
        intg[4:7] += d*f3
        intg[7] += d[0]*(v0[1]*g0[0] + v1[1]*g1[0] + v2[1]*g2[0])
        intg[8] += d[1]*(v0[2]*g0[1] + v1[2]*g1[1] + v2[2]*g2[1])
        intg[9] += d[2]*(v0[0]*g0[2] + v1[0]*g1[2] + v2[0]*g2[2])

    intg *= factors

    mass = intg[0]
    com = intg[1:4]/mass

    moment = np.zeros(6)

    moment[0] = intg[5] + intg[6] - mass*np.sum(com[1:]**2)
    moment[1] = -(intg[7] - mass*com[0]*com[1])
    moment[2] = -(intg[9] - mass*com[0]*com[2])
    moment[3] = intg[4] + intg[6] - mass*np.sum(com[[0, 2]]**2)
    moment[4] = -(intg[8] - mass*com[1]*com[2])
    moment[5] = intg[4] + intg[5] - mass*np.sum(com[:2]**2)

    return mass*factor, com, moment*factor

def twiceTriangleArea(p0, p1, p2):
    """Returns twice the signed area of the triangle specified by the
    2D numpy points (p0, p1, p2)."""
    p1 = p1 - p0;
    p2 = p2 - p0;
    return p1[0]*p2[1] - p2[0]*p1[1];

## Compute basic properties of a polygon, stored as a list of adjacent vertices
#
# ### Attributes:
#
# - vertices nx2 numpy array of adjacent vertices
# - n number of vertices in the polygon
# - triangles cached numpy array of constituent triangles
#
class Polygon:
    """Basic class to hold a set of points for a 2D polygon"""
    def __init__(self, verts):
        """Initialize a polygon with a list of 2D points."""
        self.vertices = np.array(verts, dtype=np.float32);

        self.rmax = np.sqrt(np.max(np.sum(self.vertices**2, axis=-1)))

        if len(self.vertices) < 3:
            raise TypeError("a polygon must have at least 3 vertices");
        if len(self.vertices[1]) != 2:
            raise TypeError("positions must be an Nx2 array");
        self.n = len(self.vertices);

    def area(self):
        """Calculate and return the signed area of the polygon with
        counterclockwise shapes having positive area"""
        shifted = np.roll(self.vertices, -1, axis=0);

        # areas is twice the signed area of each triangle in the shape
        areas = self.vertices[:, 0]*shifted[:, 1] - shifted[:, 0]*self.vertices[:, 1];

        return np.sum(areas)/2;

    def center(self):
        """Center this polygon around (0, 0)"""
        (_, com, _) = massProperties(self.vertices)
        self.vertices -= com[np.newaxis, :]

    @property
    def triangleIndices(self):
        """A cached property of an Ntx3x2 np array of vertex indices, where
        Nt is the number of triangles in this polygon."""
        try:
            return self._triangles;
        except AttributeError:
            self._triangles = self._triangulation();
        return self._triangles;

    def _triangulation(self):
        """Return a numpy array of triangle indices with shape (Nt, 3) for Nt
        triangles.

        """

        if self.n == 3:
            vertices = np.array(self.vertices)
            cross = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
            if cross > 0:
                return np.array([[0, 1, 2]], dtype=np.uint32)
            else:
                return np.array([[0, 2, 1]], dtype=np.uint32)
        elif self.n < 3:
            raise RuntimeError('Trying to triangulate a polygon with no area')

        result = [];
        remaining = self.vertices + np.random.uniform(-1, 1, size=self.vertices.shape)*1e-6
        remainingIndices = range(len(remaining))

        # step around the shape and grab ears until only 4 vertices are left
        while len(remaining) > 4:
            signs = [];
            for vert in (remaining[-1], remaining[1]):
                arms1 = remaining[2:-2] - vert;
                arms2 = vert - remaining[3:-1];
                signs.append(np.sign(arms1[:, 1]*arms2[:, 0] -
                                        arms2[:, 1]*arms1[:, 0]));
            for rest in (remaining[2:-2], remaining[3:-1]):
                arms1 = remaining[-1] - rest;
                arms2 = rest - remaining[1];
                signs.append(np.sign(arms1[:, 1]*arms2[:, 0] -
                                        arms2[:, 1]*arms1[:, 0]));

            cross = np.any(np.bitwise_and(signs[0] != signs[1],
                                                signs[2] != signs[3]));
            if not cross and twiceTriangleArea(remaining[-1], remaining[0],
                                               remaining[1]) > 0.:
                # triangle [-1, 0, 1] is a good one, cut it out
                result.append((remainingIndices[-1], remainingIndices[0],
                               remainingIndices[1]))
                remaining = remaining[1:];
                remainingIndices = remainingIndices[1:]
            else:
                remaining = np.roll(remaining, 1, axis=0);
                remainingIndices = np.roll(remainingIndices, 1, axis=0)

        # there must now be 0 or 1 concave vertices left; find the
        # concave vertex (or a vertex) and fan out from it
        vertices = remaining;
        shiftedUp = vertices - np.roll(vertices, 1, axis=0);
        shiftedBack = np.roll(vertices, -1, axis=0) - vertices;

        # signed area for each triangle (i-1, i, i+1) for vertex i
        areas = shiftedBack[:, 1]*shiftedUp[:, 0] - shiftedUp[:, 1]*shiftedBack[:, 0];

        concave = np.where(areas < 0.)[0];

        fan = (concave[0] if len(concave) else 0);
        fanIndex = remainingIndices[fan]
        remainingIndices = np.roll(remainingIndices, -fan, axis=0)[1:];

        result.extend([(fanIndex, remainingIndices[0], remainingIndices[1]),
                       (fanIndex, remainingIndices[1], remainingIndices[2])]);

        return np.array(result, dtype=np.uint32);

## \internal Outline class for Polygon
# is not meant to be called except by Polygon. Use at own discretion
class Outline(object):
    def __init__(self, polygon, width):
        """Initialize an outline of a given Polygon object. Takes the
        polygon in question and the outline width to inset."""
        self.polygon = polygon;
        self.width = width;

    @property
    def width(self):
        """Property for the width of the outline. Updates the
        triangulation when set."""
        return self._width;

    @width.setter
    def width(self, width):
        self._width = width;
        self._triangulate();

    def _triangulate(self):
        drs = np.roll(self.polygon.vertices, -1, axis=0) - self.polygon.vertices;
        ns = drs/np.sqrt(np.sum(drs*drs, axis=1)).reshape((len(drs), 1));
        thetas = np.arctan2(drs[:, 1], drs[:, 0]);
        dthetas = (thetas - np.roll(thetas, 1))%(2*np.pi);

        concave = dthetas > np.pi;
        convex = concave == False;

        hs = np.repeat(self.width, len(drs));
        hs[convex] /= np.cos(dthetas[convex]/2);
        # flip the concave bisectors
        hs[concave] *= -1;
        hs[concave] /= np.sin((dthetas[concave]-np.pi)/2);
        hs = hs.reshape((len(hs), 1));

        bisectors = ns - np.roll(ns, 1, axis=0);
        bisectors /= np.sqrt(np.sum(bisectors*bisectors, axis=1)).reshape((len(ns), 1));

        inners = self.polygon.vertices + hs.reshape((len(ns), 1))*bisectors;
        self.inner = Polygon(inners);
        self.outer = self.polygon;
