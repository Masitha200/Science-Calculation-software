// Chemistry Laboratory Visualizer Engine
let bohrCanvas, bohrCtx;
let moleculeCanvas, moleculeCtx;
let molecule3dCanvas, molecule3dCtx;
let titrationCanvas, titrationCtx;
let flameCanvas, flameCtx;
let isChemistryInitialized = false;

// pH Titration State
const titrationState = {
    acidVol: 50.0, // ml of HCl
    baseVol: 0.0, // ml NaOH added
    acidCc: 0.1, // M
    baseCc: 0.1, // M
    indicator: 'phenolphthalein',
    autoRunning: false
};

// Flame Spectrography State
const flameState = {
    selectedSalt: 'NaCl',
    heatProgress: 0.0, // 0 = cold loop, 1 = maximum flame excitation color
    loopActive: false
};

const molState = {
    preset: 'H2O',
    rx: 0.3,
    ry: 0.5,
    rz: 0,
    autoSpd: 1.0,
    scale: 100,
    isDragging: false,
    lastX: 0,
    lastY: 0
};

// Sample Periodic Table Element Database (Rich metadata representation)
const elementsData = [
    { num: 1, symbol: 'H', name: 'Hydrogen', mass: '1.008', group: 'nonmetal', period: 1, col: 1, shell: [1], melt: -259.1, boil: -252.9, neg: 2.20, config: '1s¹', fact: 'Most abundant element in the universe. Highly flammable & key star fuel.' },
    { num: 2, symbol: 'He', name: 'Helium', mass: '4.0026', group: 'noble', period: 1, col: 18, shell: [2], melt: -272.2, boil: -268.9, neg: 0.0, config: '1s²', fact: 'Does not burn or react. Superfluid near absolute zero.' },
    { num: 3, symbol: 'Li', name: 'Lithium', mass: '6.94', group: 'alkali', period: 2, col: 1, shell: [2, 1], melt: 180.5, boil: 1342.0, neg: 0.98, config: '[He] 2s¹', fact: 'Lightest metal. Reacts violently with water; floats in oil.' },
    { num: 4, symbol: 'Be', name: 'Beryllium', mass: '9.0122', group: 'alkaline', period: 2, col: 2, shell: [2, 2], melt: 1287.0, boil: 2471.0, neg: 1.57, config: '[He] 2s²', fact: 'Highly toxic but incredibly lightweight; used in space telescopes and missiles.' },
    { num: 5, symbol: 'B', name: 'Boron', mass: '10.81', group: 'metalloid', period: 2, col: 13, shell: [2, 3], melt: 2076.0, boil: 3927.0, neg: 2.04, config: '[He] 2s² 2p¹', fact: 'Used in borosilicate pyrex glassware. Highly heat-resistant metalloid.' },
    { num: 6, symbol: 'C', name: 'Carbon', mass: '12.011', group: 'nonmetal', period: 2, col: 14, shell: [2, 4], melt: 3550.0, boil: 4827.0, neg: 2.55, config: '[He] 2s² 2p²', fact: 'Forms the chemical basis of all known organic life.' },
    { num: 7, symbol: 'N', name: 'Nitrogen', mass: '14.007', group: 'nonmetal', period: 2, col: 15, shell: [2, 5], melt: -210.0, boil: -195.8, neg: 3.04, config: '[He] 2s² 2p³', fact: 'Makes up 78% of Earth\'s atmosphere. Liquid nitrogen is a powerful coolant.' },
    { num: 8, symbol: 'O', name: 'Oxygen', mass: '15.999', group: 'nonmetal', period: 2, col: 16, shell: [2, 6], melt: -218.8, boil: -183.0, neg: 3.44, config: '[He] 2s² 2p⁴', fact: 'Highly reactive gas. Essential for cellular respiration in animals.' },
    { num: 9, symbol: 'F', name: 'Fluorine', mass: '18.998', group: 'halogen', period: 2, col: 17, shell: [2, 7], melt: -219.6, boil: -188.1, neg: 3.98, config: '[He] 2s² 2p⁵', fact: 'Most chemically reactive and electronegative of all elements.' },
    { num: 10, symbol: 'Ne', name: 'Neon', mass: '20.180', group: 'noble', period: 2, col: 18, shell: [2, 8], melt: -248.6, boil: -246.1, neg: 0.0, config: '[He] 2s² 2p⁶', fact: 'Emits a reddish-orange glow in high voltage vacuum discharge tubes.' },
    { num: 11, symbol: 'Na', name: 'Sodium', mass: '22.990', group: 'alkali', period: 3, col: 1, shell: [2, 8, 1], melt: 97.79, boil: 882.8, neg: 0.93, config: '[Ne] 3s¹', fact: 'Soft alkali metal. Explodes in water. Standard table salt component.' },
    { num: 12, symbol: 'Mg', name: 'Magnesium', mass: '24.305', group: 'alkaline', period: 3, col: 2, shell: [2, 8, 2], melt: 650.0, boil: 1090.0, neg: 1.31, config: '[Ne] 3s²', fact: 'Burns in air with a blinding white light. Key biology chlorophyll ion.' },
    { num: 13, symbol: 'Al', name: 'Aluminium', mass: '26.982', group: 'post-transition', period: 3, col: 13, shell: [2, 8, 3], melt: 660.3, boil: 2519.0, neg: 1.61, config: '[Ne] 3s² 3p¹', fact: 'Most abundant metal in Earth\'s crust; does not rust easily.' },
    { num: 14, symbol: 'Si', name: 'Silicon', mass: '28.085', group: 'metalloid', period: 3, col: 14, shell: [2, 8, 4], melt: 1414.0, boil: 3265.0, neg: 1.90, config: '[Ne] 3s² 3p²', fact: 'Primary semiconductor material in computing and microchips.' },
    { num: 15, symbol: 'P', name: 'Phosphorus', mass: '30.974', group: 'nonmetal', period: 3, col: 15, shell: [2, 8, 5], melt: 44.15, boil: 280.5, neg: 2.19, config: '[Ne] 3s² 3p³', fact: 'Found in matchups and DNA links. Highly toxic white phosphorus glows in the dark.' },
    { num: 16, symbol: 'S', name: 'Sulfur', mass: '32.06', group: 'nonmetal', period: 3, col: 16, shell: [2, 8, 6], melt: 115.2, boil: 444.6, neg: 2.58, config: '[Ne] 3s² 3p⁴', fact: 'Produces a strong rotten egg smell when bonded; burns with a blue flame.' },
    { num: 17, symbol: 'Cl', name: 'Chlorine', mass: '35.45', group: 'halogen', period: 3, col: 17, shell: [2, 8, 7], melt: -101.5, boil: -34.04, neg: 3.16, config: '[Ne] 3s² 3p⁵', fact: 'Highly swimming pool sanitiser gas. Greenish toxic gas in pure state.' },
    { num: 18, symbol: 'Ar', name: 'Argon', mass: '39.948', group: 'noble', period: 3, col: 18, shell: [2, 8, 8], melt: -189.3, boil: -185.8, neg: 0.0, config: '[Ne] 3s² 3p⁶', fact: 'Used in incandescent light bulbs to prevent filament oxidisation.' },
    { num: 19, symbol: 'K', name: 'Potassium', mass: '39.098', group: 'alkali', period: 4, col: 1, shell: [2, 8, 8, 1], melt: 63.5, boil: 759.0, neg: 0.82, config: '[Ar] 4s¹', fact: 'Reacts violently with air/water. Rich in bananas, keeps nerves firing.' },
    { num: 20, symbol: 'Ca', name: 'Calcium', mass: '40.078', group: 'alkaline', period: 4, col: 2, shell: [2, 8, 8, 2], melt: 842.0, boil: 1484.0, neg: 1.00, config: '[Ar] 4s²', fact: 'Primary building block of bone and tooth structures, chalk, and cement.' },
    { num: 26, symbol: 'Fe', name: 'Iron', mass: '55.845', group: 'transition', period: 4, col: 8, shell: [2, 8, 14, 2], melt: 1538.0, boil: 2862.0, neg: 1.83, config: '[Ar] 3d⁶ 4s²', fact: 'Core element of steel construction; binds oxygen in blood hemoglobin.' },
    { num: 29, symbol: 'Cu', name: 'Copper', mass: '63.546', group: 'transition', period: 4, col: 11, shell: [2, 8, 18, 1], melt: 1085.0, boil: 2562.0, neg: 1.90, config: '[Ar] 3d¹⁰ 4s¹', fact: 'Excellent electrical and heat conductor. Green patina forms when oxidized.' },
    { num: 79, symbol: 'Au', name: 'Gold', mass: '196.97', group: 'transition', period: 6, col: 11, shell: [2, 8, 18, 32, 18, 1], melt: 1064.0, boil: 2856.0, neg: 2.54, config: '[Xe] 4f¹⁴ 5d¹⁰ 6s¹', fact: 'Extremely inert, malleable, and beautiful noble metal. High value.' }
];

// Bohr model drawing variables
const bohrState = {
    selectedElementNum: 1,
    angle: 0
};

// Molecule display variables
const balancerState = {
    balanced: false,
    reactants: [],
    products: []
};

// Main chemistry module initialize
function initChemistryModule() {
    if (isChemistryInitialized) {
        resizeChemistryCanvases();
        renderPeriodicTable();
        return;
    }

    bohrCanvas = document.getElementById('bohr-canvas');
    bohrCtx = bohrCanvas.getContext('2d');

    moleculeCanvas = document.getElementById('molecule-canvas');
    moleculeCtx = moleculeCanvas.getContext('2d');

    molecule3dCanvas = document.getElementById('molecule-3d-canvas');
    molecule3dCtx = molecule3dCanvas.getContext('2d');

    // Setup filter event listeners
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filterGroup = btn.getAttribute('data-filter');
            filterPeriodicElements(filterGroup);
        });
    });

    // Balancer submit
    document.getElementById('btn-balance-equation').addEventListener('click', balanceEquationAction);

    // 3D Molecule Controls
    document.getElementById('molecule-preset').addEventListener('change', (e) => {
        molState.preset = e.target.value;
        updateMolecule3DProperties();
    });

    document.getElementById('mol-rotation-speed').addEventListener('input', (e) => {
        molState.autoSpd = parseFloat(e.target.value);
        document.getElementById('mol-spd-val').textContent = molState.autoSpd.toFixed(1);
    });

    document.getElementById('mol-atom-scale').addEventListener('input', (e) => {
        molState.scale = parseFloat(e.target.value);
        document.getElementById('mol-scale-val').textContent = `${molState.scale}%`;
    });

    // Mouse drag rotation listeners
    molecule3dCanvas.addEventListener('mousedown', (e) => {
        molState.isDragging = true;
        const rect = molecule3dCanvas.getBoundingClientRect();
        molState.lastX = e.clientX - rect.left;
        molState.lastY = e.clientY - rect.top;
    });

    window.addEventListener('mouseup', () => {
        molState.isDragging = false;
    });

    molecule3dCanvas.addEventListener('mousemove', (e) => {
        if (!molState.isDragging) return;
        const rect = molecule3dCanvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const dx = mx - molState.lastX;
        const dy = my - molState.lastY;

        molState.ry += dx * 0.01;
        molState.rx += dy * 0.01;

        molState.lastX = mx;
        molState.lastY = my;
    });

    // Titration Event Listeners
    titrationCanvas = document.getElementById('titration-canvas');
    titrationCtx = titrationCanvas.getContext('2d');

    document.getElementById('tit-acid-conc').addEventListener('input', (e) => {
        titrationState.acidCc = parseFloat(e.target.value);
        document.getElementById('tit-acid-val').textContent = titrationState.acidCc.toFixed(2) + ' M';
        resetTitration();
    });

    document.getElementById('tit-base-conc').addEventListener('input', (e) => {
        titrationState.baseCc = parseFloat(e.target.value);
        document.getElementById('tit-base-val').textContent = titrationState.baseCc.toFixed(2) + ' M';
        resetTitration();
    });

    document.getElementById('tit-drop-vol').addEventListener('input', (e) => {
        document.getElementById('tit-drop-val').textContent = parseFloat(e.target.value).toFixed(1) + ' mL/drop';
    });

    document.getElementById('tit-indicator').addEventListener('change', (e) => {
        titrationState.indicator = e.target.value;
    });

    document.getElementById('btn-tit-drop').addEventListener('click', () => {
        const dropRate = parseFloat(document.getElementById('tit-drop-vol').value);
        addTitrateBaseDrop(dropRate);
    });

    document.getElementById('btn-tit-auto').addEventListener('click', (e) => {
        titrationState.autoRunning = !titrationState.autoRunning;
        e.target.textContent = titrationState.autoRunning ? 'Stop Auto Titrate' : 'Auto Titrate';
    });

    document.getElementById('btn-tit-reset').addEventListener('click', () => {
        resetTitration();
    });

    // Flame Spectrograph event listeners
    flameCanvas = document.getElementById('flame-canvas');
    flameCtx = flameCanvas.getContext('2d');

    document.getElementById('flame-element-select').addEventListener('change', (e) => {
        flameState.selectedSalt = e.target.value;
        flameState.heatProgress = 0.0;
        flameState.loopActive = false;
        const strikeBtn = document.getElementById('btn-flame-strike');
        if (strikeBtn) {
            strikeBtn.textContent = 'Insert Loop to Flame';
        }
        updateFlameSpectraHUD();
    });

    document.getElementById('btn-flame-strike').addEventListener('click', (e) => {
        flameState.loopActive = !flameState.loopActive;
        e.target.textContent = flameState.loopActive ? 'Withdraw Loop' : 'Insert Loop to Flame';
        if (flameState.loopActive) {
            flameState.heatProgress = 0.0;
        }
    });

    resetTitration();
    updateFlameSpectraHUD();

    isChemistryInitialized = true;
    resizeChemistryCanvases();
    renderPeriodicTable();

    // Default element select
    selectElement(1);

    // 3D molecule properties update
    updateMolecule3DProperties();

    // Start Bohr Orbit animation loop
    animateBohrModel();

    // Start 3D molecule animation loop
    animateMolecule3D();

    // Start general chemistry loops
    requestAnimationFrame(chemistryAnimationLoop);
}

function resizeChemistryCanvases() {
    if (!bohrCanvas) return;
    const bRect = bohrCanvas.parentElement.getBoundingClientRect();
    bohrCanvas.width = bRect.width;
    bohrCanvas.height = bRect.height;

    const mRect = moleculeCanvas.parentElement.getBoundingClientRect();
    moleculeCanvas.width = mRect.width;
    moleculeCanvas.height = mRect.height;

    if (molecule3dCanvas) {
        const dRect = molecule3dCanvas.parentElement.getBoundingClientRect();
        molecule3dCanvas.width = dRect.width;
        molecule3dCanvas.height = dRect.height;
    }

    if (titrationCanvas) {
        const tRect = titrationCanvas.parentElement.getBoundingClientRect();
        titrationCanvas.width = tRect.width;
        titrationCanvas.height = tRect.height;
    }

    if (flameCanvas) {
        const fRect = flameCanvas.parentElement.getBoundingClientRect();
        flameCanvas.width = fRect.width;
        flameCanvas.height = fRect.height;
    }
}

window.addEventListener('resize', () => {
    if (isChemistryInitialized) {
        resizeChemistryCanvases();
        drawBohrAtom();
        drawMolecules();
    }
});

// Programmatic periodic table rendering
function renderPeriodicTable() {
    const grid = document.getElementById('periodic-elements-grid');
    if (!grid) return;
    grid.innerHTML = '';

    // Create elements positioning grid cells
    for (let row = 1; row <= 7; row++) {
        for (let col = 1; col <= 18; col++) {
            // Find if standard element coordinates match
            const element = elementsData.find(e => e.period === row && e.col === col);

            const cell = document.createElement('div');
            if (element) {
                cell.className = `element-cell bg-${element.group}`;
                cell.setAttribute('data-num', element.num);
                cell.setAttribute('data-group', element.group);

                cell.innerHTML = `
                    <span class="cell-num">${element.num}</span>
                    <span class="cell-symbol">${element.symbol}</span>
                    <span class="cell-name">${element.name}</span>
                `;

                // Clicking selects active element details
                cell.addEventListener('click', () => {
                    document.querySelectorAll('.element-cell').forEach(c => c.classList.remove('active-sel'));
                    cell.classList.add('active-sel');
                    selectElement(element.num);
                });

                if (element.num === bohrState.selectedElementNum) {
                    cell.classList.add('active-sel');
                }
            } else {
                cell.className = 'element-cell empty-cell';
                cell.style.opacity = 0; // invisible spacing
                cell.style.pointerEvents = 'none';
            }
            // Grid positions
            cell.style.gridColumn = col;
            cell.style.gridRow = row;
            grid.appendChild(cell);
        }
    }
}

function filterPeriodicElements(group) {
    document.querySelectorAll('.element-cell:not(.empty-cell)').forEach(cell => {
        const elGroup = cell.getAttribute('data-group');
        if (group === 'all' || elGroup === group) {
            cell.classList.remove('dimmed');
        } else {
            cell.classList.add('dimmed');
        }
    });
}

function selectElement(num) {
    const el = elementsData.find(e => e.num === num);
    if (!el) return;

    bohrState.selectedElementNum = num;

    // Details pane updates
    document.getElementById('details-num').textContent = el.num;
    document.getElementById('details-symbol').textContent = el.symbol;
    document.getElementById('details-name').textContent = el.name;
    document.getElementById('details-mass').textContent = `${el.mass} u`;

    // Format group text
    const displayGroups = {
        nonmetal: 'Reactive Nonmetal', noble: 'Noble Gas', alkali: 'Alkali Metal',
        alkaline: 'Alkaline Earth', metalloid: 'Metalloid', halogen: 'Halogen',
        transition: 'Transition Metal', 'post-transition': 'Post-transition Metal', lanact: 'Lanthanide/Actinide'
    };
    document.getElementById('details-group-tag').textContent = displayGroups[el.group] || el.group;
    document.getElementById('details-group-tag').className = `element-group-tag text-${el.group}`;

    // Highlight badge border color
    const colors = {
        nonmetal: '#3b82f6', noble: '#a855f7', alkali: '#ef4448',
        alkaline: '#f97316', metalloid: '#eab308', halogen: '#ec4899',
        transition: '#64748b', 'post-transition': '#0ea5e9', lanact: '#14b8a6'
    };
    const highlightColor = colors[el.group] || '#00ff88';
    document.getElementById('details-symbol-badge').style.borderColor = highlightColor;
    document.getElementById('details-symbol-badge').style.boxShadow = `0 0 12px ${highlightColor}40`;

    // Text properties readouts
    document.getElementById('details-config').textContent = el.config;
    document.getElementById('details-melt').textContent = el.melt !== null ? `${el.melt} °C` : 'N/A';
    document.getElementById('details-boil').textContent = el.boil !== null ? `${el.boil} °C` : 'N/A';
    document.getElementById('details-neg').textContent = el.neg !== 0 ? el.neg : 'N/A';
    document.getElementById('details-fact').textContent = el.fact;

    drawBohrAtom();
}

// Atom orbit drawing
function drawBohrAtom() {
    if (!bohrCanvas) return;

    bohrCtx.clearRect(0, 0, bohrCanvas.width, bohrCanvas.height);

    const el = elementsData.find(e => e.num === bohrState.selectedElementNum);
    if (!el) return;

    const cx = bohrCanvas.width / 2;
    const cy = bohrCanvas.height / 2;

    // Draw Nucleus sphere
    const colors = {
        nonmetal: '#3b82f6', noble: '#a855f7', alkali: '#ef4448',
        alkaline: '#f97316', metalloid: '#eab308', halogen: '#ec4899',
        transition: '#64748b', 'post-transition': '#0ea5e9', lanact: '#14b8a6'
    };
    const primaryColor = colors[el.group] || '#00ff88';

    // Proton / Neutron cluster drawing
    bohrCtx.shadowBlur = 10;
    bohrCtx.shadowColor = primaryColor;
    bohrCtx.fillStyle = primaryColor;
    bohrCtx.beginPath();
    bohrCtx.arc(cx, cy, 14, 0, Math.PI * 2);
    bohrCtx.fill();
    bohrCtx.shadowBlur = 0; // reset

    // Text on nucleus symbol
    bohrCtx.fillStyle = '#000';
    bohrCtx.font = 'bold 9px JetBrains Mono';
    bohrCtx.textAlign = 'center';
    bohrCtx.textBaseline = 'middle';
    bohrCtx.fillText(`+${el.num}p`, cx, cy);

    // Draw concentric electron orbital shells
    const shellData = el.shell;
    for (let i = 0; i < shellData.length; i++) {
        const radius = 32 + i * 22;
        const count = shellData[i];

        // Draw shell circle
        bohrCtx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        bohrCtx.lineWidth = 1;
        bohrCtx.beginPath();
        bohrCtx.arc(cx, cy, radius, 0, Math.PI * 2);
        bohrCtx.stroke();

        // Draw revolving electrons on shell
        // Rotate shell particles with varying speed per level
        const orbitalSpeedFactor = 1.0 - (i * 0.15); // outer shells orbit slower
        const shellAngle = bohrState.angle * orbitalSpeedFactor;

        for (let j = 0; j < count; j++) {
            // Distribute electrons equally around circle
            const angleOffset = (j / count) * Math.PI * 2 + shellAngle;

            const ex = cx + radius * Math.cos(angleOffset);
            const ey = cy + radius * Math.sin(angleOffset);

            // Draw glowing blue electron dot
            bohrCtx.fillStyle = '#00e5ff';
            bohrCtx.shadowBlur = 6;
            bohrCtx.shadowColor = '#00e5ff';
            bohrCtx.beginPath();
            bohrCtx.arc(ex, ey, 3.5, 0, Math.PI * 2);
            bohrCtx.fill();
            bohrCtx.shadowBlur = 0;
        }
    }
}

function animateBohrModel() {
    if (isChemistryInitialized && typeof state !== 'undefined' && state.activeTab === 'chemistry' && activeChemistrySubtabName === 'chemistry-periodic') {
        bohrState.angle += 0.015;
        drawBohrAtom();
    }
    requestAnimationFrame(animateBohrModel);
}

// Stoichiometry Balancer operations
function balanceEquationAction() {
    const rawEq = document.getElementById('chem-input-eq').value;
    const outputEl = document.getElementById('balancer-results-output');

    try {
        const result = solveChemicalEquation(rawEq);

        // Draw success output
        let reactantsJoin = result.reactants.map(r => `${r.coeff > 1 ? r.coeff : ''}${r.expr}`).join(' + ');
        let productsJoin = result.products.map(p => `${p.coeff > 1 ? p.coeff : ''}${p.expr}`).join(' + ');

        let successHTML = `
            <div class="chem-bal-success">
                <div class="chem-final-eq">${reactantsJoin} &rarr; ${productsJoin}</div>
                <div class="matrix-sol-step">Conservation system values balanced:</div>
                <div style="font-family: monospace; font-size:11px; color:#cbd5e1; line-height:1.5;">
        `;

        // List coefficient fractions solves
        result.compounds.forEach(comp => {
            successHTML += `Compound <strong style="color:#00ff88">${comp.expr}</strong> coefficient solver = ${comp.coeff}<br>`;
        });

        successHTML += `
                </div>
            </div>
        `;

        outputEl.innerHTML = successHTML;

        // Set state for drawing molecules visualizer
        balancerState.reactants = result.reactants;
        balancerState.products = result.products;
        balancerState.balanced = true;

        drawMolecules();

    } catch (err) {
        outputEl.innerHTML = `<span style="color:#ef4444;">Balancer error: ${err.message}</span>`;
        balancerState.balanced = false;
        drawMolecules();
    }
}

function setReactionPreset(eq) {
    document.getElementById('chem-input-eq').value = eq;
    balanceEquationAction();
}

// Chemistry Balancer solver mathematical core
function solveChemicalEquation(eqCode) {
    // Standard balancer parse: split left and right
    const sides = eqCode.replace(/\s+/g, '').split(/[==\->]/).filter(s => s !== '');
    if (sides.length !== 2) {
        throw new Error("Equation must contain reactants and products separated by '=' or '->'.");
    }

    const reactantsRaw = sides[0].split('+');
    const productsRaw = sides[1].split('+');

    // Parse compound elements counts
    // e.g. "C3H8" => {C:3, H:8}
    const parseCompound = (expr) => {
        const counts = {};
        // Match elements: Capital followed by lowercase, followed by optional number
        const matches = expr.match(/([A-Z][a-z]*)(\d*)/g);
        if (!matches || matches.join('') !== expr) {
            throw new Error(`Invalid chemical compound formula structure: "${expr}"`);
        }

        matches.forEach(m => {
            const parts = m.match(/([A-Z][a-z]*)(\d*)/);
            const element = parts[1];
            const count = parts[2] === '' ? 1 : parseInt(parts[2]);
            counts[element] = (counts[element] || 0) + count;
        });
        return counts;
    };

    const reactants = reactantsRaw.map(r => ({ expr: r, counts: parseCompound(r), side: -1 })); // side -1 for reactants
    const products = productsRaw.map(p => ({ expr: p, counts: parseCompound(p), side: 1 })); // side 1 for products

    const allCompounds = [...reactants, ...products];

    // Build set of all unique chemical elements
    const elementsSet = new Set();
    allCompounds.forEach(c => {
        Object.keys(c.counts).forEach(el => elementsSet.add(el));
    });

    const elementsList = Array.from(elementsSet);

    // Build system matrix
    // Rows = elements, Columns = compounds
    // e.g. for C, a_C * c_a + b_C * c_b - c_C * c_c - d_C * c_d = 0
    const A = [];
    elementsList.forEach((el, r) => {
        const row = [];
        allCompounds.forEach(c => {
            const val = c.counts[el] || 0;
            // Reactants coefficients count negative on LHS equations
            row.push(v_sideScale(c.side, val));
        });
        A.push(row);
    });

    function v_sideScale(side, val) {
        return side === -1 ? val : -val;
    }

    // Solve matrix null space (kernel) coefficients
    const coeffs = nullspace(A);

    if (!coeffs) {
        throw new Error("Unable to resolve a single unique integer balancing solution.");
    }

    // Map solved integer coefficients back
    allCompounds.forEach((comp, idx) => {
        comp.coeff = coeffs[idx];
    });

    return {
        reactants: reactants,
        products: products,
        compounds: allCompounds
    };
}

// Find integer nullspace vectors via reduction
function nullspace(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;

    // Solve via Gaussian reduction
    let aug = matrix.map(row => [...row]);

    let lead = 0;
    for (let r = 0; r < rows; r++) {
        if (lead >= cols) break;
        let i = r;
        while (aug[i][lead] === 0) {
            i++;
            if (i === rows) {
                i = r;
                lead++;
                if (lead === cols) return null;
            }
        }

        let temp = aug[r];
        aug[r] = aug[i];
        aug[i] = temp;

        const lv = aug[r][lead];
        for (let c = 0; c < cols; c++) aug[r][c] /= lv;

        for (let j = 0; j < rows; j++) {
            if (j !== r) {
                const lv2 = aug[j][lead];
                for (let c = 0; c < cols; c++) aug[j][c] -= lv2 * aug[r][c];
            }
        }
        lead++;
    }

    // Extract free variables (usually the last column coefficient)
    // E.g. we assume coeff[last] = 1, and work backwards
    // A simple solver for chemical equations is often fully specified with cols = rows + 1
    // We guess fraction ratios
    const solution = new Array(cols).fill(0);
    solution[cols - 1] = 1.0;

    // Backward substitution
    for (let r = rows - 1; r >= 0; r--) {
        // Find leading variable
        let pivotCol = -1;
        for (let c = 0; c < cols - 1; c++) {
            if (Math.abs(aug[r][c] - 1.0) < 1e-9) {
                pivotCol = c;
                break;
            }
        }

        if (pivotCol !== -1) {
            // Solve for leading variable
            solution[pivotCol] = -aug[r][cols - 1];
        }
    }

    // Check if solution has valid counts
    if (solution.some(v => v <= 0)) {
        // Retry reversing direction
        for (let i = 0; i < cols; i++) solution[i] = -solution[i];
        if (solution.some(v => v <= 0)) return null;
    }

    // Convert float fraction coefficients to whole integers (least common multiple scaling)
    // We try scaling up to denominator of 30
    for (let scale = 1; scale <= 60; scale++) {
        const candidate = solution.map(v => Math.round(v * scale));
        let error = 0;
        for (let i = 0; i < cols; i++) {
            error += Math.abs(candidate[i] - solution[i] * scale);
        }

        if (error < 1e-5) {
            return candidate;
        }
    }

    return null;
}

// Molecule visual drawing canvas representation
function drawMolecules() {
    if (!moleculeCanvas) return;

    moleculeCtx.clearRect(0, 0, moleculeCanvas.width, moleculeCanvas.height);

    if (!balancerState.balanced) {
        moleculeCtx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        moleculeCtx.font = '14px Outfit';
        moleculeCtx.textAlign = 'center';
        moleculeCtx.fillText('Run solver to draw balanced stoichiometric molecular models.', moleculeCanvas.width / 2, moleculeCanvas.height / 2);
        return;
    }

    const width = moleculeCanvas.width;
    const height = moleculeCanvas.height;
    const midX = width / 2;

    // Draw boundary line: Reactants side vs Products side
    moleculeCtx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    moleculeCtx.setLineDash([8, 8]);
    moleculeCtx.lineWidth = 1.5;

    moleculeCtx.beginPath();
    moleculeCtx.moveTo(midX, 0);
    moleculeCtx.lineTo(midX, height);
    moleculeCtx.stroke();
    moleculeCtx.setLineDash([]);

    // Title markings
    moleculeCtx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    moleculeCtx.font = '10px JetBrains Mono';
    moleculeCtx.textAlign = 'left';
    moleculeCtx.fillText('REACTANTS (RHS)', 20, 30);
    moleculeCtx.textAlign = 'right';
    moleculeCtx.fillText('PRODUCTS (LHS)', width - 20, 30);

    // Render Reactants
    const rCount = balancerState.reactants.length;
    balancerState.reactants.forEach((c, idx) => {
        // Distribute columns inside left half
        const cellX = (midX - 40) * ((idx + 0.5) / rCount);
        const cellY = height / 2;

        drawCompoundMoleculeStack(c, cellX, cellY, c.coeff);
    });

    // Render Products
    const pCount = balancerState.products.length;
    balancerState.products.forEach((c, idx) => {
        // Distribute columns inside right half
        const cellX = midX + 40 + (midX - 40) * (idx / pCount);
        const cellY = height / 2;

        drawCompoundMoleculeStack(c, cellX + 40, cellY, c.coeff);
    });
}

// Draw a stack/block of balanced molecules floating around
function drawCompoundMoleculeStack(comp, startX, startY, count) {
    const elColors = {
        H: '#ffffff', // White
        He: '#e2e8f0',
        Li: '#a78bfa',
        Be: '#8b5cf6',
        B: '#f59e0b',
        C: '#334155', // Charcoal/Dark gray
        N: '#3b82f6', // Blue
        O: '#ef4444', // Red
        F: '#ec4899',
        Ne: '#f472b6',
        Na: '#a78bfa',
        Mg: '#ec4899',
        Al: '#94a3b8',
        Si: '#64748b',
        P: '#ea580c',
        S: '#eab308', // Yellow
        Cl: '#22c55e', // Green
        Ar: '#a855f7',
        K: '#6366f1',
        Ca: '#acc8ff',
        Fe: '#f97316', // Orange
        Cu: '#f59e0b',
        Au: '#eab308'
    };

    const rAtom = 12;
    const atoms = [];

    // Parse atoms to raw list for drawing layout
    Object.keys(comp.counts).forEach(el => {
        const atomColor = elColors[el] || '#cbd5e1';
        for (let i = 0; i < comp.counts[el]; i++) {
            atoms.push({ element: el, color: atomColor });
        }
    });

    // Draw stack depending on count
    for (let c = 0; c < count; c++) {
        // Float offset for copies
        const ox = (c % 3) * 45 - (Math.min(count, 3) - 1) * 20;
        const oy = Math.floor(c / 3) * 45 - (Math.ceil(count / 3) - 1) * 20;

        const mx = startX + ox;
        const my = startY + oy;

        // Draw bond lines connecting atoms first
        moleculeCtx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
        moleculeCtx.lineWidth = 3;
        for (let i = 0; i < atoms.length; i++) {
            for (let j = i + 1; j < atoms.length; j++) {
                // If small molecule details, connect everything, else connect to first (central atom)
                if (atoms.length < 5 || i === 0) {
                    const ang = (i / atoms.length) * Math.PI * 2;
                    const ang2 = (j / atoms.length) * Math.PI * 2;
                    const rDist = atoms.length === 1 ? 0 : 12;

                    const x1 = mx + rDist * Math.cos(ang);
                    const y1 = my + rDist * Math.sin(ang);
                    const x2 = mx + rDist * Math.cos(ang2);
                    const y2 = my + rDist * Math.sin(ang2);

                    moleculeCtx.beginPath();
                    moleculeCtx.moveTo(x1, y1);
                    moleculeCtx.lineTo(x2, y2);
                    moleculeCtx.stroke();
                }
            }
        }

        // Draw atom body spheres
        atoms.forEach((atom, idx) => {
            // Radial layout from center mx, my
            const angle = (idx / atoms.length) * Math.PI * 2;
            const rDist = atoms.length === 1 ? 0 : 12;

            const ax = mx + rDist * Math.cos(angle);
            const ay = my + rDist * Math.sin(angle);

            // Sphere body
            moleculeCtx.fillStyle = atom.color;
            moleculeCtx.strokeStyle = 'rgba(0,0,0,0.5)';
            moleculeCtx.lineWidth = 1;

            moleculeCtx.beginPath();
            moleculeCtx.arc(ax, ay, rAtom, 0, Math.PI * 2);
            moleculeCtx.fill();
            moleculeCtx.stroke();

            // Text Symbol overlay
            moleculeCtx.fillStyle = (atom.color === '#ffffff' || atom.color === '#e2e8f0') ? '#000' : '#fff';
            moleculeCtx.font = 'bold 9px JetBrains Mono';
            moleculeCtx.textAlign = 'center';
            moleculeCtx.textBaseline = 'middle';
            moleculeCtx.fillText(atom.element, ax, ay);
        });
    }
}

function resetChemistryModule() {
    document.getElementById('chem-input-eq').value = 'C3H8 + O2 = CO2 + H2O';
    document.getElementById('balancer-results-output').textContent = 'Enter an equation or select standard presets to solve matrix coefficient values.';

    // Clear filter
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelector('.filter-btn[data-filter="all"]').classList.add('active');
    filterPeriodicElements('all');

    // Reset selected
    selectElement(1);

    balancerState.reactants = [];
    balancerState.products = [];
    balancerState.balanced = false;

    // Reset 3D molecule selection
    molState.preset = 'H2O';
    molState.rx = 0.3;
    molState.ry = 0.5;
    molState.autoSpd = 1.0;
    molState.scale = 100;

    document.getElementById('molecule-preset').value = 'H2O';
    document.getElementById('mol-rotation-speed').value = 1.0;
    document.getElementById('mol-spd-val').textContent = '1.0';
    document.getElementById('mol-atom-scale').value = 100;
    document.getElementById('mol-scale-val').textContent = '100%';

    updateMolecule3DProperties();
    drawMolecules();
}

// Database of 3D molecule presets
const moleculeData3d = {
    H2O: {
        formula: 'H₂O',
        angle: '104.5°',
        mass: '18.015 g/mol',
        desc: 'A polar inorganic compound that is the main constituent of Earth\'s hydrosphere.',
        atoms: [
            { el: 'O', x: 0, y: 0.2, z: 0, color: '#ef4444', size: 18 },
            { el: 'H', x: 1.1, y: -0.7, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.1, y: -0.7, z: 0, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 }
        ]
    },
    CO2: {
        formula: 'CO₂',
        angle: '180°',
        mass: '44.01 g/mol',
        desc: 'A linear molecule consisting of a carbon atom double bonded to two oxygen atoms.',
        atoms: [
            { el: 'C', x: 0, y: 0, z: 0, color: '#64748b', size: 16 },
            { el: 'O', x: 1.4, y: 0, z: 0, color: '#ef4444', size: 18 },
            { el: 'O', x: -1.4, y: 0, z: 0, color: '#ef4444', size: 18 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 }
        ]
    },
    CH4: {
        formula: 'CH₄',
        angle: '109.5°',
        mass: '16.04 g/mol',
        desc: 'Simplest alkane with tetrahedral molecular structure. Primary component of natural gas.',
        atoms: [
            { el: 'C', x: 0, y: 0, z: 0, color: '#64748b', size: 16 },
            { el: 'H', x: 0, y: 1.3, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: 1.25, y: -0.4, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -0.6, y: -0.4, z: 1.1, color: '#ffffff', size: 12 },
            { el: 'H', x: -0.6, y: -0.4, z: -1.1, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 },
            { from: 0, to: 3 },
            { from: 0, to: 4 }
        ]
    },
    NH3: {
        formula: 'NH₃',
        angle: '107.8°',
        mass: '17.031 g/mol',
        desc: 'Trigonal pyramidal molecule with a single pair of non-bonding electrons on the nitrogen atom.',
        atoms: [
            { el: 'N', x: 0, y: 0.3, z: 0, color: '#3b82f6', size: 17 },
            { el: 'H', x: 1.1, y: -0.4, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -0.55, y: -0.4, z: 0.95, color: '#ffffff', size: 12 },
            { el: 'H', x: -0.55, y: -0.4, z: -0.95, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 },
            { from: 0, to: 3 }
        ]
    },
    C2H5OH: {
        formula: 'C₂H₅OH',
        angle: '109.5°',
        mass: '46.07 g/mol',
        desc: 'Ethanol. Contains two carbon centers, one oxygen atom and six hydrogen atoms.',
        atoms: [
            { el: 'C', x: -0.8, y: -0.3, z: 0, color: '#64748b', size: 16 },
            { el: 'C', x: 0.6, y: 0.3, z: 0, color: '#64748b', size: 16 },
            { el: 'O', x: 1.7, y: -0.6, z: 0, color: '#ef4444', size: 18 },
            { el: 'H', x: 2.5, y: -0.2, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -0.8, y: -1.3, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.3, y: 0.1, z: 0.9, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.3, y: 0.1, z: -0.9, color: '#ffffff', size: 12 },
            { el: 'H', x: 0.6, y: 1.0, z: 0.8, color: '#ffffff', size: 12 },
            { el: 'H', x: 0.6, y: 1.0, z: -0.8, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 1, to: 2 },
            { from: 2, to: 3 },
            { from: 0, to: 4 },
            { from: 0, to: 5 },
            { from: 0, to: 6 },
            { from: 1, to: 7 },
            { from: 1, to: 8 }
        ]
    },
    O2: {
        formula: 'O₂',
        angle: 'N/A',
        mass: '31.998 g/mol',
        desc: 'Oxygen Gas. A diatomic molecule essential for respiration in most living organisms.',
        atoms: [
            { el: 'O', x: 0.8, y: 0, z: 0, color: '#ef4444', size: 18 },
            { el: 'O', x: -0.8, y: 0, z: 0, color: '#ef4444', size: 18 }
        ],
        bonds: [
            { from: 0, to: 1 }
        ]
    },
    N2: {
        formula: 'N₂',
        angle: 'N/A',
        mass: '28.013 g/mol',
        desc: 'Nitrogen Gas. Diatomic gas forming roughly 78% of the Earth\'s atmosphere.',
        atoms: [
            { el: 'N', x: 0.75, y: 0, z: 0, color: '#3b82f6', size: 17 },
            { el: 'N', x: -0.75, y: 0, z: 0, color: '#3b82f6', size: 17 }
        ],
        bonds: [
            { from: 0, to: 1 }
        ]
    },
    HCl: {
        formula: 'HCl',
        angle: 'N/A',
        mass: '36.46 g/mol',
        desc: 'Hydrogen Chloride. A diatomic gas that forms strong hydrochloric acid in water.',
        atoms: [
            { el: 'H', x: -0.9, y: 0, z: 0, color: '#ffffff', size: 12 },
            { el: 'Cl', x: 0.6, y: 0, z: 0, color: '#22c55e', size: 20 }
        ],
        bonds: [
            { from: 0, to: 1 }
        ]
    },
    SO2: {
        formula: 'SO₂',
        angle: '119°',
        mass: '64.066 g/mol',
        desc: 'Sulfur Dioxide. Bent gas released during volcanic outbreaks and fossil fuel combustion.',
        atoms: [
            { el: 'S', x: 0, y: 0.35, z: 0, color: '#eab308', size: 18 },
            { el: 'O', x: 1.15, y: -0.4, z: 0, color: '#ef4444', size: 17 },
            { el: 'O', x: -1.15, y: -0.4, z: 0, color: '#ef4444', size: 17 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 }
        ]
    },
    C2H4: {
        formula: 'C₂H₄',
        angle: '121.3°',
        mass: '28.05 g/mol',
        desc: 'Ethylene. Planar organic molecule containing a carbon-carbon double bond. Fruit ripening agent.',
        atoms: [
            { el: 'C', x: 0.7, y: 0, z: 0, color: '#64748b', size: 16 },
            { el: 'C', x: -0.7, y: 0, z: 0, color: '#64748b', size: 16 },
            { el: 'H', x: 1.3, y: 0.9, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: 1.3, y: -0.9, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.3, y: 0.9, z: 0.9, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.3, y: -0.9, z: -0.9, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 },
            { from: 0, to: 3 },
            { from: 1, to: 4 },
            { from: 1, to: 5 }
        ]
    },
    H2SO4: {
        formula: 'H₂SO₄',
        angle: '109.5°',
        mass: '98.079 g/mol',
        desc: 'Sulfuric Acid. Highly acidic mineral compound structured as a sulfur center with oxygens.',
        atoms: [
            { el: 'S', x: 0, y: 0, z: 0, color: '#eab308', size: 18 },
            { el: 'O', x: 0, y: 1.25, z: 0.5, color: '#ef4444', size: 17 },
            { el: 'O', x: 0, y: -1.25, z: 0.5, color: '#ef4444', size: 17 },
            { el: 'O', x: 1.2, y: 0, z: -0.7, color: '#ef4444', size: 17 },
            { el: 'O', x: -1.2, y: 0, z: -0.7, color: '#ef4444', size: 17 },
            { el: 'H', x: 1.9, y: 0.5, z: -1.1, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.9, y: -0.5, z: -1.1, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 0, to: 2 },
            { from: 0, to: 3 },
            { from: 0, to: 4 },
            { from: 3, to: 5 },
            { from: 4, to: 6 }
        ]
    },
    C6H6: {
        formula: 'C₆H₆',
        angle: '120°',
        mass: '78.11 g/mol',
        desc: 'Benzene. A cyclic planar aromatic hydrocarbon compound formed by a hexagon ring of carbons and alternating pi bonds.',
        atoms: [
            { el: 'C', x: 1.2, y: 0, z: 0, color: '#64748b', size: 16 },
            { el: 'C', x: 0.6, y: 1.04, z: 0.05, color: '#64748b', size: 16 },
            { el: 'C', x: -0.6, y: 1.04, z: -0.05, color: '#64748b', size: 16 },
            { el: 'C', x: -1.2, y: 0, z: 0, color: '#64748b', size: 16 },
            { el: 'C', x: -0.6, y: -1.04, z: 0.05, color: '#64748b', size: 16 },
            { el: 'C', x: 0.6, y: -1.04, z: -0.05, color: '#64748b', size: 16 },
            { el: 'H', x: 2.1, y: 0, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: 1.05, y: 1.82, z: 0.1, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.05, y: 1.82, z: -0.1, color: '#ffffff', size: 12 },
            { el: 'H', x: -2.1, y: 0, z: 0, color: '#ffffff', size: 12 },
            { el: 'H', x: -1.05, y: -1.82, z: 0.1, color: '#ffffff', size: 12 },
            { el: 'H', x: 1.05, y: -1.82, z: -0.1, color: '#ffffff', size: 12 }
        ],
        bonds: [
            { from: 0, to: 1 },
            { from: 1, to: 2 },
            { from: 2, to: 3 },
            { from: 3, to: 4 },
            { from: 4, to: 5 },
            { from: 5, to: 0 },
            { from: 0, to: 6 },
            { from: 1, to: 7 },
            { from: 2, to: 8 },
            { from: 3, to: 9 },
            { from: 4, to: 10 },
            { from: 5, to: 11 }
        ]
    }
};

function updateMolecule3DProperties() {
    const data = moleculeData3d[molState.preset];
    if (!data) return;

    document.getElementById('mol-formula').textContent = data.formula;
    document.getElementById('mol-angle').textContent = data.angle;
    document.getElementById('mol-mass').textContent = data.mass;
    document.getElementById('mol-desc').textContent = data.desc;
}

function rotate3DPoint(x, y, z, rx, ry, rz) {
    // Y Rotation
    let cosY = Math.cos(ry), sinY = Math.sin(ry);
    let x1 = x * cosY - z * sinY;
    let z1 = x * sinY + z * cosY;

    // X Rotation
    let cosX = Math.cos(rx), sinX = Math.sin(rx);
    let y2 = y * cosX - z1 * sinX;
    let z2 = y * sinX + z1 * cosX;

    // Z Rotation
    let cosZ = Math.cos(rz), sinZ = Math.sin(rz);
    let x3 = x1 * cosZ - y2 * sinZ;
    let y3 = x1 * sinZ + y2 * cosZ;

    return { x: x3, y: y3, z: z2 };
}

function animateMolecule3D() {
    if (molecule3dCanvas && isChemistryInitialized && typeof state !== 'undefined' && state.activeTab === 'chemistry' && activeChemistrySubtabName === 'chemistry-molecule') {
        if (!molState.isDragging && molState.autoSpd > 0) {
            molState.ry += 0.012 * molState.autoSpd;
            molState.rx += 0.006 * molState.autoSpd;
        }
        drawMolecule3D();
    }
    requestAnimationFrame(animateMolecule3D);
}

function drawMolecule3D() {
    if (!molecule3dCanvas) return;

    molecule3dCtx.clearRect(0, 0, molecule3dCanvas.width, molecule3dCanvas.height);

    const w = molecule3dCanvas.width;
    const h = molecule3dCanvas.height;
    const cx = w / 2;
    const cy = h / 2;

    const data = moleculeData3d[molState.preset];
    if (!data) return;

    const zoomScale = Math.min(cx, cy) * 0.45 * (molState.scale / 100);

    const rotatedAtoms = data.atoms.map((atom, idx) => {
        const pt = rotate3DPoint(atom.x, atom.y, atom.z, molState.rx, molState.ry, 0);
        return {
            el: atom.el,
            color: atom.color,
            baseSize: atom.size,
            x: cx + pt.x * zoomScale,
            y: cy - pt.y * zoomScale,
            z: pt.z,
            idx: idx
        };
    });

    // Draw Bonds
    molecule3dCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    molecule3dCtx.lineWidth = 4;
    data.bonds.forEach(bond => {
        const a1 = rotatedAtoms[bond.from];
        const a2 = rotatedAtoms[bond.to];

        molecule3dCtx.beginPath();
        molecule3dCtx.moveTo(a1.x, a1.y);
        molecule3dCtx.lineTo(a2.x, a2.y);
        molecule3dCtx.stroke();
    });

    const sortedAtoms = [...rotatedAtoms].sort((a, b) => a.z - b.z);

    sortedAtoms.forEach(atom => {
        const depthFactor = 1 + (atom.z * 0.15);
        const radius = Math.max(4, atom.baseSize * depthFactor);

        const grad = molecule3dCtx.createRadialGradient(
            atom.x - radius * 0.3,
            atom.y - radius * 0.3,
            radius * 0.1,
            atom.x,
            atom.y,
            radius
        );

        grad.addColorStop(0, '#ffffff');
        grad.addColorStop(0.2, atom.color);
        grad.addColorStop(1, darkenColor(atom.color, 0.4));

        molecule3dCtx.shadowBlur = 8;
        molecule3dCtx.shadowColor = atom.color;

        molecule3dCtx.fillStyle = grad;
        molecule3dCtx.beginPath();
        molecule3dCtx.arc(atom.x, atom.y, radius, 0, Math.PI * 2);
        molecule3dCtx.fill();

        molecule3dCtx.shadowBlur = 0;

        molecule3dCtx.fillStyle = (atom.color === '#ffffff') ? '#000000' : '#ffffff';
        molecule3dCtx.font = `bold ${Math.round(radius * 0.6)}px Outfit`;
        molecule3dCtx.textAlign = 'center';
        molecule3dCtx.textBaseline = 'middle';
        molecule3dCtx.fillText(atom.el, atom.x, atom.y);
    });
}

function darkenColor(hex, percent) {
    if (!hex.startsWith('#')) return hex;
    let num = parseInt(hex.slice(1), 16),
        amt = Math.round(2.55 * percent * 100),
        R = (num >> 16) - amt,
        G = (num >> 8 & 0x00FF) - amt,
        B = (num & 0x0000FF) - amt;
    return "#" + (0x1000000 + (R < 0 ? 0 : R) * 0x10000 + (G < 0 ? 0 : G) * 0x100 + (B < 0 ? 0 : B)).toString(16).slice(1);
}

// pH Titration Laboratory Calculations & Visuals
function resetTitration() {
    titrationState.baseVol = 0.0;
    titrationState.autoRunning = false;
    const autoBtn = document.getElementById('btn-titrate-auto');
    if (autoBtn) autoBtn.textContent = 'Auto Titrate';
    updateTitrationHUD();
}

function addTitrateBaseDrop(vol) {
    titrationState.baseVol = Math.min(50.0, titrationState.baseVol + vol);
    updateTitrationHUD();
}

function updateTitrationHUD() {
    const phVal = calculateTitrationPH(titrationState.baseVol);

    const phDisplay = document.getElementById('tit-lbl-ph');
    if (!phDisplay) return;

    phDisplay.textContent = phVal.toFixed(2);
    document.getElementById('tit-lbl-base-added').textContent = titrationState.baseVol.toFixed(1) + ' mL';

    const statusDisplay = document.getElementById('tit-lbl-indicator');
    if (statusDisplay) {
        const ind = titrationState.indicator;
        let indText = 'Neutral (Clear)';
        if (ind === 'phenolphthalein') {
            if (phVal >= 8.2) {
                indText = 'Basic (Pink)';
                statusDisplay.style.color = '#ec4899'; // pink
            } else {
                indText = 'Acidic (Colorless)';
                statusDisplay.style.color = '#94a3b8'; // greyish
            }
        } else if (ind === 'methyl_orange') {
            if (phVal < 3.1) {
                indText = 'Acidic (Red)';
                statusDisplay.style.color = '#ef4444';
            } else if (phVal > 4.4) {
                indText = 'Basic (Yellow)';
                statusDisplay.style.color = '#eab308';
            } else {
                indText = 'Transition (Orange)';
                statusDisplay.style.color = '#f97316';
            }
        } else if (ind === 'litmus') {
            if (phVal < 4.5) {
                indText = 'Acidic (Red)';
                statusDisplay.style.color = '#ef4444';
            } else if (phVal > 8.3) {
                indText = 'Basic (Blue)';
                statusDisplay.style.color = '#3b82f6';
            } else {
                indText = 'Transition (Purple)';
                statusDisplay.style.color = '#a855f7';
            }
        } else if (ind === 'bromothymol_blue') {
            if (phVal < 6.0) {
                indText = 'Acidic (Yellow)';
                statusDisplay.style.color = '#eab308';
            } else if (phVal > 7.6) {
                indText = 'Basic (Blue)';
                statusDisplay.style.color = '#3b82f6';
            } else {
                indText = 'Transition (Green)';
                statusDisplay.style.color = '#22c55e';
            }
        }
        statusDisplay.textContent = indText;
    }
}

function calculateTitrationPH(volB) {
    const Va = titrationState.acidVol; // 50 ml
    const Ca = titrationState.acidCc;
    const Cb = titrationState.baseCc;

    const molesAcid = Va * Ca; // millimoles
    const molesBase = volB * Cb; // millimoles

    if (molesBase < molesAcid) {
        // Excess acid
        const remainingH = molesAcid - molesBase;
        const concH = remainingH / (Va + volB);
        return -Math.log10(concH);
    } else if (Math.abs(molesBase - molesAcid) < 0.0001) {
        return 7.0; // Equivalence for strong acid / strong base
    } else {
        // Excess base
        const excessOH = molesBase - molesAcid;
        const concOH = excessOH / (Va + volB);
        const pOH = -Math.log10(concOH);
        return 14.0 - pOH;
    }
}

function renderTitrationSpace() {
    if (!titrationCanvas) return;
    const w = titrationCanvas.width;
    const h = titrationCanvas.height;
    if (w === 0 || h === 0) return;

    titrationCtx.clearRect(0, 0, w, h);

    if (titrationState.autoRunning) {
        addTitrateBaseDrop(0.12);
        if (titrationState.baseVol >= 50.0) {
            titrationState.autoRunning = false;
            const autoBtn = document.getElementById('btn-tit-auto');
            if (autoBtn) autoBtn.textContent = 'Auto Titrate';
        }
    }

    const midX = w * 0.28;
    const centerY = h / 2;

    // Draw background grid
    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.015)';
    titrationCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
        titrationCtx.beginPath(); titrationCtx.moveTo(x, 0); titrationCtx.lineTo(x, h); titrationCtx.stroke();
    }

    // 1. Draw Glass Burette (Contains NaOH base)
    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    titrationCtx.lineWidth = 2.5;
    titrationCtx.beginPath();
    // left line of tube
    titrationCtx.moveTo(midX - 10, 20);
    titrationCtx.lineTo(midX - 10, centerY - 40);
    // right line of tube
    titrationCtx.moveTo(midX + 10, 20);
    titrationCtx.lineTo(midX + 10, centerY - 40);
    titrationCtx.stroke();

    // Burette nozzle taper
    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
    titrationCtx.beginPath();
    titrationCtx.moveTo(midX - 10, centerY - 40);
    titrationCtx.lineTo(midX - 2, centerY - 25);
    titrationCtx.lineTo(midX - 2, centerY - 15);
    titrationCtx.moveTo(midX + 10, centerY - 40);
    titrationCtx.lineTo(midX + 2, centerY - 25);
    titrationCtx.lineTo(midX + 2, centerY - 15);
    titrationCtx.stroke();

    // Valve (Stopcock)
    titrationCtx.fillStyle = titrationState.autoRunning ? '#ef4444' : '#3b82f6';
    titrationCtx.fillRect(midX - 6, centerY - 28, 12, 6);

    // Liquid in burette (NaOH)
    const baseHeight = 120; // max length of burette fluid columns
    const filledPercentage = (50.0 - titrationState.baseVol) / 50.0;
    const liquidFillLength = baseHeight * filledPercentage;

    titrationCtx.fillStyle = 'rgba(59, 130, 246, 0.15)';
    titrationCtx.fillRect(midX - 8, centerY - 40 - liquidFillLength, 16, liquidFillLength);

    // Burette measurement ticks
    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    titrationCtx.lineWidth = 1;
    for (let ml = 0; ml <= 50; ml += 5) {
        const tickY = centerY - 40 - (baseHeight * (50 - ml) / 50);
        titrationCtx.beginPath();
        titrationCtx.moveTo(midX + 2, tickY);
        titrationCtx.lineTo(midX + 9, tickY);
        titrationCtx.stroke();

        titrationCtx.fillStyle = 'rgba(255,255,255,0.4)';
        titrationCtx.font = '7px Outfit';
        titrationCtx.fillText(ml, midX - 17, tickY + 2.5);
    }

    // 2. Draw falling drops animation
    if (titrationState.autoRunning || (Math.random() < 0.1 && titrationState.baseVol > 0 && titrationState.baseVol < 50)) {
        titrationCtx.fillStyle = '#60a5fa';
        const tDrop = (Date.now() % 500) / 500; // 0 to 1 loop
        const dropY = (centerY - 12) + tDrop * (h - centerY - 70);

        titrationCtx.beginPath();
        titrationCtx.arc(midX, dropY, 2.5, 0, Math.PI * 2);
        titrationCtx.fill();
    }

    // 3. Draw Erlenmeyer Flask at the bottom
    const flaskBottomY = h - 25;
    const flaskTopY = centerY + 15;
    const flaskWidth = 60;

    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    titrationCtx.lineWidth = 3;
    titrationCtx.beginPath();
    // Neck
    titrationCtx.moveTo(midX - 12, flaskTopY);
    titrationCtx.lineTo(midX - 12, flaskTopY + 20);
    // Body taper
    titrationCtx.lineTo(midX - flaskWidth / 2, flaskBottomY);
    // Base
    titrationCtx.lineTo(midX + flaskWidth / 2, flaskBottomY);
    // Right body taper
    titrationCtx.lineTo(midX + 12, flaskTopY + 20);
    titrationCtx.lineTo(midX + 12, flaskTopY);
    titrationCtx.stroke();

    // Calculate current solution volume inside flask (originally 50 ml H+, adding NaOH baseVol)
    const phVal = calculateTitrationPH(titrationState.baseVol);
    const flaskLiquidHeight = 25 + (titrationState.baseVol / 50.0) * 15; // grows slightly as base drops

    // 4. Indicator Color Determination
    let litColor = 'rgba(255, 255, 255, 0.05)'; // clear default
    const ind = titrationState.indicator;

    if (ind === 'phenolphthalein') {
        if (phVal >= 8.2) {
            const intensity = Math.min(1.0, (phVal - 8.2) / 1.8); // transitions up to pH 10
            litColor = `rgba(236, 72, 153, ${intensity * 0.7})`; // glowing base pink
        } else {
            litColor = 'rgba(255,255,255,0.06)'; // clear acidic
        }
    } else if (ind === 'methyl_orange') {
        if (phVal < 3.1) {
            litColor = 'rgba(239, 68, 68, 0.65)'; // Red
        } else if (phVal > 4.4) {
            litColor = 'rgba(234, 179, 8, 0.65)'; // Yellow
        } else {
            const factor = (phVal - 3.1) / 1.3;
            const r = Math.round(239 + factor * (234 - 239));
            const g = Math.round(68 + factor * (179 - 68));
            const b = Math.round(68 + factor * (8 - 68));
            litColor = `rgba(${r}, ${g}, ${b}, 0.65)`; // Orange transition
        }
    } else if (ind === 'litmus') {
        if (phVal < 4.5) {
            litColor = 'rgba(239, 68, 68, 0.6)'; // Red
        } else if (phVal > 8.3) {
            litColor = 'rgba(59, 130, 246, 0.6)'; // Blue
        } else {
            const factor = (phVal - 4.5) / 3.8;
            const r = Math.round(239 + factor * (59 - 239));
            const g = Math.round(68 + factor * (130 - 68));
            const b = Math.round(68 + factor * (246 - 68));
            litColor = `rgba(${r}, ${g}, ${b}, 0.65)`; // Purple
        }
    } else if (ind === 'bromothymol_blue') {
        if (phVal < 6.0) {
            litColor = 'rgba(234, 179, 8, 0.65)'; // Yellow
        } else if (phVal > 7.6) {
            litColor = 'rgba(59, 130, 246, 0.65)'; // Blue
        } else {
            const factor = (phVal - 6.0) / 1.6;
            const r = Math.round(234 + factor * (59 - 234));
            const g = Math.round(179 + factor * (130 - 179));
            const b = Math.round(8 + factor * (246 - 8));
            litColor = `rgba(${r}, ${g}, ${b}, 0.65)`; // Green
        }
    }

    // Draw liquid filled in Flask
    titrationCtx.fillStyle = litColor;
    titrationCtx.beginPath();

    // Bottom left taper coords
    const lWaterX = midX - (flaskWidth / 2 - 2);
    const rWaterX = midX + (flaskWidth / 2 - 2);
    const waterTopY = flaskBottomY - flaskLiquidHeight;
    const neckSpanAtWaterHeight = 12 + ((flaskBottomY - flaskLiquidHeight) - (flaskTopY + 20)) * ((flaskWidth / 2 - 12) / (flaskBottomY - (flaskTopY + 20)));
    const lWaterTopX = midX - neckSpanAtWaterHeight + 1.5;
    const rWaterTopX = midX + neckSpanAtWaterHeight - 1.5;

    titrationCtx.moveTo(lWaterX, flaskBottomY - 1.5);
    titrationCtx.lineTo(rWaterX, flaskBottomY - 1.5);
    titrationCtx.lineTo(rWaterTopX, waterTopY);
    titrationCtx.lineTo(lWaterTopX, waterTopY);
    titrationCtx.closePath();
    titrationCtx.fill();

    // 5. Draw Titration curve graph on the right side
    const graphLeft = w * 0.52;
    const graphTop = 30;
    const graphWidth = w * 0.43;
    const graphHeight = h - 60;

    // Draw graph axes
    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    titrationCtx.lineWidth = 1.5;
    titrationCtx.beginPath();
    titrationCtx.moveTo(graphLeft, graphTop);
    titrationCtx.lineTo(graphLeft, graphTop + graphHeight);
    titrationCtx.lineTo(graphLeft + graphWidth, graphTop + graphHeight);
    titrationCtx.stroke();

    // Graph grid labels
    titrationCtx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    titrationCtx.font = '8px JetBrains Mono';

    // Y-axis label (pH 0, 7, 14)
    titrationCtx.fillText("14", graphLeft - 15, graphTop + 4);
    titrationCtx.fillText("7", graphLeft - 10, graphTop + graphHeight / 2 + 3);
    titrationCtx.fillText("0", graphLeft - 10, graphTop + graphHeight + 2);

    // X-axis label (NaOH Added 50 mL)
    titrationCtx.fillText("0", graphLeft - 2, graphTop + graphHeight + 12);
    titrationCtx.fillText("25", graphLeft + graphWidth / 2 - 5, graphTop + graphHeight + 12);
    titrationCtx.fillText("50 mL NaOH", graphLeft + graphWidth - 25, graphTop + graphHeight + 12);

    // Plot full titration curve
    titrationCtx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    titrationCtx.lineWidth = 1;
    titrationCtx.beginPath();
    for (let vx = 0; vx <= 50; vx += 0.5) {
        const curvesPH = calculateTitrationPH(vx);
        const gx = graphLeft + (vx / 50.0) * graphWidth;
        const gy = graphTop + graphHeight - (curvesPH / 14.0) * graphHeight;
        if (vx === 0) {
            titrationCtx.moveTo(gx, gy);
        } else {
            titrationCtx.lineTo(gx, gy);
        }
    }
    titrationCtx.stroke();

    // Plot colored active line up to current volume
    titrationCtx.strokeStyle = '#bd00ff';
    titrationCtx.lineWidth = 2.5;
    titrationCtx.beginPath();
    let started = false;
    for (let vx = 0; vx <= titrationState.baseVol; vx += 0.25) {
        const curvesPH = calculateTitrationPH(vx);
        const gx = graphLeft + (vx / 50.0) * graphWidth;
        const gy = graphTop + graphHeight - (curvesPH / 14.0) * graphHeight;
        if (!started) {
            titrationCtx.moveTo(gx, gy);
            started = true;
        } else {
            titrationCtx.lineTo(gx, gy);
        }
    }
    titrationCtx.stroke();

    // Current pointer node
    const dotX = graphLeft + (titrationState.baseVol / 50.0) * graphWidth;
    const dotY = graphTop + graphHeight - (phVal / 14.0) * graphHeight;
    titrationCtx.fillStyle = '#00e5ff';
    titrationCtx.shadowBlur = 4;
    titrationCtx.shadowColor = '#00e5ff';
    titrationCtx.beginPath();
    titrationCtx.arc(dotX, dotY, 4, 0, Math.PI * 2);
    titrationCtx.fill();
    titrationCtx.shadowBlur = 0;
}

// Flame Spectrograph Details & Database
const flameSaltsDB = {
    NaCl: { name: 'Sodium Chloride (NaCl)', colorName: 'Intense Yellow-Orange', wl: '589 nm', col: 'rgba(255, 220, 0, opacity)', desc: 'Sodium atoms emit intense yellow light at 589 nm due to the classic 3p to 3s valence electron orbital transition doublet.' },
    CuCl2: { name: 'Copper(II) Chloride (CuCl₂)', colorName: 'Bright Blue-Green', wl: '510 nm', col: 'rgba(0, 255, 180, opacity)', desc: 'Copper emission shows green-blue bands resulting from flame excitation of diatomic copper monochlorides (CuCl) and copper oxide intermediates.' },
    LiCl: { name: 'Lithium Chloride (LiCl)', colorName: 'Carmine Red', wl: '670 nm', col: 'rgba(244, 63, 94, opacity)', desc: 'Lithium emissions produce a brilliant carmine red line at 671 nm arising from the principal 2p to 2s atomic doublet transitions.' },
    KCl: { name: 'Potassium Chloride (KCl)', colorName: 'Pale Violet (Lilac)', wl: '404 nm', col: 'rgba(224, 180, 255, opacity)', desc: 'Potassium ions emit a violet/lilac emission at 404 nm, representing the high-energy 5p to 4s valence electronic transitions.' },
    SrCl2: { name: 'Strontium Chloride (SrCl₂)', colorName: 'Crimson Red', wl: '640 nm', col: 'rgba(239, 68, 68, opacity)', desc: 'Strontium chloride gives a deep crimson red spectrum due to molecular strontium hydroxide (SrOH) band emissions in the flame.' },
    BaCl2: { name: 'Barium Chloride (BaCl₂)', colorName: 'Apple Green', wl: '550 nm', col: 'rgba(163, 230, 53, opacity)', desc: 'Barium chloride gives a characteristic apple green flame emission, mostly originating from molecular barium oxide (BaO) transitions.' },
    CaCl2: { name: 'Calcium Chloride (CaCl₂)', colorName: 'Brick Red', wl: '620 nm', col: 'rgba(251, 146, 60, opacity)', desc: 'Calcium chloride emits brick-red light formed by combustion products like calcium hydroxide (CaOH) bands and calcium atomic lines.' }
};

function updateFlameSpectraHUD() {
    const salt = flameSaltsDB[flameState.selectedSalt];
    const cationVal = flameState.selectedSalt === 'NaCl' ? 'Na⁺' :
        flameState.selectedSalt === 'CuCl2' ? 'Cu²⁺' :
            flameState.selectedSalt === 'KCl' ? 'K⁺' :
                flameState.selectedSalt === 'LiCl' ? 'Li⁺' :
                    flameState.selectedSalt === 'BaCl2' ? 'Ba²⁺' :
                        flameState.selectedSalt === 'SrCl2' ? 'Sr²⁺' :
                            flameState.selectedSalt === 'CaCl2' ? 'Ca²⁺' : '';

    const cationDisplay = document.getElementById('flame-lbl-cation');
    if (cationDisplay) {
        cationDisplay.textContent = cationVal;
    }
    const colorDisplay = document.getElementById('flame-lbl-color');
    if (colorDisplay) {
        colorDisplay.textContent = salt.colorName;
        colorDisplay.style.color = salt.col.replace('opacity', '1.0');
    }
    const wlDisplay = document.getElementById('flame-lbl-wavelength');
    if (wlDisplay) {
        wlDisplay.textContent = salt.wl;
    }
    const descDisplay = document.getElementById('flame-lbl-desc');
    if (descDisplay) {
        descDisplay.textContent = salt.desc;
    }
}

function drawFlameSpectraSpace() {
    if (!flameCanvas) return;
    const w = flameCanvas.width;
    const h = flameCanvas.height;
    if (w === 0 || h === 0) return;

    flameCtx.clearRect(0, 0, w, h);

    // Grid details
    flameCtx.strokeStyle = 'rgba(255, 255, 255, 0.01)';
    flameCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 40) {
        flameCtx.beginPath(); flameCtx.moveTo(x, 0); flameCtx.lineTo(x, h); flameCtx.stroke();
    }

    // Heat excitation animation calculations
    if (flameState.loopActive) {
        flameState.heatProgress = Math.min(1.0, flameState.heatProgress + 0.015);
    } else {
        flameState.heatProgress = Math.max(0.0, flameState.heatProgress - 0.015);
    }

    // Render Bunsen Burner base
    const burnerCenterX = w * 0.28;
    const burnerTopY = h - 130;

    // Gas stand base
    flameCtx.fillStyle = '#64748b';
    flameCtx.fillRect(burnerCenterX - 25, h - 35, 50, 10);
    // Tube column
    flameCtx.fillStyle = '#94a3b8';
    flameCtx.fillRect(burnerCenterX - 6, burnerTopY, 12, h - burnerTopY - 35);

    // Collars
    flameCtx.fillStyle = '#475569';
    flameCtx.fillRect(burnerCenterX - 8, burnerTopY + 10, 16, 8);

    // Draw Flame
    flameCtx.save();

    const flameHeight = 70 + Math.sin(Date.now() * 0.035) * 4;
    const flameY = burnerTopY;

    // Normal blue flame (gradient)
    const normFlame = flameCtx.createRadialGradient(
        burnerCenterX, flameY - 20, 5,
        burnerCenterX, flameY - flameHeight, flameHeight
    );
    normFlame.addColorStop(0, 'rgba(59, 130, 246, 0.9)'); // bright blue core
    normFlame.addColorStop(0.3, 'rgba(30, 58, 138, 0.45)');
    normFlame.addColorStop(1, 'rgba(0, 0, 255, 0)');

    flameCtx.fillStyle = normFlame;
    flameCtx.beginPath();
    flameCtx.moveTo(burnerCenterX - 18, flameY);
    flameCtx.quadraticCurveTo(burnerCenterX - 22, flameY - flameHeight / 2, burnerCenterX, flameY - flameHeight);
    flameCtx.quadraticCurveTo(burnerCenterX + 22, flameY - flameHeight / 2, burnerCenterX + 18, flameY);
    flameCtx.closePath();
    flameCtx.fill();

    // Excitation salt colored overlay flame based on progress
    if (flameState.heatProgress > 0) {
        const activeSalt = flameSaltsDB[flameState.selectedSalt];
        const saltFlameColStr = activeSalt.col;

        const saltFlame = flameCtx.createRadialGradient(
            burnerCenterX, flameY - 20, 5,
            burnerCenterX, flameY - flameHeight - 10, flameHeight + 10
        );

        const op1 = flameState.heatProgress * 0.85;
        const op2 = flameState.heatProgress * 0.4;

        saltFlame.addColorStop(0, '#ffffff'); // super hot center core
        saltFlame.addColorStop(0.2, saltFlameColStr.replace('opacity', op1));
        saltFlame.addColorStop(0.7, saltFlameColStr.replace('opacity', op2));
        saltFlame.addColorStop(1, 'rgba(0, 0, 0, 0)');

        flameCtx.fillStyle = saltFlame;
        flameCtx.beginPath();
        flameCtx.moveTo(burnerCenterX - 22, flameY);
        flameCtx.quadraticCurveTo(burnerCenterX - 26, flameY - flameHeight / 2 - 10, burnerCenterX, flameY - flameHeight - 15);
        flameCtx.quadraticCurveTo(burnerCenterX + 26, flameY - flameHeight / 2 - 10, burnerCenterX + 22, flameY);
        flameCtx.closePath();
        flameCtx.fill();
    }
    flameCtx.restore();

    // 2. Draw Nichrome Wire Loop
    // Tip rests in middle of flame when striked, moves to container when cold.
    const loopX = burnerCenterX + (1.0 - flameState.heatProgress) * 90;
    const loopY = burnerTopY - 28 + (1.0 - flameState.heatProgress) * 45;

    // Handle rod
    flameCtx.strokeStyle = '#4b5563';
    flameCtx.lineWidth = 4;
    flameCtx.beginPath();
    flameCtx.moveTo(w * 0.8, h - 80);
    flameCtx.lineTo(loopX + 35, loopY + 12);
    flameCtx.stroke();

    // Wire rod taper
    flameCtx.strokeStyle = '#9ca3af';
    flameCtx.lineWidth = 1.8;
    flameCtx.beginPath();
    flameCtx.moveTo(loopX + 35, loopY + 12);
    flameCtx.lineTo(loopX + 8, loopY + 2.5);
    flameCtx.stroke();

    // Tip circular loop wire
    // Changes color as it heats up in flame.
    const wireTipColor = () => {
        if (flameState.heatProgress === 0) return '#cbd5e1'; // grey
        const r = Math.round(203 + flameState.heatProgress * (255 - 203));
        const g = Math.round(213 + flameState.heatProgress * (100 - 213));
        const b = Math.round(225 + flameState.heatProgress * (0 - 225));
        return `rgba(${r}, ${g}, ${b}, 1)`; // glowing thermal hot orange
    };

    flameCtx.strokeStyle = wireTipColor();
    flameCtx.lineWidth = 2;
    flameCtx.beginPath();
    flameCtx.arc(loopX, loopY, 5, 0, Math.PI * 2);
    flameCtx.stroke();

    // 3. Draw Emission Spectrum scale at the bottom
    const specLeft = w * 0.12;
    const specTop = h - 60;
    const specWidth = w * 0.76;
    const specHeight = 25;

    // Spectrograph black bounding container
    flameCtx.fillStyle = '#090d16';
    flameCtx.fillRect(specLeft, specTop, specWidth, specHeight);
    flameCtx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    flameCtx.lineWidth = 1.5;
    flameCtx.strokeRect(specLeft, specTop, specWidth, specHeight);

    // Spectrum wavelength tick labels (400 nm to 700 nm)
    flameCtx.fillStyle = 'rgba(255, 255, 255, 0.4)';
    flameCtx.font = '8px JetBrains Mono';

    for (let wl = 400; wl <= 700; wl += 50) {
        const ratio = (wl - 400) / 300.0;
        const tickX = specLeft + ratio * specWidth;

        flameCtx.beginPath();
        flameCtx.moveTo(tickX, specTop + specHeight);
        flameCtx.lineTo(tickX, specTop + specHeight - 4);
        flameCtx.stroke();

        flameCtx.fillText(wl + "", tickX - 8, specTop + specHeight + 11);
    }

    // Plot emission lines
    const drawSpectralLine = (wl, relStrength, intensityColor) => {
        if (wl < 400 || wl > 700) return;

        const ratio = (wl - 400) / 300.0;
        const lineX = specLeft + ratio * specWidth;

        // Intensity grows with heatprogress
        const lineWeight = flameState.heatProgress * relStrength;
        if (lineWeight > 0.01) {
            flameCtx.strokeStyle = intensityColor;
            flameCtx.lineWidth = 2.0;
            flameCtx.shadowBlur = 5;
            flameCtx.shadowColor = intensityColor;
            flameCtx.beginPath();
            flameCtx.moveTo(lineX, specTop + 1.5);
            flameCtx.lineTo(lineX, specTop + specHeight - 1.5);
            flameCtx.stroke();
            flameCtx.shadowBlur = 0;
        }
    };

    // Emission databases for elements (Wavelength in nm, strength 0-1, color)
    if (flameState.selectedSalt === 'NaCl') {
        // Sodium D doublet
        drawSpectralLine(589, 1.0, 'rgba(255, 230, 0, 0.9)');
    } else if (flameState.selectedSalt === 'CuCl2') {
        // Copper lines
        drawSpectralLine(510, 0.8, 'rgba(0, 255, 180, 0.9)'); // teal green
        drawSpectralLine(521, 0.7, 'rgba(100, 255, 120, 0.8)'); // green
        drawSpectralLine(578, 0.55, 'rgba(234, 179, 8, 0.7)'); // yellow
        drawSpectralLine(435, 0.4, 'rgba(120, 50, 255, 0.6)'); // violet
    } else if (flameState.selectedSalt === 'LiCl') {
        // Lithium lines
        drawSpectralLine(671, 1.0, 'rgba(244, 63, 94, 0.9)'); // bright red
        drawSpectralLine(610, 0.25, 'rgba(251, 146, 60, 0.5)'); // orange
    } else if (flameState.selectedSalt === 'KCl') {
        // Potassium lines
        drawSpectralLine(404, 0.8, 'rgba(180, 100, 255, 0.8)'); // violet
        drawSpectralLine(695, 0.5, 'rgba(239, 68, 68, 0.65)'); // dark red
    } else if (flameState.selectedSalt === 'SrCl2') {
        // Strontium lines
        drawSpectralLine(640, 0.8, 'rgba(239, 68, 68, 0.85)'); // crimson
        drawSpectralLine(650, 0.9, 'rgba(244, 63, 94, 0.9)');
        drawSpectralLine(606, 0.6, 'rgba(251, 146, 60, 0.7)'); // orange
        drawSpectralLine(460, 0.45, 'rgba(59, 130, 246, 0.7)'); // deep blue
    } else if (flameState.selectedSalt === 'BaCl2') {
        // Barium lines
        drawSpectralLine(513, 0.7, 'rgba(132, 204, 22, 0.85)'); // light green
        drawSpectralLine(524, 0.6, 'rgba(34, 197, 94, 0.75)');
        drawSpectralLine(543, 0.8, 'rgba(34, 197, 94, 0.85)');
        drawSpectralLine(553, 0.9, 'rgba(163, 230, 53, 0.9)');
    } else if (flameState.selectedSalt === 'CaCl2') {
        // Calcium lines
        drawSpectralLine(616, 0.85, 'rgba(249, 115, 22, 0.85)'); // orange
        drawSpectralLine(622, 0.7, 'rgba(239, 68, 68, 0.75)'); // orange-red
        drawSpectralLine(559, 0.5, 'rgba(163, 230, 53, 0.6)'); // green
    }
}

// Coordinate animation loop switches
let activeChemistrySubtabName = 'chemistry-periodic';
function chemistryAnimationLoop() {
    if (isChemistryInitialized && typeof state !== 'undefined' && state.activeTab === 'chemistry') {
        const activeSub = document.querySelector('#tab-chemistry .subtab-btn.active');
        if (activeSub) {
            activeChemistrySubtabName = activeSub.getAttribute('data-subtab');
            if (activeChemistrySubtabName === 'chemistry-titration') {
                renderTitrationSpace();
            } else if (activeChemistrySubtabName === 'chemistry-flame') {
                drawFlameSpectraSpace();
            }
        }
    }

    requestAnimationFrame(chemistryAnimationLoop);
}
