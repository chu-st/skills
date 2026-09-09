# GitHub artwork

The covers and avatar use the existing chu.st design-system logo, inverse symbol,
Uni Sans Heavy Caps and Roboto. Locked colours: `#137E7A`, `#0D5452`, `#19A8A3`.
The marks are reused without redrawing or recolouring their internal details.

Editable layout: `scripts/build_brand.cjs`. Supply a local copy of the design system:

```text
node scripts/build_brand.cjs <design-system-directory> assets/brand
```

The renderer requires Playwright and Chromium. `CHUST_BROWSER_BIN` can select a
local browser executable. Font files are used locally to render the artwork;
they are not included in this repository.

Branding belongs in the GitHub profile, repository pages and documentation.
Runtime skill instructions do not add promotional text to user deliverables.
