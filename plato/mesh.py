
from collections import defaultdict, namedtuple
from itertools import repeat

import numpy as np

from .geometry import convexHull, insetPolygon, massProperties, Polygon

def computeNormals_(vertices, indices):
    # first, compute the normal for each face
    expandedVertices = vertices[indices]
    faceNormals = np.cross(expandedVertices[:, 1, :] - expandedVertices[:, 0, :],
                            expandedVertices[:, 2, :] - expandedVertices[:, 0, :])
    faceNormals /= np.linalg.norm(faceNormals, axis=-1, keepdims=True)

    # store the normals of faces adjacent to each vertex here
    vertexFaceNormals = defaultdict(list)

    for ((i, j, k), normal) in zip(indices, faceNormals):
        vertexFaceNormals[i].append(normal)
        vertexFaceNormals[j].append(normal)
        vertexFaceNormals[k].append(normal)

    # use the (normalized) mean normal of each adjacent face
    # as the vertex normal
    vertexNormals = []
    for i in range(len(vertices)):
        if vertexFaceNormals[i]:
            normal = np.mean(vertexFaceNormals[i], axis=0)
            normal /= np.linalg.norm(normal)
        else:
            normal = [0, 0, 0]
        vertexNormals.append(normal)

    normal = np.array(vertexNormals, dtype=np.float32)
    return normal

def unfoldProperties(*args):
    """Unfolds (i.e. replicates) groups of NxM properties (M is assumed to be 1
    if given an array of shape (M,)). As an example, given arguments with shapes::

      unfoldProperties([(M0, N0), (M0, N1), ...], [(M1, N2), (M1, N3), ...], ...)

    The result would be a list with element shapes::

      [(M0, M1, ..., N0), (M0, M1, ..., N1), ..., (M0, M1, ..., N2), (M0, M1, ..., N3), ...]
    """
    groups = [[np.asarray(chunk) for chunk in list(group)] for group in args]

    sizeTemplate = [1]*len(groups) + [-1]
    resizedGroups = []
    groupSizes = []
    for (i, group) in enumerate(groups):
        reshapedGroup = []
        for chunk in group:
            if chunk.ndim > 2:
                chunk = chunk.reshape((-1, chunk.shape[-1]))
            elif chunk.ndim < 2:
                chunk = chunk.reshape((-1, 1))
            newSize = list(sizeTemplate)
            newSize[i] = chunk.shape[0]
            newSize[-1] = chunk.shape[-1]
            reshapedGroup.append(chunk.reshape(newSize))
        try:
            groupSize = min(grp.size//grp.shape[-1] for grp in reshapedGroup
                            if grp.size//grp.shape[-1] > 1)
        except ValueError: # empty sequence
            groupSize = 1
        groupSizes.append(groupSize)

        resizedGroups.append([])
        for chunk in reshapedGroup:
            # broadcast single values
            if chunk.shape[i] == 1 and groupSize > 1:
                tile = chunk.ndim*[1]
                tile[i] = groupSize
                chunk = np.tile(chunk, tile)
            resizedGroups[-1].append(chunk)

    result = []
    for (i, group) in enumerate(resizedGroups):
        tile = list(groupSizes) + [1]
        tile[i] = 1
        for chunk in group:
            if chunk.shape[0] > groupSizes[i]:
                chunk = chunk[:groupSizes[i]]
            result.append(np.tile(chunk, tile))

    return result

ConvexPolyhedronMesh = namedtuple(
    'ConvexPolyhedronMesh',
    ['image', 'normal', 'indices', 'face_centers', 'outline_delta'])

def convexPolyhedronMesh(vertices):
    """Generates a mesh (lists of per-vertex properties) of a convex
    polyhedron's image (tessellated vertices of the shape), normal
    (face normal for each vertex), triangle indices, face center, and
    outline offset for an outline width of 1.
    """
    (vertices, faces) = convexHull(vertices)
    vertices = vertices.astype(np.float32)

    image = [[vertices[i] for i in face] for face in faces]
    outline_image = [insetPolygon(vertices[face], 1.0) for face in faces]
    outline_delta = [oimg - img for (oimg, img) in zip(outline_image, image)]

    vidx = 0
    indices = []
    normal = []
    face_centers = []
    for face in faces:
        verts = vertices[face[:3]]
        cross = np.cross(verts[1] - verts[0], verts[2] - verts[0])
        cross /= np.sqrt(np.sum(cross**2))
        normal.extend(len(face)*[cross])
        shiftedFace = list(range(vidx, vidx + len(face)))
        indices.extend(list(zip(repeat(shiftedFace[0]), shiftedFace[1:], shiftedFace[2:])))
        face_centers.extend(len(face)*[np.mean(vertices[face], axis=0)])
        vidx += len(face)
    indices = np.array(indices, dtype=np.uint16).reshape((-1, 3))
    normal = np.array(normal, dtype=np.float32).reshape((-1, 3))
    face_centers = np.array(face_centers, dtype=np.float32).reshape((-1, 3))

    image = sum(image, [])
    image = np.array(image, dtype=np.float32).reshape((-1, 3))

    outline_delta = np.concatenate(outline_delta, axis=0)

    return ConvexPolyhedronMesh(image, normal, indices, face_centers, outline_delta)

ConvexSpheropolyhedronMesh = namedtuple('ConvexSpheropolyhedronMesh',
                        ['image', 'innerImage', 'normal', 'indices'])

def convexSpheropolyhedronMesh(vertices, radius=.5):
    """Generates a mesh (lists of per-vertex properties) of a convex
    spheropolyhedron's image (tessellated vertices of the inner shape
    expanded out by the given radius), inner image ("source" vertex before
    expansion by the given radius), normal (face normal for each vertex),
    and triangle indices."""
    (vertices, faces) = convexHull(vertices)

    edgeNormals = defaultdict(list)
    vertexNormals = defaultdict(list)
    temps = {}

    for face in faces:
        inners = vertices[face]
        deltas = np.roll(inners, -1, axis=0) - inners
        # deltas is normalized
        deltas /= np.sqrt(np.sum(deltas**2, axis=1))[:, np.newaxis]

        cross = np.cross(inners[1] - inners[0], inners[2] - inners[0])
        cross /= np.sqrt(np.sum(cross**2))

        temps[tuple(face)] = (inners, deltas, cross)

        for vert in face:
            vertexNormals[vert].append(cross)

        for pair in (tuple(sorted(p)) for p in zip(face, np.roll(face, 1))):
            edgeNormals[pair].append(cross)

    avgEdgeNormals, avgVertNormals = {}, {}
    for key in edgeNormals:
        norm = np.mean(edgeNormals[key], axis=0)
        norm /= np.sqrt(np.sum(norm**2))
        avgEdgeNormals[key] = norm

    for key in vertexNormals:
        norm = np.mean(vertexNormals[key], axis=0)
        norm /= np.sqrt(np.sum(norm**2))
        avgVertNormals[key] = norm

    capIndices = {}
    image = []
    innerImage = []
    normal = []
    indices = []
    vidx = 0
    for face in faces:
        (inners, deltas, cross) = temps[tuple(face)]
        shiftedInners = inners + radius*cross

        # first triangulate the inner polygons of the face
        faceInnerImage = list(inners)
        faceImage = list(shiftedInners)
        shiftedFace = list(range(vidx, vidx + len(face)))
        faceIndices = list(zip(repeat(shiftedFace[0]), shiftedFace[1:], shiftedFace[2:]))

        # next triangulate the "fins" that stick out of the face
        finDeltas = np.array([avgEdgeNormals[tuple(sorted(p))] for p in zip(face, np.roll(face, -1))], dtype=np.float32)
        finVertices = np.array([inners + radius*finDeltas,
                                np.roll(inners, -1, axis=0) + radius*finDeltas], dtype=np.float32)

        faceInnerImage.extend(list(inners) + list(np.roll(inners, -1, axis=0)))
        faceImage.extend(list(finVertices.reshape((-1, 3))))

        innerStart = vidx
        firstFinStart = vidx + len(face)
        secondFinStart = vidx + 2*len(face)

        for (curInner, nextInner, curFin, nextFin) in zip(
                range(innerStart, innerStart + len(face)),
                np.roll(list(range(innerStart, innerStart + len(face))), -1),
                range(firstFinStart, firstFinStart + len(face)),
                range(secondFinStart, secondFinStart + len(face))):
            faceIndices.append((curInner, curFin, nextFin))
            faceIndices.append((curInner, nextFin, nextInner))

        # finally triangulate the rounded caps
        for vertidx in face:
            if vertidx not in capIndices:
                faceInnerImage.append(vertices[vertidx])
                faceImage.append(vertices[vertidx] + radius*avgVertNormals[vertidx])
                capIndices[vertidx] = vidx + 3*len(face)
                vidx += 1

        for (inner, curFin, nextFin, vertidx) in zip(
                range(innerStart, innerStart + len(face)),
                np.roll(list(range(secondFinStart, secondFinStart + len(face))), 1),
                range(firstFinStart, firstFinStart + len(face)),
                face):
            faceIndices.append((inner, curFin, capIndices[vertidx]))
            faceIndices.append((inner, capIndices[vertidx], nextFin))

        image.extend(faceImage)
        innerImage.extend(faceInnerImage)
        normal.extend(len(faceImage)*[cross])
        indices.extend(faceIndices)
        vidx += len(face)*3

    image = np.asarray(image, dtype=np.float32)
    innerImage = np.asarray(innerImage, dtype=np.float32)
    normal = np.asarray(normal, dtype=np.float32)
    indices = np.asarray(indices, dtype=np.uint32)

    return ConvexSpheropolyhedronMesh(image, innerImage, normal, indices)

SpheropolygonMesh = namedtuple(
    'SpheropolygonMesh', ['image', 'innerImage', 'indices', 'vertex_types'])

def spheropolygonMesh(vertices, radius=1.0, granularity=5):
    """Approximate a spheropolygon by adding rounding to the
    corners."""
    vertices = np.asarray(vertices, dtype=np.float32)

    # Make 3D unit vectors drs from each vertex i to its neighbor i+1
    drs = np.roll(vertices, -1, axis=0) - vertices;
    drs /= np.sqrt(np.sum(drs*drs, axis=1))[:, np.newaxis];
    drs = np.hstack([drs, np.zeros((drs.shape[0], 1))]);

    # relStarts are the offsets relative to the first point
    # of each straight line segment in the polygon.
    rvec = np.array([[0, 0, -1]])*radius;
    relStarts = np.cross(rvec, drs)[:, :2];
    relEnds = np.roll(relStarts, 1, axis=0)

    # absStarts and absEnds are the beginning and end points for each
    # straight line segment.
    absStarts = vertices + relStarts
    absEnds = vertices + relEnds

    # We will join each of these segments by a round cap; this will be
    # done by tracing an arc with the given radius, centered at each
    # vertex from an end of a line segment to a beginning of the next
    theta1s = np.arctan2(relEnds[:, 1], relEnds[:, 0]);
    theta2s = np.arctan2(relStarts[:, 1], relStarts[:, 0]);
    dthetas = (theta2s - theta1s) % (2*np.pi);

    # thetas are the angles at which we'll place points for each
    # vertex; curves are the points on the approximate curves on the
    # corners.
    thetas = np.zeros((vertices.shape[0], granularity));
    # increase the radius of each point by a factor to completely
    # enclose the rounded cap
    factors = 1./np.cos(dthetas/(granularity + 1))
    factors[dthetas > np.pi] = 1.
    for i, (theta1, dtheta) in enumerate(zip(theta1s, dthetas)):
        thetas[i] = theta1 + np.linspace(0, dtheta, 2 + granularity)[1:-1];
    curves = radius*np.vstack([np.cos(thetas).flat, np.sin(thetas).flat]).T;
    curves = curves.reshape((-1, granularity, 2))*factors[:, np.newaxis, np.newaxis];
    curves += vertices[:, np.newaxis, :];

    # Now interleave the pieces
    image = vertices.tolist()
    # vertex_types: int mask with mask&1 indicating "inside shape (not
    # boundary)", mask&2 "part of a curve", mask&4 "is an added curve
    # vertex", mask&8 "is a vertex immediately before a curve"; this
    # translates to: 1 inside vertex; 10 pre-curve boundary; 2
    # post-curve boundary; 6 mid-curve boundary; 0 concave boundary
    vertex_types = len(image)*[1]
    # image and innerImage are the same for the interior region
    innerImage = vertices.tolist()
    indices = Polygon(vertices).triangleIndices.tolist()
    numVerts = len(vertices)
    # by default, absStarts[i] and absEnds[i] are the start and end of
    # the rectangular segment past vertices[i] going counterclockwise.
    for (end, curve, start, vert, dtheta, vertidx, nextvertidx) in \
        zip(absEnds, curves, absStarts, vertices, dthetas,
            np.arange(len(vertices)),
            np.roll(np.arange(len(vertices)), -1)):
        # Don't round a vertex if it is degenerate
        skip = dtheta < 1e-6 or np.abs(2*np.pi - dtheta) < 1e-6

        # convex case: add the end of the last straight line
        # segment, the curved edge, then the start of the next
        # straight line segment.
        if dtheta <= np.pi and not skip:
            triangles = [(vertidx, i, i + 1)
                         for i in range(numVerts, numVerts + granularity + 1)]
            triangles.append((vertidx, numVerts + granularity + 1, nextvertidx))
            triangles.append((numVerts + granularity + 2, nextvertidx, numVerts + granularity + 1))
            indices.extend(triangles)
            numVerts += granularity + 2

            image.append(end);
            image.append(curve);
            image.append(start);

            innerImage.extend((granularity + 2)*[vert])
            vertex_types.append(10)
            vertex_types.extend(granularity*[6])
            vertex_types.append(2)
        # concave case: don't use the curved region, just find the
        # intersection and add that point.
        elif not skip:
            indices.append((vertidx, numVerts + 1, nextvertidx))
            indices.append((numVerts + 1, vertidx, numVerts))
            numVerts += 1

            l = radius/np.cos(dtheta/2);
            p = 2*vert - start - end;
            p /= np.sqrt(np.dot(p, p));

            image.append(vert + p*l);
            innerImage.append(vert)
            vertex_types.append(0)

    image = np.vstack(image)
    innerImage = np.vstack(innerImage)
    indices = np.vstack(indices)
    vertex_types = np.array(vertex_types, dtype=np.int32)

    # rounded segment indexing should be modulo number of rounded
    # segment vertices
    indices[indices >= len(image)] -= len(image) - len(vertices)

    return SpheropolygonMesh(image, innerImage, indices, vertex_types)

def splitChunks(indices, maxIndex=None):
    """Split an index array into a series of chunks such that the
    resulting index arrays always contain elements with values less
    than maxIndex.

    Returns [(scatter, triangleIndices)] where scatter is a list of
    the indices in the source array and triangleIndices are the
    indices (Nx3) of triangles.
    """

    # trivial cases: identity
    if maxIndex is None:
        maxFound = np.max(indices)
        return [(np.arange(maxFound + 1), indices)]
    elif not len(indices):
        return []

    # otherwise, split up into three
    indices = np.asarray(indices, dtype=np.uint64)
    segments = indices//int(maxIndex)
    maxSet = np.max(segments, axis=-1)
    minSet = np.min(segments, axis=-1)
    minorIndices = indices%int(maxIndex)

    result = []
    for segIdx in range(int(np.max(maxSet)) + 1):
        segIndices = np.where(np.all([maxSet == segIdx, minSet == segIdx], axis=0))
        if segIndices[0].size:
            (scat, new) = np.unique(indices[segIndices], return_inverse=True)
            result.append((scat, new.reshape((-1, 3))))

    remainingMask = maxSet != minSet
    remainingIndices = indices[remainingMask]
    (scat, new) = np.unique(remainingIndices, return_inverse=True)
    new = new.reshape((-1, 3))
    remainingChunks = splitChunks(new, maxIndex)
    result.extend([(scat[idx[0]], idx[1])
                   for idx in remainingChunks])

    return result
