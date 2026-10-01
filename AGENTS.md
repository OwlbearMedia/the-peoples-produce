# AGENTS.md

Guide for AI coding agents working in this repository. People should start with
[README.md](README.md).

## What this is

Monitoring and control for home hydroponic systems. ESPHome firmware runs on one ESP32
node per grow location; each node serves one or more reservoirs and runs all control
loops itself. Home Assistant is the shared UI and alerting hub. There is no custom
backend or frontend code.

Current state: phase 1, one DWC reservoir (`res_a`) on node `dwc-1`. Reservoir B is
written but commented out. An NFT node is planned. See [docs/roadmap.md](docs/roadmap.md).

## Read before changing things

| If you are touching… | Read |
|---|---|
| Anything | [docs/architecture.md](docs/architecture.md) (design rules), [docs/decisions.md](docs/decisions.md) |
| ESPHome YAML | [docs/esphome.md](docs/esphome.md) (package contract, conventions) |
| Pumps, dosing, top-off, alarms | [docs/control-logic.md](docs/control-logic.md), [docs/safety.md](docs/safety.md) |
| Sensors or probes | [docs/sensors-and-isolation.md](docs/sensors-and-isolation.md) |
| Pins, wiring, addresses | [docs/hardware/dwc-node.md](docs/hardware/dwc-node.md) |
| New reservoir, node, system type or module | [docs/extending.md](docs/extending.md) |
| Crop targets or the crop database | [docs/crop-profiles.md](docs/crop-profiles.md) (research rules) |
| A deferred feature (e.g. dissolved oxygen) | [docs/research/](docs/README.md#research-notes) |

Full index: [docs/README.md](docs/README.md).

## Repository map

```
esphome/dwc-1.yaml               node config (board, pins, bundles)
esphome/packages/node/           per-node packages (base, buses, tank, leak)
esphome/packages/reservoir/      per-reservoir modules, IDs prefixed ${res}_
esphome/packages/systems/        bundles composing modules into a system type
esphome/secrets.yaml.example     template; real secrets.yaml is git-ignored
crops/crops.yaml                 sourced crop database (source of truth for profiles)
tools/gen_crop_profiles.py       generates crop_profile.yaml and the docs table from it
tools/validate.sh                check generated files, validate (optionally compile) nodes
tools/dfrobot_rs485.py           bench tool for DFRobot RS485 sensors
docs/                            documentation for people and agents
```

## Commands

```bash
uv run tools/gen_crop_profiles.py  # after editing crops/crops.yaml
tools/validate.sh            # config validation, seconds; no hardware or secrets needed
tools/validate.sh --compile  # also builds firmware; checks C++ lambdas; first run is slow
```

Run `tools/validate.sh` after any YAML change and `--compile` after changing a lambda.
Both must pass before committing. You cannot flash or test against hardware; say so
when hardware testing is still needed.

## Safety-critical rules

This firmware switches pumps that add water and acid to a reservoir. A bug can flood a
floor or kill plants. Never do these without the user explicitly asking:

- Change a pump `restore_mode` from `ALWAYS_OFF`.
- Remove, bypass or lengthen a pump watchdog script.
- Remove an interlock (leak, top-off tank low, level fault) or a rate limit.
- Set `reboot_timeout` on `api` or `wifi` to anything but `0s`. A reboot clears the
  RAM rate-limit counters.
- Move control logic from the node into Home Assistant. Control must work offline.
- Make an automation switch default on. New automation ships off.
- Add a second non-isolated probe to the same water.

New actuators follow the checklist in [docs/extending.md](docs/extending.md#adding-a-sensor-or-actuator-module).

## Conventions

- Follow the package header contract (Vars / Requires / Provides) in every package.
- Reservoir IDs `${res}_<thing>`, entity names `"${res_name} <thing>"`.
- Units: EC in mS/cm, temperature in °C.
- New problem sensors: `device_class: problem`, and add them to the status roll-up in
  the system bundle.
- Crop data lives only in `crops/crops.yaml`. Never edit the generated
  `esphome/packages/reservoir/crop_profile.yaml` or the generated table in
  `docs/crop-profiles.md`; regenerate them.
- Adding crop data: follow the research rules in
  [docs/crop-profiles.md](docs/crop-profiles.md#research-rules). Cite only what you
  actually read, record every source's values under `evidence`, and mark crops with
  conflicting sources `status: conflicting` instead of picking a number.
- Match the existing comment style: explain why, not what.

## Keeping docs current

Docs are part of the change. When behavior, pins, parts, addresses or defaults change,
update the matching doc in the same commit. Record significant design choices in
[docs/decisions.md](docs/decisions.md). New docs get a link in
[docs/README.md](docs/README.md), and in this file's table if agents need them.

## Commits and pull requests

- Short imperative subject line; body explains why.
- Do not add AI attribution of any kind: no `Co-Authored-By` trailers for AI tools and
  no "Generated with" lines in commits or PR descriptions.
- Never commit `esphome/secrets.yaml` or `.esphome/` build output.
