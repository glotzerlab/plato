function fetchJSON(filename) {
  httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = function() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        jsondata = JSON.parse(httpRequest.responseText);
        console.log(jsondata);
        drawScene(jsondata);
        animate();
      } else {
        alert('There was a problem with the request.');
      }
    }
  };
  httpRequest.open('GET', filename, true);
  httpRequest.send();
}

let scene, sceneSize, camera, renderer, controls;

function makeColor(c) {
  return new THREE.Color(c[0], c[1], c[2]);
}

function makeVec3(v) {
  return new THREE.Vector3(v[0], v[1], v[2]);
}

function makeFace3(f) {
  return new THREE.Face3(f[0], f[1], f[2]);
}

function makeQuat(q) {
  // Converts from (w, x, y, z) to (x, y, z, w) order.
  return new THREE.Quaternion(q[1], q[2], q[3], q[0]);
}

function flattenArray(arr) {
  // Reduces 2D array into a 1D array
  return arr.reduce((acc,val) => acc.concat(val), []);
}

function makeFloatArray(arr) {
  return new Float32Array(flattenArray(arr));
}

function makeBufferAttribute(arr, width=3) {
  return new THREE.Float32BufferAttribute(flattenArray(arr), width);
}

function drawScene(jsonscene) {
  scene = new THREE.Scene();
  scene.background = makeColor([1, 1, 1]);

  // Lights...
  let ambientLightValue = 0.25;
  if (jsonscene.features && jsonscene.features.ambient_light &&
      jsonscene.features.ambient_light.value) {
    ambientLightValue = jsonscene.features.ambient_light.value;
  }
  let ambientLight = new THREE.AmbientLight(0xffffff, ambientLightValue);
  scene.add(ambientLight);
  let directionalLightVector = [0, 1, 0];
  if (jsonscene.features && jsonscene.features.directional_light &&
      jsonscene.features.directional_light.value) {
    directionalLightVector = jsonscene.features.directional_light.value;
  }
  directionalLightVector = makeVec3(directionalLightVector);
  let directionalLight = new THREE.DirectionalLight(
      0xffffff, directionalLightVector.length());
  directionalLight.position.set(directionalLightVector.x,
                                directionalLightVector.y,
                                directionalLightVector.z).negate().normalize();
  scene.add(directionalLight);

  // Camera...
  sceneSize = jsonscene.size;
  let sceneAspect = sceneSize[0] / sceneSize[1];
  let windowAspect = window.innerWidth / window.innerHeight;
  let cameraBounds = [0.5 * sceneSize[0] * Math.max(windowAspect / sceneAspect, 1),
                      0.5 * sceneSize[1] * Math.max(sceneAspect / windowAspect, 1)];

  camera = new THREE.OrthographicCamera(-cameraBounds[0], cameraBounds[0],
                                        cameraBounds[1], -cameraBounds[1],
                                        0, 1000);
  let cameraPosition = makeVec3(jsonscene.translation || [0, 0, -1]).negate();
  cameraPosition.applyQuaternion(makeQuat(
        jsonscene.rotation || [1, 0, 0, 0]).inverse());
  camera.position.set(cameraPosition.x, cameraPosition.y, cameraPosition.z);
  camera.zoom = jsonscene.zoom;
  camera.updateProjectionMatrix();

  // Controls...
  controls = new THREE.OrthographicTrackballControls( camera );
  controls.rotateSpeed = 2.0;
  controls.zoomSpeed = 1.2;
  controls.panSpeed = 1.5;
  controls.noZoom = false;
  controls.noPan = false;
  controls.staticMoving = true;
  controls.dynamicDampingFactor = 0.3;
  controls.keys = [ 65, 83, 68 ];
  controls.addEventListener( 'change', render );

  // Renderer...
  renderer = new THREE.WebGLRenderer();
  renderer.setSize( window.innerWidth, window.innerHeight );
  document.body.appendChild( renderer.domElement );

  // Primitives...
  for (const prim of jsonscene.primitives) {
    const pa = prim.attributes;
    console.debug("Creating " + prim.class + "...");

    if (prim.class == 'Spheres') {
      const geometry = new THREE.SphereBufferGeometry(1, 48, 24);
      for (const [position, color, radius] of pa.positions.map(
            (e, i) => [e, pa.colors[i], pa.radii[i]] )) {
        const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
        const shape = new THREE.Mesh(geometry, material);
        shape.position.set(position[0],
                           position[1],
                           position[2]);
        shape.scale.x = shape.scale.y = shape.scale.z = radius;
        scene.add(shape);
      }
    } else if (prim.class == 'Lines') {
      for (const [start, end, color, width] of pa.start_points.map(
            (e, i) => [e, pa.end_points[i], pa.colors[i], pa.widths[i]] )) {
        const geometry = new THREE.Geometry();
        geometry.vertices.push(makeVec3(start));
        geometry.vertices.push(makeVec3(end));
        const material = new THREE.LineBasicMaterial({color: makeColor(color)});
        const shape = new THREE.Line(geometry, material);
        scene.add(shape);
      }
    } else if (prim.class == 'Mesh') {
      const geometry = new THREE.BufferGeometry();
      geometry.setIndex(flattenArray(pa.indices));
      geometry.addAttribute('position', makeBufferAttribute(pa.vertices));
      for (const color of pa.colors) {
        const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
        const shape = new THREE.Mesh(geometry, material);
        scene.add(shape);
      }
    } else if (prim.class == 'ConvexPolyhedra') {
      vertices = pa.vertices.map((e) => makeVec3(e));
      const geometry = new THREE.ConvexBufferGeometry(vertices);
      for (const [position, orientation, color] of pa.positions.map(
            (e, i) => [e, pa.orientations[i], pa.colors[i]] )) {
        const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
        const shape = new THREE.Mesh(geometry, material);
        shape.position.set(position[0], position[1], position[2]);
        shape.applyQuaternion(makeQuat(orientation));
        scene.add(shape);
      }
    } else if (prim.class == 'ConvexSpheropolyhedra') {
      // TODO: This doesn't render spheroshapes yet, just ConvexPolyhedra
      radius = pa.radius;
      vertices = pa.vertices.map((e) => makeVec3(e));
      const geometry = new THREE.ConvexBufferGeometry(vertices);
      for (const [position, orientation, color] of pa.positions.map(
            (e, i) => [e, pa.orientations[i], pa.colors[i]] )) {
        const material = new THREE.MeshPhongMaterial({color: makeColor(color)});
        const shape = new THREE.Mesh(geometry, material);
        shape.position.set(position[0], position[1], position[2]);
        shape.applyQuaternion(makeQuat(orientation));
        scene.add(shape);
      }
   } else {
      console.error("Primitive " + prim.class + " is not supported.");
      console.log(prim);
    }
  }

  // Action!
  window.addEventListener( 'resize', onWindowResize, false );
  render();
}

function onWindowResize() {
  let sceneAspect = sceneSize[0] / sceneSize[1];
  let windowAspect = window.innerWidth / window.innerHeight;
  let cameraBounds = [0.5 * sceneSize[0] * Math.max(windowAspect / sceneAspect, 1),
                      0.5 * sceneSize[1] * Math.max(sceneAspect / windowAspect, 1)];
  camera.left = -cameraBounds[0];
  camera.right = cameraBounds[0];
  camera.top = cameraBounds[1];
  camera.bottom = -cameraBounds[1];
  camera.updateProjectionMatrix();
  renderer.setSize( window.innerWidth, window.innerHeight );
  controls.handleResize();
  render();
}

function animate() {
  requestAnimationFrame( animate );
  controls.update();
}

function render() {
  renderer.render( scene, camera );
}

fetchJSON('4.json');
