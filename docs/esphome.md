# ESPHome configuration

## Layout

```
esphome/
├── dwc-1.yaml                 node config: board, pins, which bundles
├── secrets.yaml.example       copy to secrets.yaml (git-ignored)
└── packages/
    ├── node/                  once per node
    │   ├── base.yaml          name, Wi-Fi, API, OTA, health entities
    │   ├── i2c.yaml           I2C bus (bus_i2c)
    │   ├── rs485.yaml         RS485 Modbus bus (modbus_rs485)
    │   ├── climate_sht4x.yaml air temperature and humidity
    │   ├── topoff_tank.yaml   shared top-off tank level (topoff_tank_low)
    │   └── leak_sensor.yaml   floor leak probe (floor_leak)
    ├── reservoir/             once per reservoir, keyed by ${res}
    │   ├── core.yaml          crop profile and setpoints
    │   ├── ph_ezo.yaml        Atlas EZO-pH
    │   ├── ec_dfrobot_rs485.yaml  DFRobot SEN0707 EC and water temperature
    │   ├── level_dual_switch.yaml two level switches
    │   ├── topoff_pump.yaml   auto top-off
    │   └── ph_down_dosing.yaml    pH-down dosing
    └── systems/
        └── dwc_reservoir.yaml one DWC reservoir = core + ph + ec + level + topoff + dosing
```

The layers are explained in [architecture.md](architecture.md#firmware-layers).

## Package contract

Every package starts with a header comment listing:

- **Vars:** what the includer must pass (`res`, `res_name`, pins, addresses)
- **Requires:** IDs from other packages it uses
- **Provides:** IDs it defines for others to use

A missing requirement fails at compile time, which is intended.

## Conventions

- **IDs:** reservoir-level IDs are `${res}_<thing>` (`res_a_ph`). Node-level IDs have
  no prefix (`floor_leak`). IDs must be valid C++ identifiers.
- **Names:** reservoir entities start with `${res_name}`, so Home Assistant shows
  "Reservoir A pH".
- **Setpoints:** template `number` entities with `optimistic: true`,
  `restore_value: true` and `entity_category: config`.
- **Automation switches:** template switches with `restore_mode: RESTORE_DEFAULT_OFF`,
  so a new node starts with automation off.
- **Pump outputs:** `restore_mode: ALWAYS_OFF` and a watchdog script. See
  [control-logic.md](control-logic.md#safety-layers).
- **Problem sensors:** template `binary_sensor` with `device_class: problem`. Add new
  ones to the bundle's status roll-up.
- **Units:** EC in mS/cm, temperature in °C.
- **Defaults for vars:** use a `defaults:` block in the package (see `i2c.yaml`).

## Validate, build and flash

Validation needs no hardware. From the repo root:

```bash
tools/validate.sh
```

It validates every node config with throwaway secrets, using the ESPHome version pinned
in the script. Add `--compile` to also build the firmware. That checks all C++ lambdas;
the first build downloads the toolchain and takes several minutes.

To flash a real node, create `esphome/secrets.yaml` from the example, then:

```bash
uvx --from esphome==2026.9.1 esphome run esphome/dwc-1.yaml
```

The first flash is over USB; later ones can go over Wi-Fi (OTA). The Home Assistant
ESPHome add-on works too: copy the `esphome/` directory into its config folder.

## ESPHome version

Tested with ESPHome **2026.9.1**. Pinned in `tools/validate.sh` and the flash command
above. When upgrading, bump both, run `tools/validate.sh --compile` and read the
ESPHome release notes for breaking changes.
