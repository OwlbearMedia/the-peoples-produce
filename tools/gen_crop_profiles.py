# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Generate the firmware crop profile select and the docs table from crops/crops.yaml.

    uv run tools/gen_crop_profiles.py          write the generated files
    uv run tools/gen_crop_profiles.py --check  exit 1 if they are out of date

Outputs:
    esphome/packages/reservoir/crop_profile.yaml
    the table between the GENERATED markers in docs/crop-profiles.md
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CROPS = ROOT / "crops" / "crops.yaml"
PACKAGE = ROOT / "esphome" / "packages" / "reservoir" / "crop_profile.yaml"
DOC = ROOT / "docs" / "crop-profiles.md"
DOC_BEGIN = "<!-- BEGIN GENERATED: crop table -->"
DOC_END = "<!-- END GENERATED: crop table -->"

STATUSES = {"active", "conflicting", "draft"}
CONFIDENCES = {"high", "medium", "low"}
SOURCE_TYPES = {"peer-reviewed", "extension", "trade-press", "grower-guide"}
NOT_SET = "Not set"
# Must match the number entity limits in esphome/packages/reservoir/core.yaml.
PH_LIMITS = (5.0, 7.5)
EC_LIMITS = (0.0, 6.0)
MIN_PH_BAND = 0.1
# The applied profile's name is stored in a fixed-size buffer in flash.
MAX_LABEL = 47


@dataclass
class Profile:
    label: str
    crop: dict
    stage: dict | None
    ph_target: float
    ph_band: float
    ec_low: float
    ec_high: float


class DataError(Exception):
    pass


def snap(value: float, step: float = 0.05) -> float:
    return round(round(value / step) * step, 2)


def check_range(where: str, rng: object, limits: tuple[float, float]) -> tuple[float, float]:
    if not isinstance(rng, dict) or set(rng) != {"min", "max"}:
        raise DataError(f"{where}: expected {{min, max}}, got {rng!r}")
    lo, hi = float(rng["min"]), float(rng["max"])
    if not limits[0] <= lo < hi <= limits[1]:
        raise DataError(f"{where}: {lo}-{hi} must satisfy {limits[0]} <= min < max <= {limits[1]}")
    return lo, hi


def load_profiles(data: dict) -> list[Profile]:
    if data.get("schema_version") != 1:
        raise DataError("schema_version must be 1")
    sources = data.get("sources") or {}
    for key, src in sources.items():
        for field in ("title", "type", "url"):
            if not src.get(field):
                raise DataError(f"source {key}: missing {field}")
        if src["type"] not in SOURCE_TYPES:
            raise DataError(f"source {key}: type must be one of {sorted(SOURCE_TYPES)}")

    profiles: list[Profile] = []
    seen_ids: set[str] = set()
    for crop in data.get("crops") or []:
        cid = crop.get("id")
        where = f"crop {cid}"
        if not cid or cid in seen_ids:
            raise DataError(f"{where}: missing or duplicate id")
        seen_ids.add(cid)
        if crop.get("status") not in STATUSES:
            raise DataError(f"{where}: status must be one of {sorted(STATUSES)}")
        if crop.get("confidence") not in CONFIDENCES:
            raise DataError(f"{where}: confidence must be one of {sorted(CONFIDENCES)}")
        if not crop.get("evidence") or not crop.get("rationale"):
            raise DataError(f"{where}: needs evidence and a rationale")
        for item in crop["evidence"]:
            if item.get("source") not in sources:
                raise DataError(f"{where}: unknown source {item.get('source')!r}")
            if not item.get("says"):
                raise DataError(f"{where}: evidence from {item['source']} needs 'says'")
        if crop["status"] != "active":
            continue

        if ("ec" in crop) == ("stages" in crop):
            raise DataError(f"{where}: give either one 'ec' range or 'stages', not both")
        stages = crop.get("stages") or [None]
        for stage in stages:
            swhere = f"{where} stage {stage['id']}" if stage else where
            ph_lo, ph_hi = check_range(f"{swhere} ph", (stage or {}).get("ph", crop.get("ph")), PH_LIMITS)
            ec_lo, ec_hi = check_range(f"{swhere} ec", (stage or crop).get("ec"), EC_LIMITS)
            label = f"{crop['name']} - {stage['name']}" if stage else crop["name"]
            if len(label) > MAX_LABEL:
                raise DataError(f"{swhere}: label {label!r} longer than {MAX_LABEL} characters")
            if label == NOT_SET or any(p.label == label for p in profiles):
                raise DataError(f"{swhere}: duplicate label {label!r}")
            profiles.append(Profile(
                label=label,
                crop=crop,
                stage=stage,
                ph_target=snap((ph_lo + ph_hi) / 2),
                ph_band=max(MIN_PH_BAND, snap((ph_hi - ph_lo) / 2)),
                ec_low=ec_lo,
                ec_high=ec_hi,
            ))
    if not profiles:
        raise DataError("no active crops")
    return profiles


def render_package(profiles: list[Profile]) -> str:
    options = "\n".join(f'      - "{label}"' for label in [NOT_SET] + [p.label for p in profiles])
    rows = "\n".join(
        f'            {{"{p.label}", {p.ph_target:.2f}f, {p.ph_band:.2f}f, {p.ec_low:.2f}f, {p.ec_high:.2f}f}},'
        for p in profiles
    )
    return f"""\
# GENERATED by tools/gen_crop_profiles.py from crops/crops.yaml. Do not edit by hand.
#
# Crop profile select for one reservoir. Choosing a profile writes its pH target,
# pH alarm band and EC limits into the setpoints from reservoir/core.yaml. The
# setpoints can then be tuned by hand; the select keeps showing the last profile
# applied. The applied profile is restored by name, so reordering or adding crops
# never relabels a reservoir.
#
# Vars: res, res_name
# Requires: ${{res}}_ph_target, ${{res}}_ph_alarm_band, ${{res}}_ec_low, ${{res}}_ec_high
#           (reservoir/core.yaml)
# Provides: ${{res}}_profile

globals:
  - id: ${{res}}_profile_applied
    type: std::array<char, {MAX_LABEL + 1}>
    restore_value: true

select:
  - platform: template
    id: ${{res}}_profile
    name: "${{res_name}} crop profile"
    entity_category: config
    optimistic: true
    options:
{options}
    initial_option: "{NOT_SET}"
    set_action:
      - lambda: |-
          struct Profile {{ const char *name; float ph, ph_band, ec_low, ec_high; }};
          static const Profile PROFILES[] = {{
{rows}
          }};
          for (const auto &p : PROFILES) {{
            if (x != p.name) continue;
            auto apply = [](number::Number *n, float v) {{
              auto call = n->make_call();
              call.set_value(v);
              call.perform();
            }};
            apply(id(${{res}}_ph_target), p.ph);
            apply(id(${{res}}_ph_alarm_band), p.ph_band);
            apply(id(${{res}}_ec_low), p.ec_low);
            apply(id(${{res}}_ec_high), p.ec_high);
            auto &applied = id(${{res}}_profile_applied);
            applied.fill(0);
            memcpy(applied.data(), p.name, std::min(strlen(p.name), applied.size() - 1));
            ESP_LOGI("profile", "${{res_name}}: applied profile '%s'", p.name);
            return;
          }}

esphome:
  on_boot:
    # After globals are restored: show the last applied profile, if it still exists.
    - priority: -100
      then:
        - lambda: |-
            std::string applied(id(${{res}}_profile_applied).data());
            if (!applied.empty() && id(${{res}}_profile).has_option(applied))
              id(${{res}}_profile).publish_state(applied);
"""


def render_doc_table(profiles: list[Profile], data: dict) -> str:
    lines = [
        "| Profile | pH target | pH range | EC range (mS/cm) | Confidence |",
        "|---|---|---|---|---|",
    ]
    for p in profiles:
        lines.append(
            f"| {p.label} | {p.ph_target:.2f} | {p.ph_target - p.ph_band:.2f}-{p.ph_target + p.ph_band:.2f} "
            f"| {p.ec_low:.1f}-{p.ec_high:.1f} | {p.crop['confidence']} |"
        )
    inactive = [c for c in data["crops"] if c["status"] != "active"]
    if inactive:
        lines += ["", "Recorded but not in the firmware:", ""]
        lines += [f"- **{c['name']}** ({c['status']}): {' '.join(c['rationale'].split())}" for c in inactive]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if generated files are out of date")
    args = parser.parse_args()

    data = yaml.safe_load(CROPS.read_text())
    try:
        profiles = load_profiles(data)
    except DataError as err:
        sys.exit(f"{CROPS.relative_to(ROOT)}: {err}")

    package = render_package(profiles)
    doc = DOC.read_text()
    begin, end = doc.index(DOC_BEGIN) + len(DOC_BEGIN), doc.index(DOC_END)
    doc = f"{doc[:begin]}\n{render_doc_table(profiles, data)}\n{doc[end:]}"

    stale = [path for path, text in ((PACKAGE, package), (DOC, doc))
             if not path.exists() or path.read_text() != text]
    if args.check:
        if stale:
            sys.exit("Out of date, run: uv run tools/gen_crop_profiles.py\n  "
                     + "\n  ".join(str(p.relative_to(ROOT)) for p in stale))
        return
    PACKAGE.write_text(package)
    DOC.write_text(doc)
    for path in stale:
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
