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
| Crop targets | [docs/crop-profiles.md](docs/crop-profiles.md) |

Full index: [docs/README.md](docs/README.md).

## Repository map

```
esphome/dwc-1.yaml               node config (board, pins, bundles)
esphome/packages/node/           per-node packages (base, buses, tank, leak)
esphome/packages/reservoir/      per-reservoir modules, IDs prefixed ${res}_
esphome/packages/systems/        bundles composing modules into a system type
esphome/secrets.yaml.example     template; real secrets.yaml is git-ignored
tools/validate.sh                validate (and optionally compile) every node config
tools/dfrobot_rs485.py           bench tool for DFRobot RS485 sensors
docs/                            documentation for people and agents
```

## Commands

```bash
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
- Crop profile values live in `esphome/packages/reservoir/core.yaml`; keep
  [docs/crop-profiles.md](docs/crop-profiles.md) in step.
- Match the existing comment style: explain why, not what.

## Keeping docs current

Docs are part of the change. When behavior, pins, parts, addresses or defaults change,
update the matching doc in the same commit. Record significant design choices in
[docs/decisions.md](docs/decisions.md). New docs get a link in
[docs/README.md](docs/README.md), and in this file's table if agents need them.

### Suggest docs for what you had to learn

Before wrapping up a session, think about what you had to work out that the docs
would have told you: an undocumented behavior, a tool or library quirk, a source
that blocks automated reading, the reasoning behind a choice. If documenting it would
help future sessions, **suggest it to the user**. Say what you learned and which doc
it belongs in (or propose a new one under `docs/`). Write it only once they agree,
unless they already asked you to update the docs.

Examples of the kind of thing worth suggesting:

- ESPHome template selects restore their state by index, not by option name.
- PMC and ResearchGate pages often block automated fetching; the in-app browser or a
  journal's own site may still work.

## Commits and pull requests

- Short imperative subject line; body explains why.
- Do not add AI attribution of any kind: no `Co-Authored-By` trailers for AI tools and
  no "Generated with" lines in commits or PR descriptions.
- Never commit `esphome/secrets.yaml` or `.esphome/` build output.
