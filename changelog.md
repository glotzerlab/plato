## v1.10 - 2020/03/27

- `mesh.SpheropolygonMesh` returned object now also includes integer types for each vertex indicating convexity and concavity (mspells)
- Add `Arrows2D`, `Disks`, `Polygons`, and `Spheropolygons` to zdog backend (mspells)
- Add `Box` and `Lines` to matplotlib backend (mspells)
- Update matplotlib primitives to broadcast quantities of length 1 (mspells)
- Remove margin when saving matplotlib scenes (mspells)
- Fix some features not being properly enabled when passed into `Scene` constructor (mspells)
- Add `Scene.transform()` (mspells)
- Add features to select points and rectangles in vispy (mspells)

## v1.9 - 2020/02/26

- Improve display of many Scene objects in jupyter notebooks (mspells)
- `mesh.unfoldProperties` now broadcasts quantities of length 1 (mspells)
- Unify the broadcasting behavior of primitive attributes for vispy, blender, povray, and zdog backends; these backends now broadcast array quantities of length 1 when required (mspells)

## v1.8

- Add imperative API (mspells)
- Add `Shape.copy_from` (mspells)
- Add extra keyword arguments to `Scene.convert` (mspells)
- Remove requirement for Polygon vertices to be counterclockwise (mspells)

## v1.7

- Add pan argument to zdog scenes (mspells)
- Add new keyboard shortcuts for vispy camera control (hp393)
- Change x/y/z key-axis mappings for vispy scenes (mspells)
- Improve SSAO configuration in vispy backend (mspells)
- Add configurable caps to vispy and povray Lines (mspells,bdice)
- Add Box primitive (amayank,yeinlim,bdice,mspells)

## v1.6

- Enable directional_light by default in all scenes (mspells)
- Improve rendering of scenes with multiple matplotlib 3D primitives (mspells)
- Add outlines to base ConvexPolyhedra (mspells)
- Implement outlines in matplotlib ConvexPolyhedra (mspells)
- Use distance- rather than scaling-based outlines in vispy ConvexPolyhedra (mspells)
- Add zdog backend with support for ConvexPolyhedra, ConvexSpheropolyhedra, Lines, and Spheres (mspells)
- Add static rendering feature to vispy scenes (mspells)
- Fix pythreejs scenes not rendering when translation attribute is not given (bdice,mspells)

## v1.5

- Use gamma correction in fresnel backend (bdice)
- Make fresnel Scenes showable in IPython (bdice)
- Add DiskUnions in vispy and matplotlib (wzygmunt)
- Enable translucency in pythreejs (bdice)
- Add Arrows and DiskUnions to fresnel (bdice)
- Add SphereUnions (wzygmunt)
- Add `vertex_count` property to pythreejs Spheres (bdice)
- Fix pythreejs Scene orientation (bdice,mspells)
- Add Ellipsoids and vispy implementation (mspells)
- Add Ellipsoids povray, fresenel, and pythreejs implementations (bdice)
- Consolidate uses of plato.geometry.fibonacciPositions (mspells)

## v1.4

- Make povray Mesh objects smooth (mspells)
- Add pythreejs backend (mspells)
- Fix vispy-specialized attributes in `Scene.copy()` (mspells)
- Fix usage of outline attributes in fresnel backend for Spheres and Lines (mspells)

## v1.3

- Add fresnel backend (bdice)
- Replicated Mesh objects given positions/orientations (mootimot)
- `Scene.convert()` method (mspells)

## v1.2

- Support multiple directional lights in vispy (mspells)
- Add double-sided Mesh helper function (mspells)
- Experimental vispy normal-rendering mode (mspells)
- Increased povray light intensity (mspells)
- Fix vispy canvas kwargs (mootimot)

## v1.1

- Add outlines to vispy Spheres (mspells)
- Made povray backend able to save raw .pov files (mspells)

## v1.0

- Reorganized entire project from being vispy focused (`plato.gl`) to having multiple backends (`plato.draw.*`) (mspells)
- Port vispy backend (mspells)
- Basic blender backend (mspells)
- Basic matplotlib backend (mspells)
- Basic povray backend (bdice)

## v0.6

- Quantized light/cel-shading effects (mspells)
- Voronoi primitive (mspells)

## v0.5

- Additive rendering (mspells)

## v0.4

- Fast Approximate Antialiasing (mspells)
- Screen Space Ambient Occlusion (mspells)

## v0.3

- Povray export (mspells)

## v0.2

- ConvexSpheropolyhedra primitive (mspells)
- ConvexPolyhedra primitive (mspells)
- Polygons primitive (mspells)
- Spheropolygons primitive (mspells)
- Disks and Spheres primitives (mspells)
- SpherePoints primitive (mspells)
- Arrows2D primitive (jamesaan)
- Lines primitive (askaras)
- Meshes (erteich)
- Smoothed meshes (jproc)
- Order-independent transparency (bvansade, vramasub)
- SVG export (harperic)
