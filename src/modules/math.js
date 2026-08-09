// Mathematics Visualizer Engine
let mathCanvas, mathCtx;
let matrixCanvas, matrixCtx;
let vectorCanvas, vectorCtx;
let fourierCanvas, fourierCtx;
let galtonCanvas, galtonCtx;
let isMathInitialized = false;

const vectorState = {
    ax: 4,
    ay: 3,
    bx: -3,
    by: 4
};

const fourierState = {
    waveType: 'square',
    harmonics: 10,
    freq: 1.0,
    time: 0,
    waveHistory: []
};

const galtonState = {
    elasticity: 0.6,
    rows: 10,
    balls: [],
    bins: [],
    accumulatedCount: 0,
    autoRunning: false
};

// Graph settings
const graphState = {
    zoom: 30, // Pixels per unit
    offsetX: 0, // Pixels offset from center
    offsetY: 0,
    isDragging: false,
    dragStartX: 0,
    dragStartY: 0,
    activeMode: 'move', // 'move', 'derivative', 'integral'
    selectedFunc: 'sin',
    customExpr: 'x * sin(x)',
    tangentX: 0,
    integralA: -4,
    integralB: 4,
    integralN: 20
};

// Matrix settings
const matrixState = {
    dimension: 2,
    matrix: [
        [2, 1, 0],
        [0.5, 1.5, 0],
        [0, 0, 1]
    ],
    animationFrame: 0,
    totalFrames: 60,
    isAnimating: false,
    t: 1.0, // Interpolation factor (0 to 1) for transformation animation. 1 = fully transformed.
    vectorPoints: []
};

// Math expression safe evaluation
function evaluateExpr(expr, x) {
    // Process input expression safety
    let clean = expr.toLowerCase();

    // Whitelist check
    const allowedPatterns = /^[0-9a-x\s\+\-\*\/\^\(\)\.,]+$/;
    // Strip mathematical functions we support to validate remainder
    let testString = clean
        .replace(/sin/g, '')
        .replace(/cos/g, '')
        .replace(/tan/g, '')
        .replace(/abs/g, '')
        .replace(/exp/g, '')
        .replace(/log/g, '')
        .replace(/pow/g, '')
        .replace(/sqrt/g, '')
        .replace(/pi/g, '')
        .replace(/e/g, '');

    if (!allowedPatterns.test(testString)) {
        throw new Error("Contains unsupported characters or functions.");
    }

    // Replace terms for evaluation
    clean = clean.replace(/pi/g, 'Math.PI');
    clean = clean.replace(/e/g, 'Math.E');
    clean = clean.replace(/\^/g, '**');
    clean = clean.replace(/sin/g, 'Math.sin');
    clean = clean.replace(/cos/g, 'Math.cos');
    clean = clean.replace(/tan/g, 'Math.tan');
    clean = clean.replace(/abs/g, 'Math.abs');
    clean = clean.replace(/exp/g, 'Math.exp');
    clean = clean.replace(/log/g, 'Math.log');
    clean = clean.replace(/sqrt/g, 'Math.sqrt');

    // Evaluate in a secure boundary using Function constructor
    // Binding parameters to function
    const mathFn = new Function('x', `return ${clean};`);
    const val = mathFn(x);
    if (isNaN(val) || !isFinite(val)) return null;
    return val;
}

// Get f(x) based on selections
function getFunctionValue(x) {
    switch (graphState.selectedFunc) {
        case 'sin':
            return Math.sin(x);
        case 'quadratic':
            return 0.2 * x * x - 3;
        case 'cubic':
            return 0.05 * x * x * x - x;
        case 'gaussian':
            return 4 * Math.exp(-0.2 * x * x);
        case 'damped':
            return 3 * Math.exp(-0.1 * x) * Math.cos(x);
        case 'custom':
            try {
                return evaluateExpr(graphState.customExpr, x);
            } catch (err) {
                return null;
            }
        default:
            return 0;
    }
}

// Module Initializer
function initMathModule() {
    if (isMathInitialized) {
        resizeMathCanvases();
        drawGraph();
        drawMatrixSpace();
        updateVectorMath();
        return;
    }

    mathCanvas = document.getElementById('math-canvas');
    mathCtx = mathCanvas.getContext('2d');

    matrixCanvas = document.getElementById('matrix-canvas');
    matrixCtx = matrixCanvas.getContext('2d');

    vectorCanvas = document.getElementById('vector-canvas');
    vectorCtx = vectorCanvas.getContext('2d');

    // Set up dragging listeners for function graph
    mathCanvas.addEventListener('mousedown', (e) => {
        if (graphState.activeMode === 'move') {
            graphState.isDragging = true;
            graphState.dragStartX = e.clientX - graphState.offsetX;
            graphState.dragStartY = e.clientY - graphState.offsetY;
        }
    });

    window.addEventListener('mouseup', () => {
        graphState.isDragging = false;
    });

    mathCanvas.addEventListener('mousemove', (e) => {
        const rect = mathCanvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Cartesian coordinates
        const xVal = (mouseX - (mathCanvas.width / 2 + graphState.offsetX)) / graphState.zoom;
        const yVal = -((mouseY - (mathCanvas.height / 2 + graphState.offsetY)) / graphState.zoom);
        document.getElementById('graph-coords').textContent = `x: ${xVal.toFixed(2)}, y: ${yVal.toFixed(2)}`;

        if (graphState.isDragging) {
            graphState.offsetX = e.clientX - graphState.dragStartX;
            graphState.offsetY = e.clientY - graphState.dragStartY;
            drawGraph();
        }
    });

    // Zoom on wheel scroll
    mathCanvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomFactor = 1.1;
        if (e.deltaY < 0) {
            graphState.zoom = Math.min(graphState.zoom * zoomFactor, 150);
        } else {
            graphState.zoom = Math.max(graphState.zoom / zoomFactor, 10);
        }
        drawGraph();
    });

    // Bind parameters
    document.getElementById('math-func-select').addEventListener('change', (e) => {
        graphState.selectedFunc = e.target.value;
        const customField = document.getElementById('custom-equation-input-group');
        if (e.target.value === 'custom') {
            customField.style.display = 'block';
        } else {
            customField.style.display = 'none';
        }
        drawGraph();
    });

    document.getElementById('math-custom-expr').addEventListener('input', (e) => {
        graphState.customExpr = e.target.value;
        const errorEl = document.getElementById('math-expr-error');
        try {
            evaluateExpr(graphState.customExpr, 1);
            errorEl.textContent = '';
            drawGraph();
        } catch (err) {
            errorEl.textContent = 'Invalid expression. Check formula variables/operators.';
        }
    });

    // Sub-mode controls radio group
    document.querySelectorAll('input[name="math-mode"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            graphState.activeMode = e.target.value;

            document.getElementById('controls-derivative').style.display = (graphState.activeMode === 'derivative') ? 'block' : 'none';
            document.getElementById('controls-integral').style.display = (graphState.activeMode === 'integral') ? 'block' : 'none';

            drawGraph();
        });
    });

    // Sliders
    const tangentSlider = document.getElementById('tangent-x-slider');
    tangentSlider.addEventListener('input', (e) => {
        graphState.tangentX = parseFloat(e.target.value);
        document.getElementById('tangent-x-val').textContent = graphState.tangentX.toFixed(1);
        drawGraph();
    });

    const SliderA = document.getElementById('integral-a');
    SliderA.addEventListener('input', (e) => {
        graphState.integralA = parseFloat(e.target.value);
        document.getElementById('integral-a-val').textContent = graphState.integralA.toFixed(1);
        drawGraph();
    });

    const SliderB = document.getElementById('integral-b');
    SliderB.addEventListener('input', (e) => {
        graphState.integralB = parseFloat(e.target.value);
        document.getElementById('integral-b-val').textContent = graphState.integralB.toFixed(1);
        drawGraph();
    });

    const SliderN = document.getElementById('integral-n');
    SliderN.addEventListener('input', (e) => {
        graphState.integralN = parseInt(e.target.value);
        document.getElementById('integral-n-val').textContent = graphState.integralN;
        drawGraph();
    });

    // Matrix Bindings
    document.getElementById('btn-matrix-2d').addEventListener('click', () => {
        toggleMatrixDimensions(2);
    });
    document.getElementById('btn-matrix-3d').addEventListener('click', () => {
        toggleMatrixDimensions(3);
    });
    document.getElementById('btn-matrix-det').addEventListener('click', calculateMatrixDeterminant);
    document.getElementById('btn-matrix-inv').addEventListener('click', calculateMatrixInverse);
    document.getElementById('btn-matrix-animate').addEventListener('click', runMatrixTransformationAnimation);

    // Matrix Inputs change bindings
    document.querySelectorAll('.matrix-grid-3x3 input').forEach(input => {
        input.addEventListener('change', () => {
            readMatrixFromInputs();
            drawMatrixSpace();
        });
    });

    // Presets
    document.getElementById('preset-matrix-identity').addEventListener('click', () => {
        setMatrixPreset([[1, 0, 0], [0, 1, 0], [0, 0, 1]]);
    });
    document.getElementById('preset-matrix-shear').addEventListener('click', () => {
        setMatrixPreset([[1.5, 1, 0], [0, 1, 0], [0, 0, 1]]);
    });
    document.getElementById('preset-matrix-rotation').addEventListener('click', () => {
        const rad = Math.PI / 4; // 45 dg
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        setMatrixPreset([
            [cos, -sin, 0],
            [sin, cos, 0],
            [0, 0, 1]
        ]);
    });
    document.getElementById('preset-matrix-reflection').addEventListener('click', () => {
        setMatrixPreset([[-1, 0, 0], [0, 1, 0], [0, 0, 1]]);
    });

    // Vector Bindings
    const listenVectorInput = (id, prop) => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', (e) => {
                vectorState[prop] = parseFloat(e.target.value);
                document.getElementById(`${id}-val`).textContent = vectorState[prop].toFixed(1);
                updateVectorMath();
            });
        }
    };

    listenVectorInput('vec-ax', 'ax');
    listenVectorInput('vec-ay', 'ay');
    listenVectorInput('vec-bx', 'bx');
    listenVectorInput('vec-by', 'by');

    document.getElementById('preset-vec-ortho').addEventListener('click', () => {
        setVectorPresetVals(4, 3, -3, 4);
    });
    document.getElementById('preset-vec-parallel').addEventListener('click', () => {
        setVectorPresetVals(3, 2, 6, 4);
    });
    document.getElementById('preset-vec-opposite').addEventListener('click', () => {
        setVectorPresetVals(5, 2, -5, -2);
    });

    // Fourier Synthesizer Event Listeners
    fourierCanvas = document.getElementById('fourier-canvas');
    fourierCtx = fourierCanvas.getContext('2d');

    document.getElementById('fourier-wave-type').addEventListener('change', (e) => {
        fourierState.waveType = e.target.value;
        fourierState.waveHistory = [];
        updateFourierFormula();
    });

    document.getElementById('fourier-harmonics').addEventListener('input', (e) => {
        fourierState.harmonics = parseInt(e.target.value);
        document.getElementById('fourier-harm-val').textContent = e.target.value;
        updateFourierFormula();
    });

    document.getElementById('fourier-freq').addEventListener('input', (e) => {
        fourierState.freq = parseFloat(e.target.value);
        document.getElementById('fourier-freq-val').textContent = fourierState.freq.toFixed(1);
    });

    // Galton Board Event Listeners
    galtonCanvas = document.getElementById('galton-canvas');
    galtonCtx = galtonCanvas.getContext('2d');

    document.getElementById('galton-friction').addEventListener('input', (e) => {
        galtonState.elasticity = parseFloat(e.target.value);
        document.getElementById('galton-elasticity-val').textContent = galtonState.elasticity.toFixed(2);
    });

    document.getElementById('galton-rows').addEventListener('input', (e) => {
        galtonState.rows = parseInt(e.target.value);
        document.getElementById('galton-rows-val').textContent = e.target.value;
        initGaltonBins();
    });

    document.getElementById('btn-galton-run').addEventListener('click', (e) => {
        galtonState.autoRunning = !galtonState.autoRunning;
        e.target.textContent = galtonState.autoRunning ? 'Pause Drop' : 'Auto Drop';
    });

    document.getElementById('btn-galton-drop').addEventListener('click', () => {
        dropGaltonBall();
    });

    document.getElementById('btn-galton-clear').addEventListener('click', () => {
        clearGaltonBoard();
    });

    initGaltonBins();
    updateFourierFormula();

    // Start math animation loop
    requestAnimationFrame(mathAnimationLoop);

    isMathInitialized = true;
    resizeMathCanvases();

    // Start grid points list
    initMatrixPoints();

    drawGraph();
    drawMatrixSpace();
    updateVectorMath();
}

function resizeMathCanvases() {
    if (!mathCanvas) return;

    const mathRect = mathCanvas.parentElement.getBoundingClientRect();
    mathCanvas.width = mathRect.width;
    mathCanvas.height = mathRect.height;

    const matRect = matrixCanvas.parentElement.getBoundingClientRect();
    matrixCanvas.width = matRect.width;
    matrixCanvas.height = matRect.height;

    if (vectorCanvas) {
        const vecRect = vectorCanvas.parentElement.getBoundingClientRect();
        vectorCanvas.width = vecRect.width;
        vectorCanvas.height = vecRect.height;
    }

    if (fourierCanvas) {
        const fourierRect = fourierCanvas.parentElement.getBoundingClientRect();
        fourierCanvas.width = fourierRect.width;
        fourierCanvas.height = fourierRect.height;
    }

    if (galtonCanvas) {
        const galtonRect = galtonCanvas.parentElement.getBoundingClientRect();
        galtonCanvas.width = galtonRect.width;
        galtonCanvas.height = galtonRect.height;
    }
}

window.addEventListener('resize', () => {
    if (isMathInitialized) {
        resizeMathCanvases();
        drawGraph();
        drawMatrixSpace();
        updateVectorMath();
    }
});

// Graph rendering logic
function drawGraph() {
    if (!mathCanvas) return;

    mathCtx.clearRect(0, 0, mathCanvas.width, mathCanvas.height);

    const width = mathCanvas.width;
    const height = mathCanvas.height;
    const centerX = width / 2 + graphState.offsetX;
    const centerY = height / 2 + graphState.offsetY;
    const zoom = graphState.zoom;

    // Draw grid lines
    mathCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    mathCtx.lineWidth = 1;

    // Vertical grid lines
    for (let x = centerX % zoom; x < width; x += zoom) {
        mathCtx.beginPath();
        mathCtx.moveTo(x, 0);
        mathCtx.lineTo(x, height);
        mathCtx.stroke();
    }

    // Horizontal grid lines
    for (let y = centerY % zoom; y < height; y += zoom) {
        mathCtx.beginPath();
        mathCtx.moveTo(0, y);
        mathCtx.lineTo(width, y);
        mathCtx.stroke();
    }

    // Draw Axis lines
    mathCtx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    mathCtx.lineWidth = 2;

    // X Axis
    mathCtx.beginPath();
    mathCtx.moveTo(0, centerY);
    mathCtx.lineTo(width, centerY);
    mathCtx.stroke();

    // Y Axis
    mathCtx.beginPath();
    mathCtx.moveTo(centerX, 0);
    mathCtx.lineTo(centerX, height);
    mathCtx.stroke();

    // Labels and axis numbering
    mathCtx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    mathCtx.font = '10px JetBrains Mono';

    // X numbering
    for (let i = Math.floor(-centerX / zoom); i < Math.ceil((width - centerX) / zoom); i++) {
        if (i !== 0) {
            const x = centerX + i * zoom;
            mathCtx.fillText(i, x - 4, centerY + 14);
        }
    }
    // Y numbering
    for (let i = Math.floor(-centerY / zoom); i < Math.ceil((height - centerY) / zoom); i++) {
        if (i !== 0) {
            const y = centerY - i * zoom;
            mathCtx.fillText(i, centerX - 16, y + 4);
        }
    }

    // Plot actual Function y = f(x)
    mathCtx.strokeStyle = '#00e5ff';
    mathCtx.lineWidth = 3;
    mathCtx.shadowBlur = 8;
    mathCtx.shadowColor = 'rgba(0, 229, 255, 0.4)';
    mathCtx.beginPath();

    let started = false;
    for (let px = 0; px < width; px++) {
        const x = (px - centerX) / zoom;
        const y = getFunctionValue(x);

        if (y !== null) {
            const py = centerY - y * zoom;
            if (!started) {
                mathCtx.moveTo(px, py);
                started = true;
            } else {
                mathCtx.lineTo(px, py);
            }
        }
    }
    mathCtx.stroke();

    // Reset shadow
    mathCtx.shadowBlur = 0;

    // Mode specific renders
    if (graphState.activeMode === 'derivative') {
        renderTangentLine(centerX, centerY, zoom);
    } else if (graphState.activeMode === 'integral') {
        renderRiemannSum(centerX, centerY, zoom);
    } else {
        document.getElementById('math-results-content').innerHTML = `
            <div class="calc-line"><span class="c-lbl">Graph Zoom:</span><span class="c-val">${zoom.toFixed(0)} px/unit</span></div>
            <div class="calc-line"><span class="c-lbl">Center Position:</span><span class="c-val">(${(-graphState.offsetX / zoom).toFixed(1)}, ${(graphState.offsetY / zoom).toFixed(1)})</span></div>
        `;
    }
}

// Render tangent (Derivative Mode)
function renderTangentLine(centerX, centerY, zoom) {
    const x0 = graphState.tangentX;
    const y0 = getFunctionValue(x0);

    if (y0 === null) return;

    // Compute derivative slope numerically
    const h = 0.0001;
    const y1 = getFunctionValue(x0 + h);
    const y_1 = getFunctionValue(x0 - h);

    if (y1 === null || y_1 === null) return;
    const slope = (y1 - y_1) / (2 * h);

    // Equation: y - y0 = slope * (x - x0) => y = slope * x + (y0 - slope * x0)
    const intercept = y0 - slope * x0;

    // Draw tangent line
    mathCtx.strokeStyle = '#ea580c';
    mathCtx.lineWidth = 2;
    mathCtx.setLineDash([5, 5]);

    mathCtx.beginPath();
    const x_start = -20;
    const x_end = 20;
    const y_start = slope * x_start + intercept;
    const y_end = slope * x_end + intercept;

    mathCtx.moveTo(centerX + x_start * zoom, centerY - y_start * zoom);
    mathCtx.lineTo(centerX + x_end * zoom, centerY - y_end * zoom);
    mathCtx.stroke();
    mathCtx.setLineDash([]); // Reset dash

    // Point on graph
    mathCtx.fillStyle = '#ffae00';
    mathCtx.beginPath();
    mathCtx.arc(centerX + x0 * zoom, centerY - y0 * zoom, 5, 0, Math.PI * 2);
    mathCtx.fill();

    // Text output
    const resultsEl = document.getElementById('math-results-content');
    resultsEl.innerHTML = `
        <div class="calc-line"><span class="c-lbl">Coordinates:</span><span class="c-val">(${x0.toFixed(2)}, ${y0.toFixed(2)})</span></div>
        <div class="calc-line"><span class="c-lbl">Slope (dy/dx):</span><span class="c-val text-sol-highlight" style="color:#00e5ff">${slope.toFixed(4)}</span></div>
        <div class="calc-line"><span class="c-lbl">Angle of slope:</span><span class="c-val">${(Math.atan(slope) * 180 / Math.PI).toFixed(1)}&deg;</span></div>
        <div class="calc-line" style="border-top:1px solid rgba(255,255,255,0.05); margin-top:6px; padding-top:4px;"><span class="c-lbl">Tangent Eq:</span><span class="c-val" style="font-size:10px;">y = ${slope.toFixed(2)}x ${intercept >= 0 ? '+' : '-'} ${Math.abs(intercept).toFixed(2)}</span></div>
    `;
}

// Render Riemann integrals
function renderRiemannSum(centerX, centerY, zoom) {
    const a = Math.min(graphState.integralA, graphState.integralB);
    const b = Math.max(graphState.integralA, graphState.integralB);
    const n = graphState.integralN;
    const dx = (b - a) / n;

    let sumArea = 0;

    mathCtx.fillStyle = 'rgba(0, 229, 255, 0.15)';
    mathCtx.strokeStyle = 'rgba(0, 229, 255, 0.4)';
    mathCtx.lineWidth = 1;

    for (let i = 0; i < n; i++) {
        // Choose midpoint Riemann Sum
        const x_mid = a + (i + 0.5) * dx;
        const y = getFunctionValue(x_mid);

        if (y !== null) {
            sumArea += y * dx;

            const x_px = centerX + (a + i * dx) * zoom;
            const width_px = dx * zoom;
            let y_px = centerY - y * zoom;

            mathCtx.beginPath();
            // Rectangle shape
            if (y >= 0) {
                mathCtx.rect(x_px, y_px, width_px, y * zoom);
            } else {
                mathCtx.rect(x_px, centerY, width_px, -y * zoom);
            }
            mathCtx.fill();
            mathCtx.stroke();
        }
    }

    // Bounds boundaries indicators
    mathCtx.strokeStyle = '#bd00ff';
    mathCtx.lineWidth = 1.5;

    // Draw a line
    mathCtx.beginPath();
    mathCtx.moveTo(centerX + a * zoom, 0);
    mathCtx.lineTo(centerX + a * zoom, mathCanvas.height);
    mathCtx.stroke();

    // Draw b line
    mathCtx.beginPath();
    mathCtx.moveTo(centerX + b * zoom, 0);
    mathCtx.lineTo(centerX + b * zoom, mathCanvas.height);
    mathCtx.stroke();

    // Render calculations
    const resultsEl = document.getElementById('math-results-content');
    resultsEl.innerHTML = `
        <div class="calc-line"><span class="c-lbl">Interval [a, b]:</span><span class="c-val">[${a.toFixed(1)}, ${b.toFixed(1)}]</span></div>
        <div class="calc-line"><span class="c-lbl">Step width (dx):</span><span class="c-val">${dx.toFixed(4)}</span></div>
        <div class="calc-line"><span class="c-lbl">Riemann Sum (A):</span><span class="c-val" style="color:#00e5ff">${sumArea.toFixed(5)}</span></div>
        <div class="calc-line"><span class="c-lbl">Rectangles (n):</span><span class="c-val">${n}</span></div>
    `;
}

// Matrix vector structure initializer (smiley face shape / lattice grid for visual mapping)
function initMatrixPoints() {
    matrixState.vectorPoints.length = 0;
    // Draw grid of points
    for (let x = -5; x <= 5; x += 0.5) {
        for (let y = -5; y <= 5; y += 0.5) {
            matrixState.vectorPoints.push({ x: x, y: y, baseColor: 'rgba(255,255,255,0.1)' });
        }
    }

    // Smiley face points!
    const smileColor = '#00ff88';
    // Head circle
    for (let angle = 0; angle < Math.PI * 2; angle += 0.1) {
        const radius = 2.5;
        matrixState.vectorPoints.push({
            x: Math.cos(angle) * radius,
            y: Math.sin(angle) * radius,
            baseColor: smileColor,
            isFeature: true
        });
    }
    // Eyes
    matrixState.vectorPoints.push({ x: -0.8, y: 0.8, baseColor: smileColor, isFeature: true });
    matrixState.vectorPoints.push({ x: 0.8, y: 0.8, baseColor: smileColor, isFeature: true });
    // Mouth
    for (let angle = 0.8 * Math.PI; angle < 1.2 * Math.PI; angle += 0.1) {
        matrixState.vectorPoints.push({
            x: Math.cos(angle) * 1.5,
            y: Math.sin(angle) * 1.5 + 0.4,
            baseColor: smileColor,
            isFeature: true
        });
    }
}

// Draw Matrix grid vectors 2D representation
function drawMatrixSpace() {
    if (!matrixCanvas) return;

    matrixCtx.clearRect(0, 0, matrixCanvas.width, matrixCanvas.height);

    const width = matrixCanvas.width;
    const height = matrixCanvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const zoom = 40; // Scale matrix grid pixels

    // Matrix coefficients
    const m = matrixState.matrix;
    const t = matrixState.t;

    // Calculate current interpolated matrix
    // I = Identity matrix
    // Mt = (1 - t)*I + t*M
    const mt = [
        [(1 - t) * 1 + t * m[0][0], (1 - t) * 0 + t * m[0][1]],
        [(1 - t) * 0 + t * m[1][0], (1 - t) * 1 + t * m[1][1]]
    ];

    // Draw transformed Grid lines
    matrixCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    matrixCtx.lineWidth = 1;

    // Let us draw transformed grid lines by plotting line segments
    // Vertical grid lines
    for (let xl = -6; xl <= 6; xl++) {
        matrixCtx.beginPath();
        for (let yl = -6; yl <= 6; yl += 0.2) {
            // Apply current matrix transformation
            const tx = mt[0][0] * xl + mt[0][1] * yl;
            const ty = mt[1][0] * xl + mt[1][1] * yl;

            const px = centerX + tx * zoom;
            const py = centerY - ty * zoom;

            if (yl === -6) {
                matrixCtx.moveTo(px, py);
            } else {
                matrixCtx.lineTo(px, py);
            }
        }
        matrixCtx.stroke();
    }

    // Horizontal grid lines
    for (let yl = -6; yl <= 6; yl++) {
        matrixCtx.beginPath();
        for (let xl = -6; xl <= 6; xl += 0.2) {
            const tx = mt[0][0] * xl + mt[0][1] * yl;
            const ty = mt[1][0] * xl + mt[1][1] * yl;

            const px = centerX + tx * zoom;
            const py = centerY - ty * zoom;

            if (xl === -6) {
                matrixCtx.moveTo(px, py);
            } else {
                matrixCtx.lineTo(px, py);
            }
        }
        matrixCtx.stroke();
    }

    // Draw transformed Basis vectors i-hat (1,0) and j-hat (0,1)
    // Transformed i-hat
    const ix = mt[0][0];
    const iy = mt[1][0];

    // Transformed j-hat
    const jx = mt[0][1];
    const jy = mt[1][1];

    // Draw i-hat as Cyan arrow
    drawArrow(centerX, centerY, centerX + ix * zoom, centerY - iy * zoom, '#00e5ff', 3, 'i-hat');
    // Draw j-hat as Magenta arrow
    drawArrow(centerX, centerY, centerX + jx * zoom, centerY - jy * zoom, '#bd00ff', 3, 'j-hat');

    // Plot points in grid & smiley face
    for (let i = 0; i < matrixState.vectorPoints.length; i++) {
        const pt = matrixState.vectorPoints[i];

        // Transform point coordinates
        const tx = mt[0][0] * pt.x + mt[0][1] * pt.y;
        const ty = mt[1][0] * pt.x + mt[1][1] * pt.y;

        const px = centerX + tx * zoom;
        const py = centerY - ty * zoom;

        matrixCtx.fillStyle = pt.isFeature ? pt.baseColor : 'rgba(255, 255, 255, 0.2)';
        matrixCtx.beginPath();
        matrixCtx.arc(px, py, pt.isFeature ? 2.5 : 1, 0, Math.PI * 2);
        matrixCtx.fill();
    }
}

function drawArrow(fromx, fromy, tox, toy, color, width, label) {
    matrixCtx.strokeStyle = color;
    matrixCtx.fillStyle = color;
    matrixCtx.lineWidth = width;

    matrixCtx.beginPath();
    matrixCtx.moveTo(fromx, fromy);
    matrixCtx.lineTo(tox, toy);
    matrixCtx.stroke();

    const angle = Math.atan2(toy - fromy, tox - fromx);
    const headlen = 10;

    matrixCtx.beginPath();
    matrixCtx.moveTo(tox, toy);
    matrixCtx.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
    matrixCtx.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
    matrixCtx.closePath();
    matrixCtx.fill();

    // Add text label
    matrixCtx.font = 'bold 9px JetBrains Mono';
    matrixCtx.fillText(label, tox + 5 * Math.cos(angle), toy + 5 * Math.sin(angle));
}

// Animate transition identity -> current matrix coefficients
function runMatrixTransformationAnimation() {
    if (matrixState.isAnimating) return;

    matrixState.isAnimating = true;
    matrixState.animationFrame = 0;
    matrixState.t = 0;

    function step() {
        matrixState.animationFrame++;
        matrixState.t = matrixState.animationFrame / matrixState.totalFrames;

        // easing sine
        matrixState.t = Math.sin(matrixState.t * Math.PI / 2);

        drawMatrixSpace();

        if (matrixState.animationFrame < matrixState.totalFrames) {
            requestAnimationFrame(step);
        } else {
            matrixState.isAnimating = false;
            matrixState.t = 1.0;
            drawMatrixSpace();
        }
    }
    requestAnimationFrame(step);
}

// Dimensions toggle
function toggleMatrixDimensions(dim) {
    matrixState.dimension = dim;
    document.getElementById('btn-matrix-2d').classList.toggle('active', dim === 2);
    document.getElementById('btn-matrix-3d').classList.toggle('active', dim === 3);

    // Hide/show inputs
    document.querySelectorAll('.dim-3-only').forEach(el => {
        el.style.display = (dim === 3) ? 'block' : 'none';
        if (dim === 2) {
            el.classList.add('dim-3-ghost');
        } else {
            el.classList.remove('dim-3-ghost');
        }
    });

    readMatrixFromInputs();
    drawMatrixSpace();
}

function readMatrixFromInputs() {
    matrixState.matrix[0][0] = parseFloat(document.getElementById('m00').value) || 0;
    matrixState.matrix[0][1] = parseFloat(document.getElementById('m01').value) || 0;
    matrixState.matrix[1][0] = parseFloat(document.getElementById('m10').value) || 0;
    matrixState.matrix[1][1] = parseFloat(document.getElementById('m11').value) || 0;

    if (matrixState.dimension === 3) {
        matrixState.matrix[0][2] = parseFloat(document.getElementById('m02').value) || 0;
        matrixState.matrix[1][2] = parseFloat(document.getElementById('m12').value) || 0;
        matrixState.matrix[2][0] = parseFloat(document.getElementById('m20').value) || 0;
        matrixState.matrix[2][1] = parseFloat(document.getElementById('m21').value) || 0;
        matrixState.matrix[2][2] = parseFloat(document.getElementById('m22').value) || 0;
    } else {
        // Force 2D identity elements in 3rd dimension columns
        matrixState.matrix[0][2] = 0;
        matrixState.matrix[1][2] = 0;
        matrixState.matrix[2][0] = 0;
        matrixState.matrix[2][1] = 0;
        matrixState.matrix[2][2] = 1;
    }
}

function setMatrixPreset(presetMatrixData) {
    document.getElementById('m00').value = presetMatrixData[0][0];
    document.getElementById('m01').value = presetMatrixData[0][1];
    document.getElementById('m10').value = presetMatrixData[1][0];
    document.getElementById('m11').value = presetMatrixData[1][1];

    if (presetMatrixData.length === 3) {
        document.getElementById('m02').value = presetMatrixData[0][2];
        document.getElementById('m12').value = presetMatrixData[1][2];
        document.getElementById('m20').value = presetMatrixData[2][0];
        document.getElementById('m21').value = presetMatrixData[2][1];
        document.getElementById('m22').value = presetMatrixData[2][2];
        toggleMatrixDimensions(3);
    } else {
        toggleMatrixDimensions(2);
    }

    readMatrixFromInputs();
    runMatrixTransformationAnimation();
}

// Matrix calculation scripts
function calculateMatrixDeterminant() {
    readMatrixFromInputs();

    const m = matrixState.matrix;
    let det = 0;
    let explanationHTML = "";

    if (matrixState.dimension === 2) {
        // det2x2 = ad - bc
        const a = m[0][0], b = m[0][1];
        const c = m[1][0], d = m[1][1];
        det = a * d - b * c;

        explanationHTML = `
            <div class="matrix-sol-step">
                Determinant formula (2&times;2): Det(M) = m₀₀·m₁₁ - m₀₁·m₁₀
            </div>
            <div class="matrix-sol-step">
                Det(M) = (${a})(${d}) - (${b})(${c})
            </div>
            <div class="matrix-sol-step">
                Det(M) = <span class="matrix-sol-highlight">${det}</span>
            </div>
        `;
    } else {
        // det3x3 = a(ei - fh) - b(di - fg) + c(dh - eg)
        const a = m[0][0], b = m[0][1], c = m[0][2];
        const d = m[1][0], e = m[1][1], f = m[1][2];
        const g = m[2][0], h = m[2][1], i = m[2][2];

        const minorA = e * i - f * h;
        const minorB = d * i - f * g;
        const minorC = d * h - e * g;

        det = a * minorA - b * minorB + c * minorC;

        explanationHTML = `
            <div class="matrix-sol-step">
                Expand along first row elements: a=M₀₀, b=M₀₁, c=M₀₂
            </div>
            <div class="matrix-sol-step">
                Det = ${a}·Det([${e}, ${f}; ${h}, ${i}]) - ${b}·Det([${d}, ${f}; ${g}, ${i}]) + ${c}·Det([${d}, ${e}; ${g}, ${h}])
            </div>
            <div class="matrix-sol-step">
                Det = ${a}(${minorA}) - ${b}(${minorB}) + ${c}(${minorC})
            </div>
            <div class="matrix-sol-step">
                Det(M) = <span class="matrix-sol-highlight">${det}</span>
            </div>
        `;
    }

    document.getElementById('matrix-solutions-output').innerHTML = explanationHTML;
}

function calculateMatrixInverse() {
    readMatrixFromInputs();

    const m = matrixState.matrix;
    let explanationHTML = "";

    if (matrixState.dimension === 2) {
        const a = m[0][0], b = m[0][1];
        const c = m[1][0], d = m[1][1];
        const det = a * d - b * c;

        if (Math.abs(det) < 0.000001) {
            explanationHTML = `<div class="matrix-sol-step" style="border-color:#ef4444; color:#fca5a5;">Inverse matrix does not exist. Determinant is zero (singular matrix).</div>`;
        } else {
            const inv00 = d / det;
            const inv01 = -b / det;
            const inv10 = -c / det;
            const inv11 = a / det;

            explanationHTML = `
                <div class="matrix-sol-step">Det(M) = ${det}</div>
                <div class="matrix-sol-step">Adjugate Matrix = [${d}, ${-b}; ${-c}, ${a}]</div>
                <div class="matrix-sol-step">
                    M⁻¹ = (1/Det) &middot; Adj = 
                    <div style="font-family: monospace; padding: 4px; background:rgba(0,0,0,0.2); margin-top:4px;">
                        [ ${inv00.toFixed(2)}, ${inv01.toFixed(2)} ;<br>
                          ${inv10.toFixed(2)}, ${inv11.toFixed(2)} ]
                    </div>
                </div>
            `;
        }
    } else {
        // Gaussian Elimination or Adjugate for 3x3
        // We write out Gaussian Elimination workflow
        explanationHTML = execute3x3GaussianEliminationOutput(m);
    }

    document.getElementById('matrix-solutions-output').innerHTML = explanationHTML;
}

// Full 3x3 Inverse step Solver (Gaussian elimination details)
function execute3x3GaussianEliminationOutput(m) {
    const dim = 3;
    // Create augmented grid: [A | I]
    const aug = [];
    for (let r = 0; r < dim; r++) {
        aug.push([m[r][0], m[r][1], m[r][2], r === 0 ? 1 : 0, r === 1 ? 1 : 0, r === 2 ? 1 : 0]);
    }

    let steps = [];
    steps.push(`<div class="matrix-sol-step">Initialize Augmented Matrix [M | I]:</div>`);
    steps.push(formatAugmentedMatrixHTML(aug));

    // Gaussian elimination forward and back
    for (let i = 0; i < dim; i++) {
        // Find pivot 
        let pivotRow = i;
        for (let r = i + 1; r < dim; r++) {
            if (Math.abs(aug[r][i]) > Math.abs(aug[pivotRow][i])) {
                pivotRow = r;
            }
        }

        // Swap rows
        if (pivotRow !== i) {
            const temp = aug[i];
            aug[i] = aug[pivotRow];
            aug[pivotRow] = temp;
            steps.push(`<div class="matrix-sol-step">Swap Row ${i + 1} with Row ${pivotRow + 1}:</div>`);
            steps.push(formatAugmentedMatrixHTML(aug));
        }

        const pivotVal = aug[i][i];
        if (Math.abs(pivotVal) < 1e-9) {
            return `<div class="matrix-sol-step" style="border-color:#ef4444; color:#fca5a5;">M matrix is singular (Det = 0). Inverse cannot be solved.</div>`;
        }

        // Scale pivot row
        if (Math.abs(pivotVal - 1) > 1e-9) {
            for (let c = 0; c < 2 * dim; c++) {
                aug[i][c] /= pivotVal;
            }
            steps.push(`<div class="matrix-sol-step">Scale Row ${i + 1} by 1 / ${pivotVal.toFixed(2)}:</div>`);
            steps.push(formatAugmentedMatrixHTML(aug));
        }

        // Eliminate column elements
        for (let r = 0; r < dim; r++) {
            if (r !== i) {
                const multiplier = aug[r][i];
                if (Math.abs(multiplier) > 1e-9) {
                    for (let c = 0; c < 2 * dim; c++) {
                        aug[r][c] -= multiplier * aug[i][c];
                    }
                    steps.push(`<div class="matrix-sol-step">Replace Row ${r + 1} with Row ${r + 1} - (${multiplier.toFixed(2)} &middot; Row ${i + 1}):</div>`);
                    steps.push(formatAugmentedMatrixHTML(aug));
                }
            }
        }
    }

    // Extract inverse matrix
    const inv = aug.map(row => row.slice(dim));
    steps.push(`<div class="matrix-sol-step">Augmented matrix reduced. Right hand side contains M⁻¹:</div>`);
    steps.push(`
        <div style="font-family:monospace; background:rgba(0,0,0,0.3); padding:8px; border-radius:6px; color:#00e5ff">
            [ ${inv[0][0].toFixed(3)}, ${inv[0][1].toFixed(3)}, ${inv[0][2].toFixed(3)} ;<br>
              ${inv[1][0].toFixed(3)}, ${inv[1][1].toFixed(3)}, ${inv[1][2].toFixed(3)} ;<br>
              ${inv[2][0].toFixed(3)}, ${inv[2][1].toFixed(3)}, ${inv[2][2].toFixed(3)} ]
        </div>
    `);

    return steps.join('');
}

function formatAugmentedMatrixHTML(aug) {
    let rowsHTML = aug.map(row => {
        let left = row.slice(0, 3).map(v => v.toFixed(1).padStart(5, ' ')).join(' ');
        let right = row.slice(3).map(v => v.toFixed(1).padStart(5, ' ')).join(' ');
        return `[ ${left} | ${right} ]`;
    }).join('<br>');

    return `<div style="font-family: monospace; font-size:10px; background:rgba(255,255,255,0.02); padding:6px; border-radius:6px; margin: 4px 0 10px; color:var(--text-secondary); line-height:1.4;">${rowsHTML}</div>`;
}

// Reset functions
function resetMathModule() {
    graphState.zoom = 30;
    graphState.offsetX = 0;
    graphState.offsetY = 0;
    graphState.activeMode = 'move';
    graphState.selectedFunc = 'sin';
    graphState.tangentX = 0;
    graphState.integralA = -4;
    graphState.integralB = 4;
    graphState.integralN = 20;

    // Reset controls
    document.getElementById('math-func-select').value = 'sin';
    document.getElementById('custom-equation-input-group').style.display = 'none';

    // Sliders
    document.getElementById('tangent-x-slider').value = 0;
    document.getElementById('tangent-x-val').textContent = "0.0";

    document.getElementById('integral-a').value = -4;
    document.getElementById('integral-a-val').textContent = "-4.0";

    document.getElementById('integral-b').value = 4;
    document.getElementById('integral-b-val').textContent = "4.0";

    document.getElementById('integral-n').value = 20;
    document.getElementById('integral-n-val').textContent = "20";

    document.querySelector('input[name="math-mode"][value="move"]').checked = true;
    document.getElementById('controls-derivative').style.display = 'none';
    document.getElementById('controls-integral').style.display = 'none';

    // Matrix settings reset
    document.getElementById('m00').value = 2;
    document.getElementById('m01').value = 1;
    document.getElementById('m02').value = 0;
    document.getElementById('m10').value = 0.5;
    document.getElementById('m11').value = 1.5;
    document.getElementById('m12').value = 0;
    document.getElementById('m20').value = 0;
    document.getElementById('m21').value = 0;
    document.getElementById('m22').value = 1;
    toggleMatrixDimensions(2);

    document.getElementById('matrix-solutions-output').textContent = 'Compute determinant or operations to view steps.';

    drawGraph();
    drawMatrixSpace();

    // Reset vectors
    document.getElementById('vec-ax').value = 4;
    document.getElementById('vec-ax-val').textContent = "4.0";
    document.getElementById('vec-ay').value = 3;
    document.getElementById('vec-ay-val').textContent = "3.0";
    document.getElementById('vec-bx').value = -3;
    document.getElementById('vec-bx-val').textContent = "-3.0";
    document.getElementById('vec-by').value = 4;
    document.getElementById('vec-by-val').textContent = "4.0";

    vectorState.ax = 4;
    vectorState.ay = 3;
    vectorState.bx = -3;
    vectorState.by = 4;

    updateVectorMath();
}

function setVectorPresetVals(ax, ay, bx, by) {
    document.getElementById('vec-ax').value = ax;
    document.getElementById('vec-ax-val').textContent = ax.toFixed(1);
    document.getElementById('vec-ay').value = ay;
    document.getElementById('vec-ay-val').textContent = ay.toFixed(1);
    document.getElementById('vec-bx').value = bx;
    document.getElementById('vec-bx-val').textContent = bx.toFixed(1);
    document.getElementById('vec-by').value = by;
    document.getElementById('vec-by-val').textContent = by.toFixed(1);

    vectorState.ax = ax;
    vectorState.ay = ay;
    vectorState.bx = bx;
    vectorState.by = by;

    updateVectorMath();
}

function updateVectorMath() {
    if (!vectorCanvas) return;
    drawVectorSpace();

    const ax = vectorState.ax;
    const ay = vectorState.ay;
    const bx = vectorState.bx;
    const by = vectorState.by;

    const sumX = ax + bx;
    const sumY = ay + by;
    const dot = ax * bx + ay * by;
    const cross = ax * by - ay * bx;

    const magA = Math.sqrt(ax * ax + ay * ay);
    const magB = Math.sqrt(bx * bx + by * by);
    let angleDeg = 0;
    if (magA > 0 && magB > 0) {
        const cosTheta = Math.max(-1, Math.min(1, dot / (magA * magB)));
        angleDeg = Math.acos(cosTheta) * 180 / Math.PI;
    }

    document.getElementById('calc-vec-a').textContent = `${ax.toFixed(1)}, ${ay.toFixed(1)}`;
    document.getElementById('calc-vec-b').textContent = `${bx.toFixed(1)}, ${by.toFixed(1)}`;
    document.getElementById('calc-vec-sum').textContent = `[${sumX.toFixed(1)}, ${sumY.toFixed(1)}]`;
    document.getElementById('calc-vec-dot').textContent = dot.toFixed(2);
    document.getElementById('calc-vec-cross').textContent = cross.toFixed(2);
    document.getElementById('calc-vec-angle').innerHTML = `${angleDeg.toFixed(1)}&deg;`;
}

function drawVectorSpace() {
    if (!vectorCanvas) return;
    vectorCtx.clearRect(0, 0, vectorCanvas.width, vectorCanvas.height);

    const width = vectorCanvas.width;
    const height = vectorCanvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    const zoom = Math.min(centerX, centerY) / 12;

    // Draw grid
    vectorCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    vectorCtx.lineWidth = 1;
    for (let x = centerX % zoom; x < width; x += zoom) {
        vectorCtx.beginPath();
        vectorCtx.moveTo(x, 0);
        vectorCtx.lineTo(x, height);
        vectorCtx.stroke();
    }
    for (let y = centerY % zoom; y < height; y += zoom) {
        vectorCtx.beginPath();
        vectorCtx.moveTo(0, y);
        vectorCtx.lineTo(width, y);
        vectorCtx.stroke();
    }

    // Draw Axis lines
    vectorCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    vectorCtx.lineWidth = 2;
    vectorCtx.beginPath();
    vectorCtx.moveTo(0, centerY); vectorCtx.lineTo(width, centerY);
    vectorCtx.moveTo(centerX, 0); vectorCtx.lineTo(centerX, height);
    vectorCtx.stroke();

    const ax = vectorState.ax;
    const ay = vectorState.ay;
    const bx = vectorState.bx;
    const by = vectorState.by;

    const sumX = ax + bx;
    const sumY = ay + by;

    // Draw vector A (Cyan)
    drawVectorArrow(centerX, centerY, centerX + ax * zoom, centerY - ay * zoom, '#00e5ff', 3, 'A');
    // Draw vector B (Purple/Magenta)
    drawVectorArrow(centerX, centerY, centerX + bx * zoom, centerY - by * zoom, '#bd00ff', 3, 'B');

    // Draw vector A + B (Neon yellow)
    drawVectorArrow(centerX, centerY, centerX + sumX * zoom, centerY - sumY * zoom, '#eab308', 4, 'A+B');

    // Draw dashed components (parallelogram)
    vectorCtx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
    vectorCtx.lineWidth = 1;
    vectorCtx.setLineDash([4, 4]);

    vectorCtx.beginPath();
    vectorCtx.moveTo(centerX + ax * zoom, centerY - ay * zoom);
    vectorCtx.lineTo(centerX + sumX * zoom, centerY - sumY * zoom);
    vectorCtx.stroke();

    vectorCtx.beginPath();
    vectorCtx.moveTo(centerX + bx * zoom, centerY - by * zoom);
    vectorCtx.lineTo(centerX + sumX * zoom, centerY - sumY * zoom);
    vectorCtx.stroke();
    vectorCtx.setLineDash([]);
}

function drawVectorArrow(fromx, fromy, tox, toy, color, width, label) {
    vectorCtx.strokeStyle = color;
    vectorCtx.fillStyle = color;
    vectorCtx.lineWidth = width;

    vectorCtx.beginPath();
    vectorCtx.moveTo(fromx, fromy);
    vectorCtx.lineTo(tox, toy);
    vectorCtx.stroke();

    const angle = Math.atan2(toy - fromy, tox - fromx);
    const headlen = 10;

    vectorCtx.fill();

    vectorCtx.fillStyle = '#fff';
    vectorCtx.font = 'bold 11px Outfit';
    vectorCtx.fillText(label, tox + 8 * Math.cos(angle), toy + 8 * Math.sin(angle));
}

// Fourier Synthesizer Calculations & Rendering
function updateFourierFormula() {
    const type = fourierState.waveType;
    const n = fourierState.harmonics;
    const formulaDisplay = document.getElementById('fourier-eqn-display');
    if (!formulaDisplay) return;

    if (type === 'square') {
        formulaDisplay.innerHTML = `f(t) = 4/&pi; &middot; &Sigma;<sub>i=0</sub><sup>${n - 1}</sup> sin((2i+1)&omega;t) / (2i+1)`;
    } else if (type === 'sawtooth') {
        formulaDisplay.innerHTML = `f(t) = 2/&pi; &middot; &Sigma;<sub>i=1</sub><sup>${n}</sup> (-1)<sup>i+1</sup> &middot; sin(i&omega;t) / i`;
    } else if (type === 'triangle') {
        formulaDisplay.innerHTML = `f(t) = 8/&pi;<sup>2</sup> &middot; &Sigma;<sub>i=0</sub><sup>${n - 1}</sup> (-1)<sup>i</sup> &middot; sin((2i+1)&omega;t) / (2i+1)<sup>2</sup>`;
    }
}

function drawFourierSpace() {
    if (!fourierCanvas) return;
    const w = fourierCanvas.width;
    const h = fourierCanvas.height;
    if (w === 0 || h === 0) return;

    fourierCtx.clearRect(0, 0, w, h);

    // Draw background grid lines
    fourierCtx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
    fourierCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
        fourierCtx.beginPath(); fourierCtx.moveTo(x, 0); fourierCtx.lineTo(x, h); fourierCtx.stroke();
    }
    for (let y = 0; y < h; y += 40) {
        fourierCtx.beginPath(); fourierCtx.moveTo(0, y); fourierCtx.lineTo(w, y); fourierCtx.stroke();
    }

    // Separation axis
    fourierCtx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    fourierCtx.setLineDash([2, 5]);
    fourierCtx.beginPath();
    fourierCtx.moveTo(w * 0.35, 0);
    fourierCtx.lineTo(w * 0.35, h);
    fourierCtx.stroke();
    fourierCtx.setLineDash([]);

    // Mid level line
    const midY = h / 2;
    fourierCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    fourierCtx.beginPath();
    fourierCtx.moveTo(w * 0.35, midY);
    fourierCtx.lineTo(w, midY);
    fourierCtx.stroke();

    // Increment time
    fourierState.time += 0.02 * fourierState.freq;

    // Calculate epicycles
    let cx = w * 0.18;
    let cy = midY;
    let currentX = cx;
    let currentY = cy;

    const baseRadius = Math.min(w * 0.09, h * 0.2);

    for (let i = 0; i < fourierState.harmonics; i++) {
        let n = i + 1;
        let radius = 0;
        let angle = n * fourierState.time;

        if (fourierState.waveType === 'square') {
            n = 2 * i + 1;
            radius = baseRadius * (4 / (Math.PI * n));
            angle = n * fourierState.time;
        } else if (fourierState.waveType === 'sawtooth') {
            radius = baseRadius * (2 / (Math.PI * n)) * (i % 2 === 0 ? 1 : -1);
            angle = n * fourierState.time;
        } else if (fourierState.waveType === 'triangle') {
            n = 2 * i + 1;
            radius = baseRadius * (8 / (Math.PI * Math.PI * n * n)) * (i % 2 === 0 ? 1 : -1);
            angle = n * fourierState.time;
        }

        let prevX = currentX;
        let prevY = currentY;

        currentX += radius * Math.cos(angle);
        currentY += radius * Math.sin(angle);

        // Draw orbital cycles
        fourierCtx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
        fourierCtx.lineWidth = 1;
        fourierCtx.beginPath();
        fourierCtx.arc(prevX, prevY, radius, 0, Math.PI * 2);
        fourierCtx.stroke();

        // Draw rotating linkage vector
        fourierCtx.strokeStyle = i === 0 ? '#3b82f6' : 'rgba(0, 229, 255, 0.3)';
        fourierCtx.lineWidth = 1.2;
        fourierCtx.beginPath();
        fourierCtx.moveTo(prevX, prevY);
        fourierCtx.lineTo(currentX, currentY);
        fourierCtx.stroke();

        // Dot at end
        fourierCtx.fillStyle = '#00e5ff';
        fourierCtx.beginPath();
        fourierCtx.arc(currentX, currentY, 2, 0, Math.PI * 2);
        fourierCtx.fill();
    }

    // Add point to wave history
    fourierState.waveHistory.unshift(currentY);
    if (fourierState.waveHistory.length > w * 0.65) {
        fourierState.waveHistory.pop();
    }

    // Draw tracking connector line from current phasor end to beginning of wave plot
    fourierCtx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    fourierCtx.lineWidth = 1;
    fourierCtx.setLineDash([2, 2]);
    fourierCtx.beginPath();
    fourierCtx.moveTo(currentX, currentY);
    fourierCtx.lineTo(w * 0.38, currentY);
    fourierCtx.stroke();
    fourierCtx.setLineDash([]);

    // Plot final synthesized wave output
    fourierCtx.strokeStyle = '#bd00ff';
    fourierCtx.lineWidth = 2.5;
    fourierCtx.shadowBlur = 6;
    fourierCtx.shadowColor = 'rgba(189, 0, 255, 0.3)';
    fourierCtx.beginPath();

    const startPlotX = w * 0.38;
    for (let idx = 0; idx < fourierState.waveHistory.length; idx++) {
        const plotX = startPlotX + idx;
        const plotY = fourierState.waveHistory[idx];
        if (idx === 0) {
            fourierCtx.moveTo(plotX, plotY);
        } else {
            fourierCtx.lineTo(plotX, plotY);
        }
    }
    fourierCtx.stroke();
    fourierCtx.shadowBlur = 0;
}

// Galton Board Logic & Rendering
function initGaltonBins() {
    const r = galtonState.rows;
    galtonState.bins = new Array(r + 1).fill(0);
    galtonState.balls = [];
    galtonState.accumulatedCount = 0;
    updateGaltonHUD();
}

function clearGaltonBoard() {
    initGaltonBins();
}

function dropGaltonBall() {
    if (!galtonCanvas) return;
    const w = galtonCanvas.width;
    galtonState.balls.push({
        x: w / 2 + (Math.random() * 2 - 1),
        y: 20,
        vx: (Math.random() * 0.4 - 0.2),
        vy: 1,
        radius: 3.5
    });
}

function updateGaltonHUD() {
    const meanDisplay = document.getElementById('galton-lbl-mean');
    const stdDisplay = document.getElementById('galton-lbl-std');
    const ballsDisplay = document.getElementById('galton-lbl-balls');
    if (!meanDisplay) return;

    ballsDisplay.textContent = galtonState.accumulatedCount;

    if (galtonState.accumulatedCount === 0) {
        meanDisplay.textContent = '0.00';
        stdDisplay.textContent = '0.00';
        return;
    }

    // Calculate actual mean and std dev from bins
    let sumX = 0;
    let sumX2 = 0;
    const n = galtonState.rows;

    for (let c = 0; c <= n; c++) {
        const value = c - n / 2;
        const count = galtonState.bins[c];
        sumX += value * count;
        sumX2 += value * value * count;
    }

    const mean = sumX / galtonState.accumulatedCount;
    const variance = (sumX2 / galtonState.accumulatedCount) - (mean * mean);
    const stdDev = Math.sqrt(Math.max(0, variance));

    meanDisplay.textContent = mean.toFixed(2);
    stdDisplay.textContent = stdDev.toFixed(2);
}

function drawGaltonSpace() {
    if (!galtonCanvas) return;
    const w = galtonCanvas.width;
    const h = galtonCanvas.height;
    if (w === 0 || h === 0) return;

    galtonCtx.clearRect(0, 0, w, h);

    // Auto drop balls periodically
    if (galtonState.autoRunning && Math.random() < 0.15) {
        dropGaltonBall();
    }

    // Peg grid parameters
    const rows = galtonState.rows;
    const spacingY = 22;
    const spacingX = 26;
    const startY = 60;
    const pegRadius = 3;

    // Draw Pegs
    galtonCtx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    const pegs = [];
    for (let r = 0; r < rows; r++) {
        const count = r + 1;
        const startX = w / 2 - ((count - 1) * spacingX) / 2;
        for (let c = 0; c < count; c++) {
            const pegX = startX + c * spacingX;
            const pegY = startY + r * spacingY;
            pegs.push({ x: pegX, y: pegY });

            galtonCtx.beginPath();
            galtonCtx.arc(pegX, pegY, pegRadius, 0, Math.PI * 2);
            galtonCtx.fill();
        }
    }

    // Update and Draw Balls
    const gravity = 0.12;
    const bottomY = h - 65;

    galtonCtx.fillStyle = '#ef4444';
    galtonCtx.shadowBlur = 4;
    galtonCtx.shadowColor = 'rgba(239, 68, 68, 0.4)';

    for (let i = galtonState.balls.length - 1; i >= 0; i--) {
        const b = galtonState.balls[i];

        b.vy += gravity;
        b.x += b.vx;
        b.y += b.vy;

        // Collision check with walls
        if (b.x < b.radius) {
            b.x = b.radius;
            b.vx = -b.vx * galtonState.elasticity;
        } else if (b.x > w - b.radius) {
            b.x = w - b.radius;
            b.vx = -b.vx * galtonState.elasticity;
        }

        // Collision check with pegs
        for (let j = 0; j < pegs.length; j++) {
            const p = pegs[j];
            const dist = Math.hypot(b.x - p.x, b.y - p.y);
            const minD = b.radius + pegRadius;

            if (dist < minD) {
                // Overlap resolution
                const overlap = minD - dist;
                const nx = (b.x - p.x) / dist;
                const ny = (b.y - p.y) / dist;

                b.x += nx * overlap;
                b.y += ny * overlap;

                const k = b.vx * nx + b.vy * ny;
                b.vx -= (1 + galtonState.elasticity) * k * nx;
                b.vy -= (1 + galtonState.elasticity) * k * ny;

                b.vx += (Math.random() * 0.4 - 0.2);
                b.vy = Math.abs(b.vy) * 0.95;
            }
        }

        // Check entry to bins
        if (b.y >= bottomY) {
            const lastRowIndex = rows - 1;
            const lastRowStartX = w / 2 - (lastRowIndex * spacingX) / 2;
            const binIndex = Math.round((b.x - lastRowStartX) / spacingX);
            const clampedBin = Math.max(0, Math.min(rows, binIndex));

            galtonState.bins[clampedBin]++;
            galtonState.accumulatedCount++;
            updateGaltonHUD();

            galtonState.balls.splice(i, 1);
            continue;
        }

        // draw ball
        galtonCtx.beginPath();
        galtonCtx.arc(b.x, b.y, b.radius, 0, Math.PI * 2);
        galtonCtx.fill();
    }
    galtonCtx.shadowBlur = 0;

    // Draw bins bars at bottom
    const binCount = rows + 1;
    const lastRowStartX = w / 2 - ((rows - 1) * spacingX) / 2;
    const maxBinVal = Math.max(1, ...galtonState.bins);
    const binMaxHeight = h - bottomY - 5;

    galtonCtx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    galtonCtx.lineWidth = 1.5;

    for (let c = 0; c < binCount; c++) {
        const binCenterX = lastRowStartX + (c - 0.5) * spacingX;

        galtonCtx.beginPath();
        galtonCtx.moveTo(binCenterX, bottomY);
        galtonCtx.lineTo(binCenterX, h);
        galtonCtx.stroke();

        const count = galtonState.bins[c];
        if (count > 0) {
            const barH = (count / maxBinVal) * binMaxHeight;
            galtonCtx.fillStyle = 'rgba(34, 197, 94, 0.7)';
            galtonCtx.fillRect(
                binCenterX + 2,
                h - barH,
                spacingX - 4,
                barH
            );
        }
    }

    if (galtonState.accumulatedCount > 5) {
        galtonCtx.strokeStyle = 'rgba(0, 229, 255, 0.7)';
        galtonCtx.lineWidth = 2.5;
        galtonCtx.setLineDash([4, 2]);
        galtonCtx.beginPath();

        const dev = rows * 0.16;
        for (let lx = 0; lx < w; lx++) {
            const offsetIdx = (lx - w / 2) / spacingX;
            const gaussian = Math.exp(-0.5 * Math.pow(offsetIdx, 2) / Math.pow(dev, 2));

            const curvesY = bottomY - gaussian * binMaxHeight * 0.85;
            if (lx === 0) {
                galtonCtx.moveTo(lx, curvesY);
            } else {
                galtonCtx.lineTo(lx, curvesY);
            }
        }
        galtonCtx.stroke();
        galtonCtx.setLineDash([]);
    }
}

// Coordinate animations
let activeMathSubtabName = 'math-grapher';
function mathAnimationLoop() {
    if (isMathInitialized && typeof state !== 'undefined' && state.activeTab === 'math') {
        const activeSub = document.querySelector('#tab-math .subtab-btn.active');
        if (activeSub) {
            activeMathSubtabName = activeSub.getAttribute('data-subtab');
            if (activeMathSubtabName === 'math-fourier') {
                drawFourierSpace();
            } else if (activeMathSubtabName === 'math-galton') {
                drawGaltonSpace();
            }
        }
    }

    requestAnimationFrame(mathAnimationLoop);
}
