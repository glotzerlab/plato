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

function makeVec2(v) {
  return new THREE.Vector2(v[0], v[1]);
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
  let ambientLightValue = 1;
  if (jsonscene.features && jsonscene.features.ambient_light &&
      jsonscene.features.ambient_light.value) {
    ambientLightValue = jsonscene.features.ambient_light.value;
  }
  scene.add(new THREE.AmbientLight(0xffffff, ambientLightValue));

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
  let cameraQuat = jsonscene.rotation || [1, 0, 0, 0];
  cameraQuat = makeQuat(cameraQuat).inverse().normalize();
  cameraPosition.applyQuaternion(cameraQuat);
  camera.position.set(cameraPosition.x, cameraPosition.y, cameraPosition.z);
  camera.zoom = jsonscene.zoom;
  camera.updateProjectionMatrix();

  // Controls...
  let pan_mode = false;
  if (jsonscene.features && jsonscene.features.pan &&
      jsonscene.features.pan.value) {
    pan_mode = jsonscene.features.pan.value;
  }

  controls = new THREE.OrthographicTrackballControls( camera, pan_mode );
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
  prim_render = new PrimitiveRenderer(scene);
  jsonscene.primitives.map((prim) => {
    if (prim.class && prim_render[prim.class]) {
      prim_render[prim.class](prim.attributes);
    } else {
      console.error("Primitive " + prim.class + " is not supported.");
      console.log(prim);
    }
  });

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
