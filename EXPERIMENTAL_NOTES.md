# Experimental Notes — SOLEIL Surface Diffraction Beamline

## Goniometer and Geometric Parameters

A diffractometer is a goniometer. Key angles:

| Angle | Meaning | Role |
|---|---|---|
| **μ (mu)** | Sample rotation | Normally invariant if the sample is homogeneous on the surface. In practice, the sample is not homogeneous → varying μ allows intercepting more sample and improving the signal. |
| **Δ (delta)** | Out-of-plane circle | Controls the out-of-plane incidence/emergence angle. |
| **γ (gamma)** | In-plane circle | Enables 2θ scanning (diffraction angle in the plane). |

---

## XAS White Line (WL)

The **white line** is the region of the XAS spectrum where the signal is most intense — just above the absorption edge.

**Goal:** maximize signal intensity to perform the braggap scan more quickly.

### White line mapping

1. **WL map Δ-γ:** scan delta and gamma to find the geometry that maximizes the white line.
2. **WL map μ:** scan mu to find the sample orientation that maximizes the signal.
3. **WL map Δ:** scan delta alone to fine-tune the out-of-plane angle.

These maps optimize the geometry before starting the energy scan.

---

## Mu scan: signal optimization

**Goal:** find the μ angle that intercepts the maximum amount of sample.

- Vary μ and measure signal intensity.
- Calculate the **beam footprint** (beam size on the sample) to understand which area is interrogated.
- Choose the optimal μ to maximize the signal-to-noise ratio.

---

## XAS Analysis: 3 Parts

XAS analysis is divided into three parts:

### 1. XANES (X-ray Absorption Near Edge Structure)

- Region near the absorption edge (±50 eV).
- Gives the **oxidation state** and **local geometry** of atoms.
- The white line is in this region.

### 2. EXAFS (Extended X-ray Absorption Fine Structure)

- Region beyond the edge (+50 to +1000 eV).
- Oscillations that give **interatomic distances** and **coordination numbers**.
- Fourier transform analysis to extract coordination shells.

### 3. Normalization and Pre-edge Subtraction

- Subtract the pre-edge (before the edge).
- Normalize by the edge jump height.
- Use `larch`/`xraylarch` for standard procedures.

---

## Additional Tests

### Fluorescence Detector vs XPAD

- **Test a fluorescence detector** to compare with the XPAD signal.
- Compare signal-to-noise ratio, linearity, and spectral fidelity.
- This would validate that the XPAD background noise is a reliable substitute for a dedicated fluorescence detector.

---

## Experimental Workflow Summary

1. **WL mapping** → find optimal geometry (Δ, γ, μ).
2. **Mu scan** → maximize sample interception, calculate beam footprint.
3. **Braggap scan** → scan energy while maintaining constant intensity.
4. **XAS extraction** → XANES + EXAFS from XPAD background noise.
5. **Validation** → compare with a fluorescence detector if available.
