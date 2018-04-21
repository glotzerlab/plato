function PrimitiveRenderer(scene) {
  this.scene = scene;

  this.Spheres = function(attributes) {
    const geometry = new THREE.SphereBufferGeometry(1, 48, 24);
    for (const [position, color, radius] of attributes.positions.map(
          (e, i) => [e, attributes.colors[i], attributes.radii[i]] )) {
      const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], position[2]);
      shape.scale.x = shape.scale.y = shape.scale.z = radius;
      this.scene.add(shape);
    }
  }

  this.Lines = function(attributes) {
    for (const [start, end, color, width] of attributes.start_points.map(
          (e, i) => [e, attributes.end_points[i], attributes.colors[i], attributes.widths[i]] )) {
      const geometry = new THREE.Geometry();
      geometry.vertices.push(makeVec3(start));
      geometry.vertices.push(makeVec3(end));
      const material = new THREE.LineBasicMaterial({color: makeColor(color)});
      const shape = new THREE.Line(geometry, material);
      this.scene.add(shape);
    }
  }

  this.Mesh = function(attributes) {
    const geometry = new THREE.BufferGeometry();
    geometry.setIndex(flattenArray(attributes.indices));
    geometry.addAttribute('position', makeBufferAttribute(attributes.vertices));
    for (const color of attributes.colors) {
      const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
      const shape = new THREE.Mesh(geometry, material);
      this.scene.add(shape);
    }
  }

  this.ConvexPolyhedra = function(attributes) {
    vertices = attributes.vertices.map((e) => makeVec3(e));
    const geometry = new THREE.ConvexBufferGeometry(vertices);
    for (const [position, orientation, color] of attributes.positions.map(
          (e, i) => [e, attributes.orientations[i], attributes.colors[i]] )) {
      const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], position[2]);
      shape.applyQuaternion(makeQuat(orientation).normalize());
      this.scene.add(shape);
    }
  }

  this.ConvexSpheropolyhedra = function(attributes) {
    // TODO: This doesn't render spheroshapes yet, just ConvexPolyhedra
    radius = attributes.radius;
    vertices = attributes.vertices.map((e) => makeVec3(e));
    const geometry = new THREE.ConvexBufferGeometry(vertices);
    for (const [position, orientation, color] of attributes.positions.map(
          (e, i) => [e, attributes.orientations[i], attributes.colors[i]] )) {
      const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], position[2]);
      shape.applyQuaternion(makeQuat(orientation).normalize());
      this.scene.add(shape);
    }
  }

  this.Disks = function(attributes) {
    const geometry = new THREE.CircleBufferGeometry(1, 48);
    for (const [position, color, radius] of attributes.positions.map(
          (e, i) => [e, attributes.colors[i], attributes.radii[i]] )) {
      const material = new THREE.MeshPhongMaterial({
        color: makeColor(color), side: THREE.DoubleSide});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], 0);
      shape.scale.x = shape.scale.y = radius;
      this.scene.add(shape);
    }
  }

  this.Arrows2D = function(attributes) {
    const polyshape = new THREE.Shape();
    polyshape.moveTo(attributes.vertices[0][0], attributes.vertices[0][1]);
    attributes.vertices.map(v => polyshape.lineTo(v[0], v[1]));
    polyshape.lineTo(attributes.vertices[0][0], attributes.vertices[0][1]);
    const geometry = new THREE.ShapeBufferGeometry(polyshape);
    for (const [position, orientation, color, magnitude] of attributes.positions.map(
          (e, i) => [e, attributes.orientations[i], attributes.colors[i], attributes.magnitudes[i]] )) {
      const material = new THREE.MeshPhongMaterial({
        color: makeColor(color), side: THREE.DoubleSide});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], 0);
      shape.applyQuaternion(makeQuat(orientation).normalize());
      shape.scale.x = shape.scale.y = magnitude;
      this.scene.add(shape);
    }
  }

  this.Polygons = function(attributes) {
    const polyshape = new THREE.Shape();
    polyshape.moveTo(attributes.vertices[0][0], attributes.vertices[0][1]);
    attributes.vertices.map(v => polyshape.lineTo(v[0], v[1]));
    polyshape.lineTo(attributes.vertices[0][0], attributes.vertices[0][1]);
    const geometry = new THREE.ShapeBufferGeometry(polyshape);
    for (const [position, orientation, color] of attributes.positions.map(
          (e, i) => [e, attributes.orientations[i], attributes.colors[i]] )) {
      const material = new THREE.MeshPhongMaterial({
        color: makeColor(color), side: THREE.DoubleSide});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], 0);
      shape.applyQuaternion(makeQuat(orientation).normalize());
      this.scene.add(shape);
    }
  }

  this.Spheropolygons = function(attributes) {
    function edgeExpand(r, v0, v1) {
      return new THREE.Vector2().subVectors(v1, v0)
        .normalize().rotateAround(new THREE.Vector2(0, 0), -Math.PI/2)
        .multiplyScalar(r);
    }

    function pathLineArc(s, r, v0, v1, v2) {
      v0 = makeVec2(v0);
      v1 = makeVec2(v1);
      v2 = makeVec2(v2);
      const expand01 = edgeExpand(r, v0, v1);
      const expand12 = edgeExpand(r, v1, v2);
      const vexp0 = new THREE.Vector2().addVectors(v0, expand01);
      const vexp1 = new THREE.Vector2().addVectors(v1, expand01);
      s.moveTo(vexp0.x, vexp0.y);
      s.lineTo(vexp1.x, vexp1.y);
      s.absarc(v1.x, v1.y, r, expand01.angle(), expand12.angle());
    }

    let spheropolyshape = new THREE.Shape();
    let nverts = attributes.vertices.length;
    attributes.vertices.map((v, i) => pathLineArc(
          spheropolyshape, attributes.radius, attributes.vertices[i % nverts],
          attributes.vertices[(i+1) % nverts], attributes.vertices[(i+2) % nverts]));
    const geometry = new THREE.ShapeBufferGeometry(spheropolyshape);
    for (const [position, orientation, color] of attributes.positions.map(
          (e, i) => [e, attributes.orientations[i], attributes.colors[i]] )) {
      const material = new THREE.MeshPhongMaterial({
        color: makeColor(color), side: THREE.DoubleSide});
      const shape = new THREE.Mesh(geometry, material);
      shape.position.set(position[0], position[1], 0);
      shape.applyQuaternion(makeQuat(orientation).normalize());
      this.scene.add(shape);
    }
  }
}
