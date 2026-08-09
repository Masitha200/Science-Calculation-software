// SciMath main application state & general UI routes
const state = {
    activeTab: 'dashboard',
    quotes: [
        { text: "Mathematics is the language in which God has written the universe.", author: "Galileo Galilei" },
        { text: "Equipped with his five senses, man explores the universe around him and calls the adventure Science.", author: "Edwin Hubble" },
        { text: "Look deep into nature, and then you will understand everything better.", author: "Albert Einstein" },
        { text: "In mathematics the art of proposing a question must be held of higher value than solving it.", author: "Georg Cantor" },
        { text: "What we know is a drop, what we don't know is an ocean.", author: "Isaac Newton" },
        { text: "There is geometry in the humming of the strings, there is music in the spacing of the spheres.", author: "Pythagoras" },
        { text: "The important thing is not to stop questioning. Curiosity has its own reason for existence.", author: "Albert Einstein" },
        { text: "Mathematics reveals its secrets only to those who approach it with pure love, for its beauty.", author: "Archimedes" }
    ],
    selectedQuoteIndex: 0
};

// Start particle animation for welcome card
let particleCanvas, particleCtx, particleAnimationId;
const particlesArray = [];

class Particle {
    constructor(width, height) {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = Math.random() * 0.4 - 0.2;
        this.speedY = Math.random() * 0.4 - 0.2;
        this.color = Math.random() > 0.5 ? 'rgba(59, 130, 246, 0.4)' : 'rgba(0, 229, 255, 0.4)';
    }
    update(width, height) {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x < 0 || this.x > width) this.speedX *= -1;
        if (this.y < 0 || this.y > height) this.speedY *= -1;
    }
    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
    }
}

function initParticles() {
    particleCanvas = document.getElementById('dashboard-particles');
    if (!particleCanvas) return;
    particleCtx = particleCanvas.getContext('2d');

    resizeParticleCanvas();

    // Clear and build particles
    particlesArray.length = 0;
    const numberOfParticles = 80;
    for (let i = 0; i < numberOfParticles; i++) {
        particlesArray.push(new Particle(particleCanvas.width, particleCanvas.height));
    }

    animateParticles();
}

function resizeParticleCanvas() {
    if (!particleCanvas) return;
    const rect = particleCanvas.parentElement.getBoundingClientRect();
    particleCanvas.width = rect.width;
    particleCanvas.height = rect.height;
}

function animateParticles() {
    if (state.activeTab !== 'dashboard') {
        cancelAnimationFrame(particleAnimationId);
        return;
    }

    particleCtx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);

    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update(particleCanvas.width, particleCanvas.height);
        particlesArray[i].draw(particleCtx);
    }

    particleAnimationId = requestAnimationFrame(animateParticles);
}

// Window sizing listeners
window.addEventListener('resize', () => {
    if (state.activeTab === 'dashboard') {
        resizeParticleCanvas();
    }
});

// Routing Navigation
function switchTab(tabName) {
    if (state.activeTab === tabName) return;

    // Deactivate current tab elements
    document.getElementById(`tab-${state.activeTab}`).classList.remove('active');
    document.getElementById(`nav-${state.activeTab}`).classList.remove('active');

    if (state.activeTab === 'dashboard') {
        cancelAnimationFrame(particleAnimationId);
    }

    // Activate new tab elements
    state.activeTab = tabName;
    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.getElementById(`nav-${tabName}`).classList.add('active');

    // Update Header Text dynamically
    updateHeaderDescription(tabName);

    // Call module initialization code
    if (tabName === 'dashboard') {
        initParticles();
    } else if (tabName === 'math') {
        initMathModule();
    } else if (tabName === 'physics') {
        initPhysicsModule();
    } else if (tabName === 'chemistry') {
        initChemistryModule();
    }
}

function updateHeaderDescription(tabName) {
    const titleEl = document.getElementById('current-tab-title');
    const descEl = document.getElementById('current-tab-description');

    const lang = appLangState.currentLang;
    const trans = tabBannerTranslations[lang] || tabBannerTranslations['en'];

    switch (tabName) {
        case 'dashboard':
            titleEl.textContent = trans.dashboard_title;
            descEl.textContent = trans.dashboard_desc;
            break;
        case 'math':
            titleEl.textContent = trans.math_title;
            descEl.textContent = trans.math_desc;
            break;
        case 'physics':
            titleEl.textContent = trans.physics_title;
            descEl.textContent = trans.physics_desc;
            break;
        case 'chemistry':
            titleEl.textContent = trans.chemistry_title;
            descEl.textContent = trans.chemistry_desc;
            break;
    }
}

// Clock updates
function initClock() {
    const clockEl = document.getElementById('header-clock');
    setInterval(() => {
        const now = new Date();
        clockEl.textContent = now.toLocaleTimeString();
    }, 1000);
}

// Quotes rotation
function initQuotes() {
    const quoteTxt = document.getElementById('daily-quote');
    const quoteAuth = document.getElementById('daily-quote-author');
    const rotateBtn = document.getElementById('btn-next-quote');

    if (!rotateBtn) return;

    rotateBtn.addEventListener('click', () => {
        state.selectedQuoteIndex = (state.selectedQuoteIndex + 1) % state.quotes.length;
        const targetQ = state.quotes[state.selectedQuoteIndex];

        quoteTxt.style.opacity = 0;
        quoteAuth.style.opacity = 0;

        setTimeout(() => {
            quoteTxt.textContent = targetQ.text;
            quoteAuth.textContent = `— ${targetQ.author}`;
            quoteTxt.style.opacity = 1;
            quoteAuth.style.opacity = 1;
        }, 150);
    });
}

// Setup resetting handler
function initResets() {
    const resetBtn = document.getElementById('btn-reset-layout');
    resetBtn.addEventListener('click', () => {
        // Trigger resets in active module
        if (state.activeTab === 'math') {
            resetMathModule();
        } else if (state.activeTab === 'physics') {
            resetPhysicsModule();
        } else if (state.activeTab === 'chemistry') {
            resetChemistryModule();
        } else {
            // General reload
            window.location.reload();
        }
    });

    // Subtab event bindings
    document.querySelectorAll('.subtab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const parent = btn.parentElement;
            parent.querySelectorAll('.subtab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Toggle panes
            const targetPaneId = btn.getAttribute('data-subtab');
            const siblingPanes = parent.parentElement.querySelectorAll('.subtab-pane');
            siblingPanes.forEach(pane => pane.classList.remove('active'));
            document.getElementById(`subtab-${targetPaneId}`).classList.add('active');

            // Trigger canvas redraws on tab show
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 50);
        });
    });
}

// Translation Dictionaries
const translationDictionary = {
    en: {
        app_title: "SciMath",
        app_subtitle: "Visual Studio",
        nav_dash: "Dashboard",
        nav_sec_title: "Solvers & Labs",
        nav_math: "Mathematics Studio",
        nav_physics: "Physics Sandbox",
        nav_chemistry: "Chemistry Lab",
        footer_status: "Offline Engine Active",
        btn_reset: "Reset Demo",
        dash_badge: "OFFLINE DESKTOP LAB",
        dash_welcome_title: "Exploration through Visualizing",
        dash_welcome_desc: "Unlock the secrets of math and physics. Choose a lab from the sidebar, adjust simulation parameters in real time, and watch the calculations dynamically unfold step-by-step!",
        dash_btn_math: "Math Studio",
        dash_btn_physics: "Physics Sandbox",
        constants_title: "Scientific Constants Drawer",
        constants_desc: "Quick look at universal constants for science & math calculations.",
        const_sol: "Speed of Light",
        const_grav: "Standard Gravity",
        const_gconst: "Gravitational Const",
        const_planck: "Planck Constant",
        const_pi: "Pi (Circle Ratio)",
        const_euler: "Euler's Number",
        btn_next_quote: "Next Quote →",
        banner_math_h4: "Calculus & Graphing",
        banner_math_p: "Plot custom equations, move tangent vectors dynamically to view differentials, and slide subdivisions to see Riemann calculations.",
        banner_phys_h4: "Physics Mechanics",
        banner_phys_p: "Simulate perfect motion under varying gravity, air drag, and angles. Run harmonic oscillations and witness conservation of energy graphs.",
        banner_chem_h4: "Chemistry & Atoms",
        banner_chem_p: "Inspect electron distribution in elements with revolving orbital simulations. Balance equations and view molecule diagrams instantly.",
        banner_launch: "Launch Lab →"
    },
    si: {
        app_title: "SciMath",
        app_subtitle: "විෂුවල් ස්ටුඩියෝ",
        nav_dash: "ප්‍රධාන පුවරුව",
        nav_sec_title: "විද්‍යාගාර සහ මෙවලම්",
        nav_math: "ගණිත ස්ටුඩියෝව",
        nav_physics: "භෞතික විද්‍යා සංදර්ශකය",
        nav_chemistry: "රසායනික විද්‍යාගාරය",
        footer_status: "Offline ක්‍රියාකාරීත්වය සක්‍රීයයි",
        btn_reset: "නැවත සකසන්න",
        dash_badge: "නොබැඳි ඩෙස්ක්ටොප් විද්‍යාගාරය",
        dash_welcome_title: "දෘශ්‍යකරණයෙන් ගවේෂණය කරන්න",
        dash_welcome_desc: "ගණිතයේ සහ භෞතික විද්‍යාවේ රහස් හෙළි කරගන්න. පැති මෙනුවෙන් විද්‍යාගාරයක් තෝරාගෙන, සජීවීව පරාමිතීන් වෙනස් කර, ගණනය කිරීම් පියවරෙන් පියවර සිදුවන ආකාරය නරඹන්න!",
        dash_btn_math: "ගණිත ස්ටුඩියෝව",
        dash_btn_physics: "භෞතික සංදර්ශකය",
        constants_title: "විද්‍යාත්මක නියතයන්ගේ ලේඛනය",
        constants_desc: "විද්‍යාත්මක සහ ගණිතමය ගණනය කිරීම් සඳහා විශ්වීය නියතයන් ඉක්මනින් බලාගන්න.",
        const_sol: "ආලෝකයේ වේගය",
        const_grav: "සම්මත ගුරුත්වාකර්ෂණය",
        const_gconst: "විශ්වීය ගුරුත්වාකර්ෂණ නියතය",
        const_planck: "ප්ලෑන්ක් නියතය",
        const_pi: "පයි (වෘත්ත අනුපාතය)",
        const_euler: "ඔයිලර්ගේ අංකය",
        btn_next_quote: "මීළඟ කියමන →",
        banner_math_h4: "කලනය සහ ප්‍රස්තාරකරණය",
        banner_math_p: "ඔබට අවශ්‍ය සමීකරණ ප්‍රස්තාරගත කරන්න, අවකලන සහ අනුකලන විෂුවල් එකක් ලෙස පියවරෙන් පියවර හඳුනාගන්න.",
        banner_phys_h4: "භෞතික විද්‍යා යාන්ත්‍ර විද්‍යාව",
        banner_phys_p: "ගුරුත්වාකර්ෂණය සහ වායු ප්‍රතිරෝධය යටතේ සිදුවන චලිතයන්, ලෝලකයක සජීවී ශක්ති පරිවර්තනයන් නිරීක්ෂණය කරන්න.",
        banner_chem_h4: "රසායන විද්‍යාව සහ පරමාණු",
        banner_chem_p: "ආවර්තිතා වගුව, බෝර් පරමාණුක ආකෘතික ඉලෙක්ට්‍රෝන කක්ෂගත වීම් සහ රසායනික සමීකරණ ක්ෂණිකව තුලිත කරන්න.",
        banner_launch: "විද්‍යාගාරය අරඹන්න →"
    },
    ta: {
        app_title: "SciMath",
        app_subtitle: "விஷுவல் ஸ்டுடியோ",
        nav_dash: "முகப்புப்பலகை",
        nav_sec_title: "ஆய்வகங்கள் & கருவிகள்",
        nav_math: "கணிதக்கூடம்",
        nav_physics: "பௌதிகக்கூடம்",
        nav_chemistry: "வேதியியல் ஆய்வகம்",
        footer_status: "ஆஃப்லைன் என்ஜின் இயங்குகிறது",
        btn_reset: "மீட்டமைக்கவும்",
        dash_badge: "ஆஃப்லைன் டெஸ்க்டாப் லேப்",
        dash_welcome_title: "காட்சிப்படுத்தலின் மூலம் ஆராயுங்கள்",
        dash_welcome_desc: "கணிதம் மற்றும் இயற்பியலின் ரகசியங்களைக் கண்டறியவும். பக்க மெனுவிலிருந்து ஓர் ஆய்வகத்தைத் தேர்ந்தெடுத்து, அளவீடுகளை நிகழ்நேரத்தில் மாற்றி, கணிப்பீடுகள் செய்யப்படுவதை நேரில் பாருங்கள்!",
        dash_btn_math: "கணிதக்கூடம்",
        dash_btn_physics: "பௌதிகக்கூடம்",
        constants_title: "அறிவியல் மாறிலிகளின் பட்டியல்",
        constants_desc: "அறிவியல் மற்றும் கணித கணக்கீடுகளுக்கான உலகளாவிய மாறிலிகளின் விரைவான பார்வை.",
        const_sol: "ஒளியின் வேகம்",
        const_grav: "ஈர்ப்பு முடுக்கம்",
        const_gconst: "ஈர்ப்பு மாறிலி",
        const_planck: "பிளாங்க் மாறிலி",
        const_pi: "பை (வட்ட விகிதம்)",
        const_euler: "யூலர் எண்",
        btn_next_quote: "அடுத்த மேற்கோள் →",
        banner_math_h4: "கணிதம் & வரைபடங்கள்",
        banner_math_p: "சார்புகளை வரைந்து பகுப்பாய்வு செய்க, தொகையீடுகளைப் பெறுக, அணிகளின் வரிசை மாற்றங்களைக் காண்க.",
        banner_phys_h4: "இயற்பியல் இயக்கவியல்",
        banner_phys_p: "விசைகள், காற்று எதிர்ப்பு மற்றும் கோணங்களின் கீழ் இயக்கத்தை உருவகப்படுத்துங்கள். ஆற்றல் பாதுகாப்பு வரைபடங்களைக் கவனியுங்கள்.",
        banner_chem_h4: "வேதியியல் & அணுக்கள்",
        banner_chem_p: "தனிமங்களின் எலக்ட்ரான் அமைப்பைக் கவனியுங்கள். சமன்பாடுகளைச் சமநிலைப்படுத்தி, மூலக்கூறு வரைபடங்களை உடனடியாகப் பெறுங்கள்.",
        banner_launch: "தொடங்குங்கள் →"
    }
};

const tabBannerTranslations = {
    en: {
        dashboard_title: "Interactive Dashboard",
        dashboard_desc: "Explore science and mathematics through beautiful dynamic simulations.",
        math_title: "Mathematics Studio",
        math_desc: "Analyse functions, approximate definite integrals visually, and inspect matrix operations.",
        physics_title: "Physics Sandbox",
        physics_desc: "Adjust coefficients, observe projectile trajectories, and inspect real-time pendulum energy bars.",
        chemistry_title: "Chemistry Laboratory",
        chemistry_desc: "Navigate the periodic table, inspect atomic Bohr models, and balance stoichiometry chemical equations."
    },
    si: {
        dashboard_title: "ප්‍රධාන පුවරුව",
        dashboard_desc: "සජීවීකරණ සිමියුලේෂන්ස් මගින් විද්‍යාව සහ ගණිතය ගවේෂණය කරන්න.",
        math_title: "ගණිත ස්ටුඩියෝව",
        math_desc: "මෙහිදී ඔබට සමීකරණ ප්‍රස්තාරගත කර අවකලන/අනුකලන සහ න්‍යාසයන් සජීවීව විශ්ලේෂණය කල හැක.",
        physics_title: "භෞතික විද්‍යා සංදර්ශකය",
        physics_desc: "වායු ප්‍රතිරෝධය යටතේ ප්‍රක්ෂිප්ත චලිතය සහ ලෝලකයක ශක්ති සංස්ථිතිය ප්‍රස්ථාර මඟින් නිරීක්ෂණය කරන්න.",
        chemistry_title: "රසායනික විද්‍යාගාරය",
        chemistry_desc: "මූලද්‍රව්‍යවල Bohr ආකෘති අධ්‍යයනය සහ ඕනෑම රසායනික සමීකරණයක් ක්ෂණිකව තුලිත කර අනුකෘති සැකසීම කරන්න."
    },
    ta: {
        dashboard_title: "முகப்புப்பலகை",
        dashboard_desc: "அழகான பௌதிக கணித உருவகப்படுத்துதல்கள் மூலம் அறிவியல் கற்றல்.",
        math_title: "கணிதக்கூடம்",
        math_desc: "சார்புகளை வரைந்து பகுப்பாய்வு செய்க, தொகையீடுகளைப் பெறுக, அணிகளின் வரிசை மாற்றங்களைக் காண்க.",
        physics_title: "பௌதிகக்கூடம்",
        physics_desc: "விசைகள், புவியீர்ப்பு தாக்கங்களை ஆராய்க. ஊசலின் இயக்க ஆற்றல் மாற்றங்களைச் சஜீவமாகக் காண்க.",
        chemistry_title: "வேதியியல் ஆய்வகம்",
        chemistry_desc: "தனிம அட்டவணை, போர் அணு மாதிரி மற்றும் வேதியியல் சமன்பாட்டுத் துல்லியங்களை ஆராய்க."
    }
};

const appLangState = {
    currentLang: 'en'
};

function updateAppLanguage(lang) {
    appLangState.currentLang = lang;
    localStorage.setItem('scimath_lang', lang);

    // Update elements with data-translate attributes
    document.querySelectorAll('[data-translate]').forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translationDictionary[lang] && translationDictionary[lang][key]) {
            el.textContent = translationDictionary[lang][key];
        }
    });

    // Update active tab title & description
    updateHeaderDescription(state.activeTab);
}

// Main entry
document.addEventListener('DOMContentLoaded', () => {
    // Bind navigation buttons
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const tab = item.getAttribute('data-tab');
            switchTab(tab);
        });
    });

    // Bind language selector
    const langSelect = document.getElementById('lang-select');
    if (langSelect) {
        const savedLang = localStorage.getItem('scimath_lang') || 'en';
        langSelect.value = savedLang;
        updateAppLanguage(savedLang);

        langSelect.addEventListener('change', (e) => {
            updateAppLanguage(e.target.value);
        });
    }

    initClock();
    initQuotes();
    initResets();
    initParticles();
});
