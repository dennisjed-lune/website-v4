/* Pearl moon: a WebGL shader that draws the home page moon as a lit sphere.
   landing.js calls LuneMoon.create() once. Then, on each scroll change, it calls draw(R, phase, absorb, shift)
   and copies the returned canvas onto its own 2D canvas. If WebGL is not available, create() returns null
   and landing.js draws the 2D moon.
   - phase 0..1 moves the light from behind the moon (thin crescent) to the front (full moon).
   - absorb 0..1 is how much the moon is taking in descriptions at that scroll point: the inner mint glow gets brighter.
   - shift is the scroll position: the faint surface shimmer moves with the scroll, never on its own. */
(() => {
const VERT = `
attribute vec2 p;
varying vec2 uv;
void main(){ uv = p; gl_Position = vec4(p, 0.0, 1.0); }`;

const FRAG = `
precision highp float;
varying vec2 uv;
uniform float uPhase, uAbsorb, uShift, uPx;
// Colours of the Lune logo mark: a deep teal disc with a muted sea-green crescent (img/lune-logo.svg).
const vec3 SHADE = vec3(0.000, 0.180, 0.165);  // #002E2A lune-teal, the disc
const vec3 DEEP  = vec3(0.039, 0.388, 0.302);  // #0A634D teal-700
const vec3 CRES  = vec3(0.275, 0.604, 0.576);  // #469A93 the crescent in the logo
const vec3 GLOW  = vec3(0.063, 0.639, 0.498);  // #10A37F emerald, only while descriptions go in
float hash(vec2 q){ return fract(sin(dot(q, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 q){
  vec2 i = floor(q), f = fract(q); f = f*f*(3.0-2.0*f);
  return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
}
void main(){
  float r = length(uv);
  float edge = 1.0 - smoothstep(1.0 - 1.6*uPx, 1.0, r);        // anti-aliased disc
  if (edge <= 0.0) { gl_FragColor = vec4(0.0); return; }
  vec3 n = vec3(uv.x, uv.y, sqrt(max(0.0, 1.0 - r*r)));
  // The crescent is drawn the way the logo mark draws it: the disc minus a shadow circle that sits up and to the left.
  // As the phase grows, the shadow circle slides away and more of the disc is lit. Phase 0.05 gives a thin crescent.
  vec2 dir = normalize(vec2(1.0, -1.0));                        // lit side: lower right
  float off = 0.13 + 2.2 * pow(uPhase, 1.35);
  float dist = length(uv + dir * off);
  float lit = smoothstep(1.0 - 0.05, 1.0 + 0.12, dist);
  // light for the shading inside the lit part
  vec3 L = normalize(vec3(dir * 0.75, 0.66));
  float d = dot(n, L);
  // surface: a very faint shimmer that follows the scroll
  float sh = noise(n.xy*3.2 + vec2(uShift*0.35, -uShift*0.2)) * 0.6 + noise(n.xy*7.0 - vec2(uShift*0.2, 0.0)) * 0.4;
  float tone = clamp(d*0.5 + 0.5 + (sh - 0.5)*0.05, 0.0, 1.0);
  vec3 litCol = mix(DEEP, CRES, smoothstep(0.35, 0.85, tone));
  vec3 col = mix(SHADE, litCol, lit);
  // a quiet sheen on the dark side, so the disc reads as a sphere and not a flat circle
  col += vec3(0.06, 0.14, 0.13) * pow(max(0.0, dot(n, normalize(vec3(-0.5, 0.6, 0.65)))), 6.0) * (1.0 - lit);
  // soft highlight on the crescent
  vec3 h = normalize(L + vec3(0.0, 0.0, 1.0));
  col += CRES * pow(max(dot(n, h), 0.0), 22.0) * 0.35 * lit;
  // rim: the crescent colour at rest, emerald while descriptions go in
  float fres = pow(1.0 - n.z, 2.4);
  col = mix(col, mix(CRES, GLOW, uAbsorb), fres * (0.18 + 0.45*uAbsorb));
  gl_FragColor = vec4(col * edge, edge);                        // premultiplied alpha
}`;

function create(){
  const cv = document.createElement('canvas');
  const gl = cv.getContext('webgl', { premultipliedAlpha: true, alpha: true, antialias: false, preserveDrawingBuffer: true });
  if (!gl) return null;
  const sh = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); return gl.getShaderParameter(s, gl.COMPILE_STATUS) ? s : null; };
  const vs = sh(gl.VERTEX_SHADER, VERT), fs = sh(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return null;
  const pr = gl.createProgram(); gl.attachShader(pr, vs); gl.attachShader(pr, fs); gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) return null;
  gl.useProgram(pr);
  const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  const u = n => gl.getUniformLocation(pr, n);
  const uPhase = u('uPhase'), uAbsorb = u('uAbsorb'), uShift = u('uShift'), uPx = u('uPx');
  let lost = false;
  cv.addEventListener('webglcontextlost', e => { e.preventDefault(); lost = true; });
  return {
    canvas: cv,
    // R is the moon radius in CSS px. Returns the canvas, or null if the context is lost (landing.js then draws 2D).
    draw(R, phase, absorb, shift){
      if (lost) return null;
      const dpr = Math.min(devicePixelRatio || 1, 2);
      const size = Math.max(32, Math.ceil(2 * R * dpr / 32) * 32);     // grow in steps of 32 px, not every frame
      if (cv.width !== size) { cv.width = cv.height = size; }
      const used = Math.round(2 * R * dpr);
      gl.viewport(0, 0, used, used);
      gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.uniform1f(uPhase, phase); gl.uniform1f(uAbsorb, absorb); gl.uniform1f(uShift, shift); gl.uniform1f(uPx, 2 / used);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      this.used = used;
      return cv;
    }
  };
}
window.LuneMoon = { create };
})();
