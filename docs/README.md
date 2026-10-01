# Documentation

Reference for both people and AI agents working on this project.

## Design

- [Architecture](architecture.md): nodes and hub, design rules, firmware layers, naming
- [Decision log](decisions.md): what was decided and why
- [Sensors and isolation](sensors-and-isolation.md): why probes interfere, the one-non-isolated-probe rule, sensor choices
- [Control logic](control-logic.md): top-off, pH dosing, safety layers, alarms, commissioning
- [Crop profiles](crop-profiles.md): pH and EC targets per crop
- [Safety](safety.md): electrical, water, chemical and firmware rules

## Hardware

- [DWC node (`dwc-1`)](hardware/dwc-node.md): parts list, pin map, addresses, wiring, bench test
- [DFRobot SEN0707 EC sensor](hardware/dfrobot-sen0707.md): specs, wiring, Modbus registers

## Firmware and operations

- [ESPHome configuration](esphome.md): package layout and contract, conventions, validating and flashing
- [Calibration and sensor setup](calibration.md): EZO I2C mode, pH calibration, EC checks, Modbus addresses, pump flow
- [Home Assistant](home-assistant.md): adding nodes, dashboard, alerts, air pump monitoring
- [Extending the system](extending.md): adding a reservoir, a node, a system type (NFT), a module
- [Roadmap](roadmap.md)
