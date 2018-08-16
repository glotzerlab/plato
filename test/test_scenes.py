import collections
import itertools
import numpy as np
import plato
import plato.draw as draw

ALL_TEST_SCENES = []

EXCLUDED_SCENES = collections.defaultdict(set)

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

@selectively_register_scene('matplotlib')
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

    prims = [prim, prim2, prim3, prim4, prim5]
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
                      widths=widths, colors=colors)

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
