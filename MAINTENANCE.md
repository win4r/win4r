# Maintaining this profile

The GitHub profile is rendered from `scripts/render_profile.py` and `profile.json`.
All custom visuals are SVG files in this repository. No stats-card service,
visitor tracker, API key, package installation or paid service is required.

```sh
python3 scripts/render_profile.py            # render saved data, offline
python3 scripts/render_profile.py --refresh  # update public GitHub stars first
```

The GitHub Action refreshes repository stars weekly and can also be run manually.
It uses the repository's built-in token with contents write permission.
All seven API reads must succeed before saved data changes. A failed read does
not replace a star count with zero. Review the workflow run if it fails.

YouTube's **77K+** is a manually verified lower bound, based on the channel's
77.6K subscribers shown on 2026-10-30. It is not an automatically updated count.
When raising this milestone, update `minimum_subscribers` and the verification
date in `profile.json`, then render. No channel API key is stored.

Bilibili's **108,350 followers** was supplied by the profile owner on 2026-10-30.
This is a manually maintained count, stored as `bilibili.followers` in
`profile.json`; the GitHub star refresh preserves it. Both metric-panel themes
use content-hashed filenames so updated counts are visible without stale images.

Star totals cover only the seven named featured repositories. They are neither
an all-account total nor a claim that all projects were authored from scratch.
ClawTeam-OpenClaw credits HKUDS/ClawTeam. The deprecated lossless-claw fork is
shown as an upstream contribution and is not included in the featured-star total.

Video and social links are selected manually. Keep the associated repository and
video paired when changing them. Long-lived profile descriptions intentionally
avoid model version rankings, unverified benchmark claims and release promises.

The header, metrics and flagship panel have light and dark variants using HTML
`picture` sources. Project descriptions remain native GitHub text for readability
on narrow screens. SVGs contain no scripts, external fonts or embedded web pages.

The dark hero uses `scripts/hero_motion.py`: a 24-second looping 3D wireframe,
three computation slices, a scanning plane, moving data pulses and two orbital
particles. Projected geometry is generated offline and interpolated by native
SVG animation; subtle orbit and glow effects use internal CSS. No JavaScript is
embedded in the SVG. Text stays stationary. Browsers requesting reduced motion
receive the static core and no decorative motion. The light hero stays static.
The README also selects `hero-dark-static.svg` through a picture media source
when reduced motion is requested, so the fallback does not depend on media
emulation propagating into an external SVG image.
The README uses content-hashed image filenames, generated automatically from
`hero-dark.svg` and `hero-dark-static.svg`. Changing the artwork changes its
URL path, avoiding stale branch-image caches and redirects that drop query
parameters. Canonical SVG filenames remain available. Rendering identical
artwork reuses the same aliases; older aliases can remain for existing links.
Regenerate through the main renderer so the weekly refresh preserves this design.

To undo the redesign, revert the profile commit. No other project is modified.
