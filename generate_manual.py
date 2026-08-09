import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter

def build_pdf_manual():
    print("Initializing PyQt5 environment for document processing...")
    app = QApplication(sys.argv)
    
    html_content = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {
        font-family: "Nirmala UI", "Segoe UI", Arial, sans-serif;
        color: #1e293b;
        margin: 30px;
        line-height: 1.6;
    }
    .header-box {
        text-align: center;
        background: linear-gradient(135deg, #1e3a8a, #0f766e);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    .header-box h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .header-box p {
        margin: 5px 0 0 0;
        font-size: 16px;
        opacity: 0.9;
    }
    h2 {
        color: #1e3a8a;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
        margin-top: 30px;
        font-size: 20px;
    }
    h3 {
        color: #0f766e;
        font-size: 15px;
        margin-top: 20px;
        margin-bottom: 5px;
    }
    p {
        font-size: 12.5px;
        text-align: justify;
        margin-bottom: 12px;
    }
    .lang-si {
        background-color: #f8fafc;
        border-left: 4px solid #0f766e;
        padding: 10px 15px;
        color: #334155;
        margin-bottom: 25px;
        font-size: 12px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 12px;
    }
    th, td {
        border: 1px solid #cbd5e1;
        padding: 10px;
        text-align: left;
    }
    th {
        background-color: #f1f5f9;
        font-weight: bold;
        color: #0f172a;
    }
    .footer-box {
        text-align: center;
        margin-top: 50px;
        border-top: 1px solid #e2e8f0;
        padding-top: 15px;
        font-size: 11px;
        color: #64748b;
    }
</style>
</head>
<body>

    <div class="header-box">
        <h1>SciMath Visual Studio</h1>
        <p>Interactive Offline Desktop Lab & Reference Manual</p>
        <p style="font-size: 12px; margin-top: 10px; opacity: 0.8;">අන්තර්ක්‍රියාකාරී විද්‍යා සහ ගණිත ප්‍රායෝගික විද්‍යාගාර අත්පොත</p>
    </div>

    <h2>1. Introduction / හැඳින්වීම</h2>
    
    <p class="lang-en">
        <strong>SciMath Visual Studio</strong> is a standalone offline interactive simulation suite built for student physics, chemistry, and mathematics experimentation. The system packages HTML5 canvas animations, stoichiometric algorithms, Verlet gravity orbits, and refractive optics math calculations into a single desktop application powered by an embedded Python PyQt5 web view container. This manual serves as a technical parameter setup and operating guide for the simulations.
    </p>
    
    <div class="lang-si">
        <strong>SciMath Visual Studio</strong> යනු විද්‍යාව, ගණිතය සහ රසායන විද්‍යා පර්යේෂණාත්මක අත්හදා බැලීම් ඩෙස්ක්ටොප් පරිගණකයක තත්‍ය කාලීනව සිදු කිරීම සඳහා නිපදවන ලද අනුකරණ (simulation) මෘදුකාංගයකි. HTML5 Canvas විදැහුම්කරණය, stoichiometric තුල්‍යකරණ න්‍යායයන්, Verlet ගුරුත්වාකර්ෂණ කක්ෂ ගණනයන් සහ ප්‍රකාශ විද්‍යාවේ කාච සුත්‍රයන් යොදාගනිමින් නිපදවන ලද මෙය PyQt5 desktop shell එකක් මඟින් ක්‍රියාත්මක වේ.
    </div>

    <h2>2. Mathematics Studio / ගණිත විද්‍යාගාරය</h2>
    
    <h3>A. Fourier Wave Synthesizer / ෆූරියර් තරංග සංස්ලේෂක මාලාව</h3>
    <p class="lang-en">
        The Fourier tool uses sine-wave summation to synthesize square, triangle, and sawtooth periodic waveforms in real-time. Signals are additive. Users can modify parameters such as output frequency, amplitude, and the number of discrete harmonics. Slide controls dynamically show how increasing harmonics converges the synthesized line to the theoretical ideal shape.
    </p>
    <div class="lang-si">
        ෆූරියර් සංස්ලේෂකය මඟින් සයින් තරංග කිහිපයක් එකිනෙක එකතු කිරීමෙන් කොටු, ත්‍රිකෝණ සහ කියත්-දත් හැඩැති තරංග නිපදවන ආකාරය ග්‍රැෆික්ස් මඟින් පෙන්වයි. මෙහිදී තරංගයේ සංඛ්‍යාතය (frequency), විස්තාරය (amplitude) සහ හාමොනික්ස් (harmonics) සංඛ්‍යාව වෙනස් කරන විට තරංගය සලකා බලන සීමාවට ක්‍රමයෙන් ළඟා වන ආකාරය නිරීක්ෂණය කළ හැකිය.
    </div>

    <h3>B. Galton Board Probability Simulator / ගෝල්ටන් බෝඩ් සම්භාවිතාව</h3>
    <p class="lang-en">
        Simulates physical marble drop vectors colliding with rows of triangular pins. The cumulative deviation converges into the normal distribution curve (Gaussian Bell Curve). Provides variable input speeds and ball count settings, effectively illustrating the Central Limit Theorem.
    </p>
    <div class="lang-si">
        කුඩා රවුම් බෝල කූඤ්ඤ අතරින් පහළට වැටෙද්දී සිදුවන ඝට්ටන පිලිබඳ සංඛ්‍යාන දත්ත ගණනය කර අවසානයේදී සාමාන්‍ය ව්‍යාප්ති වක්‍රය (Gaussian Bell Curve) ගොඩනැගෙන ආකාරය මෙයින් නිරූපණය කෙරේ. මෙහි ධාවන වේගය සහ බෝල සංඛ්‍යාව වෙනස් කළ හැකිය.
    </div>

    <h2>3. Physics Sandbox / භෞතික විද්‍යා මොඩියුලය</h2>
    
    <h3>A. Convex/Concave Ray Optics / කිරණ ප්‍රකාශ විද්‍යාගාරය</h3>
    <p class="lang-en">
        Simulates Light Ray Tracing using geometric optical laws on thin glass lenses. The focal length and object distance parameter sliders automatically calculate image distance, image height, magnification, and type (Real vs Virtual; Inverted vs Upright). Shows principal parallel, focal, and center axis rays.
    </p>
    <div class="lang-si">
        ජ්‍යාමිතික කිරණ නීති භාවිතයෙන් උත්තල සහ අවතල තුනී කාච තුළින් ආලෝකය වර්තනය වන ආකාරය පෙන්වයි. නාභීය දුර (focal length) සහ වස්තුවේ පිහිටීම (object position) වෙනස් කරන විට සැබෑ හෝ අතාත්වික, උඩුකුරු හෝ යටිකුරු ප්‍රතිබිම්බ සෑදෙන ආකාරය සජීවීව කැන්වසය මත ගණනය කෙරේ.
    </div>

    <h3>B. Kepler Planetary Gravity / කක්ෂීය ගුරුත්වාකර්ෂණය</h3>
    <p class="lang-en">
        Applies Verlet Integration to run planetary gravitational orbits around a high-mass star. Leverages orbital velocity vectors, star mass multipliers, and distance vectors to visualize gravity field loops. Tracks escape trajectories and stellar mass collisions.
    </p>
    <div class="lang-si">
        Verlet Integration ක්‍රමය භාවිතයෙන් මධ්‍යගත තාරකාවක් වටා ග්‍රහලෝකවල ගුරුත්වාකර්ෂණ ගමන් මාර්ගයන් තත්‍ය කාලීනව ගණනය කරයි. central star ස්කන්ධය, ග්‍රහලෝකයේ ආරම්භක වේගය වෙනස් කර කක්ෂීය චලිත නියමයන්, ඝට්ටන මෙන්ම ගුරුත්වාකර්ෂණයෙන් මිදී යන කෝණ අධ්‍යයනය කළ හැකිය.
    </div>

    <h2>4. Chemistry Lab / රසායනික විද්‍යා විද්‍යාගාරය</h2>
    
    <h3>A. Bohr Orbitals & Dynamic Periodic table / ආවර්තිතා වගුව සහ බෝර් ආකෘතිය</h3>
    <p class="lang-en">
        Interact with the elements database that renders electron configurations, atomic shells, electronegativities, and points. Features dynamic electron configuration orbital diagrams that rotate to display atomic structures.
    </p>
    <div class="lang-si">
        මූලද්‍රව්‍ය ආවර්තිතා වගුවේ දත්ත පිරික්සීමට සහ තෝරාගන්නා ලවණ අයන වල බෝර් කක්ෂීය කවයන්හි සජීවී ඉලෙක්ට්‍රෝන භ්‍රමණ සජීවීකරණයන් මෙහිදී දැකගත හැකිය.
    </div>

    <h3>B. Ball-and-Stick 3D Compound Viewer / ත්‍රිමාන අණු ආකෘති දර්ශකය</h3>
    <p class="lang-en">
        A coordinate-transformed interactive 3D chemical compound viewer. Allows users to load presets (Water, CO2, Methane, Ethanol, etc.) and perform manual mouse rotation, scaling, and auto-rotation configurations.
    </p>
    <div class="lang-si">
        ජලය, CO₂, මෙතේන් වැනි රසායනික සංයෝගයන්හි සැබෑ බන්ධන ආකෘති ත්‍රිමාන අවකාශය තුළ (3D rendering) මූසිකය භාවිතයෙන් කරකවමින් සහ විශාල කරමින් පරීක්ෂා කිරීමට හැකියාව ඇත.
    </div>

    <h3>C. Potentiometric pH Titration Lab / pH මාලනය</h3>
    <p class="lang-en">
        Interactive hydrochloric acid and sodium hydroxide (HCl + NaOH) neutralization simulation. Features adjustable concentrations for both acid and base inputs, addition rates, and indicators (Phenolphthalein, Litmus, Methyl Orange, Bromothymol Blue). Renders a live titration equivalence curve graph mapping volumetric change against solution pH.
    </p>
    <div class="lang-si">
        ප්‍රබල අම්ල-භෂ්ම (HCl + NaOH) මධ්‍යස්ථකරණ රසායනික ලැබ් අනුකරණයයි. මෙහිදී සාන්ද්‍රණයන් සහ එක් කරන දියර බිංදු වේගය පාලනය කරමින්, තෝරාගන්නා දර්ශකය ප්‍රකාරව (Phenolphthalein/Litmus/Methyl Orange) ද්‍රාවණයේ වර්ණ වෙනස් වීම් නිශ්චය කළ හැකිය. දකුණු පසින් pH අගයට අනුරූප ප්‍රස්තාරය සජීවීව ඇඳේ.
    </div>

    <h3>D. Spectrograph Flame Test / දැල් වර්ණාවලීක්ෂය</h3>
    <p class="lang-en">
        Demonstrates atomic cation transition emission spectra. Allows inserting a virtual nichrome loop wire coated with chloride salts (NaCl, CuCl2, LiCl, KCl, BaCl2, SrCl2, CaCl2) into a Bunsen burner flame, showing ionization color shifts and emission spectrum wavelength lines (in nanometers) matching quantum mechanics configurations.
    </p>
    <div class="lang-si">
        Bunsen burner දැල්ල වෙත ලෝහ ලවණ වර්ග (Sodium, Copper, Lithium, Potassium, Strontium, Barium) ළං කළ විට ඇතිවන වර්ණ වෙනස් වීම් (Flame test) පෙන්වන අතර වර්ණාවලිමාන පුවරුවක එම මූලද්‍රව්‍යවල විමෝචන වර්ණාවලි රේඛා (emission lines) මනින තරංග ආයාම (wavelength) සමඟ විදහා දක්වයි.
    </div>

    <h2>5. Main User Controls Summary / සංක්ෂිප්ත පාලක ලැයිස්තුව</h2>
    
    <table>
        <thead>
            <tr>
                <th width="30%">Feature / පාලකය</th>
                <th width="35%">English User Action</th>
                <th width="35%">සිංහල ක්‍රියාවලිය</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Sliders (Range)</strong></td>
                <td>Drag left/right to modify physical settings and trigger recalculated renders.</td>
                <td>භෞතික අගයන් වෙනස් කර කැන්වසයේ ගණිතමය දත්ත තත්‍ය කාලීනව යාවත්කාලීන කිරීමට ලිස්සනයන් දෙපසට අදින්න.</td>
            </tr>
            <tr>
                <td><strong>Dropdowns (Select)</strong></td>
                <td>Click elements to load presets (e.g. Salts, Compounds, and Indicators).</td>
                <td>නියමිත ලවණ වර්ග, අණු සහ දර්ශක වැනි වෙනස්කම් තේරීමට dropdown මෙනුව ක්ලික් කරන්න.</td>
            </tr>
            <tr>
                <td><strong>Mouse Drag</strong></td>
                <td>Rotate 3D Compounds, shift objects, or drag light source coordinates.</td>
                <td>ත්‍රිමාන අණු කරකැවීමට හෝ ආලෝක කිරන ප්‍රභව වෙනස් කිරීමට cursor එක අල්ලා අදින්න (drag).</td>
            </tr>
            <tr>
                <td><strong>Action Buttons</strong></td>
                <td>Trigger auto-titration loops, drop bases, or insert/withdraw wire loops.</td>
                <td>ස්වයංක්‍රීය pH මාලනය හෝ දැල්ලට ලවණ කූර ඇතුළු කිරීම/ඉවත් කිරීම වැනි ක්‍රියාවන් සිදුකරන්න.</td>
            </tr>
        </tbody>
    </table>

    <div class="footer-box">
        <p>SciMath Visual Studio &bull; Offline Laboratory Companion Software</p>
        <p style="font-size: 10px; margin-top: 5px;">Generated automatically via PyQt5 QtPrintSupport Suite. All rights reserved.</p>
    </div>

</body>
</html>
"""

    print("Writing HTML content to document object...")
    doc = QTextDocument()
    doc.setHtml(html_content)
    
    pdf_filename = "SciMath_Visual_Studio_Manual.pdf"
    print(f"Configuring PDF printer target: {pdf_filename}...")
    printer = QPrinter()
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(pdf_filename)
    # Configure neat margins
    printer.setPageMargins(15.0, 15.0, 15.0, 15.0, QPrinter.Millimeter)
    
    print("Printing document layout to standalone PDF file...")
    doc.print_(printer)
    
    if os.path.exists(pdf_filename):
        print(f"SUCCESS! stand-alone PDF user manual generated. Size: {os.path.getsize(pdf_filename)} bytes")
    else:
        print("ERROR: PDF was not found after execution.")

if __name__ == "__main__":
    build_pdf_manual()
