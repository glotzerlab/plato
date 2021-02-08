import collections
import itertools
import numpy as np
import os
import plato
import plato.draw as draw
import rowan

ALL_TEST_SCENES = []

EXCLUDED_SCENES = collections.defaultdict(set)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def register_scene(f):
    ALL_TEST_SCENES.append(f)

    return f

def selectively_register_scene(*excluded_names):
    def result(f):
        for name in excluded_names:
            EXCLUDED_SCENES[name].add(f)
        return register_scene(f)

    return result

def translate_usable_scenes(draw):
    result = []
    for scene_fun in ALL_TEST_SCENES:
        draw_name = draw.__name__.split('.')[-1]
        scene = scene_fun()
        usable = all(hasattr(draw, type(prim).__name__) for prim in scene)
        usable = usable and scene_fun not in EXCLUDED_SCENES[draw_name]
        if usable:
            primitives = [getattr(draw, type(prim).__name__).copy(prim) for prim in scene]
            new_scene = draw.Scene(primitives, features=scene._enabled_features,
                                   size=scene.size, translation=scene.translation,
                                   rotation=scene.rotation, zoom=scene.zoom,
                                   pixel_scale=scene.pixel_scale)
            result.append((scene_fun.__name__, new_scene))
    return result

@register_scene
def sunflower_2d(seed=13):

    center_disk = draw.Disks(outline=.05, positions=np.zeros((1, 2)),
                             colors=np.array([0.225, 0.1, 0., 1]),
                             diameters=np.sqrt(3))
    thetas = np.linspace(0, 2*np.pi, 6, endpoint=False)
    vertices = np.array([np.cos(thetas), np.sin(thetas)]).T
    orientations = np.array([[np.cos(np.pi/12), 0, 0, np.sin(np.pi/12)]] * 6)
    petals = draw.Polygons(positions=np.sqrt(3)*vertices, colors=np.array([[0.9, 0.7, 0, 1]]*6),
                           vertices=vertices, outline=.05, orientations=orientations)

    """
    prim2 = draw.Disks(outline=.05, positions=positions,
                       colors=colors, diameters=np.ones((num_particles,)))
    prim3 = draw.Polygons(positions=-positions, colors=colors, vertices=vertices,
                          outline=.05, orientations=orientations)
                          """

    scene = draw.Scene([center_disk, petals], zoom=4, features=dict(pan=True))
    return scene

@register_scene
def concave_2d(seed=16, num_particles=3):
    np.random.seed(seed)

    positions = np.random.uniform(0, 6, (num_particles, 2))
    colors = np.random.rand(num_particles, 4)
    colors[:, 3] = 1
    angles = np.random.uniform(0, 2*np.pi, num_particles)

    thetas = np.linspace(0, 2*np.pi, 7, endpoint=False)
    rs = [.1, .5, .5, .2, .5, .5, .5]
    vertices = np.array([rs*np.cos(thetas), rs*np.sin(thetas)]).T

    prim1 = draw.Polygons(
        positions=positions, colors=colors, angles=angles, vertices=vertices)
    prim2 = draw.Spheropolygons(
        radius=.1, colors=colors, angles=angles, vertices=vertices)
    prim2.positions = -prim1.positions

    scene = draw.Scene([prim1, prim2], zoom=4, features=dict(pan=True))
    return scene

@register_scene
def simple_2d(seed=13, num_particles=2):
    np.random.seed(seed)

    positions = np.random.uniform(0, 3, (num_particles, 2))
    colors = np.random.rand(num_particles, 4)
    orientations = np.random.rand(num_particles, 4)
    orientations[:, 1:3] = 0
    orientations /= np.linalg.norm(orientations, axis=-1, keepdims=True)

    thetas = np.linspace(0, 2*np.pi, 5, endpoint=False)
    vertices = np.array([np.cos(thetas), np.sin(thetas)]).T

    prim1 = draw.Arrows2D(positions=positions, colors=colors*.5,
                          orientations=orientations, magnitudes=[.25, .5])
    prim1.vertices = prim1.vertices - (-.5, 0)
    prim2 = draw.Disks(outline=.05, positions=positions,
                       colors=colors, diameters=np.ones((num_particles,)))
    prim3 = draw.Polygons(positions=-positions, colors=colors, vertices=vertices,
                          outline=.05, orientations=orientations)
    prim4 = draw.Spheropolygons(positions=-positions, colors=colors,
                                vertices=vertices, outline=.05,
                                orientations=orientations)
    prim4.radius = .1
    prim4.positions = prim3.positions + (3, 2)

    scene = draw.Scene([prim2, prim3, prim4, prim1], zoom=4, features=dict(pan=True))
    return scene

@register_scene
def voronoi_with_disks(seed=13, num_points=32):
    np.random.seed(seed)

    positions = np.random.uniform(-3, 3, (num_points, 2))
    colors = np.random.rand(num_points, 4)
    colors[:, 3] = 1
    invbox = np.linalg.inv([[6, 0], [0, 6]])*2

    prim = draw.Voronoi(positions=positions, colors=colors, clip_extent=invbox)
    prim2 = draw.Disks(positions=positions, colors=colors,
                       diameters=np.ones((num_points,))*.5, outline=.125)

    scene = draw.Scene([prim, prim2], zoom=4, features=dict(pan=True))
    return scene

@register_scene
def disk_union(seed=15, num_unions=5):
    np.random.seed(seed)

    points = np.array([[1.0, 0.0], [-0.5, 0.866], [-0.5, -0.866]])
    positions = np.random.uniform(-3, 3, (num_unions, 2))*2
    angles = np.random.uniform(0, 2*np.pi, 4)
    colors = np.random.rand(len(points), 4)
    radii = np.random.uniform(0.5, 1.0, (len(points), 1))

    prim1 = draw.DiskUnions(positions=positions, angles=angles, colors=colors,
                           points=points, radii=radii, outline=.125)

    scene = draw.Scene([prim1], zoom=2, features=dict(pan=True))
    return scene

@register_scene
def sphere_union(seed=15, num_unions=5):
    np.random.seed(seed)

    points = np.array([[0.5, 0.5, 0.5],[0.5, -0.5, -0.5],[-0.5, 0.5, -0.5], [-0.5, -0.5, 0.5]])
    positions = np.random.uniform(-3, 3, (num_unions, 3))*2
    orientations = np.random.rand(num_unions, 4)
    orientations /= np.linalg.norm(orientations, axis=-1, keepdims=True)
    colors = np.random.rand(len(points), 4)
    radii = np.random.uniform(0.5, 1.0, (len(points), 1))

    prim1 = draw.SphereUnions(positions=positions, orientations=orientations,colors=colors,
                           points=points, radii=radii, outline=.10)
    features = dict(ambient_light=.25)
    features['directional_light'] = .5*np.array([(.5, .25, -.5), (0, -.25, -.25)])
    rotation = [ 0.7696833 ,  0.27754638,  0.4948657 , -0.29268363]
    scene = draw.Scene([prim1], zoom=2, features=features, rotation=rotation)
    return scene

@register_scene
def colored_spheres(num_per_side=6):
    xs = np.arange(num_per_side).astype(np.float32)
    rs = np.array(list(itertools.product(*(3*[xs]))))
    rs = np.concatenate([rs, rs + .5], axis=0)

    colors = np.ones((rs.shape[0], 4))
    colors[:, :3] = rs/(num_per_side - 1)
    diameters = np.ones((rs.shape[0],))/np.sqrt(2)
    rs -= np.mean(rs, axis=0, keepdims=True)

    prim = draw.Spheres(positions=rs, colors=colors, diameters=diameters, outline=.02)
    features = dict(ambient_light=.25)
    features['directional_light'] = .5*np.array([(.5, .25, -.5), (0, -.25, -.25)])
    rotation = [0.43797198, -0.4437895 ,  0.08068451,  0.7776423]
    return draw.Scene(prim, features=features, zoom=4, rotation=rotation)

@register_scene
def spoly_cubes_tetrahedra(seed=13, num_per_side=7):
    np.random.seed(seed)

    xs = np.arange(num_per_side).astype(np.float32)
    rs = np.array(list(itertools.product(*(3*[xs]))))
    rs -= np.mean(rs, axis=0, keepdims=True)
    indices = np.arange(rs.shape[0])
    types = (indices%3).astype(np.int32)
    colors = plato.cmap.cubehelix(np.linspace(.3, .7, rs.shape[0]), r=3)
    orientations = np.tile([(1, 0, 0, 0)], (rs.shape[0], 1)).astype(np.float32)
    for i in range(3):
        half_angles = 0.5*np.random.randint(0, 3, rs.shape[0])*np.pi/2
        new_rotation = np.zeros_like(orientations)
        new_rotation[:, 0] = np.cos(half_angles)
        new_rotation[:, 1 + i] = np.sin(half_angles)
        orientations = plato.math.quatquat(orientations, new_rotation)

    tet_verts = np.array([(1, 1, -1), (1, -1, 1), (-1, 1, 1), (-1, -1, -1)],
                         dtype=np.float32)/3
    cube_verts = np.concatenate([tet_verts, -tet_verts], axis=0)

    filt = types == 0
    prim1 = draw.ConvexSpheropolyhedra(
        vertices=tet_verts, radius=1/6, positions=rs[filt],
        orientations=orientations[filt], colors=colors[filt])

    filt = types == 1
    prim2 = draw.ConvexSpheropolyhedra(
        vertices=cube_verts, radius=1/6, positions=rs[filt],
        orientations=orientations[filt], colors=colors[filt])

    rotation = [0.94578046, 0.0234278 , 0.32349595, 0.01735411]
    features = dict(ambient_light=.25, directional_light=(-.1, -.15, -1))
    scene = draw.Scene([prim1, prim2], zoom=4, features=features,
                       rotation=rotation)
    return scene

@register_scene
def convex_polyhedra(seed=16, num_particles=3):
    np.random.seed(seed)
    positions = np.random.uniform(0, 9, (num_particles, 3))
    colors = np.random.uniform(.75, .9, (num_particles, 4))**1.5
    colors[:, 3] = 0.7
    orientations = np.random.rand(num_particles, 4)
    orientations /= np.linalg.norm(orientations, axis=-1, keepdims=True)

    vertices = np.array([(1, 1, 1), (-1, 1, 1), (1, -1, 1), (1, 1, -1)], dtype=np.float32)
    prim = draw.ConvexPolyhedra(
        positions=positions, colors=colors, orientations=orientations,
        vertices=vertices, radius=.1)

    prim2 = prim.copy(prim)
    prim2.vertices = np.concatenate([prim2.vertices, -prim2.vertices], axis=0)
    prim2.positions = -prim2.positions

    prims = [prim, prim2]
    features = dict(ambient_light=.25, directional_light=(-.1, -.15, -1),
                    translucency=True)
    scene = draw.Scene(prims, zoom=2, clip_scale=10, features=features)
    return scene

@register_scene
def many_3d_primitives(seed=15, num_particles=3):
    np.random.seed(seed)
    positions = np.random.uniform(0, 3, (num_particles, 3))
    colors = np.random.uniform(.75, .9, (num_particles, 4))**1.5
    orientations = np.random.rand(num_particles, 4)
    orientations /= np.linalg.norm(orientations, axis=-1, keepdims=True)

    vertices = np.random.rand(12, 3)
    vertices -= np.mean(vertices, axis=0, keepdims=True)
    diameters = np.random.rand(num_particles)

    prim = draw.ConvexSpheropolyhedra(
        positions=positions, colors=colors, orientations=orientations,
        vertices=vertices, radius=.1)

    prim2 = draw.ConvexPolyhedra.copy(prim)
    prim2.positions = (-1, -1, -1) - prim2.positions

    prim3 = draw.Spheres.copy(prim)
    prim3.diameters = diameters
    prim3.positions = (1, -1, 1) - prim.positions

    prim4 = draw.Lines(start_points=prim.positions, end_points=prim2.positions,
                       colors=np.random.rand(num_particles, 4),
                       widths=np.ones((num_particles,))*.1)

    (vertices, faces) = plato.geometry.convexHull(vertices)
    vertices -= (-1, 1, -1)
    indices = list(plato.geometry.fanTriangleIndices(faces))
    colors = np.random.rand(len(vertices), 4)
    colors[:] = .5
    prim5 = draw.Mesh(vertices=vertices, indices=indices, colors=colors)

    prim6 = draw.Ellipsoids.copy(prim)
    prim6.b = 1.05
    prim6.c = 0.8
    prim6.positions = (-1, 1, -1) - prim6.positions

    prims = [prim, prim2, prim3, prim4, prim5, prim6]
    features = dict(ambient_light=.25, directional_light=(-.1, -.15, -1),
                    translucency=True)
    scene = draw.Scene(prims, zoom=5, clip_scale=10, features=features)
    return scene

@register_scene
def sphere_points(seed=14, num_points=128):
    np.random.seed(seed)
    phi = .5*(1 + np.sqrt(5))
    # vertices of a regular dodecahedron
    vertices = np.array(list(itertools.product(*(3*[[-1, 1]])))).tolist()
    for (i, x, y) in itertools.product(range(3), [-phi, phi], [-1/phi, 1/phi]):
        vertices.append(np.roll([0, x, y], i))

    positions = np.concatenate([v + np.random.normal(scale=1e-1, size=(num_points, 3))
                                for v in vertices], axis=0)

    prim = draw.SpherePoints(points=positions, blur=10, intensity=1e3)
    features = dict(ambient_light=.25, directional_light=dict(lights=(-.1, -.15, -1)),
                    additive_rendering=dict(invert=True))
    rotation = [ 0.7696833 ,  0.27754638,  0.4948657 , -0.29268363]
    scene = draw.Scene(prim, zoom=10, features=features, rotation=rotation)
    return scene

@register_scene
def lines_cube():
    vertices = np.array(list(itertools.product(*(3*[[-1, 1]]))), dtype=np.float32)
    edge_indices = np.array([0, 1, 1, 3, 3, 2, 2, 0, 0, 4, 1, 5, 3, 7, 2, 6, 4,
                             5, 5, 7, 7, 6, 6, 4], dtype=np.uint32).reshape((12, 2))
    widths = np.ones((12,))*.1
    colors = plato.cmap.cubehelix(edge_indices[:, 0].astype(np.float32)/8)

    prim = draw.Lines(start_points=vertices[edge_indices[:, 0]],
                      end_points=vertices[edge_indices[:, 1]],
                      widths=widths, colors=colors, cap_mode=1)

    features = dict(ambient_light=.25, directional_light=dict(lights=(-.1, -.15, -1)))
    rotation = [ 9.9774611e-01,  2.3801494e-02, -6.2734932e-02,  5.5756618e-04]
    return draw.Scene(prim, features=features, rotation=rotation, zoom=11)

@register_scene
def disks_and_lines():
    thetas = np.linspace(0, 2*np.pi, 6, endpoint=False)
    extra_positions = np.array([np.cos(thetas), np.sin(thetas)]).T*1.1
    positions = np.array([[0, 0]] + extra_positions.tolist())
    colors = np.tile([[.25, .25, .8, 1]], (len(positions), 1))
    diameters = np.ones((len(positions),))

    prim1 = draw.Disks(positions=positions, colors=colors, diameters=diameters)

    positions_3d = np.pad(positions, ((0, 0), (0, 1)), 'constant')

    colors = np.tile([[.1, .1, .1, 1]], (6, 1))
    prim2 = draw.Lines(start_points=np.tile(positions_3d[:1], (6, 1)),
                       end_points=positions_3d[1:],
                       widths=np.ones((6,))*.25, colors=colors)

    return draw.Scene([prim2, prim1], zoom=10)

def axes_scene(rotation=[1, 0, 0, 0]):
    x = np.array([[6, 0, 0],
                  [6, -1, -1],
                  [6, -1, 1],
                  [6, 1, -1],
                  [6, 1, 1],
                  [6, -0.5, -0.5],
                  [6, -0.5, 0.5],
                  [6, 0.5, -0.5],
                  [6, 0.5, 0.5]])
    x_lines_prim = draw.Lines(start_points=np.array([[0, 0, 0], *x[1:5]]),
                              end_points=np.array([x[0]]*5),
                              widths=0.5*np.ones(5),
                              colors=[[1, 0, 0, 1]]*5,
                              cap_mode=1)
    y = np.array([[0, 6, 0],
                  [1, 6, 1],
                  [-1, 6, 1],
                  [0, 6, -1],
                  [0.5, 6, 0.5],
                  [-0.5, 6, 0.5],
                  [0, 6, -0.5]])
    y_lines_prim = draw.Lines(start_points=np.array([[0, 0, 0], *y[1:4]]),
                              end_points=np.array([y[0]]*4),
                              widths=0.5*np.ones(4),
                              colors=[[0, 1, 0, 1]]*4,
                              cap_mode=1)
    z = np.array([[0, 0, 6],
                  [-1, 1, 6],
                  [1, 1, 6],
                  [-1, -1, 6],
                  [1, -1, 6],
                  [-0.5, -1, 6],
                  [0, -1, 6],
                  [0.5, -1, 6],
                  [-0.5, 1, 6],
                  [0, 1, 6],
                  [0.5, 1, 6],
                  [-0.5, -0.5, 6],
                  [0.5, 0.5, 6]])
    z_lines_prim = draw.Lines(start_points=np.array([[0, 0, 0], *z[1:4]]),
                              end_points=np.array([z[0], *z[2:5]]),
                              widths=0.5*np.ones(4),
                              colors=[[0, 0, 1, 1]]*4,
                              cap_mode=1)
    scene = draw.Scene([x_lines_prim,
                        y_lines_prim,
                        z_lines_prim],
                       rotation=rotation)
    return scene

@register_scene
def axes_unrotated():
    return axes_scene()

@register_scene
def axes_isometric():
    return axes_scene([0.88047624, 0.27984814, 0.3647052, 0.1159169])

@register_scene
def axes_rotated_30_deg_around_z():
    return axes_scene([.96592583, 0., 0., 0.25881905])

@register_scene
def axes_rotated_randomly():
    return axes_scene([0.22886531, -0.61944334, -0.68368065, 0.31063063])

@register_scene
def meshes():
    vertices = plato.geometry.fibonacciPositions(64)
    vertices, faces = plato.mesh.convexHull(vertices)
    # distance from y axis
    x = vertices[:, 0]
    y = vertices[:, 1]
    z = vertices[:, 2]
    d = np.sqrt(x*x + y*y)
    # deform y
    vertices[:, 2] -= 1 * (1-d)*z
    colors = np.tile([[0.25, 0.25, 0.7, 1.0]], (len(vertices), 1))
    colors[:, 0] = vertices[:, 0]
    colors[:, 0] -= np.min(colors[:, 0])
    colors[:, 0] /= np.max(colors[:, 0])

    positions = [[-1, 0, 0], [1, 0, 0.0]]
    orientations = np.tile([[1, 0, 0, 0]], (len(positions), 1)).astype(np.float32)
    halftheta = -np.pi/5
    orientations[0] = (np.cos(halftheta), 0, np.sin(halftheta), 0)
    prim = draw.Mesh(vertices=vertices, indices=faces, colors=colors,
            positions=positions, orientations=orientations)

    prim.shape_colors = [(0, .5, 0, 1), (0, 0, .5, 1)]
    prim.shape_color_fraction = .5

    features = dict(ambient_light=.25, directional_light=(-.1, -.15, -1))
    return draw.Scene(prim, zoom=10, features=features)

@register_scene
def ellipsoids():
    prim0 = draw.Ellipsoids()
    primx = draw.Ellipsoids(positions=(2, 0, 0), a=1.5, b=1.25)
    primy = draw.Ellipsoids(positions=(0, 2, 0), b=1.5, c=2)
    primz = draw.Ellipsoids(positions=(0, 0, 2), c=1.5)

    prims = [prim0, primx, primy, primz]

    features = dict(ambient_light=.25, directional_light=(-.1, -.15, -1))
    return draw.Scene(prims, zoom=4.6, features=features,
                      rotation=[0.88047624, 0.27984814, 0.3647052, 0.1159169])

def example_vector_field(N):
    xs = np.linspace(-N/2, N/2, N)
    positions = np.array(list(itertools.product(xs, xs, xs)), dtype=np.float32)
    positions = positions.reshape((-1, 3))

    thetas = np.arctan2(positions[:, 1], positions[:, 0])
    circle = np.array([-np.sin(thetas), np.cos(thetas), np.zeros_like(thetas)]).T

    rotated = np.cross(positions, circle)
    rotated /= np.linalg.norm(rotated, axis=-1, keepdims=True)
    rotated[np.logical_not(np.all(np.isfinite(rotated), axis=-1))] = (1, 0, 0)

    return positions, rotated

def field_scene(N=10, use='ellipsoids'):
    features = dict(ambient_light=.4)
    (positions, units) = example_vector_field(5)

    normalized_z = positions[:, 2].copy()
    normalized_z -= np.min(normalized_z)
    normalized_z /= np.max(normalized_z)

    colors = plato.cmap.cubehelix(normalized_z, h=1.4)
    colors[:, :3] = .5*(colors[:, :3] +
        plato.cmap.cubeellipse(np.arctan2(positions[:, 1], positions[:, 0])))

    if use == 'ellipsoids':
        orientations = rowan.vector_vector_rotation([(1, 0, 0)], units)
        prim = draw.Ellipsoids(
            positions=positions, orientations=orientations, colors=colors,
            a=.5, b=.125, c=.125)
    elif use == 'lines':
        features['ambient_light'] = 1
        starts = positions - units/2
        ends = positions + units/2

        prim = draw.Lines(
            start_points=starts, end_points=ends,
            colors=colors, widths=np.ones(len(positions))*.25)
    else:
        raise NotImplementedError('Unknown primitive {}'.format(use))

    rotation = [ 0.8126942 ,  0.35465172, -0.43531808,  0.15571932]
    scene = draw.Scene(
        prim, zoom=4, features=features, rotation=rotation)
    return scene

@register_scene
def field_lines(N=10):
    return field_scene(N, 'lines')

@register_scene
def field_ellipsoids(N=10):
    return field_scene(N, 'ellipsoids')

@register_scene
def simple_cubes_octahedra(N=4):
    xs = np.linspace(-N/2, N/2, N)
    positions = np.array(list(itertools.product(xs, xs, xs)))

    cube_positions = positions[::2]
    oct_positions = positions[1::2]

    cube_colors = np.ones((len(cube_positions), 4))
    cube_colors[:] = (.5, .6, .7, 1)
    oct_colors = np.ones((len(oct_positions), 4))
    oct_colors[:] = (.7, .5, .6, 1)

    cube_vertices = list(itertools.product(*(3*[[-.5, .5]])))
    oct_vertices = [np.roll((0, 0, v), i) for (i, v) in
                    itertools.product(range(3), [-.5, .5])]

    cubes = draw.ConvexPolyhedra(
        vertices=cube_vertices, positions=cube_positions,
        colors=cube_colors, orientations=np.ones_like(cube_colors)*(1, 0, 0, 0))
    octahedra = draw.ConvexPolyhedra(
        vertices=oct_vertices, positions=oct_positions, outline=.025,
        colors=oct_colors, orientations=np.ones_like(oct_colors)*(1, 0, 0, 0))

    rotation = [0.99795496,  0.01934275, -0.06089295,  0.00196485]
    scene = draw.Scene([cubes, octahedra], rotation=rotation, zoom=5.5)
    return scene

@register_scene
def boxes_3d():
    prim = draw.Box(Lx=5, Ly=5, Lz=6, xy=0.2, xz=0.4, yz=0,
                    width=0.2, color=[0, 0.2, 0.6, 1])
    prim2 = draw.Box.from_box([3, 2.5, 4, 0.1, -0.2, 0.5],
                    width=0.15, color=[0.9, 0.9, 0.2, 1])
    prim3 = draw.Box.from_box(box=[2, 1.5, 2, 0.8, 0.1, -0.2],
                    width=0.1, color=[0.5, 0.5, 0.5, 1])
    features = dict(ambient_light=.25,
                    directional_light=dict(lights=(-.1, -.15, -1)))
    rotation = [9.9774611e-01, 2.3801494e-02, -6.2734932e-02, 5.5756618e-04]
    return draw.Scene((prim, prim2, prim3), features=features,
                      rotation=rotation, zoom=3)

@register_scene
def boxes_2d():
    prim = draw.Box(Lx=5, Ly=5, Lz=0, xy=0.2, xz=0.4, yz=0,
                    width=0.2, color=[0, 0.2, 0.6, 1])
    prim2 = draw.Box.from_box({'Lx': 3, 'Ly': 2.5, 'xy': -0.3},
                    width=0.15, color=[0.9, 0.9, 0.2, 1])
    prim3 = draw.Box.from_box([2, 1.5],
                    width=0.1, color=[0.5, 0.5, 0.5, 1])
    return draw.Scene((prim, prim2, prim3), zoom=3)

@register_scene
def low_poly_stanford_bunny():
    """Low-poly Stanford Bunny 3D model.

    Model data from https://www.thingiverse.com/thing:151081 by johnny6, licensed CC BY-NC 4.0.

    This example shows a mesh with nonzero outline width and vertex colors.
    """
    data = np.load(os.path.join(DATA_DIR, "low_poly_stanford_bunny", "data.npz"))
    vertices = data["vertices"]
    indices = data["indices"]
    colors = data["colors"]
    prim = draw.Mesh(vertices=vertices,
                     indices=indices,
                     colors=colors,
                     outline=2e-2)
    rotation = [-0.795798,  0.58683366, -0.12027311, -0.08869123]
    return draw.Scene(prim, rotation=rotation, zoom=2)