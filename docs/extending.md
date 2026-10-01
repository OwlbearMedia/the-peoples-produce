# Extending the system

## Adding a reservoir to an existing node

Example: Reservoir B on `dwc-1`.

1. Buy the per-reservoir parts ([hardware/dwc-node.md](hardware/dwc-node.md#parts-phase-1)).
2. Set the new EZO-pH's I2C address and the new EC sensor's Modbus address
   **before** connecting them ([calibration.md](calibration.md)). Every address on a
   bus must be unique.
3. Wire it to the reserved pins in the [pin map](hardware/dwc-node.md#pin-map).
4. Uncomment the `reservoir_b` block in `esphome/dwc-1.yaml` and delete its
   `BEGIN PLANNED`/`END PLANNED` marker lines.
5. Validate, flash, bench test, calibrate, then commission it
   ([control-logic.md](control-logic.md#commissioning)).
6. Add its `needs attention` entity to the Home Assistant alert
   ([home-assistant.md](home-assistant.md)).

`tools/validate.sh` already checks `dwc-1` with Reservoir B enabled, so the config
should validate unchanged once uncommented.

## Adding a node

Example: the NFT system in another room.

1. Create `esphome/<system>-<n>.yaml` (for example `nft-1.yaml`), modeled on
   `dwc-1.yaml`: board, `substitutions` for the name, node packages, one bundle
   per reservoir.
2. Document its parts, pin map and addresses in `docs/hardware/<node>.md`, and link
   it from [docs/README.md](README.md).
3. Each node has its own buses, so addresses only need to be unique within one node.

## Adding a system type

A system type is a bundle in `esphome/packages/systems/` that composes reservoir
modules. Reuse modules where they fit and add new ones where they don't.

### Planned: NFT (`nft_reservoir.yaml`)

NFT shares most of the DWC bundle (core, pH, EC, level, top-off, pH dosing) and adds:

- **`circulation_pump.yaml`:** the node switches the 12 V circulation pump (or a mains
  pump through a smart plug, per [safety.md](safety.md)).
- **`flow_hall.yaml`:** a Hall-effect flow sensor (YF-S201 type) on the supply line,
  read with ESPHome's `pulse_meter`. It touches the water only through plastic, so no
  isolation concern. Use one of the input-only pins (34-39) with an external pull-up.
  - If the pump is on but flow stays below a minimum for about 30 s, power-cycle the
    pump once.
  - If flow is still low, raise a **no flow** problem. In NFT, roots can dry out
    within minutes to hours, so this alert should be urgent.
- **Optional return check:** a float or capacitive switch in the return gutter. Supply
  flowing but return dry means a clog or a leak. Gravity returns don't flow well
  through Hall sensors, so a switch is easier.
- **No air pump check:** NFT has no air stone, so the air pump plug is DWC-only.

The air-gap rule for top-off lines applies here too.

## Adding a sensor or actuator module

1. Create `esphome/packages/reservoir/<thing>.yaml` with the header contract
   (Vars / Requires / Provides). See [esphome.md](esphome.md#package-contract).
2. Use `${res}_` IDs and `${res_name}` names.
3. Actuators: `restore_mode: ALWAYS_OFF`, a watchdog script, rate limits and an enable
   switch that defaults off.
4. Problem sensors: `device_class: problem`. Add them to the bundle's status roll-up.
5. Probes that touch water: check the isolation rule
   ([sensors-and-isolation.md](sensors-and-isolation.md)).
6. Include it from the relevant bundle, run `tools/validate.sh --compile`, and update
   the docs.
