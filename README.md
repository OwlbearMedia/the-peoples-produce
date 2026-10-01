# The People's Produce

Monitoring and control for home hydroponic systems, built on
[ESPHome](https://esphome.io) and [Home Assistant](https://www.home-assistant.io).

One small ESP32 controller per grow location watches pH, EC, water temperature and
reservoir level, tops off the water and doses pH-down on its own. Home Assistant brings
every location into one dashboard with history and phone alerts.

## The systems

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
- **Fails safe.** Pumps boot off, every pump has a watchdog, automatic actions are
  rate-limited, and a leak or empty top-off tank stops everything that adds water.

Per reservoir it measures pH, EC, water temperature and level, and controls auto
top-off and pH-down dosing. Each node also measures air temperature and humidity and
watches the top-off tank and a floor leak probe.

## Repository layout

```
esphome/           ESPHome firmware: node configs and reusable packages
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
- [DWC node hardware](docs/hardware/dwc-node.md) · [Calibration](docs/calibration.md) · [Safety](docs/safety.md)
- [ESPHome configuration](docs/esphome.md) · [Home Assistant](docs/home-assistant.md) · [Extending](docs/extending.md)

## License

[MIT](LICENSE)
