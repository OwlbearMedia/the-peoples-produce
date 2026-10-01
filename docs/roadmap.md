# Roadmap

## Phase 1: one DWC bucket (current)

- [x] Firmware for `dwc-1` with Reservoir A: pH, EC, water temperature, level, auto
      top-off, pH-down dosing, crop profiles, alarms
- [x] Firmware compile-tested with Reservoir B enabled
- [x] Sourced crop database with generated crop profiles
- [ ] Buy the parts ([hardware/dwc-node.md](hardware/dwc-node.md#parts-phase-1))
- [ ] Build and bench test
- [ ] Calibrate and commission ([control-logic.md](control-logic.md#commissioning))
- [ ] Home Assistant dashboard and alerts ([home-assistant.md](home-assistant.md))
- [ ] Run a full tomato cycle and tune the defaults

## Phase 2: second DWC bucket

- [ ] Set addresses on Reservoir B's EZO-pH and EC sensor
- [ ] Wire to the reserved pins and enable `reservoir_b` in `dwc-1.yaml`
- [ ] Calibrate and commission

## Phase 3: NFT node

- [ ] Choose the location and layout
- [ ] `circulation_pump.yaml` and `flow_hall.yaml` modules, `nft_reservoir.yaml` bundle
      ([extending.md](extending.md#planned-nft-nft_reservoiryaml))
- [ ] `docs/hardware/nft-node.md` and `esphome/nft-1.yaml`

## Later ideas

- Dissolved oxygen sensing, or an inline airline pressure sensor as a cheaper aeration
  check ([research notes](research/dissolved-oxygen.md))
- Research and add more crops to [`crops/crops.yaml`](../crops/crops.yaml), starting
  with resolving the pepper conflict ([crop-profiles.md](crop-profiles.md#research-rules))
- Nutrient A/B dosing driven by EC (two more peristaltic pumps per reservoir)
- Volume tracking: log top-off pump run time to estimate water use per reservoir
- Upgrade EC to Atlas EZO-EC with an isolated carrier if ±0.2 mS/cm proves too coarse
- CI: run `tools/validate.sh` on every push
