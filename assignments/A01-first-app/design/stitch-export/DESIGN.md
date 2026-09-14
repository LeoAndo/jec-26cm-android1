---
name: First Step Minimalist
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1c1c'
  on-surface-variant: '#3e4946'
  inverse-surface: '#303030'
  inverse-on-surface: '#f3f0ef'
  outline: '#6d7a76'
  outline-variant: '#bdc9c5'
  surface-tint: '#006b5f'
  primary: '#006a5e'
  on-primary: '#ffffff'
  primary-container: '#008577'
  on-primary-container: '#ffffff'
  inverse-primary: '#73d8c7'
  secondary: '#20695d'
  on-secondary: '#ffffff'
  secondary-container: '#a7eddd'
  on-secondary-container: '#266e61'
  tertiary: '#93482f'
  on-tertiary: '#ffffff'
  tertiary-container: '#b16045'
  on-tertiary-container: '#ffffff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#90f4e3'
  primary-fixed-dim: '#73d8c7'
  on-primary-fixed: '#00201c'
  on-primary-fixed-variant: '#005047'
  secondary-fixed: '#aaf0e0'
  secondary-fixed-dim: '#8ed4c4'
  on-secondary-fixed: '#00201b'
  on-secondary-fixed-variant: '#005045'
  tertiary-fixed: '#ffdbd0'
  tertiary-fixed-dim: '#ffb59d'
  on-tertiary-fixed: '#390b00'
  on-tertiary-fixed-variant: '#76321b'
  background: '#fcf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e5e2e1'
typography:
  headline-lg:
    fontFamily: Noto Sans
    fontSize: 32px
    fontWeight: '400'
    lineHeight: 40px
  headline-md:
    fontFamily: Noto Sans
    fontSize: 24px
    fontWeight: '400'
    lineHeight: 32px
  headline-sm:
    fontFamily: Noto Sans
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
  body-lg:
    fontFamily: Noto Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Noto Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Noto Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.1px
  label-md:
    fontFamily: Noto Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.5px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 16px
  margin: 24px
  space-xs: 4px
  space-sm: 8px
  space-md: 16px
  space-lg: 24px
  space-xl: 32px
---

## Brand & Style

This design system targets absolute beginners entering the Android development ecosystem. The experience is designed to feel welcoming, unobtrusive, and textbook-pure. 

The aesthetic is purely minimal and structural—embracing standard native Android Light Theme principles. It avoids ornamental distractions, gradients, or heavy visual effects, prioritizing crisp contrast, native Android rhythm, and immediate visual comprehension. The emotional tone is reassuring, clean, and foundational.

## Colors

The palette adheres to standard Android light theme conventions:
- **Canvas / Surface:** Pure White (`#FFFFFF`) ensures zero visual noise and high legibility.
- **Neutral / Text:** Material Grey 900 (`#212121`) serves as the primary text color, delivering optimal reading contrast against the white backdrop. Secondary text uses Material Grey 700 (`#616161`).
- **Primary Accent:** Classic Android Teal 700 (`#008577`) is reserved for primary focus states, key interactive controls, and native status emphasis.
- **Secondary / Variant:** Darker Teal 900 (`#00574B`) is dedicated to system status bar tinting and active press states.

## Typography

The type system is powered by `Noto Sans`, offering standard native Android rendering across Latin script and Japanese CJK typography. 

The primary introductory greeting is assigned strictly to `headline-md` (24px / 24sp with a 32px line-height), ensuring balanced vertical line boxes when centered inside portrait layouts. Body text and helper labels retain standard Material reading scales to maintain full compatibility with Android platform conventions.

## Layout & Spacing

Layouts follow standard native Android UI parameters:
- **Canvas Inset:** Root content containers implement a fixed `24dp` (`margin: 24px`) padding on all edges, providing a comfortable visual boundary from device bezels and system bars.
- **Vertical Linear Flow:** Screens use a single-axis vertical flow (`LinearLayout`-style column structure) centered horizontally and vertically (`gravity="center"`).
- **System Insets:** Respect standard Android system window insets (`fitsSystemWindows="true"`), positioning content safely below status bars and above system navigation handles.
- **Adaptation:** Mobile layouts feature full-width single-column flow with `24px` internal padding. Tablets and larger viewports center a constrained content box of max-width `480px` to maintain focused readability.

## Elevation & Depth

Visual hierarchy uses a flat, low-contrast approach without artificial skeuomorphism:
- **Default Surfaces:** The canvas sits at baseline elevation (0dp) on pure `#FFFFFF`.
- **Containers & Panels:** Outlined structures use subtle low-contrast borders (`#E0E0E0`, 1px solid) rather than drop shadows.
- **Interactive Elevation:** Interactive touch surfaces (e.g., standard raised buttons) leverage native standard Android elevation: 2dp resting elevation with a crisp 4dp elevation on state press, casting subtle ambient neutral shadows without color tinting.

## Shapes

The design system employs a soft corner radius standard (`roundedness: 1`), matching classic Android Material Design components:
- Standard elements, buttons, inputs, and educational sample cards use a 4px (`0.25rem`) corner radius.
- Chips, modal dialogs, and floating utility containers use an 8px (`0.5rem`) corner radius.

## Components

### Main Greeting / Message Display
- Centered within the parent container (`layout_gravity="center"`).
- Applied with `headline-md` (24px/sp), color `#212121`, and balanced horizontal centering.

### Buttons
- **Contained Button:** Filled background `#008577`, text `#FFFFFF`, 4px corner radius, standard 36dp–48dp minimum touch target, horizontal padding 16px.
- **Outlined / Text Button:** Background transparent, text `#008577`, 1px border `#008577` (for outline variant).

### Input Fields
- Native baseline input: Flat background `#FAFAFA` with a bottom-line stroke (`#757575`) or full 1px outlined box (`#E0E0E0`), 4px corner radius, and internal padding of 12px 16px. Active focus highlights the stroke to `#008577`.

### Cards
- Surface `#FFFFFF` with a 1px border (`#E0E0E0`), 4px corner radius, and `space-lg` (24px) internal padding. Free of dropped shadows to preserve the clean educational layout.

### Lists
- Standard vertical stack with single-line or two-line list items, 56dp item height, 16px edge padding, and subtle 1px dividers (`#EEEEEE`).

### Checkboxes & Radio Buttons
- Standard 24dp size footprint, tint color `#008577` for active/selected states and `#757575` for unselected borders.

### System App Bar
- Top app bar height of 56dp, background `#008577` (or `#FFFFFF` in high-minimalism mode), with 20px `#212121` title typography and 16px start margin.