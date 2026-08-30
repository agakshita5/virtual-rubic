import * as THREE from 'three';

const COLORS = {
  R: 0xd6342c,   // RED
  L: 0xe8801a,   // ORANGE
  U: 0x2fae4f,   // GREEN
  D: 0x2f6fd0,   // BLUE
  F: 0xf4f4f4,   // WHITE
  B: 0xf2ce1b,   // YELLOW
};

const SPACING = 0.81;   // distance between cubelet centres
const BODY    = 0.8;   // size of the black plastic body
const STICKER = 0.8;   // size of the coloured tile sitting on it

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x15171c);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(0,0,9);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
document.body.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 1)); 
const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
keyLight.position.set(5, 8, 6);
scene.add(keyLight);
// optional
const fillLight = new THREE.DirectionalLight(0xffffff, 0.7);
fillLight.position.set(-6, -3, -5);
scene.add(fillLight);

// cubeGroup holds all 27 cubelets. Rotating cubeGroup orients the whole cube on screen.
const cubeGroup = new THREE.Group();
scene.add(cubeGroup);

const STICKER_ROTATION = {
  F: [0, 0, 0],
  B: [0, Math.PI, 0],
  R: [0, Math.PI / 2, 0],
  L: [0, -Math.PI / 2, 0],
  U: [-Math.PI / 2, 0, 0],
  D: [Math.PI / 2, 0, 0],
};

const FACE_NORMALS = {
  R: [1, 0, 0], L: [-1, 0, 0],
  U: [0, 1, 0], D: [0, -1, 0],
  F: [0, 0, 1], B: [0, 0, -1],
};

const bodyGeometry    = new THREE.BoxGeometry(BODY, BODY, BODY);
const bodyMaterial    = new THREE.MeshStandardMaterial();
const stickerGeometry = new THREE.PlaneGeometry(STICKER, STICKER);

function createCubelet(gx, gy, gz) {
  const cubelet = new THREE.Group();
  cubelet.add(new THREE.Mesh(bodyGeometry, bodyMaterial));

  // a sticker exists only on faces that actually point out of the cube
  const outward = {
    R: gx === 2, L: gx === 0,
    U: gy === 2, D: gy === 0,
    F: gz === 2, B: gz === 0,
  };

  for (const face of Object.keys(outward)) {
    if (!outward[face]) continue;

    const sticker = new THREE.Mesh(
      stickerGeometry,
      new THREE.MeshStandardMaterial({ color: COLORS[face] })
    );
    const n = FACE_NORMALS[face];
    const out = BODY / 2 + 0.002;
    sticker.position.set(n[0] * out, n[1] * out, n[2] * out);
    sticker.rotation.set(...STICKER_ROTATION[face]);

    sticker.userData.face = face;
    cubelet.add(sticker);
  }

  cubelet.position.set((gx - 1) * SPACING, (gy - 1) * SPACING, (gz - 1) * SPACING);
  cubelet.userData.grid = { x: gx, y: gy, z: gz };
  return cubelet;
}

for (let gx = 0; gx < 3; gx++) {
  for (let gy = 0; gy < 3; gy++) {
    for (let gz = 0; gz < 3; gz++) {
      cubeGroup.add(createCubelet(gx, gy, gz));
    }
  }
}

// start slightly tilted so three faces are visible right away
cubeGroup.rotation.set(-0.30, -0.55, 0);

// drag the mouse and the whole cube spins to follow
const DRAG_SPEED = 0.008;   // radians per pixel

function onDrag(dx, dy) {
  // rotate around y-axis for horizontal dragging (dx)
  const qX = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), dx * DRAG_SPEED); // angle is (displacement * speed);
  
  // rotate around x-axis for vertical dragging (dy)
  const qY = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), dy * DRAG_SPEED);

  cubeGroup.quaternion.premultiply(qX);
  cubeGroup.quaternion.premultiply(qY);
}

const COLOR_BY_NAME = {
  WHITE: 0xf4f4f4, YELLOW: 0xf2ce1b, ORANGE: 0xe8801a,
  RED:   0xd6342c, GREEN:  0x2fae4f, BLUE:   0x2f6fd0,
};

const FACELET_INDEX = {
  U: (g) => [g.z, g.x],
  D: (g) => [2-g.z, g.x],
  F: (g) => [2-g.y, g.x],
  B: (g) => [2-g.y, 2-g.x],
  R: (g) => [2-g.y, 2-g.z],
  L: (g) => [2-g.y, g.z],
};

function applyFacelets(facelets) {
  for (const cubelet of cubeGroup.children) {
    const g = cubelet.userData.grid;
    if (!g) continue;

    cubelet.position.set((g.x - 1) * SPACING, (g.y - 1) * SPACING, (g.z - 1) * SPACING);
    cubelet.quaternion.identity();

    for (const child of cubelet.children) {
      const face = child.userData.face;
      if (!face) continue;  
      const [row, col] = FACELET_INDEX[face](g);
      child.material.color.setHex(COLOR_BY_NAME[facelets[face][row][col]]);
    }
  }
}

// Which cubelets move, about which axis, and which way.
// A face turn is clockwise seen from OUTSIDE that face.
// A positive rotation about an axis (right-hand rule) looks ANTIclockwise from the + end of that
// axis — so the far layers (R, U, F) take a negative angle, the near layers
// (L, D, B) a positive one.
const TURN = {
  R: { axis: 'x', layer: 2, sign: -1 },
  L: { axis: 'x', layer: 0, sign: +1 },
  U: { axis: 'y', layer: 2, sign: -1 },
  D: { axis: 'y', layer: 0, sign: +1 },
  F: { axis: 'z', layer: 2, sign: -1 },
  B: { axis: 'z', layer: 0, sign: +1 },
};

const TURN_SECONDS = 0.22;   // how long one quarter turn takes

let activeTurn = null;

function beginTurn(move) { // U or U'
  const face   = move[0];
  const suffix = move.slice(1);
  const { axis, layer, sign } = TURN[face];

  const pivot = new THREE.Group();
  cubeGroup.add(pivot);
  // added pivot to cubeGroup and not scene as it adapts the tilt of cube or else the layer would rotate in world axes and visually shear away from the tilted cube

  for (const cubelet of [...cubeGroup.children]){ 
    const g = cubelet.userData.grid;
    if (!g) continue;

    if(cubelet.userData.grid[axis] == layer) pivot.attach(cubelet); 
  }

  const direction = suffix === "'" ? -1 : 1;
  activeTurn = { pivot, axis, target: direction * sign * (Math.PI / 2), progress: 0, seconds: TURN_SECONDS };
}

function advanceTurn(dt) {
  if (!activeTurn) return;
  
  // dt / seconds is the slice of the total duration this frame covers
  activeTurn.progress += dt / activeTurn.seconds; // [0,1]

  if (activeTurn.progress >= 1) {
    activeTurn.pivot.rotation[activeTurn.axis] = activeTurn.target;
    finishTurn();
    return;
  }
  const eased = 1 - Math.pow(1 - activeTurn.progress, 3);
  activeTurn.pivot.rotation[activeTurn.axis] = activeTurn.target * eased;
}

function finishTurn() {
  const pivot = activeTurn.pivot;

  for (const cubelet of [...pivot.children]) cubeGroup.attach(cubelet);
  cubeGroup.remove(pivot);
  activeTurn = null;

  if (pendingFacelets) {
    applyFacelets(pendingFacelets);
    pendingFacelets = null;
  }
}

const hintEl = document.getElementById('hint');
const hint = (text) => { hintEl.textContent = text; };

let socket = null;
let pendingFacelets = null;

function connect() {
  socket = new WebSocket('ws://localhost:8765');

  socket.onopen = () => hint('U D L R F B  ·  shift = reverse  ·  S scramble  ·  0 reset');
  socket.onclose = () => {
    hint('server offline — run server.py, retrying...');
    setTimeout(connect, 1500);
  };
  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    // if a turn is mid-flight, hold the new colours until it lands
    if (activeTurn) pendingFacelets = message.facelets;
    else applyFacelets(message.facelets);

    if (message.solved) hint('solved');
  };
}
connect();

function send(payload) {
  if (socket && socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify(payload));
}

addEventListener('keydown', (e) => {
  if (activeTurn) return; // one turn at a time
  const key = e.key.toUpperCase();

  if (key === 'S'){ 
    send({action: 'scramble'}); 
    return; 
  }
  if (key === '0'){ 
    send({action: 'reset' });     
    return; 
  }
  if (!TURN[key])  return;

  const move = e.shiftKey ? key + "'" : key; 
  send({ action: 'move', move });
  beginTurn(move);
});

let dragging = false;
let lastX = 0, lastY = 0;

renderer.domElement.addEventListener('pointerdown', (e) => {
  dragging = true;
  lastX = e.clientX;
  lastY = e.clientY;
});

addEventListener('pointerup', () => { dragging = false; });

addEventListener('pointermove', (e) => {
  if (!dragging) return;
  onDrag(e.clientX - lastX, e.clientY - lastY);
  lastX = e.clientX;
  lastY = e.clientY;
});

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  advanceTurn(clock.getDelta());
  renderer.render(scene, camera);
}
animate();
