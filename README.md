# The People's Produce

Open-source monitoring and control for hydroponic systems, built on
[ESPHome](https://esphome.io) and [Home Assistant](https://www.home-assistant.io).

One small ESP32 controller per grow location watches pH, EC, water temperature and
reservoir level, tops off the water and doses pH-down on its own. Home Assistant brings
every location into one dashboard with history and phone alerts.

## Project direction

The goal is open-source firmware that automated hydroponic systems can run on, whether
someone builds their own or buys one finished. The control logic, crop database and
tools are kept general for that reason. The systems below are the first builds: they
are where the firmware gets proven, and they serve as reference designs for new ones.
See the [decision log](docs/decisions.md#11-one-repo-growing-into-general-open-source-firmware).

## Prototype systems

| System | Status | Grows |
|---|---|---|
| DWC bucket A (5 gal) | Phase 1, in progress | Tomatoes |
| DWC bucket B (5 gal), same controller | Phase 2 | Tomatoes, peppers or brassicas |
| NFT, another room | Planned | TBD |

## How it works

```
 ESP32 node "dwc-1"              ESP32 node "nft-1" (planned)
  ├─ Reservoir A                   └─ NFT reservoir
  └─ Reservoir B
        │ Wi-Fi                          │
        └──────────── Home Assistant ────┘
           dashboard, history, alerts, setpoints
```

- **Each node runs its own control loops.** Dosing, top-off and safety limits keep
  working if Wi-Fi or Home Assistant goes down.
- **One controller, several reservoirs.** Reservoirs that sit together share a node.
  Each has its own crop profile, so switching a bucket from tomatoes to broccoli is a
  menu choice.
- **Probes don't interfere.** The pH probe sits behind an isolated Atlas Scientific
  circuit, and the EC sensor is an industrial RS485 probe. Multiple non-isolated probes
  in one reservoir corrupt each other's readings.
- **Crop profiles from sourced data.** Picking a crop and growth stage fills in its
  pH and EC targets. The data lives in a [crop database](crops/crops.yaml) where every
  value cites its sources, because published recommendations often disagree.
- **Fails safe.** Pumps boot off, every pump has a watchdog, automatic actions are
  rate-limited, and a leak or empty top-off tank stops everything that adds water.

Per reservoir it measures pH, EC, water temperature and level, and controls auto
top-off and pH-down dosing. Each node also measures air temperature and humidity and
watches the top-off tank and a floor leak probe.

## Repository layout

```
esphome/           ESPHome firmware: node configs and reusable packages
crops/             Sourced crop database (pH and EC targets)
docs/              Design, hardware, calibration and operations docs
tools/             Bench and validation scripts
AGENTS.md          Guide for AI coding agents
```

## Getting started

1. Read the [architecture](docs/architecture.md) and [safety](docs/safety.md) docs.
2. Buy and wire the parts for the [DWC node](docs/hardware/dwc-node.md).
3. Copy `esphome/secrets.yaml.example` to `esphome/secrets.yaml` and fill it in.
4. Validate, then flash over USB:
   ```bash
   tools/validate.sh
   ```
   ```bash
   uvx --from esphome==2026.9.1 esphome run esphome/dwc-1.yaml
   ```
5. [Calibrate](docs/calibration.md), add the node to
   [Home Assistant](docs/home-assistant.md), and [commission](docs/control-logic.md#commissioning)
   the automation one piece at a time.

## Documentation

Everything is in [docs/](docs/README.md):

- [Architecture](docs/architecture.md) · [Decision log](docs/decisions.md) · [Roadmap](docs/roadmap.md)
- [Sensors and isolation](docs/sensors-and-isolation.md) · [Control logic](docs/control-logic.md) · [Crop profiles](docs/crop-profiles.md)
- [Research notes](docs/README.md#research-notes), such as [dissolved oxygen](docs/research/dissolved-oxygen.md)
- [DWC node hardware](docs/hardware/dwc-node.md) · [Calibration](docs/calibration.md) · [Safety](docs/safety.md)
- [ESPHome configuration](docs/esphome.md) · [Home Assistant](docs/home-assistant.md) · [Extending](docs/extending.md)

## License

Copyright (C) 2026 Dylan Whitney

Licensed under the [GNU General Public License v3.0 or later](LICENSE). Anyone may
use, modify and sell what they build with it, as long as what they distribute stays
open under the same license. Earlier versions were MIT-licensed; see the
[decision log](docs/decisions.md#12-gpl-30-or-later).
