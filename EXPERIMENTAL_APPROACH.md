# Experimental Approach: XAS from a Surface Diffraction Beamline

## The Challenge

Surface diffraction beamlines are designed for **fixed-energy** experiments. The optics and monochromator are optimized for a single photon energy — not for scanning across absorption edges like a dedicated XAS beamline.

**Our goal:** Perform X-ray absorption spectroscopy (XAS) on a beamline that was never meant for it.

---

## The "Braggap" Solution

### Problem

When you scan the photon energy on a fixed-energy beamline, the intensity drops dramatically because the monochromator is detuned from the beamline harmonic.

### Solution: Synchronized Undulator Gap + Bragg Angle

We performed **"braggap" scans** — simultaneously controlling two degrees of freedom:

1. **Undulator gap** → changes the photon energy emitted by the source.
2. **Bragg angle of the monochromator** → selects which harmonic passes through.

By synchronizing these two motions, we **track the harmonic** throughout the energy scan, maintaining a constant intensity while varying the selected photon energy.

### Why it's clever

- The beamline infrastructure is **repurposed**, not modified.
- Intensity is **preserved** across the entire scan — no normalization artifacts from flux variation.
- The approach is **generalizable** to any beamline with a tunable undulator and a rotating monochromator.

---

## The XPAD Background Signal

### Problem

A surface diffraction beamline has **no fluorescence detector**. Without it, how do you measure XAS?

### Solution: Use the Diffraction Detector's Background

The XPAD (pixel array detector) is designed to collect diffraction patterns. But its **background signal** — the diffuse scattering between Bragg peaks — contains information about the total absorption.

**Key insight:** When you cross an absorption edge, the absorption coefficient μ(E) changes. This increases the diffuse scattering background across the entire detector. The "noise" becomes the signal.

### Pipeline

1. **Mask defective pixels** on the XPAD detector.
2. **Sum the remaining pixels** to get a total background intensity per frame.
3. **Normalize** against the monitor diode signal: `XAS = log(ROI / monitor)`.
4. **Extract pre-edge and normalization** using standard XAS procedures (larch/xraylarch).

---

## Operando Conditions

### The Reactor

All measurements were performed **operando** — inside a small sealed reactor that reproduced real catalysis conditions (temperature, pressure, gas flow) while the hard X-ray beam passed through it.

**Why this is challenging:**

- The reactor windows must be **X-ray transparent**, **gas-tight**, and **heat-resistant**.
- The catalyst is measured **while it is working** — not before or after, but during the reaction.
- XRD (crystal structure) and XANES (chemical state) are collected **simultaneously**, not sequentially.

### The Power of Simultaneity

Most operando experiments measure XRD **or** XAS. Doing both at the same time means:

- If a diffraction peak appears (phase change) **and** the absorption edge shifts (oxidation state change) **at the same moment**, you know they are causally linked — not just correlated in time.
- The non-destructive nature of hard X-rays allows observing the catalyst **in action**, without perturbing the reaction.

---

## Why This Matters

### Scientific Impact

- **Access to XAS without a dedicated beamline:** Opens absorption spectroscopy to experiments on beamlines where fluorescence detection is impractical or impossible.
- **Operando correlation:** XRD + XANES measured simultaneously inside a working catalyst reactor — linking crystal structure and chemical state in real time.
- **Resource efficiency:** Repurposes existing infrastructure instead of requiring dedicated beamtime on an XAS line.

### Technical Innovation

| Aspect | Conventional XAS | Our Approach |
|---|---|---|
| **Beamline type** | Dedicated XAS line | Surface diffraction line |
| **Energy scan** | Monochromator rotation | Braggap (gap + angle) |
| **Detector** | Fluorescence detector | XPAD background noise |
| **Signal** | Fluorescence photons | Δbackground scattering |
| **Intensity stability** | Flux correction needed | Harmonic tracking maintains intensity |
| **Conditions** | Ex situ or in situ | **Operando** — inside a working reactor |
| **Correlation** | XRD **or** XAS | XRD **and** XAS simultaneously |

---

## Key References for Your Presentation

1. **The braggap technique:** Search for "undulator gap tuning" + "monochromator Bragg angle" in the context of energy-scanning experiments on fixed-energy beamlines.

2. **XPAD detectors:** The XPAD140 is a Medipix-based pixel detector developed at ESRF. Its use for background scattering is an unconventional application.

3. **XAS from total scattering:** The principle that μ(E) changes affect the total scattered intensity is well-established in transmission XAS — we apply it to the diffuse background of a diffraction pattern.

---

## Talking Points for Your Doctoral Student

- **Start with the constraint:** "We needed XAS, but we were on a diffraction beamline."
- **Highlight the hack:** "We turned the diffraction detector's background noise into an absorption signal."
- **Emphasize the synchronization:** "Braggap scans keep intensity constant — no flux correction needed."
- **Connect to the science:** "This lets us monitor electronic structure changes during surface diffraction experiments."
- **The operando advantage:** "All of this was done inside a working catalyst reactor — XRD and XANES measured simultaneously, non-destructively, while the reaction was running."
