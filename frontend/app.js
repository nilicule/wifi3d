import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160/examples/jsm/controls/OrbitControls.js';

// ── Three.js scene setup ─────────────────────────────────────────────────────

const container = document.getElementById('canvas-container');
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111827);

const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 2000);
camera.position.set(80, -80, 100);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.enablePan = true;
controls.enableZoom = true;

// Lighting: ambient + key + fill
scene.add(new THREE.AmbientLight(0xffffff, 0.4));
const key = new THREE.DirectionalLight(0xffffff, 1.2);
key.position.set(60, 80, 100);
scene.add(key);
const fill = new THREE.DirectionalLight(0x8ecae6, 0.5);
fill.position.set(-60, -40, 60);
scene.add(fill);

// Grid floor
const grid = new THREE.GridHelper(200, 20, 0x1f2937, 0x1f2937);
grid.position.y = -2;
scene.add(grid);

// Resize handler
function resize() {
  const w = container.clientWidth, h = container.clientHeight;
  renderer.setSize(w, h);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(container);
resize();

// Animation loop
(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();

// ── Drag hint ────────────────────────────────────────────────────────────────

let hinted = false;
controls.addEventListener('start', () => {
  if (!hinted) {
    document.getElementById('drag-hint').style.opacity = '0';
    hinted = true;
  }
});

// ── State ────────────────────────────────────────────────────────────────────

const state = {
  ssid: '',
  password: '',
  auth_type: 'WPA',
  hidden: false,
  qr_size_mm: 60,
  base_color_hex: '#ffffff',
  module_color_hex: '#1a1a1a',
  header_text: '',
  sub_label: '',
  wifi_icon: true,
  desk_stand_tab: false,
};

// ── Color swatches ────────────────────────────────────────────────────────────

const BASE_COLORS = ['#ffffff', '#f5f5dc', '#1a1a2e', '#2d3748', '#7f1d1d'];
const MOD_COLORS  = ['#1a1a1a', '#10b981', '#3b82f6', '#ef4444', '#f59e0b'];

function makeSwatch(color, swatchContainer, key) {
  const btn = document.createElement('button');
  btn.style.background = color;
  btn.className = 'w-7 h-7 rounded-md border-2 transition-all';
  btn.style.borderColor = state[key] === color ? '#10b981' : 'transparent';
  btn.onclick = () => {
    state[key] = color;
    updateColorPreview();
    swatchContainer.querySelectorAll('button').forEach(b => { b.style.borderColor = 'transparent'; });
    btn.style.borderColor = '#10b981';
    schedulePreview();
  };
  swatchContainer.appendChild(btn);
}

function updateColorPreview() {
  const el = document.getElementById('color-preview');
  const dot = document.getElementById('color-preview-dot');
  el.style.background = state.base_color_hex;
  dot.style.background = state.module_color_hex;
}

const baseContainer = document.getElementById('base-swatches');
const modContainer  = document.getElementById('mod-swatches');
BASE_COLORS.forEach(c => makeSwatch(c, baseContainer, 'base_color_hex'));
MOD_COLORS.forEach(c  => makeSwatch(c, modContainer,  'module_color_hex'));
updateColorPreview();

// ── Accordion ─────────────────────────────────────────────────────────────────

document.querySelectorAll('.accordion-btn').forEach(btn => {
  const targetId = btn.dataset.target;
  const body = document.getElementById(targetId);
  const chevron = btn.querySelector('.accordion-chevron');
  body.classList.add('open');
  chevron.style.transform = 'rotate(180deg)';
  btn.addEventListener('click', () => {
    const open = body.classList.toggle('open');
    chevron.style.transform = open ? 'rotate(180deg)' : 'rotate(0deg)';
  });
});

// ── Form bindings ─────────────────────────────────────────────────────────────

function bind(id, key, transform = v => v) {
  const el = document.getElementById(id);
  if (!el) return;
  el.addEventListener('input', () => {
    state[key] = transform(el.value);
    schedulePreview();
    updateExportButtons();
  });
}

bind('ssid', 'ssid');
bind('password', 'password');
bind('header-text', 'header_text', v => v.toUpperCase().replace(/[^A-Z0-9 ]/g, ''));
bind('sub-label', 'sub_label', v => v.toUpperCase().replace(/[^A-Z0-9 ]/g, ''));

document.getElementById('open-network').addEventListener('change', e => {
  const open = e.target.checked;
  document.getElementById('password-row').style.display = open ? 'none' : '';
  state.auth_type = open ? 'nopass' : 'WPA';
  if (open) state.password = '';
  schedulePreview();
  updateExportButtons();
});

document.getElementById('hidden-network').addEventListener('change', e => {
  state.hidden = e.target.checked;
  schedulePreview();
});

document.getElementById('wifi-icon').addEventListener('change', e => {
  state.wifi_icon = e.target.checked;
  schedulePreview();
});

document.getElementById('desk-stand').addEventListener('change', e => {
  state.desk_stand_tab = e.target.checked;
  schedulePreview();
});

// Password show/hide
document.getElementById('pw-toggle').addEventListener('click', () => {
  const pw = document.getElementById('password');
  pw.type = pw.type === 'password' ? 'text' : 'password';
});

// Password strength meter
document.getElementById('password').addEventListener('input', e => {
  const v = e.target.value;
  const strength = Math.min(4, Math.floor(v.length / 4) + (v.length > 0 ? 1 : 0));
  const colors = ['', '#ef4444', '#f59e0b', '#84cc16', '#10b981'];
  for (let i = 1; i <= 4; i++) {
    document.getElementById(`str-${i}`).style.background =
      i <= strength ? colors[Math.min(strength, 4)] : '#374151';
  }
});

// Size presets
document.querySelectorAll('.size-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.size-btn').forEach(b =>
      b.className = b.className.replace(/border-accent bg-accent\/10 text-accent/g, 'border-gray-700')
    );
    btn.className = btn.className.replace('border-gray-700', 'border-accent bg-accent/10 text-accent');
    state.qr_size_mm = parseInt(btn.dataset.size);
    schedulePreview();
  });
});

document.getElementById('custom-size').addEventListener('input', e => {
  const v = parseInt(e.target.value);
  if (v >= 30 && v <= 150) {
    state.qr_size_mm = v;
    document.querySelectorAll('.size-btn').forEach(b =>
      b.className = b.className.replace(/border-accent bg-accent\/10 text-accent/g, 'border-gray-700')
    );
    schedulePreview();
  }
});

// ── Preview engine ────────────────────────────────────────────────────────────

let previewMeshGroup = null;
let debounceTimer = null;
const emptyState = document.getElementById('empty-state');

function schedulePreview() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(fetchPreview, 300);
}

async function fetchPreview() {
  if (!state.ssid.trim()) {
    clearPreview();
    emptyState.style.display = '';
    return;
  }
  emptyState.style.display = 'none';

  try {
    const res = await fetch('/api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state),
    });
    if (!res.ok) return;
    const data = await res.json();
    renderPreview(data);
  } catch (e) {
    console.error('Preview fetch failed', e);
  }
}

function clearPreview() {
  if (previewMeshGroup) {
    scene.remove(previewMeshGroup);
    previewMeshGroup = null;
  }
  emptyState.style.display = '';
}

function buildBufferGeometry(vertices, faces) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geo.setIndex(faces);
  geo.computeVertexNormals();
  return geo;
}

function renderPreview(data) {
  if (previewMeshGroup) scene.remove(previewMeshGroup);
  previewMeshGroup = new THREE.Group();

  const plateMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(data.plate_color),
    roughness: 0.6,
    metalness: 0.05,
  });
  const modMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(data.module_color),
    roughness: 0.5,
    metalness: 0.05,
  });

  if (data.plate_vertices.length > 0) {
    const plateGeo = buildBufferGeometry(data.plate_vertices, data.plate_faces);
    previewMeshGroup.add(new THREE.Mesh(plateGeo, plateMat));
  }
  if (data.module_vertices.length > 0) {
    const modGeo = buildBufferGeometry(data.module_vertices, data.module_faces);
    previewMeshGroup.add(new THREE.Mesh(modGeo, modMat));
  }

  // Center the group
  const box = new THREE.Box3().setFromObject(previewMeshGroup);
  const center = box.getCenter(new THREE.Vector3());
  previewMeshGroup.position.sub(center);
  scene.add(previewMeshGroup);

  // Auto-frame camera
  const size = box.getSize(new THREE.Vector3()).length();
  const dist = size * 1.4;
  camera.position.set(dist * 0.7, -dist * 0.7, dist * 0.8);
  controls.target.set(0, 0, 0);
  controls.update();
}

// ── Export buttons ────────────────────────────────────────────────────────────

function updateExportButtons() {
  const valid = state.ssid.trim().length > 0 &&
    (state.auth_type === 'nopass' || state.password.length > 0);
  ['btn-stl', 'btn-3mf'].forEach(id => {
    const btn = document.getElementById(id);
    btn.disabled = !valid;
    if (valid) {
      btn.classList.remove('opacity-40', 'cursor-not-allowed');
    } else {
      btn.classList.add('opacity-40', 'cursor-not-allowed');
    }
  });
}

async function doExport(format) {
  const res = await fetch('/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...state, format }),
  });
  if (!res.ok) return;
  const blob = await res.blob();
  const slug = state.ssid.replace(/[^a-zA-Z0-9]/g, '-').slice(0, 20);
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `wifi3d-${slug}.${format}`;
  a.click();
  URL.revokeObjectURL(a.href);
}

document.getElementById('btn-stl').addEventListener('click', () => doExport('stl'));
document.getElementById('btn-3mf').addEventListener('click', () => doExport('3mf'));

document.getElementById('btn-reset').addEventListener('click', () => {
  document.getElementById('ssid').value = '';
  document.getElementById('password').value = '';
  document.getElementById('header-text').value = '';
  document.getElementById('sub-label').value = '';
  Object.assign(state, {
    ssid: '', password: '', auth_type: 'WPA', hidden: false,
    qr_size_mm: 60, base_color_hex: '#ffffff', module_color_hex: '#1a1a1a',
    header_text: '', sub_label: '', wifi_icon: true, desk_stand_tab: false,
  });
  clearPreview();
  updateExportButtons();
});

// Init
updateExportButtons();
