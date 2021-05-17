## v1.12 - 2021/05/17

- Add `Mesh` to fresnel backend (bdice@umich)
- Update fresnel backend to support fresnel 0.13.0, drops support for fresnel < 0.12.0 (bdice@umich)
- Allow matplotlib scenes to specify figure or axis when saving (thomasaarholt@uio)

## v1.11 - 2020/06/25

- Add `transparent_background` feature to povray backend (mspells@umich)
- Fix ConvexPolyhedra being disconnected from their outlines in povray, introduced in v1.9 (mspells@umich)
- Support scene translation in povray (mspells@umich)
- Fix `len(Shape)` for shapes using default values of attributes (mspells@umich)
- Add `pick` feature to vispy Scenes (mspells@umich)

## v1.10 - 2020/03/27

- `mesh.SpheropolygonMesh` returned object now also includes integer types for each vertex indicating convexity and concavity (mspells@umich)
- Add `Arrows2D`, `Disks`, `Polygons`, and `Spheropolygons` to zdog backend (mspells@umich)
- Add `Box` and `Lines` to matplotlib backend (mspells@umich)
- Update matplotlib primitives to broadcast quantities of length 1 (mspells@umich)
- Remove margin when saving matplotlib scenes (mspells@umich)
- Fix some features not being properly enabled when passed into `Scene` constructor (mspells@umich)
- Add `Scene.transform()` (mspells@umich)
- Add features to select points and rectangles in vispy (mspells@umich)

## v1.9 - 2020/02/26

- Improve display of many Scene objects in jupyter notebooks (mspells@umich)
- `mesh.unfoldProperties` now broadcasts quantities of length 1 (mspells@umich)
- Unify the broadcasting behavior of primitive attributes for vispy, blender, povray, and zdog backends; these backends now broadcast array quantities of length 1 when required (mspells@umich)

## v1.8

- Add imperative API (mspells@umich)
- Add `Shape.copy_from` (mspells@umich)
- Add extra keyword arguments to `Scene.convert` (mspells@umich)
- Remove requirement for Polygon vertices to be counterclockwise (mspells@umich)

## v1.7

- Add pan argument to zdog scenes (mspells@umich)
- Add new keyboard shortcuts for vispy camera control (hp393@cornell)
- Change x/y/z key-axis mappings for vispy scenes (mspells@umich)
- Improve SSAO configuration in vispy backend (mspells@umich)
- Add configurable caps to vispy and povray Lines (mspells@umich,bdice@umich)
- Add Box primitive (amayank@umich,yeinlim@umich,bdice@umich,mspells@umich)

## v1.6

- Enable directional_light by default in all scenes (mspells@umich)
- Improve rendering of scenes with multiple matplotlib 3D primitives (mspells@umich)
- Add outlines to base ConvexPolyhedra (mspells@umich)
- Implement outlines in matplotlib ConvexPolyhedra (mspells@umich)
- Use distance- rather than scaling-based outlines in vispy ConvexPolyhedra (mspells@umich)
- Add zdog backend with support for ConvexPolyhedra, ConvexSpheropolyhedra, Lines, and Spheres (mspells@umich)
- Add static rendering feature to vispy scenes (mspells@umich)
- Fix pythreejs scenes not rendering when translation attribute is not given (bdice@umich,mspells@umich)

## v1.5

- Use gamma correction in fresnel backend (bdice@umich)
- Make fresnel Scenes showable in IPython (bdice@umich)
- Add DiskUnions in vispy and matplotlib (wzygmunt@umich)
- Enable translucency in pythreejs (bdice@umich)
- Add Arrows and DiskUnions to fresnel (bdice@umich)
- Add SphereUnions (wzygmunt@umich)
- Add `vertex_count` property to pythreejs Spheres (bdice@umich)
- Fix pythreejs Scene orientation (bdice@umich,mspells@umich)
- Add Ellipsoids and vispy implementation (mspells@umich)
- Add Ellipsoids povray, fresenel, and pythreejs implementations (bdice@umich)
- Consolidate uses of plato.geometry.fibonacciPositions (mspells@umich)

## v1.4

- Make povray Mesh objects smooth (mspells@umich)
- Add pythreejs backend (mspells@umich)
- Fix vispy-specialized attributes in `Scene.copy()` (mspells@umich)
- Fix usage of outline attributes in fresnel backend for Spheres and Lines (mspells@umich)

## v1.3

- Add fresnel backend (bdice@umich)
- Replicated Mesh objects given positions/orientations (mootimot@umich)
- `Scene.convert()` method (mspells@umich)

## v1.2

- Support multiple directional lights in vispy (mspells@umich)
- Add double-sided Mesh helper function (mspells@umich)
- Experimental vispy normal-rendering mode (mspells@umich)
- Increased povray light intensity (mspells@umich)
- Fix vispy canvas kwargs (mootimot@umich)

## v1.1

- Add outlines to vispy Spheres (mspells@umich)
- Made povray backend able to save raw .pov files (mspells@umich)

## v1.0

- Reorganized entire project from being vispy focused (`plato.gl`) to having multiple backends (`plato.draw.*`) (mspells@umich)
- Port vispy backend (mspells@umich)
- Basic blender backend (mspells@umich)
- Basic matplotlib backend (mspells@umich)
- Basic povray backend (bdice@umich)

## v0.6

- Quantized light/cel-shading effects (mspells@umich)
- Voronoi primitive (mspells@umich)

## v0.5

- Additive rendering (mspells@umich)

## v0.4

- Fast Approximate Antialiasing (mspells@umich)
- Screen Space Ambient Occlusion (mspells@umich)

## v0.3

- Povray export (mspells@umich)

## v0.2

- ConvexSpheropolyhedra primitive (mspells@umich)
- ConvexPolyhedra primitive (mspells@umich)
- Polygons primitive (mspells@umich)
- Spheropolygons primitive (mspells@umich)
- Disks and Spheres primitives (mspells@umich)
- SpherePoints primitive (mspells@umich)
- Arrows2D primitive (jamesaan@umich)
- Lines primitive (askaras@umich)
- Meshes (erteich@umich)
- Smoothed meshes (jproc@umich)
- Order-independent transparency (bvansade@umich, vramasub@umich)
- SVG export (harperic@umich)
