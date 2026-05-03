---
name: colour-palette
description: Use when choosing, designing, generating, or reviewing colours or colour palettes for any context — CSS themes, UI components, terminal configs, status bars, or brand identity
---

# Colour Palette Design

Guide colour selection for any context — CSS themes, UI palettes, status bars, terminal configs, or anything else that needs colours chosen well.

## When to Use

When asked to choose, design, generate, or review colours or colour palettes.

## Process

1. **Understand the context.** What is the palette for? What mood or aesthetic? How many colours are needed? What format will colours be consumed in (hex, HSL, OKLCH, RGB, CSS custom properties, etc.)? Are there existing colours to work with or around?
2. **Select colours in OKLCH.** Use OKLCH as the working colour space for selection and scale generation — it is perceptually uniform, so lightness and chroma behave predictably across hues. Convert to the target format for output.
3. **Verify accessibility.** For any text/background pair, check WCAG AA contrast (4.5:1 for normal text, 3:1 for large text and UI components). Flag colour blindness risks — never rely on colour alone for meaning.
4. **Explain the reasoning.** State which harmony type was used, why the colours suit the context, and any trade-offs made.

## Reference

### Colour Wheel

12 colours in a circle. **Primaries** (red, yellow, blue in RYB; red, green, blue in RGB) → mix two to get **secondaries** (orange, green, violet) → mix primary + adjacent secondary for **tertiaries** (red-orange, yellow-orange, yellow-green, blue-green, blue-violet, red-violet).

**Warm** (red, orange, yellow): energy, urgency, advance toward viewer, higher visual weight. **Cool** (blue, green, violet): calm, trust, recede, restful. Temperature exists within hues — a red leaning orange is warmer than one leaning violet. Mixing warm-leaning and cool-leaning variants of the same hue creates subtle discord.

**Neutrals** (black, white, grey, beige) lean warm (cream, warm grey) or cool (blue-grey). Match neutral temperature to the palette's overall warmth/coolness.

### Harmony Types

| Harmony | Relationship | Best For | Watch Out |
|---------|-------------|----------|-----------|
| **Monochromatic** | Tints/shades of one hue | Clean, elegant, minimalist | Can feel flat without value contrast |
| **Complementary** | 180° apart | Maximum contrast, CTAs, bold | Jarring at equal proportions — one must dominate |
| **Split-Complementary** | Base + two adjacent to complement | Contrast with nuance | Needs careful 3-colour balance |
| **Analogous** | 3 colours within 60° arc | Nature-inspired, serene | Needs value contrast to avoid muddiness |
| **Triadic** | 3 colours at 120° intervals | Vibrant, balanced variety | Let one dominate; full saturation on all three overwhelms |
| **Tetradic** | Two complementary pairs | Complex designs, dashboards | Hardest to balance; manage warm/cool ratio |
| **Square** | 4 colours at 90° intervals | Balanced variety | Same challenges as tetradic |

### HSL/HSB

**HSL** (CSS): Hue 0–360°, Saturation 0–100%, Lightness 0–100% (0%=black, 50%=pure colour, 100%=white). Manipulation: lighter tint → increase L; darker shade → decrease L; mute → decrease S; disabled state → S−30 L+15; hover → L−5 to −10.

**HSB** (Figma, Sketch, Photoshop): B=100% is pure colour, not white. To darken: simultaneously increase S and decrease B (removes white, not adds black) — produces richer darks.

**HSL's flaw**: lightness is not perceptually uniform. Yellow at L=50% appears far brighter than blue at L=50%. Use OKLCH for palette generation.

### OKLCH

Perceptually uniform colour space (Bjorn Ottosson, 2020). CSS-native via `oklch()`. Tailwind v4 uses OKLCH for all default colours.

- **L** (Lightness): 0–1, perceptually uniform across hues
- **C** (Chroma): 0–~0.37, distance from grey
- **H** (Hue): 0–360°

Why it's superior: equal L values look equally bright regardless of hue; changing only L produces no hue drift; gradient interpolation stays vivid (no muddy midpoints); supports P3 wide gamut.

**CIELAB** is the predecessor — better than HSL but has hue non-uniformity in blue-purple.

### Tonal Scales

For an 11-step scale (50–950), use non-linear lightness distribution in OKLCH:

| Step | OKLCH L | Use |
|------|---------|-----|
| 50 | 0.97 | Subtle backgrounds |
| 100 | 0.93 | Hover backgrounds |
| 200 | 0.87 | Active backgrounds, borders |
| 300 | 0.79 | Borders, secondary elements |
| 400 | 0.70 | Placeholder text |
| 500 | 0.60 | Base — icons, key elements |
| 600 | 0.50 | Primary text on light |
| 700 | 0.40 | Headings, emphasis |
| 800 | 0.31 | Heavy emphasis |
| 900 | 0.22 | High contrast text |
| 950 | 0.14 | Near-black, dark mode backgrounds |

**500 is the base** — closest to the brand/seed colour.

**Saturation curve**: parabolic — peak chroma at mid-lightness (400–600), tapering at both extremes. Light tints are barely tinted; dark shades are deep but not garish.

**Hue compensation** (Bezold–Brücke effect): lighter variants shift slightly toward yellow/warmth, darker variants toward blue/violet, to keep perceived hue consistent.

### The 60-30-10 Rule

- **60%** Dominant: backgrounds, large surfaces (neutral/muted)
- **30%** Secondary: navigation, cards, supporting elements
- **10%** Accent: buttons, links, icons, badges

Variants: 70-25-5 (tighter accent), 80-15-5 (content-heavy). Never distribute equally — no hierarchy means no focus.

### Accessibility

**WCAG contrast**: `(L1 + 0.05) / (L2 + 0.05)` where L is relative luminance `0.2126R + 0.7152G + 0.0722B` (linearised sRGB). AA normal text: 4.5:1. AA large text/UI: 3:1. AAA normal: 7:1.

Key thresholds: lightest grey on white passing AA normal text ≈ `#767676`. Pure black on white = 21:1. Near-black on off-white ≈ 15:1 (comfortable).

**Colour blindness** (~8% of males): protanopia (no red cones), deuteranopia (no green cones, most common), tritanopia (no blue cones, rare). Rules: never colour alone for meaning; avoid pure red/green pairs; blue is safest; safe pairings are blue/orange, blue/red, blue/yellow; ensure luminance contrast not just hue contrast.

### Colour Psychology

| Colour | Associations | Common In |
|--------|-------------|-----------|
| Red | Energy, urgency, danger, appetite | Food, sales, entertainment |
| Orange | Warmth, creativity, friendliness | Entertainment, food, CTAs |
| Yellow | Optimism, clarity, caution | Warnings, children's (fatigue in large areas) |
| Green | Nature, health, growth, safety | Health, finance, eco |
| Blue | Trust, stability, professionalism | Finance, tech, healthcare, corporate |
| Purple | Luxury, creativity, royalty | Luxury brands, beauty, creative |
| Pink | Playfulness, tenderness | Beauty, fashion, confectionery |
| Black | Sophistication, luxury, power | Luxury, high-end tech |
| White | Purity, cleanliness, simplicity | Healthcare, tech, minimalist |

### Dark Mode Adaptation

Not just inversion. Background: dark grey (#121212–#1E1E1E), not pure black (causes halation). Elevation via lighter surfaces (shadows invisible on dark). Text: off-white (#E0E0E0–#ECECEC), not pure white. Reduce saturation ~20 points (saturated on dark = optical vibration). Lightness inverts: light mode text at 800–900 steps → dark mode text at 100–200. Warning yellow may need saturation boost on dark (exception to desaturation rule).

### Complete Palette Structure

When a full palette is needed:

1. **Primary** (1–2 hues, full tonal scale): main actions, links, active states
2. **Secondary** (1–2 hues): secondary buttons, tags, highlights
3. **Neutral/Grey** (full scale): text, backgrounds, borders — add subtle brand tint (pure grey feels lifeless)
4. **Semantic** (4 categories, each with scale): success (green), warning (yellow/amber), error (red), info (blue)
5. **Accent** (optional, 1–3 hues): data viz, illustrations, category coding

### Aesthetic Recipes

**Earthy/Natural**: hues 20–45° + 80–160°, saturation 15–45%, cream not white. Key: #C17756 terracotta, #87A878 sage, #7D8B55 olive, #D4C5A9 sand.

**Corporate/Professional**: hues 200–230° + neutral greys, 70-25-5 rule. Key: #1E3A5F navy, #2563EB blue, #6B7280 cool grey.

**Playful/Vibrant**: multiple hues 70–100% saturation, one dominant. Key: #EC4899 hot pink, #3B82F6 electric blue, #FACC15 vivid yellow.

**Minimalist**: 1–2 colours + black/white/grey, accent <5% of field. Key: #18181B off-black, #A1A1AA mid grey, #FAFAFA off-white.

**Retro/Vintage**: mustard/avocado/burnt orange/teal, saturation 30–60%, reduce full-sat retro hues 20–40%, cream not white. Key: #C49A2A mustard, #6B8E23 avocado, #CC5500 burnt orange.

**Pastel/Soft**: any hue at lightness >85%, saturation reduced 30–50%. OKLCH L 0.85–0.95, C 0.03–0.08. All pastels at similar lightness.

**Dark/Moody/Luxury**: jewel tones at saturation 40–70%, lightness 20–35%. Dark backgrounds as 60%, gold/copper as 10%. Key: #0F172A midnight, #064E3B emerald, #7F1D1D burgundy, #D4AF37 gold.

### Common Mistakes

1. Too many colours — 2–3 hues + neutrals, tonal variants for variety
2. Oversaturation — full saturation only for small accents; backgrounds <15% saturation
3. Inconsistent saturation — mixing muted with neon feels jarring
4. Pure black text — use near-black (#1A1A2E, #111827) for comfort
5. Insufficient contrast — verify WCAG AA for all text/background pairs
6. Colour alone for meaning — always pair with secondary indicators
7. No hierarchy — apply 60-30-10 or similar
8. No context testing — test on real components, not just swatches
9. Light mode only — both modes need explicit design
10. Trend chasing — restrained bases with updateable accents
