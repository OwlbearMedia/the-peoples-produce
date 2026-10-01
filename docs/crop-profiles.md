# Crop profiles

Each reservoir has a **crop profile** select. Choosing a profile fills in that
reservoir's pH target, pH alarm band and EC limits. Setpoints can then be tuned by
hand; the select keeps showing the last profile applied.

## Where the data lives

- [`crops/crops.yaml`](../crops/crops.yaml) is the crop database and the single source
  of truth. Every crop records what each source says, the range we chose, and why.
- [`tools/gen_crop_profiles.py`](../tools/gen_crop_profiles.py) turns it into the
  firmware package `esphome/packages/reservoir/crop_profile.yaml` and the table below.
  Both are generated; don't edit them by hand.
- `tools/validate.sh` fails if the generated files are out of date.

There is no single authoritative or maintained open database of hydroponic crop
targets. OpenFarm shut down in April 2025 and never had EC/pH data, and published
charts often disagree (a 2024 HortScience study states this outright for tomato). So
this project keeps its own, with every number traceable to a source. See
[decisions.md](decisions.md#9-our-own-sourced-crop-database).

## How a profile maps to setpoints

| Setpoint | Value |
|---|---|
| pH target | Middle of the crop's pH range, rounded to 0.05 |
| pH alarm band | Half the pH range, so "pH out of range" means outside the crop's range |
| EC low / high limits | The crop's (or stage's) EC range |
| pH dosing deadband, water temperature limit | Not set by profiles; shared defaults |

## Current profiles

<!-- BEGIN GENERATED: crop table -->
| Profile | pH target | pH range | EC range (mS/cm) | Confidence |
|---|---|---|---|---|
| Tomato - vegetative | 6.00 | 5.50-6.50 | 2.0-2.5 | medium |
| Tomato - fruiting | 6.00 | 5.50-6.50 | 2.4-3.5 | medium |
| Broccoli | 6.25 | 6.00-6.50 | 2.8-3.2 | medium |
| Brussels sprouts | 6.50 | 6.20-6.80 | 2.5-3.0 | low |

Recorded but not in the firmware:

- **Pepper** (conflicting): EC recommendations for established plants range from 0.8 to 3.5 and barely overlap. Needs a research source (ideally DWC or NFT, bell and hot separately) before it can be activated.
<!-- END GENERATED: crop table -->

## Research rules

Use these when adding or changing a crop:

1. **Prefer independent, primary sources.** In order: peer-reviewed research
   (ideally in DWC or NFT), university extension publications, trade press by named
   horticulturists, grower guides. Many grower charts copy one another, so several
   charts agreeing still counts as one source.
2. **Record what each source says,** in its own units and words, under `evidence`, even
   when it disagrees with the chosen range. Only cite what you actually read; record
   "abstract only" in the source's notes when that's all you saw.
3. **Choose the range where sources agree,** then explain it in `rationale`. Leave out
   a lone outlier, and say why.
4. **If sources genuinely conflict,** set `status: conflicting` and don't guess. The crop
   stays in the file, out of the firmware, until better evidence settles it.
5. **Rate confidence honestly:** `high` = independent research and extension agree;
   `medium` = at least one research or extension source, others consistent; `low` =
   grower charts only.
6. **Split into stages** only when a source gives stage-specific values.

## Adding or changing a crop

1. Research it using the rules above.
2. Add its sources under `sources:` and the crop under `crops:` in
   [`crops/crops.yaml`](../crops/crops.yaml).
3. Run `uv run tools/gen_crop_profiles.py`, then `tools/validate.sh`.
4. Flash the nodes (OTA is fine). Reservoirs keep their current profile: the applied
   profile is restored by name, so adding or reordering crops never relabels one.
