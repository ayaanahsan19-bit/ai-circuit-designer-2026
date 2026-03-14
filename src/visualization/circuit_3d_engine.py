"""
Three.js WebGL PCB Renderer — EasyEDA / Altium-grade 3D board visualization.
Produces a self-contained HTML page that can be embedded in a Streamlit iframe.
"""
import json


class ThreeJSPCBRenderer:
    """Generates a complete HTML page with Three.js WebGL 3D PCB rendering."""

    @staticmethod
    def generate_html(components, design_data, project_name="Circuit"):
        """
        Return a self-contained HTML string (<!DOCTYPE html> …) that renders
        the given *components* list and *design_data* dict as an interactive
        3D PCB board using Three.js r128.
        """

        components_json = json.dumps(components, default=str)
        design_json = json.dumps(design_data, default=str)
        safe_project = str(project_name).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        net_count = len(design_data.get("nets", design_data.get("netlist", [])))
        comp_count = len(components)

        html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>''' + safe_project + r''' — 3D PCB</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{width:100%;height:100%;overflow:hidden;background:#0b0d12;font-family:'Consolas','Courier New',monospace}
  canvas{display:block;width:100%;height:100%}
  #overlay-tl{position:absolute;top:12px;left:14px;background:rgba(11,13,18,0.82);
    padding:10px 16px;border-radius:6px;border:1px solid #21262d;color:#58a6ff;font-size:12px;line-height:1.7;pointer-events:none;z-index:10}
  #overlay-br{position:absolute;bottom:10px;right:14px;color:#8b949e;font-size:11px;pointer-events:none;z-index:10}
</style>
</head>
<body>
<div id="overlay-tl">
  <strong>''' + safe_project + r'''</strong><br/>
  Components: ''' + str(comp_count) + r'''<br/>
  Nets: ''' + str(net_count) + r'''
</div>
<div id="overlay-br">Left-drag: orbit &nbsp;|&nbsp; Right-drag: pan &nbsp;|&nbsp; Scroll: zoom</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
"use strict";
// --- Data injected from Python ---
var COMPONENTS_JSON = ''' + components_json + r''';
var DESIGN_DATA_JSON = ''' + design_json + r''';

// --- Renderer ---
var renderer = new THREE.WebGLRenderer({antialias:true});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.4;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.setClearColor(0x0a0c10);
document.body.appendChild(renderer.domElement);
renderer.domElement.style.filter = 'contrast(1.05) saturate(1.1)';

// --- Scene & Camera (EasyEDA-style default angle) ---
var scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x0b0d12, 600, 1200);
var camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 2000);
// EasyEDA-style camera: 45° elevation, slight perspective, showing full board
camera.position.set(120, -100, 85);
camera.up.set(0, 0, 1);
camera.lookAt(new THREE.Vector3(40, 30, 8));

// --- Lighting (cinematic photorealistic studio) ---
(function(){
  // Key light — warm directional sun
  var key = new THREE.DirectionalLight(0xfff8e0, 2.8);
  key.position.set(120, -80, 150);
  key.castShadow = true;
  key.shadow.mapSize.set(4096, 4096);
  key.shadow.camera.left = -250; key.shadow.camera.right = 250;
  key.shadow.camera.top = 250;  key.shadow.camera.bottom = -250;
  key.shadow.camera.near = 1;   key.shadow.camera.far = 1000;
  key.shadow.bias = -0.0008;
  key.shadow.normalBias = 0.03;
  scene.add(key);

  // Cool fill light (sky reflection)
  var fill = new THREE.DirectionalLight(0x4488ff, 1.2);
  fill.position.set(-150, 100, 120);
  scene.add(fill);

  // Warm rim light (backlight for separation)
  var rim = new THREE.DirectionalLight(0xffaa44, 0.8);
  rim.position.set(50, 200, -80);
  scene.add(rim);

  // Soft ambient fill
  scene.add(new THREE.AmbientLight(0x1a2b3a, 3.5));

  // PCB green bounce light for realism
  scene.add(new THREE.HemisphereLight(0x0d2818, 0x0b0d12, 0.6));

  // Environment map for metallic reflections
  var pmremGenerator = new THREE.PMREMGenerator(renderer);
  var envTexture = pmremGenerator.fromScene(new THREE.Scene()).texture;
  scene.environment = envTexture;
})();

// --- Material factory ---
function MAT(color, roughness, metalness){
  return new THREE.MeshStandardMaterial({color:color, roughness:roughness, metalness:metalness});
}
function MATT(color, roughness, metalness, opacity){
  return new THREE.MeshStandardMaterial({color:color, roughness:roughness, metalness:metalness, transparent:true, opacity:opacity});
}
var M_PCB     = new THREE.MeshStandardMaterial({color:0x0d2818, roughness:0.65, metalness:0.04, envMapIntensity:0.6});
var M_COPPER  = MAT(0xb87333, 0.28, 0.92);
var M_TIN     = MAT(0xa8b8c0, 0.35, 0.75);
var M_CERAMIC = MAT(0xe8dcc0, 0.85, 0.0);
var M_EPOXY   = MAT(0x111111, 0.8,  0.0);
var M_GOLD    = MAT(0xffd700, 0.2,  1.0);
var M_GOLD_VIA = MAT(0xffd700, 0.15, 1.0);
var M_BLUECAP = MAT(0x0f1f3f, 0.75, 0.03);
var M_BLUECAP_TOP = MAT(0x1f2f4f, 0.65, 0.08);
var M_BLUECAP_VENT = MAT(0x1a2f3f, 0.7, 0.08);
var M_ALUM    = MAT(0xc8d0d8, 0.2, 0.92);
var M_MOSFET_BODY = MAT(0x111111, 0.75, 0.05);
var M_WHITE   = MAT(0xf0f0f0, 0.9,  0.0);
var M_SILK    = MAT(0xf8f8f0, 0.95, 0.0);
var M_GREY    = MAT(0x888888, 0.7,  0.1);
var M_DARK    = MAT(0x222222, 0.85, 0.0);
var M_FLOOD   = MATT(0x0d2818, 0.85, 0.25, 0.82);
var M_SMASK   = MATT(0x0b3818, 0.88, 0.08, 0.55);

// --- Helpers ---
function addMesh(geom, mat, x, y, z, rx, ry, rz){
  var m = new THREE.Mesh(geom, mat);
  m.position.set(x||0, y||0, z||0);
  if(rx) m.rotation.x = rx;
  if(ry) m.rotation.y = ry;
  if(rz) m.rotation.z = rz;
  m.castShadow = true;
  m.receiveShadow = true;
  scene.add(m);
  return m;
}

// --- Resistor color code ---
var BAND_COLORS = [
  0x000000, // 0 black
  0x8B4513, // 1 brown
  0xFF0000, // 2 red
  0xFF8C00, // 3 orange
  0xFFFF00, // 4 yellow
  0x008000, // 5 green
  0x0000FF, // 6 blue
  0x8B00FF, // 7 violet
  0x808080, // 8 gray
  0xFFFFFF  // 9 white
];

function parseResistorBands(valueStr){
  var s = (valueStr || "0").replace(/[^0-9.kKmM]/g, "");
  var num = 0;
  if(/[kK]/.test(s)) num = parseFloat(s) * 1000;
  else if(/[mM]/.test(s)) num = parseFloat(s) * 1e6;
  else num = parseFloat(s) || 0;
  num = Math.round(num);
  if(num <= 0) return [0,0,0,1];
  var str = num.toString();
  var d1 = parseInt(str[0]) || 0;
  var d2 = (str.length > 1) ? parseInt(str[1]) || 0 : 0;
  var mult = Math.max(0, str.length - 2);
  if(mult > 9) mult = 9;
  return [d1, d2, mult, 1];
}

// --- Ground shadow catcher ---
(function(){
  var shadowPlane = new THREE.Mesh(
    new THREE.PlaneGeometry(600, 600),
    new THREE.ShadowMaterial({opacity: 0.35})
  );
  shadowPlane.rotation.x = -Math.PI/2;
  shadowPlane.position.set(40, 30, -0.5);
  shadowPlane.receiveShadow = true;
  scene.add(shadowPlane);
})();

// --- PCB Board ---
var boardW = 80, boardD = 60;
(function(){
  addMesh(new THREE.BoxGeometry(boardW, boardD, 1.6), M_PCB, boardW/2, boardD/2, 0.8);

  // Solder mask layer on top of FR4
  var maskMat = new THREE.MeshStandardMaterial({color:0x0e4a28, roughness:0.95, metalness:0.0, transparent:true, opacity:0.55});
  var mask = new THREE.Mesh(new THREE.BoxGeometry(boardW, boardD, 0.06), maskMat);
  mask.position.set(boardW/2, boardD/2, 1.63);
  mask.receiveShadow = true;
  scene.add(mask);

  // Vias — only positions inside the board
  var viaPos = [[15,15],[35,25],[55,15],[60,45],[25,45]];
  for(var v = 0; v < viaPos.length; v++){
    var vx = viaPos[v][0], vy = viaPos[v][1];
    if(vx < 1 || vx > 79 || vy < 1 || vy > 59) continue;
    addMesh(new THREE.CylinderGeometry(0.4, 0.4, 1.8, 12), M_GOLD, vx, vy, 0.9, Math.PI/2, 0, 0);
    addMesh(new THREE.CylinderGeometry(0.7, 0.7, 0.15, 12), M_GOLD_VIA, vx, vy, 1.68, Math.PI/2, 0, 0);
  }

  // Copper ground plane flood fill with clearance gaps
  var groundPlane = new THREE.Mesh(
    new THREE.BoxGeometry(boardW - 4, boardD - 4, 0.038),
    M_COPPER
  );
  groundPlane.position.set(boardW/2, boardD/2, 1.68);
  groundPlane.receiveShadow = true;
  scene.add(groundPlane);

  // Board edge — thin dark green border
  var M_EDGE = MAT(0x0f4a28, 0.9, 0.0);
  addMesh(new THREE.BoxGeometry(boardW, 0.5, 1.6), M_EDGE, boardW/2, 0.25,  0.8);
  addMesh(new THREE.BoxGeometry(boardW, 0.5, 1.6), M_EDGE, boardW/2, boardD-0.25, 0.8);
  addMesh(new THREE.BoxGeometry(0.5, boardD, 1.6), M_EDGE, 0.25, boardD/2,  0.8);
  addMesh(new THREE.BoxGeometry(0.5, boardD, 1.6), M_EDGE, boardW-0.25, boardD/2, 0.8);
})();

// --- Component label sprite helper ---
function makeLabel(text, x, y, z){
  var canvas = document.createElement('canvas');
  canvas.width = 256; canvas.height = 80;
  var ctx = canvas.getContext('2d');
  ctx.fillStyle = 'rgba(11,13,18,0.82)';
  ctx.beginPath();
  ctx.roundRect(0, 0, 256, 80, 10);
  ctx.fill();
  ctx.strokeStyle = '#58a6ff';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(1, 1, 254, 78, 10);
  ctx.stroke();
  ctx.fillStyle = '#58a6ff';
  ctx.font = 'bold 22px Courier New';
  ctx.textAlign = 'center';
  ctx.fillText((text.split('|')[0] || ''), 128, 30);
  ctx.fillStyle = '#3fb950';
  ctx.font = '17px Courier New';
  ctx.fillText((text.split('|')[1] || ''), 128, 58);
  var texture = new THREE.CanvasTexture(canvas);
  var sprite = new THREE.Sprite(new THREE.SpriteMaterial({map: texture, transparent: true, depthTest: false}));
  sprite.scale.set(12, 4, 1);
  sprite.position.set(x, y, z + 14);
  scene.add(sprite);
}

// --- Silkscreen outline helper (professional white PCB silkscreen) ---
function addSilkscreen(cx, cy, w, d){
  var silkMat = new THREE.MeshStandardMaterial({color:0xf8f8f0, roughness:1.0, metalness:0.0});
  var thickness = 0.25;
  var hw = w/2 + 0.8;
  var hd = d/2 + 0.8;
  // Top edge
  var t1 = new THREE.Mesh(new THREE.BoxGeometry(hw*2, thickness, 0.02), silkMat);
  t1.position.set(cx, cy+hd, 1.70); scene.add(t1);
  // Bottom edge
  var t2 = new THREE.Mesh(new THREE.BoxGeometry(hw*2, thickness, 0.02), silkMat);
  t2.position.set(cx, cy-hd, 1.70); scene.add(t2);
  // Left edge
  var t3 = new THREE.Mesh(new THREE.BoxGeometry(thickness, hd*2, 0.02), silkMat);
  t3.position.set(cx-hw, cy, 1.70); scene.add(t3);
  // Right edge
  var t4 = new THREE.Mesh(new THREE.BoxGeometry(thickness, hd*2, 0.02), silkMat);
  t4.position.set(cx+hw, cy, 1.70); scene.add(t4);
}

// --- Board title and silkscreen text ---
function addBoardText(text, x, y, size){
  var canvas = document.createElement('canvas');
  canvas.width = 512; canvas.height = 128;
  var ctx = canvas.getContext('2d');
  ctx.fillStyle = '#f8f8f0';
  ctx.font = 'bold 48px Arial';
  ctx.textAlign = 'center';
  ctx.fillText(text, 256, 80);
  var texture = new THREE.CanvasTexture(canvas);
  var textMat = new THREE.MeshStandardMaterial({
    map: texture, 
    transparent: true, 
    alphaTest: 0.1,
    roughness: 1.0, 
    metalness: 0.0
  });
  var textMesh = new THREE.Mesh(new THREE.PlaneGeometry(size * 0.8, size * 0.2), textMat);
  textMesh.position.set(x, y, 1.71);
  textMesh.rotation.set(-Math.PI/2, 0, 0);
  scene.add(textMesh);
}

// --- Component builders ---
function buildResistor(x, y, z, valueStr){
  // Ceramic body with realistic dimensions
  addMesh(new THREE.BoxGeometry(3.2, 1.6, 1.0), M_CERAMIC, x, y, z + 0.5);
  
  // Silver metallic end caps with proper metallic appearance
  var silverMat = MAT(0xc0c0c0, 0.15, 0.95);
  addMesh(new THREE.BoxGeometry(0.5, 1.6, 1.1), silverMat, x - 1.35, y, z + 0.55);
  addMesh(new THREE.BoxGeometry(0.5, 1.6, 1.1), silverMat, x + 1.35, y, z + 0.55);

  // Color bands with better positioning and visibility
  var bands = parseResistorBands(valueStr);
  var bandXPositions = [-0.7, -0.3, 0.1, 0.7];
  for(var i = 0; i < 4; i++){
    var bmat = MAT(BAND_COLORS[bands[i]], 0.6, 0.0);
    addMesh(new THREE.BoxGeometry(0.22, 1.62, 1.05), bmat, x + bandXPositions[i], y, z + 0.525);
  }
  
  // Tin leads extending from caps
  addMesh(new THREE.CylinderGeometry(0.25, 0.25, 2.5, 8), M_TIN, x - 1.85, y, z - 1.25, Math.PI/2, 0, 0);
  addMesh(new THREE.CylinderGeometry(0.25, 0.25, 2.5, 8), M_TIN, x + 1.85, y, z - 1.25, Math.PI/2, 0, 0);
}

function buildCapacitor(x, y, z, valueStr){
  // Parse value to decide size
  var valNum = parseFloat((valueStr || '0').replace(/[^0-9.]/g, '')) || 0;
  var r, h;
  if(valNum >= 47) { r = 5.5; h = 11; } else { r = 3.0; h = 8; }
  
  // Main navy blue electrolytic body
  addMesh(new THREE.CylinderGeometry(r, r, h, 48), M_BLUECAP, x, y, z + h/2);
  
  // Top silver vent disc with realistic appearance
  var silverVent = MAT(0xb8c8d0, 0.2, 0.9);
  addMesh(new THREE.CylinderGeometry(r - 0.3, r - 0.3, 0.15, 48), silverVent, x, y, z + h + 0.075);
  
  // White polarity stripe (negative side) - thicker and more visible
  addMesh(new THREE.BoxGeometry(0.8, r * 2, h - 1), M_WHITE, x + r - 0.4, y, z + h/2);
  
  // Silver vent markings on top (cross pattern)
  addMesh(new THREE.BoxGeometry(r * 1.4, 0.25, 0.1), silverVent, x, y, z + h + 0.21);
  addMesh(new THREE.BoxGeometry(0.25, r * 1.4, 0.1), silverVent, x, y, z + h + 0.21);
  
  // Black rubber seal at base
  var rubberMat = MAT(0x1a1a1a, 0.9, 0.0);
  addMesh(new THREE.CylinderGeometry(r + 0.2, r + 0.2, 0.3, 24), rubberMat, x, y, z + 0.15);
  
  // Extended tin leads
  addMesh(new THREE.CylinderGeometry(0.3, 0.3, 3.5, 8), M_TIN, x - 1, y, z - 1.75, Math.PI/2, 0, 0);
  addMesh(new THREE.CylinderGeometry(0.3, 0.3, 3.5, 8), M_TIN, x + 1, y, z - 1.75, Math.PI/2, 0, 0);
}

function buildInductor(x, y, z){
  // Dark charcoal ferrite block (Bourns SRR1260 style)
  var ferriteMat = MAT(0x2a2a2a, 0.6, 0.05);
  addMesh(new THREE.BoxGeometry(12.6, 12.6, 6.5), ferriteMat, x, y, z + 3.25);
  
  // Top surface with subtle marking indentation
  addMesh(new THREE.BoxGeometry(10.0, 10.0, 0.1), MAT(0x1a1a1a, 0.8, 0.0), x, y, z + 6.55);
  
  // White part number marking on top
  addMesh(new THREE.BoxGeometry(6.0, 1.0, 0.05), M_WHITE, x, y + 2.0, z + 6.58);
  addMesh(new THREE.BoxGeometry(3.0, 1.0, 0.05), M_WHITE, x, y - 2.0, z + 6.58);
  
  // Metal end caps with realistic appearance
  var endCapMat = MAT(0xb0b8c0, 0.3, 0.85);
  addMesh(new THREE.BoxGeometry(12.8, 12.8, 0.3), endCapMat, x, y, z + 0.15);
  addMesh(new THREE.BoxGeometry(12.8, 12.8, 0.3), endCapMat, x, y, z + 6.35);
  
  // Tin leads with proper spacing
  addMesh(new THREE.BoxGeometry(1.2, 2.8, 0.2), M_TIN, x - 6.4, y, z + 0.05);
  addMesh(new THREE.BoxGeometry(1.2, 2.8, 0.2), M_TIN, x + 6.4, y, z + 0.05);
  
  // Extended lead wires
  addMesh(new THREE.CylinderGeometry(0.3, 0.3, 3.0, 8), M_TIN, x - 6.4, y, z - 1.5, Math.PI/2, 0, 0);
  addMesh(new THREE.CylinderGeometry(0.3, 0.3, 3.0, 8), M_TIN, x + 6.4, y, z - 1.5, Math.PI/2, 0, 0);
}

function buildMOSFET(x, y, z){
  var g = new THREE.Group();
  
  // Black plastic TO-220 body with proper proportions
  var body = new THREE.Mesh(new THREE.BoxGeometry(4.8, 4.2, 6.0), M_MOSFET_BODY);
  body.position.set(0, 0, 3.0);
  body.castShadow = true; body.receiveShadow = true;
  g.add(body);
  
  // Brushed aluminum heatsink tab - taller than body with proper metal finish
  var brushedAlum = MAT(0xd0d8e0, 0.15, 0.92);
  var tab = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.6, 12.0), brushedAlum);
  tab.position.set(0, 2.4, 6.0);
  tab.castShadow = true; tab.receiveShadow = true;
  g.add(tab);
  
  // Metal mounting hole with realistic appearance
  var mhole = new THREE.Mesh(new THREE.CylinderGeometry(1.3, 1.3, 0.8, 16), MAT(0x888888, 0.7, 0.3));
  mhole.position.set(0, 2.4, 10.5);
  mhole.rotation.set(Math.PI/2, 0, 0);
  mhole.castShadow = true; mhole.receiveShadow = true;
  g.add(mhole);
  
  // Metal screw in mounting hole
  var screw = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.4, 12), brushedAlum);
  screw.position.set(0, 2.4, 10.3);
  screw.rotation.set(Math.PI/2, 0, 0);
  g.add(screw);
  
  // Three bent leads with proper TO-220 spacing
  var leadPositions = [-2.54, 0, 2.54];
  for(var li = 0; li < leadPositions.length; li++){
    var lead = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.28, 8, 8), M_TIN);
    lead.position.set(leadPositions[li], 0, -4.0);
    lead.rotation.set(Math.PI/2, 0, 0);
    lead.castShadow = true; lead.receiveShadow = true;
    g.add(lead);
  }
  
  // Metal tab heat sink fins
  for(var fi = 0; fi < 3; fi++){
    var fin = new THREE.Mesh(new THREE.BoxGeometry(4.8, 0.1, 0.3), brushedAlum);
    fin.position.set(0, 2.4, 2.5 + fi * 1.5);
    g.add(fin);
  }
  
  g.position.set(x, y, z);
  scene.add(g);
}

function buildIC(x, y, z, pinCount){
  var totalPins = pinCount || 16;
  var pinsPerSide = Math.max(2, Math.floor(totalPins / 4));
  var pitch = 0.8;
  var side = Math.max(5, pinsPerSide * pitch + 2);
  
  // Black epoxy IC body with proper QFP dimensions
  addMesh(new THREE.BoxGeometry(side, side, 1.6), M_EPOXY, x, y, z + 0.8);
  
  // Pin 1 indicator (small dot)
  addMesh(new THREE.BoxGeometry(0.3, 0.3, 0.1), M_WHITE, x - side/2 + 0.8, y - side/2 + 0.8, z + 1.65);
  
  // Gull-wing pins on all four sides with realistic appearance
  var halfSpan = (pinsPerSide - 1) * pitch / 2;
  var pinMat = MAT(0xb8c8c8, 0.4, 0.75);
  
  for(var p = 0; p < pinsPerSide; p++){
    var offset = -halfSpan + p * pitch;
    
    // Top side pins
    addMesh(new THREE.BoxGeometry(0.4, 1.0, 0.2), pinMat, x + offset, y + side/2 + 0.2, z + 0.1);
    addMesh(new THREE.BoxGeometry(0.3, 0.6, 0.15), pinMat, x + offset, y + side/2 + 0.8, z + 0.075);
    
    // Bottom side pins
    addMesh(new THREE.BoxGeometry(0.4, 1.0, 0.2), pinMat, x + offset, y - side/2 - 0.2, z + 0.1);
    addMesh(new THREE.BoxGeometry(0.3, 0.6, 0.15), pinMat, x + offset, y - side/2 - 0.8, z + 0.075);
    
    // Left side pins
    addMesh(new THREE.BoxGeometry(1.0, 0.4, 0.2), pinMat, x - side/2 - 0.2, y + offset, z + 0.1);
    addMesh(new THREE.BoxGeometry(0.6, 0.3, 0.15), pinMat, x - side/2 - 0.8, y + offset, z + 0.075);
    
    // Right side pins
    addMesh(new THREE.BoxGeometry(1.0, 0.4, 0.2), pinMat, x + side/2 + 0.2, y + offset, z + 0.1);
    addMesh(new THREE.BoxGeometry(0.6, 0.3, 0.15), pinMat, x + side/2 + 0.8, y + offset, z + 0.075);
  }
  
  // IC marking on top (simulated with small rectangle)
  addMesh(new THREE.BoxGeometry(side * 0.6, side * 0.3, 0.05), MAT(0x333333, 0.7, 0.0), x, y, z + 1.62);
}

function buildDiode(x, y, z){
  addMesh(new THREE.BoxGeometry(2.68, 1.7, 1.19), M_EPOXY, x, y, z + 0.595);
  addMesh(new THREE.BoxGeometry(0.25, 1.72, 1.21), M_WHITE, x + 0.9, y, z + 0.605);
  addMesh(new THREE.BoxGeometry(0.4, 1.7, 0.15), M_TIN, x - 1.54, y, z + 0.075);
  addMesh(new THREE.BoxGeometry(0.4, 1.7, 0.15), M_TIN, x + 1.54, y, z + 0.075);
}

function buildConnector(x, y, z, pinCnt){
  var pins = pinCnt || 2;
  var w = pins * 2.54;
  addMesh(new THREE.BoxGeometry(w, 7, 8.5), M_GREY, x, y, z + 4.25);
  for(var p = 0; p < pins; p++){
    var px = x - w/2 + 1.27 + p * 2.54;
    addMesh(new THREE.BoxGeometry(1.5, 1.5, 8.6), M_DARK, px, y, z + 4.3);
    addMesh(new THREE.CylinderGeometry(0.3, 0.3, 4, 8), M_GOLD, px, y, z - 2, 0, 0, 0);
  }
}

function buildSource(x, y, z){
  buildConnector(x, y, z, 2);
}

function buildMountingHole(x, y, z){
  var g = new THREE.Group();
  var ring = new THREE.Mesh(
    new THREE.RingGeometry(1.6, 3.2, 32),
    new THREE.MeshStandardMaterial({color:0xcccccc, roughness:0.9, metalness:0.1, side:THREE.DoubleSide})
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.set(x, y, 1.68);
  g.add(ring);
  var hole = new THREE.Mesh(
    new THREE.CircleGeometry(1.6, 32),
    new THREE.MeshStandardMaterial({color:0x0b0d12, roughness:1.0, metalness:0.0, side:THREE.DoubleSide})
  );
  hole.rotation.x = -Math.PI / 2;
  hole.position.set(x, y, 1.67);
  g.add(hole);
  scene.add(g);
}

// --- Layout & placement ---
var COL_SPACING = 20;
var ROW_SPACING = 24;
var START_X = 10;
var START_Y = 8;
var COLS = 5;
var PCB_Z = 1.6;

var placedPositions = [];

for(var ci = 0; ci < COMPONENTS_JSON.length; ci++){
  var comp = COMPONENTS_JSON[ci];
  var col = ci % COLS;
  var row = Math.floor(ci / COLS);
  var cx = START_X + col * COL_SPACING;
  var cy = START_Y + row * ROW_SPACING;
  var ctype = (comp.type || "").toLowerCase();
  var val = comp.value || "";

  placedPositions.push({x: cx, y: cy, id: comp.id, type: comp.type});

  // Determine role description for label
  var role = (comp.role || '').replace(/_/g, ' ');
  var silkW = 3, silkH = 2;
  var labelText = '';
  if(ctype === "resistor")       { buildResistor(cx, cy, PCB_Z, val); silkW=3; silkH=2; labelText = comp.id + '|' + val + '\u03a9 ' + role; }
  else if(ctype === "capacitor") { buildCapacitor(cx, cy, PCB_Z, val); silkW=10; silkH=10; labelText = comp.id + '|' + val + ' ' + role; }
  else if(ctype === "inductor")  { buildInductor(cx, cy, PCB_Z); silkW=8; silkH=8; labelText = comp.id + '|' + val + ' ' + role; }
  else if(ctype === "mosfet")    { buildMOSFET(cx, cy, PCB_Z); silkW=8; silkH=15; labelText = comp.id + '|' + val + ' Switch'; }
  else if(ctype === "diode")     { buildDiode(cx, cy, PCB_Z); silkW=4; silkH=2.5; labelText = comp.id + '|' + val + ' FW'; }
  else if(ctype === "terminal" || ctype === "source")  { buildSource(cx, cy, PCB_Z); silkW=6; silkH=8; labelText = comp.id + '|' + val + ' Terminal'; }
  else if(ctype === "mountinghole") { buildMountingHole(cx, cy, PCB_Z); silkW=6; silkH=6; labelText = comp.id + '|M3 Hole'; }
  else if(ctype === "ic" || ctype === "qfp") { buildIC(cx, cy, PCB_Z, 16); silkW=8; silkH=8; labelText = comp.id + '|Controller IC'; }
  else if(ctype === "connector") { buildConnector(cx, cy, PCB_Z, 4); silkW=12; silkH=8; labelText = comp.id + '|Connector'; }
  else { buildResistor(cx, cy, PCB_Z, val); labelText = comp.id + '|' + val; }

  // Tag last-added mesh(es) for hover tooltip
  var lastObj = scene.children[scene.children.length - 1];
  if(lastObj){
    if(lastObj.isGroup){
      lastObj.traverse(function(child){ if(child.isMesh) child.userData.label = labelText; });
    } else {
      lastObj.userData.label = labelText;
    }
  }

  // Silkscreen outline
  addSilkscreen(cx, cy, silkW, silkH);
  // Component label
  makeLabel(labelText, cx, cy, PCB_Z);
}

// --- Add board title and version text ---
addBoardText("AI Circuit Designer 2026", 40, 10, 20);
addBoardText("Rev 1.0", 70, 10, 8);

// --- Copper traces with realistic etched appearance ---
function addTrace(x1, y1, x2, y2, width){
  width = width || 0.35;
  // Realistic etched copper material with proper color and metallic properties
  var traceMat = new THREE.MeshStandardMaterial({
    color:0xcd7f32, 
    roughness:0.25, 
    metalness:0.94,
    envMapIntensity:0.8
  });
  
  if(Math.abs(x2 - x1) > 0.5){
    var hw = Math.abs(x2 - x1);
    // Main copper trace
    var t = new THREE.Mesh(new THREE.BoxGeometry(hw, width, 0.038), traceMat);
    t.position.set(Math.min(x1, x2) + hw/2, y1, 1.68);
    t.castShadow = false; t.receiveShadow = true;
    scene.add(t);
    
    // Solder mask opening (slightly larger than trace)
    var maskOpening = new THREE.MeshStandardMaterial({
      color:0x0a2818, 
      roughness:0.95, 
      metalness:0.0, 
      transparent:true, 
      opacity:0.3
    });
    var opening = new THREE.Mesh(new THREE.BoxGeometry(hw + 0.2, width + 0.1, 0.04), maskOpening);
    opening.position.set(Math.min(x1, x2) + hw/2, y1, 1.70);
    scene.add(opening);
  }
  if(Math.abs(y2 - y1) > 0.5){
    var vh = Math.abs(y2 - y1);
    // Main copper trace
    var t2 = new THREE.Mesh(new THREE.BoxGeometry(width, vh, 0.038), traceMat);
    t2.position.set(x2, Math.min(y1, y2) + vh/2, 1.68);
    t2.castShadow = false; t2.receiveShadow = true;
    scene.add(t2);
    
    // Solder mask opening
    var maskOpening = new THREE.MeshStandardMaterial({
      color:0x0a2818, 
      roughness:0.95, 
      metalness:0.0, 
      transparent:true, 
      opacity:0.3
    });
    var opening2 = new THREE.Mesh(new THREE.BoxGeometry(width + 0.1, vh + 0.2, 0.04), maskOpening);
    opening2.position.set(x2, Math.min(y1, y2) + vh/2, 1.70);
    scene.add(opening2);
  }
}

// Signal traces between consecutive component pairs
for(var ti = 0; ti < placedPositions.length - 1; ti++){
  addTrace(
    placedPositions[ti].x, placedPositions[ti].y,
    placedPositions[ti+1].x, placedPositions[ti+1].y
  );
}

// Power rail (thick — 1.2mm width)
addTrace(8, boardD - 8, boardW - 8, boardD - 8, 1.2);
// Ground rail (thick)
addTrace(8, 8, boardW - 8, 8, 1.2);
// Signal density inner traces
var innerTraces = [[12,12,12,boardD-12],[25,8,25,boardD-8],[40,8,40,boardD-8],
  [55,8,55,boardD-8],[8,20,boardW-8,20],[8,35,boardW-8,35]];
for(var it = 0; it < innerTraces.length; it++){
  addTrace(innerTraces[it][0], innerTraces[it][1], innerTraces[it][2], innerTraces[it][3], 0.3);
}

var netlist = DESIGN_DATA_JSON.netlist || [];
for(var ni = 0; ni < netlist.length; ni++){
  var net = netlist[ni];
  if(!net || net.length !== 2) continue;
  var aId = net[0], bId = net[1];
  var aPos = null, bPos = null;
  for(var pi = 0; pi < placedPositions.length; pi++){
    if(placedPositions[pi].id === aId) aPos = placedPositions[pi];
    if(placedPositions[pi].id === bId) bPos = placedPositions[pi];
  }
  if(aPos && bPos) addTrace(aPos.x, aPos.y, bPos.x, bPos.y);
}

// --- Enhanced hover tooltip with component highlighting ---
var raycaster = new THREE.Raycaster();
var mouse = new THREE.Vector2();
var tooltip = document.createElement('div');
tooltip.style.cssText = 'position:absolute;background:rgba(11,13,18,0.92);color:#58a6ff;padding:8px 14px;border-radius:6px;font:12px Courier New;border:1px solid #30363d;pointer-events:none;display:none;z-index:20;box-shadow:0 4px 12px rgba(0,0,0,0.3);backdrop-filter:blur(8px);transition:all 0.2s ease;';
document.body.appendChild(tooltip);

var highlightedObject = null;
var originalMaterials = new Map();

renderer.domElement.addEventListener('mousemove', function(ev){
  var rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  var hits = raycaster.intersectObjects(scene.children, true);
  
  // Reset previous highlight
  if(highlightedObject && originalMaterials.has(highlightedObject)){
    highlightedObject.material = originalMaterials.get(highlightedObject);
    originalMaterials.delete(highlightedObject);
    highlightedObject = null;
  }
  
  var found = false;
  for(var hi = 0; hi < hits.length; hi++){
    if(hits[hi].object.userData && hits[hi].object.userData.label){
      var obj = hits[hi].object;
      
      // Highlight component with subtle glow
      if(obj.material && obj.material.color){
        originalMaterials.set(obj, obj.material.clone());
        var highlightMat = obj.material.clone();
        highlightMat.emissive = new THREE.Color(0x58a6ff);
        highlightMat.emissiveIntensity = 0.15;
        obj.material = highlightMat;
        highlightedObject = obj;
      }
      
      // Show enhanced tooltip
      tooltip.style.display = 'block';
      tooltip.style.left = (ev.clientX + 15) + 'px';
      tooltip.style.top = (ev.clientY - 10) + 'px';
      
      var labelData = obj.userData.label.split('|');
      var htmlContent = '<div style="color:#58a6ff;font-weight:bold;margin-bottom:4px;">' + (labelData[0] || '') + '</div>';
      if(labelData[1]) htmlContent += '<div style="color:#3fb950;font-size:11px;">' + labelData[1] + '</div>';
      tooltip.innerHTML = htmlContent;
      
      found = true;
      break;
    }
  }
  if(!found) tooltip.style.display = 'none';
});

// Add click interaction for component selection
renderer.domElement.addEventListener('click', function(ev){
  var rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  var hits = raycaster.intersectObjects(scene.children, true);
  
  for(var hi = 0; hi < hits.length; hi++){
    if(hits[hi].object.userData && hits[hi].object.userData.label){
      var labelData = hits[hi].object.userData.label.split('|');
      console.log('Component selected:', labelData[0], labelData[1] || '');
      break;
    }
  }
});

// --- OrbitControls (vanilla JS) ---
(function(){
  var spherical = {r: 200, theta: Math.PI/3, phi: -Math.PI/4};
  var target = new THREE.Vector3(40, 30, 0);
  var targetTarget = target.clone();
  var isOrbiting = false, isPanning = false;
  var prevMouse = {x:0, y:0};
  var canvas = renderer.domElement;
  var autoRotate = true;
  var autoRotateSpeed = 0.003;

  function updateCamera(){
    var st = Math.sin(spherical.theta);
    var ct = Math.cos(spherical.theta);
    var sp = Math.sin(spherical.phi);
    var cp = Math.cos(spherical.phi);
    camera.position.set(
      target.x + spherical.r * st * cp,
      target.y + spherical.r * st * sp,
      target.z + spherical.r * ct
    );
    camera.lookAt(target);
  }

  var dx = camera.position.x - target.x;
  var dy = camera.position.y - target.y;
  var dz = camera.position.z - target.z;
  spherical.r = Math.sqrt(dx*dx + dy*dy + dz*dz);
  spherical.theta = Math.acos(Math.max(-1, Math.min(1, dz / spherical.r)));
  spherical.phi = Math.atan2(dy, dx);

  canvas.addEventListener("mousedown", function(e){
    autoRotate = false;
    if(e.button === 0) isOrbiting = true;
    if(e.button === 2) isPanning = true;
    prevMouse.x = e.clientX; prevMouse.y = e.clientY;
    e.preventDefault();
  });
  canvas.addEventListener("mousemove", function(e){
    var dx = e.clientX - prevMouse.x;
    var dy = e.clientY - prevMouse.y;
    if(isOrbiting){
      spherical.phi -= dx * 0.005;
      spherical.theta = Math.max(0.05, Math.min(Math.PI - 0.05, spherical.theta - dy * 0.005));
    }
    if(isPanning){
      var panScale = spherical.r * 0.001;
      var right = new THREE.Vector3();
      var up = new THREE.Vector3();
      camera.matrix.extractBasis(right, up, new THREE.Vector3());
      targetTarget.add(right.multiplyScalar(-dx * panScale));
      targetTarget.add(up.multiplyScalar(dy * panScale));
    }
    prevMouse.x = e.clientX; prevMouse.y = e.clientY;
  });
  canvas.addEventListener("mouseup", function(){ isOrbiting = false; isPanning = false; });
  canvas.addEventListener("mouseleave", function(){ isOrbiting = false; isPanning = false; });
  canvas.addEventListener("wheel", function(e){
    spherical.r *= (1 + e.deltaY * 0.001);
    spherical.r = Math.max(20, Math.min(800, spherical.r));
    e.preventDefault();
  }, {passive:false});
  canvas.addEventListener("contextmenu", function(e){ e.preventDefault(); });

  // Touch support
  var touches = {};
  canvas.addEventListener("touchstart", function(e){
    e.preventDefault();
    autoRotate = false;
    if(e.touches.length === 1){
      isOrbiting = true;
      prevMouse.x = e.touches[0].clientX; prevMouse.y = e.touches[0].clientY;
    }
  }, {passive:false});
  canvas.addEventListener("touchmove", function(e){
    e.preventDefault();
    if(e.touches.length === 1 && isOrbiting){
      var dx = e.touches[0].clientX - prevMouse.x;
      var dy = e.touches[0].clientY - prevMouse.y;
      spherical.phi -= dx * 0.005;
      spherical.theta = Math.max(0.05, Math.min(Math.PI - 0.05, spherical.theta - dy * 0.005));
      prevMouse.x = e.touches[0].clientX; prevMouse.y = e.touches[0].clientY;
    }
    if(e.touches.length === 2){
      isOrbiting = false;
      var d = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      );
      if(touches.pinchDist){
        var delta = touches.pinchDist - d;
        spherical.r *= (1 + delta * 0.005);
        spherical.r = Math.max(20, Math.min(800, spherical.r));
      }
      touches.pinchDist = d;
    }
  }, {passive:false});
  canvas.addEventListener("touchend", function(){
    isOrbiting = false; isPanning = false;
    touches.pinchDist = null;
  });

  // Damped animation loop with 2-second auto-rotation on load
  var autoRotateTimer = null;
  var autoRotateStartTime = Date.now();
  
  function animate(){
    requestAnimationFrame(animate);
    
    // 2-second auto-rotation on load
    if(autoRotateTimer === null){
      autoRotateTimer = setTimeout(function(){
        autoRotate = false;
      }, 2000);
    }
    
    if(autoRotate && (Date.now() - autoRotateStartTime) < 2000){
      var t = (Date.now() - autoRotateStartTime) * 0.001; // seconds
      var rotationProgress = t / 2.0; // 0 to 1 over 2 seconds
      var angle = rotationProgress * Math.PI * 2; // full rotation
      
      // Smooth rotation around the board
      var r = 180;
      camera.position.x = 40 + r * Math.cos(angle - Math.PI/2);
      camera.position.y = 30 + r * Math.sin(angle - Math.PI/2);
      camera.position.z = 85 + 15 * Math.sin(angle * 2); // slight vertical movement
      camera.lookAt(40, 30, 8);
    } else {
      autoRotate = false;
      target.lerp(targetTarget, 0.1);
      updateCamera();
    }
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", function(){
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
})();
</script>
</body>
</html>'''

        return html