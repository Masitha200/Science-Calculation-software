// Physics Sandbox Visualizer Engine
let projectileCanvas, projectileCtx;
let pendulumCanvas, pendulumCtx;
let doubleCanvas, doubleCtx;
let opticsCanvas, opticsCtx;
let gravityCanvas, gravityCtx;
let isPhysicsInitialized = false;

// Ray Optics State
const opticsState = {
    focal: 120,
    objDist: 200,
    objHeight: 60,
    isDraggingObject: false
};

// Orbital Gravity Sandbox State
const gravityState = {
    starMass: 10000,
    planetVel: 2.8,
    planetRad: 120,
    x: 0,
    y: 120,
    vx: 2.8,
    vy: 0,
    trail: [],
    running: true
};

// Double Pendulum State
const doublePendState = {
    l1: 120,
    l2: 120,
    m1: 15,
    m2: 15,
    theta1: Math.PI / 2,
    theta2: Math.PI / 2,
    omega1: 0,
    omega2: 0,
    trail: [],
    maxTrailSize: 200,
    running: true,
    gravity: 9.8
};

// Projectile parameters
const projState = {
    gravity: 9.8,
    speed: 20,
    angle: 45,
    drag: 0.05,
    height: 0,
    // Active simulation state
    running: false,
    paused: false,
    t: 0,
    x: 0,
    y: 0,
    vx: 0,
    vy: 0,
    trace: [],
    runId: null,
    // Max records
    maxHeight: 0,
    maxRange: 0,
    flightTime: 0
};

// Pendulum parameters
const pendState = {
    length: 2.5,
    mass: 2.0,
    gravity: 9.8,
    damping: 0.05,
    angle: Math.PI / 4, // Initial 45dg
    angVel: 0,
    // Drag state
    isDraggingBob: false,
    running: true,
    runId: null
};

// Physics Init
function initPhysicsModule() {
    if (isPhysicsInitialized) {
        resizePhysicsCanvases();
        drawPhysicsFrame();
        return;
    }

    projectileCanvas = document.getElementById('projectile-canvas');
    projectileCtx = projectileCanvas.getContext('2d');

    pendulumCanvas = document.getElementById('pendulum-canvas');
    pendulumCtx = pendulumCanvas.getContext('2d');

    doubleCanvas = document.getElementById('double-canvas');
    doubleCtx = doubleCanvas.getContext('2d');

    // Controls setup: Projectile
    document.getElementById('proj-speed').addEventListener('input', (e) => {
        projState.speed = parseFloat(e.target.value);
        document.getElementById('proj-speed-val').textContent = `${projState.speed} m/s`;
        resetProjectileSim();
    });

    document.getElementById('proj-angle').addEventListener('input', (e) => {
        projState.angle = parseFloat(e.target.value);
        document.getElementById('proj-angle-val').textContent = `${projState.angle}°`;
        resetProjectileSim();
    });

    document.getElementById('proj-gravity').addEventListener('input', (e) => {
        projState.gravity = parseFloat(e.target.value);
        document.getElementById('proj-gravity-val').textContent = `${projState.gravity.toFixed(1)} m/s²`;
        resetProjectileSim();
    });

    document.getElementById('proj-drag').addEventListener('input', (e) => {
        projState.drag = parseFloat(e.target.value);
        document.getElementById('proj-drag-val').textContent = projState.drag.toFixed(2);
        resetProjectileSim();
    });

    document.getElementById('proj-launch-height').addEventListener('input', (e) => {
        projState.height = parseFloat(e.target.value);
        document.getElementById('proj-height-val').textContent = `${projState.height} m`;
        resetProjectileSim();
    });

    // Run action controls
    document.getElementById('btn-proj-run').addEventListener('click', startProjectileSim);
    document.getElementById('btn-proj-pause').addEventListener('click', pauseProjectileSim);
    document.getElementById('btn-proj-clear').addEventListener('click', resetProjectileSim);

    // Controls setup: Pendulum
    document.getElementById('pend-length').addEventListener('input', (e) => {
        pendState.length = parseFloat(e.target.value);
        document.getElementById('pend-length-val').textContent = `${pendState.length.toFixed(1)} m`;
    });

    document.getElementById('pend-mass').addEventListener('input', (e) => {
        pendState.mass = parseFloat(e.target.value);
        document.getElementById('pend-mass-val').textContent = `${pendState.mass.toFixed(1)} kg`;
    });

    document.getElementById('pend-gravity').addEventListener('input', (e) => {
        pendState.gravity = parseFloat(e.target.value);
        document.getElementById('pend-gravity-val').textContent = `${pendState.gravity.toFixed(1)} m/s²`;
    });

    document.getElementById('pend-damping').addEventListener('input', (e) => {
        pendState.damping = parseFloat(e.target.value);
        document.getElementById('pend-damping-val').textContent = pendState.damping.toFixed(2);
    });

    document.getElementById('btn-pend-play').addEventListener('click', () => {
        pendState.running = !pendState.running;
        document.getElementById('btn-pend-play').textContent = pendState.running ? 'Pause' : 'Play';
    });

    document.getElementById('btn-pend-reset').addEventListener('click', () => {
        pendState.angle = Math.PI / 4;
        pendState.angVel = 0;
        if (!pendState.running) {
            pendState.running = true;
            document.getElementById('btn-pend-play').textContent = 'Pause';
        }
    });

    // Bob Interactivity - Dragging bob on canvas
    bindPendulumInteractiveDragging();

    // Double Pendulum Controls Setup
    document.getElementById('double-rod1').addEventListener('input', (e) => {
        doublePendState.l1 = parseFloat(e.target.value);
        document.getElementById('double-rod1-val').textContent = `${doublePendState.l1} px`;
    });
    document.getElementById('double-rod2').addEventListener('input', (e) => {
        doublePendState.l2 = parseFloat(e.target.value);
        document.getElementById('double-rod2-val').textContent = `${doublePendState.l2} px`;
    });
    document.getElementById('double-mass1').addEventListener('input', (e) => {
        doublePendState.m1 = parseFloat(e.target.value);
        document.getElementById('double-mass1-val').textContent = doublePendState.m1;
    });
    document.getElementById('double-mass2').addEventListener('input', (e) => {
        doublePendState.m2 = parseFloat(e.target.value);
        document.getElementById('double-mass2-val').textContent = doublePendState.m2;
    });
    document.getElementById('double-trail').addEventListener('input', (e) => {
        doublePendState.maxTrailSize = parseInt(e.target.value);
        document.getElementById('double-trail-val').textContent = `${doublePendState.maxTrailSize} frames`;
    });

    document.getElementById('btn-double-run').addEventListener('click', () => {
        doublePendState.running = true;
    });
    document.getElementById('btn-double-pause').addEventListener('click', () => {
        doublePendState.running = false;
    });
    document.getElementById('btn-double-clear').addEventListener('click', () => {
        doublePendState.theta1 = Math.PI / 2;
        doublePendState.theta2 = Math.PI / 2;
        doublePendState.omega1 = 0;
        doublePendState.omega2 = 0;
        doublePendState.trail = [];
    });

    // Optics Lab Setup
    opticsCanvas = document.getElementById('optics-canvas');
    opticsCtx = opticsCanvas.getContext('2d');

    document.getElementById('optics-focal').addEventListener('input', (e) => {
        opticsState.focal = parseFloat(e.target.value);
        document.getElementById('optics-focal-val').textContent = `${opticsState.focal} px`;
    });

    document.getElementById('optics-obj-dist').addEventListener('input', (e) => {
        opticsState.objDist = parseFloat(e.target.value);
        document.getElementById('optics-obj-val').textContent = `${opticsState.objDist} px`;
    });

    document.getElementById('optics-obj-height').addEventListener('input', (e) => {
        opticsState.objHeight = parseFloat(e.target.value);
        document.getElementById('optics-obj-h-val').textContent = `${opticsState.objHeight} px`;
    });

    opticsCanvas.addEventListener('mousedown', (e) => {
        const rect = opticsCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const centerX = opticsCanvas.width / 2;
        const centerY = opticsCanvas.height / 2;

        const arrowTipX = centerX - opticsState.objDist;
        const arrowTipY = centerY - opticsState.objHeight;

        if (Math.hypot(mouseX - arrowTipX, mouseY - arrowTipY) < 16) {
            opticsState.isDraggingObject = true;
        }
    });

    opticsCanvas.addEventListener('mousemove', (e) => {
        const rect = opticsCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        const centerX = opticsCanvas.width / 2;
        const centerY = opticsCanvas.height / 2;

        if (opticsState.isDraggingObject) {
            let dist = centerX - mouseX;
            let height = centerY - mouseY;
            dist = Math.max(50, Math.min(350, dist));
            height = Math.max(-100, Math.min(100, height));

            opticsState.objDist = dist;
            opticsState.objHeight = height;

            document.getElementById('optics-obj-dist').value = dist;
            document.getElementById('optics-obj-val').textContent = `${Math.round(dist)} px`;

            document.getElementById('optics-obj-height').value = height;
            document.getElementById('optics-obj-h-val').textContent = `${Math.round(height)} px`;
        }
    });

    window.addEventListener('mouseup', () => {
        opticsState.isDraggingObject = false;
    });

    // Gravity Orbit Setup
    gravityCanvas = document.getElementById('gravity-canvas');
    gravityCtx = gravityCanvas.getContext('2d');

    document.getElementById('grav-star-mass').addEventListener('input', (e) => {
        gravityState.starMass = parseFloat(e.target.value);
        document.getElementById('grav-star-val').textContent = gravityState.starMass;
    });

    document.getElementById('grav-planet-vel').addEventListener('input', (e) => {
        gravityState.planetVel = parseFloat(e.target.value);
        document.getElementById('grav-vel-val').textContent = gravityState.planetVel.toFixed(1);
        resetGravityOrbit();
    });

    document.getElementById('grav-planet-rad').addEventListener('input', (e) => {
        gravityState.planetRad = parseFloat(e.target.value);
        document.getElementById('grav-rad-val').textContent = `${gravityState.planetRad} px`;
        resetGravityOrbit();
    });

    document.getElementById('btn-grav-run').addEventListener('click', () => {
        gravityState.running = true;
    });

    document.getElementById('btn-grav-pause').addEventListener('click', () => {
        gravityState.running = false;
    });

    document.getElementById('btn-grav-clear').addEventListener('click', () => {
        gravityState.starMass = 10000;
        gravityState.planetVel = 2.8;
        gravityState.planetRad = 120;

        document.getElementById('grav-star-mass').value = 10000;
        document.getElementById('grav-star-val').textContent = '10000';
        document.getElementById('grav-planet-vel').value = 2.8;
        document.getElementById('grav-vel-val').textContent = '2.8';
        if (document.getElementById('grav-planet-rad')) {
            document.getElementById('grav-planet-rad').value = 120;
            document.getElementById('grav-rad-val').textContent = '120 px';
        }
        resetGravityOrbit();
    });

    resetGravityOrbit();

    isPhysicsInitialized = true;
    resizePhysicsCanvases();

    // Start simulations loop
    runPhysicsLoop();
}

function resizePhysicsCanvases() {
    if (!projectileCanvas) return;
    const pRect = projectileCanvas.parentElement.getBoundingClientRect();
    projectileCanvas.width = pRect.width;
    projectileCanvas.height = pRect.height;

    const pendRect = pendulumCanvas.parentElement.getBoundingClientRect();
    pendulumCanvas.width = pendRect.width;
    pendulumCanvas.height = pendRect.height;

    if (doubleCanvas) {
        const dRect = doubleCanvas.parentElement.getBoundingClientRect();
        doubleCanvas.width = dRect.width;
        doubleCanvas.height = dRect.height;
    }

    if (opticsCanvas) {
        const optRect = opticsCanvas.parentElement.getBoundingClientRect();
        opticsCanvas.width = optRect.width;
        opticsCanvas.height = optRect.height;
    }

    if (gravityCanvas) {
        const gravRect = gravityCanvas.parentElement.getBoundingClientRect();
        gravityCanvas.width = gravRect.width;
        gravityCanvas.height = gravRect.height;
    }
}

window.addEventListener('resize', () => {
    if (isPhysicsInitialized) {
        resizePhysicsCanvases();
    }
});

// Interactive Bob dragging logic
function bindPendulumInteractiveDragging() {
    let activeCanvas = false;

    pendulumCanvas.addEventListener('mousedown', (e) => {
        const rect = pendulumCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Anchor coordinate point
        const ax = pendulumCanvas.width / 2;
        const ay = 60;

        // Bob coordinates
        const lensP = pendState.length * 80; // Scaler
        const bx = ax + lensP * Math.sin(pendState.angle);
        const by = ay + lensP * Math.cos(pendState.angle);

        // Check mouse click distance to Bob
        const dist = Math.hypot(mx - bx, my - by);
        if (dist < 25) {
            pendState.isDraggingBob = true;
            activeCanvas = true;
        }
    });

    window.addEventListener('mouseup', () => {
        if (activeCanvas) {
            pendState.isDraggingBob = false;
            activeCanvas = false;
        }
    });

    pendulumCanvas.addEventListener('mousemove', (e) => {
        if (pendState.isDraggingBob) {
            const rect = pendulumCanvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;

            const ax = pendulumCanvas.width / 2;
            const ay = 60;

            // Calculate angle based on mouse
            pendState.angle = Math.atan2(mx - ax, my - ay);
            pendState.angVel = 0; // stop velocity
        }
    });
}

// Master frame sync
function runPhysicsLoop() {
    drawPhysicsFrame();
    requestAnimationFrame(runPhysicsLoop);
}

function drawPhysicsFrame() {
    if (!isPhysicsInitialized || typeof state === 'undefined' || state.activeTab !== 'physics') return;
    const activeSubpane = document.querySelector('#tab-physics .subtab-btn.active');
    if (!activeSubpane) return;

    const panelType = activeSubpane.getAttribute('data-subtab');
    if (panelType === 'physics-projectile') {
        updateProjectilePhysics();
        renderProjectileCanvas();
    } else if (panelType === 'physics-pendulum') {
        updatePendulumPhysics();
        renderPendulumCanvas();
    } else if (panelType === 'physics-double') {
        updateDoublePendulumPhysics();
        drawDoublePendulum();
    } else if (panelType === 'physics-optics') {
        drawOpticsSpace();
    } else if (panelType === 'physics-gravity') {
        updateGravityPhysics();
        drawGravitySpace();
    }
}

// Projectile motion physics calculations
function startProjectileSim() {
    if (projState.running && projState.paused) {
        projState.paused = false;
        return;
    }

    resetProjectileSim();
    projState.running = true;

    // Launch speeds
    const rad = projState.angle * Math.PI / 180;
    projState.vx = projState.speed * Math.cos(rad);
    projState.vy = projState.speed * Math.sin(rad);
    projState.x = 0;
    projState.y = projState.height;
    projState.t = 0;
    projState.trace = [{ x: 0, y: projState.height }];
}

function pauseProjectileSim() {
    if (projState.running) {
        projState.paused = !projState.paused;
        document.getElementById('btn-proj-pause').textContent = projState.paused ? 'Resume' : 'Pause';
    }
}

function resetProjectileSim() {
    projState.running = false;
    projState.paused = false;
    projState.t = 0;
    projState.x = 0;
    projState.y = projState.height;
    projState.trace = [];
    projState.maxHeight = 0;
    projState.maxRange = 0;
    projState.flightTime = 0;

    document.getElementById('btn-proj-pause').textContent = 'Pause';

    // Reset HUD
    document.getElementById('hud-proj-range').textContent = '0.00 m';
    document.getElementById('hud-proj-height').textContent = '0.00 m';
    document.getElementById('hud-proj-time').textContent = '0.00 s';
    document.getElementById('hud-proj-speed').textContent = '0.00 m/s';

    renderProjectileCanvas();
}

function updateProjectilePhysics() {
    if (!projState.running || projState.paused) return;

    // Time step (60fps)
    const dt = 1 / 60;

    // Integrate drag forces
    // F_d = -c_d * v * vec_v
    const velocity = Math.hypot(projState.vx, projState.vy);
    const ax = -projState.drag * velocity * projState.vx;
    const ay = -projState.gravity - projState.drag * velocity * projState.vy;

    // Semi-implicit Euler integration
    projState.vx += ax * dt;
    projState.vy += ay * dt;

    projState.x += projState.vx * dt;
    projState.y += projState.vy * dt;
    projState.t += dt;

    projState.trace.push({ x: projState.x, y: projState.y });

    // Record maximum dimensions
    if (projState.y > projState.maxHeight) {
        projState.maxHeight = projState.y;
    }

    // Check ground collision
    if (projState.y <= 0) {
        projState.y = 0;
        projState.running = false;
        projState.maxRange = projState.x;
        projState.flightTime = projState.t;
    }

    // Write dynamic values to HUD
    document.getElementById('hud-proj-range').textContent = `${(projState.x).toFixed(2)} m`;
    document.getElementById('hud-proj-height').textContent = `${(projState.maxHeight).toFixed(2)} m`;
    document.getElementById('hud-proj-time').textContent = `${(projState.t).toFixed(2)} s`;
    document.getElementById('hud-proj-speed').textContent = `${velocity.toFixed(2)} m/s`;
}

function renderProjectileCanvas() {
    if (!projectileCanvas) return;

    projectileCtx.clearRect(0, 0, projectileCanvas.width, projectileCanvas.height);

    const width = projectileCanvas.width;
    const height = projectileCanvas.height;

    // Scale factor: 1 meter = 12 pixels
    const scale = 12;
    const groundY = height - 50;
    const startX = 60;

    // Draw ground
    projectileCtx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    projectileCtx.lineWidth = 2;
    projectileCtx.beginPath();
    projectileCtx.moveTo(0, groundY);
    projectileCtx.lineTo(width, groundY);
    projectileCtx.stroke();

    projectileCtx.fillStyle = 'rgba(255,255,255,0.02)';
    projectileCtx.fillRect(0, groundY, width, 50);

    // Draw Launcher Stand
    projectileCtx.fillStyle = '#64748b';
    projectileCtx.fillRect(startX - 5, groundY - projState.height * scale, 10, projState.height * scale);
    projectileCtx.beginPath();
    projectileCtx.arc(startX, groundY - projState.height * scale, 8, 0, Math.PI * 2);
    projectileCtx.fill();

    // Target grid markings
    projectileCtx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    projectileCtx.lineWidth = 1;
    for (let m = 5; m * scale < width - startX; m += 5) {
        const x_coord = startX + m * scale;
        projectileCtx.beginPath();
        projectileCtx.moveTo(x_coord, 0);
        projectileCtx.lineTo(x_coord, groundY);
        projectileCtx.stroke();

        projectileCtx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        projectileCtx.font = '8px JetBrains Mono';
        projectileCtx.fillText(`${m}m`, x_coord - 6, groundY - 8);
    }

    for (let m = 5; m * scale < groundY; m += 5) {
        const y_coord = groundY - m * scale;
        projectileCtx.beginPath();
        projectileCtx.moveTo(startX, y_coord);
        projectileCtx.lineTo(width, y_coord);
        projectileCtx.stroke();

        projectileCtx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        projectileCtx.fillText(`${m}m`, startX - 25, y_coord + 3);
    }

    // Draw path trace curve
    if (projState.trace.length > 1) {
        projectileCtx.strokeStyle = 'rgba(189, 0, 255, 0.5)';
        projectileCtx.lineWidth = 2.5;
        projectileCtx.shadowBlur = 6;
        projectileCtx.shadowColor = 'rgba(189, 0, 255, 0.3)';
        projectileCtx.beginPath();

        projectileCtx.moveTo(startX + projState.trace[0].x * scale, groundY - projState.trace[0].y * scale);
        for (let i = 1; i < projState.trace.length; i++) {
            projectileCtx.lineTo(startX + projState.trace[i].x * scale, groundY - projState.trace[i].y * scale);
        }
        projectileCtx.stroke();
        projectileCtx.shadowBlur = 0; // reset
    }

    // Draw flying Projectile ball
    const px = startX + projState.x * scale;
    const py = groundY - projState.y * scale;

    projectileCtx.fillStyle = '#bd00ff';
    projectileCtx.beginPath();
    projectileCtx.arc(px, py, 6, 0, Math.PI * 2);
    projectileCtx.fill();

    // Draw vectors if active running
    if (projState.running) {
        // Dynamic velocity Vector arrow (vector length proportional to speed)
        const vecScale = 1.5;
        projectileCtx.strokeStyle = '#00ff88';
        projectileCtx.lineWidth = 2;
        projectileCtx.beginPath();
        projectileCtx.moveTo(px, py);
        projectileCtx.lineTo(px + projState.vx * vecScale, py - projState.vy * vecScale);
        projectileCtx.stroke();

        // Acceleration gravity vector arrow
        projectileCtx.strokeStyle = '#ef4444';
        projectileCtx.beginPath();
        projectileCtx.moveTo(px, py);
        projectileCtx.lineTo(px, py + projState.gravity * 2);
        projectileCtx.stroke();
    }
}

// Pendulum simulation physics calculations
function updatePendulumPhysics() {
    if (!pendState.running || pendState.isDraggingBob) return;

    // dt (60fps)
    const dt = 1 / 60;

    // Differential Equation:
    // theta'' = -(g / L) * sin(theta) - (damping / (mass * L)) * theta'
    const gravityTorque = -(pendState.gravity / pendState.length) * Math.sin(pendState.angle);
    const dampingTorque = -(pendState.damping / (pendState.mass * pendState.length)) * pendState.angVel;
    const angAccel = gravityTorque + dampingTorque;

    // Semi-implicit Euler integration
    pendState.angVel += angAccel * dt;
    pendState.angle += pendState.angVel * dt;
}

function renderPendulumCanvas() {
    if (!pendulumCanvas) return;

    pendulumCtx.clearRect(0, 0, pendulumCanvas.width, pendulumCanvas.height);

    const width = pendulumCanvas.width;
    const height = pendulumCanvas.height;

    const anchorX = width / 2;
    const anchorY = 60;

    const lengthScale = 80; // 1 meter = 80 pixels

    // Calculate coordinates
    const bobX = anchorX + pendState.length * lengthScale * Math.sin(pendState.angle);
    const bobY = anchorY + pendState.length * lengthScale * Math.cos(pendState.angle);

    // Draw circular reference grid lines
    pendulumCtx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
    pendulumCtx.lineWidth = 1;
    pendulumCtx.beginPath();
    pendulumCtx.arc(anchorX, anchorY, pendState.length * lengthScale, 0, Math.PI * 2);
    pendulumCtx.stroke();

    // Draw string cord
    pendulumCtx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    pendulumCtx.lineWidth = Math.max(1, pendState.mass * 0.3); // cord width based on mass
    pendulumCtx.beginPath();
    pendulumCtx.moveTo(anchorX, anchorY);
    pendulumCtx.lineTo(bobX, bobY);
    pendulumCtx.stroke();

    // Draw ceiling anchor point
    pendulumCtx.fillStyle = '#64748b';
    pendulumCtx.fillRect(anchorX - 16, anchorY - 4, 32, 8);

    // Draw Bob sphere
    const bobRadius = 10 + pendState.mass * 1.5; // size base on mass
    const bobGlowGrad = pendulumCtx.createRadialGradient(bobX, bobY, 1, bobX, bobY, bobRadius);
    bobGlowGrad.addColorStop(0, '#e879f9');
    bobGlowGrad.addColorStop(1, '#bd00ff');

    pendulumCtx.fillStyle = bobGlowGrad;
    pendulumCtx.shadowBlur = 10;
    pendulumCtx.shadowColor = 'rgba(189, 0, 255, 0.5)';

    pendulumCtx.beginPath();
    pendulumCtx.arc(bobX, bobY, bobRadius, 0, Math.PI * 2);
    pendulumCtx.fill();
    pendulumCtx.shadowBlur = 0; // reset

    // Highlight dragging hover
    if (pendState.isDraggingBob) {
        pendulumCtx.strokeStyle = '#00ff88';
        pendulumCtx.lineWidth = 1.5;
        pendulumCtx.beginPath();
        pendulumCtx.arc(bobX, bobY, bobRadius + 4, 0, Math.PI * 2);
        pendulumCtx.stroke();
    }

    // Energy calculations
    // PE = m * g * h (where h is height displacement: L * (1 - cos(theta)))
    const heightDisplacement = pendState.length * (1 - Math.cos(pendState.angle));
    const potentialEnergy = pendState.mass * pendState.gravity * heightDisplacement;

    // KE = 0.5 * m * v² (where v = L * omega)
    const velocity = pendState.length * pendState.angVel;
    const kineticEnergy = 0.5 * pendState.mass * velocity * velocity;

    const totalEnergy = potentialEnergy + kineticEnergy;

    // Update live HUD graphic bars (percent scale based on max potential energy starting at 90dg displacement)
    const maxReferenceEnergy = pendState.mass * pendState.gravity * pendState.length * 1.1; // adding buffer

    const pePercent = Math.min(100, Math.max(0, (potentialEnergy / maxReferenceEnergy) * 100));
    const kePercent = Math.min(100, Math.max(0, (kineticEnergy / maxReferenceEnergy) * 100));
    const totalPercent = Math.min(100, Math.max(0, (totalEnergy / maxReferenceEnergy) * 100));

    document.getElementById('bar-pe').style.width = `${pePercent}%`;
    document.getElementById('bar-ke').style.width = `${kePercent}%`;
    document.getElementById('bar-total').style.width = `${totalPercent}%`;
}

function resetPhysicsModule() {
    projState.gravity = 9.8;
    projState.speed = 20;
    projState.angle = 45;
    projState.drag = 0.05;
    projState.height = 0;

    // Update sliders UI
    document.getElementById('proj-speed').value = 20;
    document.getElementById('proj-speed-val').textContent = '20 m/s';

    document.getElementById('proj-angle').value = 45;
    document.getElementById('proj-angle-val').textContent = '45°';

    document.getElementById('proj-gravity').value = 9.8;
    document.getElementById('proj-gravity-val').textContent = '9.8 m/s²';

    document.getElementById('proj-drag').value = 0.05;
    document.getElementById('proj-drag-val').textContent = '0.05';

    document.getElementById('proj-launch-height').value = 0;
    document.getElementById('proj-height-val').textContent = '0 m';

    // Pendulum resets
    pendState.length = 2.5;
    pendState.mass = 2.0;
    pendState.gravity = 9.8;
    pendState.damping = 0.05;

    document.getElementById('pend-length').value = 2.5;
    document.getElementById('pend-length-val').textContent = '2.5 m';

    document.getElementById('pend-mass').value = 2.0;
    document.getElementById('pend-mass-val').textContent = '2.0 kg';

    document.getElementById('pend-gravity').value = 9.8;
    document.getElementById('pend-gravity-val').textContent = '9.8 m/s²';

    document.getElementById('pend-damping').value = 0.05;
    document.getElementById('pend-damping-val').textContent = '0.05';

    resetProjectileSim();

    pendState.angle = Math.PI / 4;
    pendState.angVel = 0;

    // Double pendulum resets
    doublePendState.l1 = 120;
    doublePendState.l2 = 120;
    doublePendState.m1 = 15;
    doublePendState.m2 = 15;
    doublePendState.theta1 = Math.PI / 2;
    doublePendState.theta2 = Math.PI / 2;
    doublePendState.omega1 = 0;
    doublePendState.omega2 = 0;
    doublePendState.trail = [];
    doublePendState.maxTrailSize = 200;
    doublePendState.running = true;

    document.getElementById('double-rod1').value = 120;
    document.getElementById('double-rod1-val').textContent = '120 px';
    document.getElementById('double-rod2').value = 120;
    document.getElementById('double-rod2-val').textContent = '120 px';
    document.getElementById('double-mass1').value = 15;
    document.getElementById('double-mass1-val').textContent = '15';
    document.getElementById('double-mass2').value = 15;
    document.getElementById('double-mass2-val').textContent = '15';
    document.getElementById('double-trail').value = 200;
    document.getElementById('double-trail-val').textContent = '200 frames';
}

function updateDoublePendulumPhysics() {
    if (!doublePendState.running) return;

    // Substep integration for numerical stability
    const substeps = 5;
    const dt = (1 / 60) / substeps;

    for (let step = 0; step < substeps; step++) {
        doublePendTimeStep(dt);
    }
}

function getDerivatives(t1, t2, w1, w2) {
    const g = doublePendState.gravity * 0.1;
    const m1 = doublePendState.m1;
    const m2 = doublePendState.m2;
    const l1 = doublePendState.l1 * 0.05;
    const l2 = doublePendState.l2 * 0.05;

    const delta = t1 - t2;

    const den1 = l1 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
    const num1 = -g * (2 * m1 + m2) * Math.sin(t1) - m2 * g * Math.sin(t1 - 2 * t2) - 2 * Math.sin(delta) * m2 * (w2 * w2 * l2 + w1 * w1 * l1 * Math.cos(delta));
    const a1 = num1 / den1;

    const den2 = l2 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
    const num2 = 2 * Math.sin(delta) * (w1 * w1 * l1 * (m1 + m2) + g * (m1 + m2) * Math.cos(t1) + w2 * w2 * l2 * m2 * Math.cos(delta));
    const a2 = num2 / den2;

    return [w1, a1, w2, a2];
}

function doublePendTimeStep(dt) {
    const s = doublePendState;
    const state = [s.theta1, s.omega1, s.theta2, s.omega2];

    const k1 = getDerivatives(state[0], state[2], state[1], state[3]);

    const s2 = [
        state[0] + k1[0] * dt / 2,
        state[1] + k1[1] * dt / 2,
        state[2] + k1[2] * dt / 2,
        state[3] + k1[3] * dt / 2
    ];
    const k2 = getDerivatives(s2[0], s2[2], s2[1], s2[3]);

    const s3 = [
        state[0] + k2[0] * dt / 2,
        state[1] + k2[1] * dt / 2,
        state[2] + k2[2] * dt / 2,
        state[3] + k2[3] * dt / 2
    ];
    const k3 = getDerivatives(s3[0], s3[2], s3[1], s3[3]);

    const s4 = [
        state[0] + k3[0] * dt,
        state[1] + k3[1] * dt,
        state[2] + k3[2] * dt,
        state[3] + k3[3] * dt
    ];
    const k4 = getDerivatives(s4[0], s4[2], s4[1], s4[3]);

    s.theta1 += (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) * dt / 6;
    s.omega1 += (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) * dt / 6;
    s.theta2 += (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2]) * dt / 6;
    s.omega2 += (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3]) * dt / 6;
}

function drawDoublePendulum() {
    if (!doubleCanvas) return;

    doubleCtx.clearRect(0, 0, doubleCanvas.width, doubleCanvas.height);

    const cx = doubleCanvas.width / 2;
    const cy = doubleCanvas.height / 3;

    const s = doublePendState;
    const l1 = s.l1;
    const l2 = s.l2;

    const x1 = cx + l1 * Math.sin(s.theta1);
    const y1 = cy + l1 * Math.cos(s.theta1);

    const x2 = x1 + l2 * Math.sin(s.theta2);
    const y2 = y1 + l2 * Math.cos(s.theta2);

    if (s.running) {
        s.trail.push({ x: x2, y: y2 });
        while (s.trail.length > s.maxTrailSize) {
            s.trail.shift();
        }
    }

    if (s.trail.length > 1) {
        doubleCtx.lineWidth = 2.5;
        for (let i = 1; i < s.trail.length; i++) {
            const p1 = s.trail[i - 1];
            const p2 = s.trail[i];
            const ratio = i / s.trail.length;

            doubleCtx.strokeStyle = `rgba(0, 255, 136, ${ratio * 0.75})`;
            doubleCtx.beginPath();
            doubleCtx.moveTo(p1.x, p1.y);
            doubleCtx.lineTo(p2.x, p2.y);
            doubleCtx.stroke();
        }
    }

    doubleCtx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    doubleCtx.lineWidth = 4;
    doubleCtx.beginPath();
    doubleCtx.moveTo(cx, cy);
    doubleCtx.lineTo(x1, y1);
    doubleCtx.stroke();

    doubleCtx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    doubleCtx.lineWidth = 3;
    doubleCtx.beginPath();
    doubleCtx.moveTo(x1, y1);
    doubleCtx.lineTo(x2, y2);
    doubleCtx.stroke();

    doubleCtx.fillStyle = '#fff';
    doubleCtx.beginPath();
    doubleCtx.arc(cx, cy, 6, 0, Math.PI * 2);
    doubleCtx.fill();

    doubleCtx.fillStyle = '#00e5ff';
    doubleCtx.strokeStyle = '#fff';
    doubleCtx.lineWidth = 1.5;
    doubleCtx.shadowBlur = 6;
    doubleCtx.shadowColor = '#00e5ff';
    doubleCtx.beginPath();
    doubleCtx.arc(x1, y1, s.m1 * 0.4 + 6, 0, Math.PI * 2);
    doubleCtx.fill();
    doubleCtx.stroke();

    doubleCtx.shadowBlur = 0;
}

// Ray Optics Simulator
function drawOpticsSpace() {
    if (!opticsCanvas) return;
    const w = opticsCanvas.width;
    const h = opticsCanvas.height;
    if (w === 0 || h === 0) return;

    opticsCtx.clearRect(0, 0, w, h);

    const centerX = w / 2;
    const centerY = h / 2;

    const f = opticsState.focal;
    const doVal = opticsState.objDist;
    const yVal = opticsState.objHeight;

    // Draw grid
    opticsCtx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
    opticsCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 30) {
        opticsCtx.beginPath(); opticsCtx.moveTo(x, 0); opticsCtx.lineTo(x, h); opticsCtx.stroke();
    }
    for (let y = 0; y < h; y += 30) {
        opticsCtx.beginPath(); opticsCtx.moveTo(0, y); opticsCtx.lineTo(w, y); opticsCtx.stroke();
    }

    // Draw Principal Axis
    opticsCtx.strokeStyle = 'rgba(255, 255, 0.2)';
    opticsCtx.lineWidth = 1.5;
    opticsCtx.beginPath();
    opticsCtx.moveTo(0, centerY);
    opticsCtx.lineTo(w, centerY);
    opticsCtx.stroke();

    // Draw Focal points F and 2F on both sides
    const drawFocalPoint = (px, label) => {
        opticsCtx.fillStyle = '#ffb300';
        opticsCtx.beginPath();
        opticsCtx.arc(px, centerY, 4, 0, Math.PI * 2);
        opticsCtx.fill();
        opticsCtx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        opticsCtx.font = '10px JetBrains Mono';
        opticsCtx.fillText(label, px - 6, centerY + 16);
    };

    // Left F points
    drawFocalPoint(centerX - f, f > 0 ? "F₁" : "F₂");
    drawFocalPoint(centerX - 2 * f, f > 0 ? "2F₁" : "2F₂");
    // Right F points
    drawFocalPoint(centerX + f, f > 0 ? "F₂" : "F₁");
    drawFocalPoint(centerX + 2 * f, f > 0 ? "2F₂" : "2F₁");

    // Draw Thin Lens (Center line representation with arrows)
    opticsCtx.strokeStyle = '#3b82f6';
    opticsCtx.lineWidth = 3;
    opticsCtx.beginPath();
    opticsCtx.moveTo(centerX, centerY - 130);
    opticsCtx.lineTo(centerX, centerY + 130);
    opticsCtx.stroke();

    // Lens arrows
    opticsCtx.fillStyle = '#3b82f6';
    if (f > 0) { // Convex arrows pointing out
        opticsCtx.beginPath();
        opticsCtx.moveTo(centerX, centerY - 130);
        opticsCtx.lineTo(centerX - 8, centerY - 120);
        opticsCtx.lineTo(centerX + 8, centerY - 120);
        opticsCtx.fill();

        opticsCtx.beginPath();
        opticsCtx.moveTo(centerX, centerY + 130);
        opticsCtx.lineTo(centerX - 8, centerY + 120);
        opticsCtx.lineTo(centerX + 8, centerY + 120);
        opticsCtx.fill();
    } else { // Concave arrows pointing in
        opticsCtx.beginPath();
        opticsCtx.moveTo(centerX, centerY - 120);
        opticsCtx.lineTo(centerX - 8, centerY - 130);
        opticsCtx.lineTo(centerX + 8, centerY - 130);
        opticsCtx.fill();

        opticsCtx.beginPath();
        opticsCtx.moveTo(centerX, centerY + 120);
        opticsCtx.lineTo(centerX - 8, centerY + 130);
        opticsCtx.lineTo(centerX + 8, centerY + 130);
        opticsCtx.fill();
    }

    // Draw Object Arrow (Green)
    const objTipX = centerX - doVal;
    const objTipY = centerY - yVal;
    drawLensArrow(centerX - doVal, centerY, objTipX, objTipY, '#22c55e', 4);

    // Draggable indicator circle on tool tip
    opticsCtx.fillStyle = opticsState.isDraggingObject ? '#ff0000' : 'rgba(255, 255, 255, 0.4)';
    opticsCtx.beginPath();
    opticsCtx.arc(objTipX, objTipY, 6, 0, Math.PI * 2);
    opticsCtx.fill();

    // Calculations
    let di = 0;
    let mag = 0;
    let type = "Real, Inverted";

    if (Math.abs(doVal - f) < 1) {
        di = Infinity;
        mag = Infinity;
        type = "No Image (At Infinite)";
    } else {
        di = (f * doVal) / (doVal - f);
        mag = -di / doVal;

        if (f < 0) {
            type = "Virtual, Upright, Diminished";
        } else {
            if (di < 0) {
                type = "Virtual, Upright, Magnified";
            } else {
                type = `Real, Inverted, ${Math.abs(mag) > 1 ? "Magnified" : "Diminished"}`;
            }
        }
    }

    // Update labels
    const diDisplay = document.getElementById('optics-lbl-di');
    if (diDisplay) {
        diDisplay.textContent = di === Infinity ? 'Infinity' : `${di.toFixed(1)} px`;
        document.getElementById('optics-lbl-yi').textContent = di === Infinity ? 'Infinity' : `${(yVal * mag).toFixed(1)} px`;
        document.getElementById('optics-lbl-mag').textContent = mag === Infinity ? 'Infinity' : mag.toFixed(2);
        document.getElementById('optics-lbl-type').textContent = type;
    }

    // Draw primary rays helper
    const traceRay = (startX, startY, midX, midY, col) => {
        opticsCtx.strokeStyle = col;
        opticsCtx.lineWidth = 1.5;
        opticsCtx.shadowBlur = 4;
        opticsCtx.shadowColor = col;

        // Draw ray from object tip to lens
        opticsCtx.beginPath();
        opticsCtx.moveTo(startX, startY);
        opticsCtx.lineTo(midX, midY);
        opticsCtx.stroke();

        // Calculate refracted ray exit coordinates
        let exitX = w;
        let dx = midX - startX;
        let dy = midY - startY;

        let exitY;
        if (di === Infinity) {
            exitY = midY;
        } else {
            const imgTipX = centerX + di;
            const imgTipY = centerY - yVal * mag;

            const refractedAngle = Math.atan2(imgTipY - midY, imgTipX - midX);
            exitY = midY + (w - midX) * Math.tan(refractedAngle);
        }

        // Draw refracted ray going to right edge
        opticsCtx.beginPath();
        opticsCtx.moveTo(midX, midY);
        opticsCtx.lineTo(exitX, exitY);
        opticsCtx.stroke();

        // If virtual image, draw extension line backward
        if (di !== Infinity && di < 0) {
            opticsCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            opticsCtx.setLineDash([2, 3]);
            opticsCtx.lineWidth = 1;

            const imgTipX = centerX + di;
            const imgTipY = centerY - yVal * mag;
            opticsCtx.beginPath();
            opticsCtx.moveTo(midX, midY);
            opticsCtx.lineTo(imgTipX, imgTipY);
            opticsCtx.stroke();
            opticsCtx.setLineDash([]);
        }

        opticsCtx.shadowBlur = 0;
    };

    // Ray 1: Parallel to Principal Axis -> refracts through focus F2
    const r1MidY = objTipY;
    const r1FocalPointX = centerX + f;
    traceRay(objTipX, objTipY, centerX, r1MidY, '#00e5ff');

    // Ray 2: Directly through central node (undeflected)
    opticsCtx.strokeStyle = '#bd00ff';
    opticsCtx.lineWidth = 1.5;
    opticsCtx.beginPath();
    opticsCtx.moveTo(objTipX, objTipY);
    opticsCtx.lineTo(centerX, centerY);

    let centerRefractAngle = Math.atan2(centerY - objTipY, centerX - objTipX);
    opticsCtx.lineTo(w, centerY + (w - centerX) * Math.tan(centerRefractAngle));
    opticsCtx.stroke();

    if (di !== Infinity && di < 0) {
        opticsCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        opticsCtx.setLineDash([2, 3]);
        opticsCtx.beginPath();
        opticsCtx.moveTo(centerX, centerY);
        opticsCtx.lineTo(centerX + di, centerY - yVal * mag);
        opticsCtx.stroke();
        opticsCtx.setLineDash([]);
    }

    // Ray 3: Through focus F1 -> refracts parallel to principal axis
    const f1X = centerX - f;
    let r3MidY;
    if (f > 0) {
        const rayAngle = Math.atan2(centerY - objTipY, f1X - objTipX);
        r3MidY = objTipY + (centerX - objTipX) * Math.tan(rayAngle);
    } else {
        const rayAngle = Math.atan2(centerY - objTipY, (centerX + Math.abs(f)) - objTipX);
        r3MidY = objTipY + (centerX - objTipX) * Math.tan(rayAngle);
    }

    opticsCtx.strokeStyle = '#eab308';
    opticsCtx.lineWidth = 1.5;
    opticsCtx.beginPath();
    opticsCtx.moveTo(objTipX, objTipY);
    opticsCtx.lineTo(centerX, r3MidY);
    opticsCtx.stroke();

    opticsCtx.beginPath();
    opticsCtx.moveTo(centerX, r3MidY);
    opticsCtx.lineTo(w, r3MidY);
    opticsCtx.stroke();

    if (di !== Infinity && di < 0) {
        opticsCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        opticsCtx.setLineDash([2, 3]);
        opticsCtx.beginPath();
        opticsCtx.moveTo(centerX, r3MidY);
        opticsCtx.lineTo(centerX + di, centerY - yVal * mag);
        opticsCtx.stroke();
        opticsCtx.setLineDash([]);
    }

    // Draw Transformed Image Arrow
    if (di !== Infinity) {
        const imgX = centerX + di;
        const imgY = centerY - yVal * mag;

        opticsCtx.save();
        if (di < 0) {
            opticsCtx.setLineDash([4, 3]);
        }
        drawLensArrow(imgX, centerY, imgX, imgY, di < 0 ? '#ef4444' : '#a855f7', 4.5);
        opticsCtx.restore();
    }
}

function drawLensArrow(fromx, fromy, tox, toy, color, width) {
    opticsCtx.strokeStyle = color;
    opticsCtx.fillStyle = color;
    opticsCtx.lineWidth = width;

    opticsCtx.beginPath();
    opticsCtx.moveTo(fromx, fromy);
    opticsCtx.lineTo(tox, toy);
    opticsCtx.stroke();

    const angle = Math.atan2(toy - fromy, tox - fromx);
    const headlen = 12;

    opticsCtx.beginPath();
    opticsCtx.moveTo(tox, toy);
    opticsCtx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
    opticsCtx.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
    opticsCtx.closePath();
    opticsCtx.fill();
}

// Gravity Orbit Simulator Physics
function resetGravityOrbit() {
    gravityState.x = 0;
    gravityState.y = gravityState.planetRad;
    gravityState.vx = Math.sqrt(0.12 * gravityState.starMass / gravityState.planetRad);
    gravityState.vy = 0;
    gravityState.trail = [];
}

function updateGravityPhysics() {
    if (!gravityState.running) return;

    const x = gravityState.x;
    const y = gravityState.y;

    const dist = Math.hypot(x, y);
    if (dist < 12) {
        gravityState.vx = 0;
        gravityState.vy = 0;
        return;
    }

    const G = 0.12;
    const accelMag = -(G * gravityState.starMass) / Math.pow(dist, 3);

    const ax = accelMag * x;
    const ay = accelMag * y;

    gravityState.vx += ax;
    gravityState.vy += ay;

    gravityState.x += gravityState.vx;
    gravityState.y += gravityState.vy;

    gravityState.trail.push({ x: gravityState.x, y: gravityState.y });
    if (gravityState.trail.length > 300) {
        gravityState.trail.shift();
    }

    const speed = Math.hypot(gravityState.vx, gravityState.vy);
    const speedDisplay = document.getElementById('grav-lbl-speed');
    if (speedDisplay) {
        speedDisplay.textContent = `${(speed * 100).toFixed(1)} km/s`;
        document.getElementById('grav-lbl-dist').textContent = `${dist.toFixed(1)} px`;
    }
}

function drawGravitySpace() {
    if (!gravityCanvas) return;
    const w = gravityCanvas.width;
    const h = gravityCanvas.height;
    if (w === 0 || h === 0) return;

    gravityCtx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2;

    // Draw background grid
    gravityCtx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
    gravityCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
        gravityCtx.beginPath(); gravityCtx.moveTo(x, 0); gravityCtx.lineTo(x, h); gravityCtx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
        gravityCtx.beginPath(); gravityCtx.moveTo(0, y); gravityCtx.lineTo(w, y); gravityCtx.stroke();
    }

    // Draw planet trail
    if (gravityState.trail.length > 1) {
        gravityCtx.lineWidth = 1.5;
        for (let i = 1; i < gravityState.trail.length; i++) {
            const p1 = gravityState.trail[i - 1];
            const p2 = gravityState.trail[i];
            const ratio = i / gravityState.trail.length;

            gravityCtx.strokeStyle = `rgba(0, 229, 255, ${ratio * 0.5})`;
            gravityCtx.beginPath();
            gravityCtx.moveTo(cx + p1.x, cy - p1.y);
            gravityCtx.lineTo(cx + p2.x, cy - p2.y);
            gravityCtx.stroke();
        }
    }

    // Draw Central Sun / Star
    gravityCtx.fillStyle = '#eab308';
    gravityCtx.shadowBlur = 15;
    gravityCtx.shadowColor = '#eab308';
    gravityCtx.beginPath();
    gravityCtx.arc(cx, cy, 14, 0, Math.PI * 2);
    gravityCtx.fill();

    // Draw Planet
    const px = cx + gravityState.x;
    const py = cy - gravityState.y;

    const dist = Math.hypot(gravityState.x, gravityState.y);

    if (dist < 15) {
        gravityCtx.fillStyle = '#ef4444';
        gravityCtx.shadowColor = '#ef4444';
        gravityCtx.beginPath();
        gravityCtx.arc(cx, cy, 25, 0, Math.PI * 2);
        gravityCtx.fill();

        gravityCtx.fillStyle = '#fff';
        gravityCtx.font = 'bold 12px Outfit';
        gravityCtx.fillText("COLLIDED WITH STAR", cx - 60, cy - 35);
    } else if (dist > Math.max(w, h)) {
        gravityCtx.fillStyle = '#ef4444';
        gravityCtx.font = 'bold 12px Outfit';
        gravityCtx.fillText("ESCAPE TRAJECTORY", cx - 65, cy - 35);
    } else {
        gravityCtx.fillStyle = '#00e5ff';
        gravityCtx.shadowColor = '#00e5ff';
        gravityCtx.shadowBlur = 8;
        gravityCtx.beginPath();
        gravityCtx.arc(px, py, 6, 0, Math.PI * 2);
        gravityCtx.fill();

        const speed = Math.hypot(gravityState.vx, gravityState.vy);
        if (speed > 0) {
            const fx = -gravityState.x / dist;
            const fy = -gravityState.y / dist;
            drawLensArrow(px, py, px + fx * 30, py - fy * 30, '#3b82f6', 1.8);

            const vxDir = gravityState.vx / speed;
            const vyDir = gravityState.vy / speed;
            drawLensArrow(px, py, px + vxDir * 25, py - vyDir * 25, '#22c55e', 1.8);
        }
    }

    gravityCtx.shadowBlur = 0;
}
