# Architecture

## Overview

```
 [Grow area 1]                              [Other room, planned]
 ESP32 node "dwc-1"                          ESP32 node "nft-1"
  ├─ Reservoir A (tomato)                     └─ NFT reservoir
  └─ Reservoir B (flex, phase 2)
          │  Wi-Fi (ESPHome native API)                │
          └──────────────────┬─────────────────────────┘
                    Hub: Home Assistant
          one dashboard, history, alerts, setpoints
```

- **Node:** one ESP32 per physical location, running ESPHome. A node serves one or
  more reservoirs that sit next to each other. It reads the sensors and runs every
  control loop (pH dosing, top-off, safety limits) itself.
- **Hub:** Home Assistant. It shows every node in one UI, keeps history, sends phone
  alerts and is where setpoints and crop profiles are changed. It controls nothing
  directly.

## Design rules

1. **Control runs on the node, not the hub.** Dosing, top-off and every safety limit
   must keep working when Wi-Fi or Home Assistant is down. The hub only changes
   setpoints and displays data. Nodes never reboot because they lost the hub
   (`reboot_timeout: 0s`).
2. **Setpoints are per-reservoir and come from crop profiles.** Switching a reservoir
   from tomatoes to broccoli means choosing a profile, not editing firmware. See
   [crop-profiles.md](crop-profiles.md).
3. **At most one non-isolated probe per body of water.** Every other probe in the
   same water is galvanically isolated. See [sensors-and-isolation.md](sensors-and-isolation.md).
4. **Every actuator fails safe.** Outputs boot off, every pump has a watchdog that
   stops it regardless of the control logic, and automatic actions have rate limits.
   See [control-logic.md](control-logic.md).
5. **Nodes switch only 12 V DC.** Mains loads (air pumps, chillers, lights) go on
   smart plugs. See [safety.md](safety.md).
6. **Systems are composed from small packages.** A new reservoir, system type or
   sensor is a new package, not a fork. See [esphome.md](esphome.md) and
   [extending.md](extending.md).

## Firmware layers

The ESPHome configuration is built in four layers, from most general to most specific:

| Layer | Path | Example | Contains |
|---|---|---|---|
| Node packages | `esphome/packages/node/` | `rs485.yaml` | Things a node has once: Wi-Fi, buses, the shared top-off tank, the leak probe |
| Reservoir modules | `esphome/packages/reservoir/` | `ph_ezo.yaml` | One sensor or actuator for one reservoir, keyed by `${res}` |
| System bundles | `esphome/packages/systems/` | `dwc_reservoir.yaml` | The set of modules that makes up one reservoir of a given system type |
| Node configs | `esphome/*.yaml` | `dwc-1.yaml` | One physical controller: board, pins and which bundles it runs |

## Entities and naming

- Node names are `<system>-<n>`: `dwc-1`, `nft-1`.
- Reservoir ID prefixes are `res_<letter>` (`res_a`, `res_b`). Display names are
  "Reservoir A", "Reservoir B".
- In Home Assistant, entity IDs come from the node's friendly name and the entity
  name, for example `sensor.dwc_1_reservoir_a_ph`.
- Each reservoir publishes a summary: `<res_name> status` (text, "OK" or a list of
  problems) and `<res_name> needs attention` (binary). Alerts can watch just those.

## Units

All firmware values are metric: EC in mS/cm, temperature in °C. Home Assistant can
display temperatures in °F.
