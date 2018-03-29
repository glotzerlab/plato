(function() {
  let fetchJSON = function(filename) {
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
  };

  let scene, camera, renderer, controls;

  let makeColor = function(c) {
    return new THREE.Color(c[0], c[1], c[2]);
  };

  let makeVec3 = function(v) {
    return new THREE.Vector3(v[0], v[1], v[2]);
  };

  let makeFace3 = function(f) {
    return new THREE.Face3(f[0], f[1], f[2]);
  };

  let makeQuat = function(q) {
    // Converts from (w, x, y, z) to (x, y, z, w) order.
    return new THREE.Quaternion(q[1], q[2], q[3], q[0]);
  };

  let makeFloatArray = function(arr) {
    // Reduces multidimensional array into a 1D array for BufferGeometry
    return new Float32Array(arr.reduce((x,y) => [...x, ...y]));
  };

  let drawScene = function(jsonscene) {
    scene = new THREE.Scene();
    scene.background = makeColor([1, 1, 1]);
    scene.add(new THREE.AmbientLight( 0x404040 )); // soft white light
    scene.add(new THREE.HemisphereLight( 0xa0a0a0, 0x080808, 0.3 ));
    scene.add(new THREE.DirectionalLight( 0xffffff, 0.5 ));

    camera = new THREE.PerspectiveCamera( 60, window.innerWidth/window.innerHeight, 0.1, 1000 );
    camera.position.z = 10;

    controls = new THREE.TrackballControls( camera );
    controls.rotateSpeed = 2.0;
    controls.zoomSpeed = 1.2;
    controls.panSpeed = 1.5;
    controls.noZoom = false;
    controls.noPan = false;
    controls.staticMoving = true;
    controls.dynamicDampingFactor = 0.3;
    controls.keys = [ 65, 83, 68 ];
    controls.addEventListener( 'change', render );

    renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );

    for (let prim of jsonscene.primitives) {
      let pa = prim.attributes;
      console.debug("Creating " + prim.class + "...");
      if (prim.class == 'Spheres') {
        //let positions = makeFloatArray(pa.positions);
        //let colors = makeFloatArray(pa.colors);
        //let radii = makeFloatArray(pa.radii);
        //let geometry = new THREE.SphereBufferGeometry(radii[0]);
        for (let [position, color, radius] of pa.positions.map(
              (e, i) => [e, pa.colors[i], pa.radii[i]] )) {
          let geometry = new THREE.SphereGeometry(radius);
          let material = new THREE.MeshPhongMaterial({color: makeColor(color)});
          let shape = new THREE.Mesh(geometry, material);
          shape.position.x = position[0];
          shape.position.y = position[1];
          shape.position.z = position[2];
          scene.add(shape);
        }
      } else if (prim.class == 'Lines') {
        for (let [start, end, color, width] of pa.start_points.map(
              (e, i) => [e, pa.end_points[i], pa.colors[i], pa.widths[i]] )) {
          let geometry = new THREE.Geometry();
          geometry.vertices.push(makeVec3(start));
          geometry.vertices.push(makeVec3(end));
          let material = new THREE.LineBasicMaterial({color: makeColor(color)});
          let shape = new THREE.Line(geometry, material);
          scene.add(shape);
        }
      } else if (prim.class == 'Mesh') {
        let geometry = new THREE.Geometry();
        for (let v of pa.vertices.map((e) => makeVec3(e))) {
          geometry.vertices.push(v);
        }
        for (let f of pa.indices.map((e) => makeFace3(e))) {
          geometry.faces.push(f);
        }
        for (let color of pa.colors) {
          let material = new THREE.MeshPhongMaterial({color: makeColor(color)});
          let shape = new THREE.Mesh(geometry, material);
          scene.add(shape);
        }

      } else if (prim.class == 'ConvexPolyhedra') {
        vertices = pa.vertices.map((e) => makeVec3(e));
        let geometry = new THREE.ConvexGeometry(vertices);
        for (let [position, orientation, color] of pa.positions.map(
              (e, i) => [e, pa.orientations[i], pa.colors[i]] )) {
          let material = new THREE.MeshPhongMaterial({color: makeColor(color)});
          let shape = new THREE.Mesh(geometry, material);
          shape.position.x = position[0];
          shape.position.y = position[1];
          shape.position.z = position[2];
          // TODO: Orientations are wrong
          shape.applyQuaternion(makeQuat(orientation));
          scene.add(shape);
        }
      } else if (prim.class == 'ConvexSpheropolyhedra') {
        // TODO: This doesn't render spheroshapes yet, just ConvexPolyhedra
        radius = pa.radius;
        vertices = pa.vertices.map((e) => makeVec3(e));
        let geometry = new THREE.ConvexGeometry(vertices);
        for (let [position, orientation, color] of pa.positions.map(
              (e, i) => [e, pa.orientations[i], pa.colors[i]] )) {
          let material = new THREE.MeshPhongMaterial({color: makeColor(color)});
          let shape = new THREE.Mesh(geometry, material);
          shape.position.x = position[0];
          shape.position.y = position[1];
          shape.position.z = position[2];
          // TODO: Orientations are wrong
          shape.applyQuaternion(makeQuat(orientation));
          scene.add(shape);
        }
     } else {
        console.error("Primitive " + prim.class + " is not supported.");
        console.log(prim);
      }
    }

    window.addEventListener( 'resize', onWindowResize, false );
    render();
  };

  let onWindowResize = function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
    controls.handleResize();
    render();
  };

  let animate = function () {
    requestAnimationFrame( animate );
    controls.update();
  };

  let render = function() {
    renderer.render( scene, camera );
  };

  fetchJSON('1.json');
})();
