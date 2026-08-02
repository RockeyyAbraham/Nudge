/* ============================================================
   Vivid Motion shared helpers
   Thin wiring around the GSAP / ScrollTrigger / SplitText / Lenis
   libraries (copied from templates/dream UI/js) so every Nudge
   page sets them up the same way instead of duplicating init code.
   ============================================================ */
(function (global) {
  var prefersReducedMotion = function () {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  };

  // Wires Lenis smooth scroll as the driver for ScrollTrigger's updates.
  // Returns the Lenis instance (or null if unavailable / reduced motion).
  function initVividScroll() {
    if (prefersReducedMotion() || typeof Lenis === 'undefined' || typeof gsap === 'undefined') {
      return null;
    }

    var lenis = new Lenis({
      duration: 1.2,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 2,
      infinite: false
    });

    if (typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);
      lenis.on('scroll', ScrollTrigger.update);
    }

    gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);

    return lenis;
  }

  // Clip-path + fade reveal for any [data-reveal] element as it scrolls
  // into view, matching the source site's text/media reveal pattern.
  function initVividReveal(selector) {
    if (typeof gsap === 'undefined') return;

    var targets = gsap.utils.toArray(selector || '[data-reveal]');
    if (!targets.length) return;

    if (prefersReducedMotion()) {
      targets.forEach(function (el) {
        el.style.visibility = 'visible';
        el.style.clipPath = 'none';
        el.style.opacity = 1;
      });
      return;
    }

    targets.forEach(function (el) {
      gsap.fromTo(el,
        { clipPath: 'inset(100% 0% 0% 0%)', opacity: 0, visibility: 'visible' },
        {
          clipPath: 'inset(0% 0% 0% 0%)',
          opacity: 1,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: el,
            start: 'top 88%',
            toggleActions: 'play none none none'
          }
        }
      );
    });
  }

  // SplitText line-reveal for headings, matching the source's text
  // animation style. Falls back to a plain fade if SplitText is absent.
  function initVividTextReveal(selector, options) {
    if (typeof gsap === 'undefined') return;
    options = options || {};

    var targets = gsap.utils.toArray(selector);
    if (!targets.length) return;

    if (prefersReducedMotion()) {
      targets.forEach(function (el) { el.style.opacity = 1; });
      return;
    }

    targets.forEach(function (el) {
      if (typeof SplitText !== 'undefined') {
        var split = new SplitText(el, { type: 'lines', linesClass: 'reveal-line' });
        gsap.from(split.lines, {
          y: '100%',
          opacity: 0,
          duration: 0.9,
          stagger: 0.08,
          ease: 'power4.out',
          delay: options.delay || 0
        });
      } else {
        gsap.from(el, { y: 20, opacity: 0, duration: 0.8, ease: 'power2.out', delay: options.delay || 0 });
      }
    });
  }

  // Toggles .is-scrolled on the navbar once the page scrolls past the hero.
  function initVividNavbar(navbarId) {
    var navbar = document.getElementById(navbarId || 'navbar-vivid');
    if (!navbar) return;

    var check = function () {
      navbar.classList.toggle('is-scrolled', window.scrollY > 60);
    };

    window.addEventListener('scroll', check, { passive: true });
    check();
  }

  // Fullscreen animated grain-gradient background, shared across all
  // pages. Gracefully no-ops if WebGL is unavailable or motion is reduced.
  function initVividCanvas(canvasId) {
    if (prefersReducedMotion()) return;

    var canvas = document.getElementById(canvasId || 'vivid-canvas');
    if (!canvas) return;

    var gl = canvas.getContext('webgl', { alpha: true, antialias: false });
    if (!gl) return;

    function resize() {
      var dpr = window.devicePixelRatio || 1;
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = window.innerWidth + 'px';
      canvas.style.height = window.innerHeight + 'px';
      gl.viewport(0, 0, canvas.width, canvas.height);
    }

    resize();
    window.addEventListener('resize', resize);

    var vsSource = [
      'attribute vec2 a_position;',
      'void main() {',
      '  gl_Position = vec4(a_position, 0.0, 1.0);',
      '}'
    ].join('\n');

    var fsSource = [
      'precision highp float;',
      'uniform vec2 u_resolution;',
      'uniform float u_time;',

      'float hash(vec2 p) {',
      '  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);',
      '}',

      'float noise(vec2 p) {',
      '  vec2 i = floor(p);',
      '  vec2 f = fract(p);',
      '  f = f * f * (3.0 - 2.0 * f);',
      '  float a = hash(i);',
      '  float b = hash(i + vec2(1.0, 0.0));',
      '  float c = hash(i + vec2(0.0, 1.0));',
      '  float d = hash(i + vec2(1.0, 1.0));',
      '  return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);',
      '}',

      'void main() {',
      '  vec2 uv = gl_FragCoord.xy / u_resolution;',
      '  vec2 center = uv - 0.5;',
      '  float dist = length(center);',
      '  float vignette = 1.0 - dist * 0.6;',

      '  vec2 noiseUV = uv * 2.5 + vec2(u_time * 0.008, u_time * 0.006);',
      '  float n = noise(noiseUV);',

      '  vec2 noiseUV2 = uv * 5.0 - vec2(u_time * 0.012, u_time * 0.01);',
      '  float n2 = noise(noiseUV2);',

      '  float grain = mix(n, n2, 0.3) * 0.12;',

      '  vec3 color = vec3(',
      '    0.025 + grain * 0.3,',
      '    0.025 + grain * 0.2,',
      '    0.035 + grain * 0.1',
      '  );',

      '  float topGlow = exp(-uv.y * 4.0) * 0.015;',
      '  color += vec3(topGlow * 1.2, topGlow * 0.8, topGlow * 0.4);',

      '  gl_FragColor = vec4(color, 0.85);',
      '}'
    ].join('\n');

    function compileShader(source, type) {
      var shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.warn('Vivid canvas shader compile error:', gl.getShaderInfoLog(shader));
        return null;
      }
      return shader;
    }

    var vs = compileShader(vsSource, gl.VERTEX_SHADER);
    var fs = compileShader(fsSource, gl.FRAGMENT_SHADER);
    if (!vs || !fs) { canvas.style.display = 'none'; return; }

    var program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.warn('Vivid canvas program link error');
      canvas.style.display = 'none';
      return;
    }

    gl.useProgram(program);

    var positions = new Float32Array([-1, -1, 1, -1, -1, 1, 1, -1, 1, 1, -1, 1]);
    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

    var attrLoc = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(attrLoc);
    gl.vertexAttribPointer(attrLoc, 2, gl.FLOAT, false, 0, 0);

    var resLoc = gl.getUniformLocation(program, 'u_resolution');
    var timeLoc = gl.getUniformLocation(program, 'u_time');
    var startTime = performance.now();

    function render() {
      var elapsed = (performance.now() - startTime) / 1000;
      gl.uniform2f(resLoc, canvas.width, canvas.height);
      gl.uniform1f(timeLoc, elapsed);
      gl.drawArrays(gl.TRIANGLES, 0, 6);
      requestAnimationFrame(render);
    }

    render();
  }

  global.initVividScroll = initVividScroll;
  global.initVividReveal = initVividReveal;
  global.initVividTextReveal = initVividTextReveal;
  global.initVividNavbar = initVividNavbar;
  global.initVividCanvas = initVividCanvas;
})(window);
