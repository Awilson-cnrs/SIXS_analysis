# Notes Expérimentales — SOLEIL Surface Diffraction Beamline

## Goniomètre et paramètres géométriques

Un diffractomètre est un goniomètre. Les angles clés :

| Angle | Signification | Rôle |
|---|---|---|
| **μ (mu)** | Rotation de l'échantillon | Normalement invariant si l'échantillon est homogène sur la surface. En pratique, l'échantillon n'est pas homogène → varier μ permet d'intercepter plus d'échantillon et d'améliorer le signal. |
| **Δ (delta)** | Cercle hors-plan | Contrôle l'angle d'incidence/émergence hors du plan de surface. |
| **γ (gamma)** | Cercle dans le plan | Permet de faire du 2θ (angle de diffraction dans le plan). |

---

## White Line (WL) du XAS

La **white line** est la région du spectre XAS où le signal est le plus intense — juste au-dessus du seuil d'absorption.

**Objectif :** maximiser l'intensité du signal pour pouvoir faire le scan braggap plus rapidement.

### Cartographies de la white line

1. **WL map Δ-γ** : balayer delta et gamma pour trouver la géométrie qui maximise la white line.
2. **WL map μ** : balayer mu pour trouver l'orientation de l'échantillon qui maximise le signal.
3. **WL map Δ** : balayer delta seul pour affiner l'angle hors-plan.

Ces cartographies permettent d'optimiser la géométrie avant de lancer le scan en énergie.

---

## Mu scan : optimisation du signal

**Objectif :** trouver l'angle μ qui intercepte le maximum d'échantillon.

- Varier μ et mesurer l'intensité du signal.
- Calculer la **beam footprint** (taille du faisceau sur l'échantillon) pour comprendre quelle zone est interrogée.
- Choisir le μ optimal pour maximiser le rapport signal/bruit.

---

## Analyse XAS : 3 parties

L'analyse XAS se décompose en trois parties :

### 1. XANES (X-ray Absorption Near Edge Structure)

- Région proche du seuil d'absorption (±50 eV).
- Donne l'**état d'oxydation** et la **géométrie locale** des atomes.
- La white line est dans cette région.

### 2. EXAFS (Extended X-ray Absorption Fine Structure)

- Région au-delà du seuil (+50 à +1000 eV).
- Oscillations qui donnent les **distances interatomiques** et le **nombre de coordination**.
- Analyse par transformée de Fourier pour extraire les shells de coordination.

### 3. Normalisation et soustraction du pré-arête

- Soustraire le pré-arête (avant le seuil).
- Normaliser par la hauteur du saut au seuil.
- Utiliser `larch`/`xraylarch` pour les procédures standard.

---

## Tests complémentaires

### Détecteur de fluorescence vs XPAD

- **Tester un détecteur de fluorescence** pour comparer avec le signal XPAD.
- Comparer le rapport signal/bruit, la linéarité, et la fidélité du spectre.
- Cela validerait que le bruit de fond XPAD est un substitut fiable du détecteur de fluorescence dédié.

---

## Résumé du workflow expérimental

1. **Cartographie WL** → trouver la géométrie optimale (Δ, γ, μ).
2. **Mu scan** → maximiser l'interception de l'échantillon, calculer la beam footprint.
3. **Scan braggap** → scanner en énergie en maintenant l'intensité constante.
4. **Extraction XAS** → XANES + EXAFS depuis le bruit de fond XPAD.
5. **Validation** → comparer avec un détecteur de fluorescence si disponible.
