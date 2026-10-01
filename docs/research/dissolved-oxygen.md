# Research: dissolved oxygen sensing

Status: **deferred** (on the [roadmap](../roadmap.md#later-ideas)). Researched
2026-09-30. Prices and specs come from the manufacturers' pages on that date.

## Why measure it

In DWC, dissolved oxygen (DO) mostly reflects whether aeration is working and how
warm the water is (warmer water holds less oxygen). Low DO suffocates roots and
favors root rot. A DO reading directly checks aeration, and catches failures the air
pump's smart-plug power check can't see:

- airline kinked, split or popped off the pump
- clogged air stone
- pump running but weak (worn diaphragm)

DO targets are roughly the same across crops, so a DO sensor would get a single
"DO low" alarm, not a per-crop setpoint. In NFT, aeration happens in the thin film
in the channels, so a reservoir DO reading tells you less.

## Options

| Option | Cost per reservoir | Isolation | Upkeep |
|---|---|---|---|
| DFRobot SEN0680 optical DO, RS485 Modbus | $199 | Plastic housing and no electrodes, so it probably doesn't touch the water electrically. Not documented; confirm with the [resistance test](../sensors-and-isolation.md#testing-whether-a-probe-is-isolated). | Fluorescent sensing film, about 1 year |
| Atlas Scientific EZO-DO kit (galvanic probe, isolated carrier) | $355 | Isolated | Membrane and electrolyte refills |
| Inline airline pressure sensor | about $15 | Doesn't touch the water | None. Detects pump and line failures, but doesn't measure DO. |

**DFRobot SEN0680 details** ([wiki](https://wiki.dfrobot.com/sen0680/)): 0-20 mg/L and
0-200% saturation, ±3% of full scale (about ±0.6 mg/L), 0.01 mg/L resolution, built-in
temperature compensation, 10-30 V DC at 0.2 W, RS485 Modbus RTU at default address 1,
IP68, 5 m cable. Salinity compensation is only on the seawater model (SEN0681).

**Atlas kit details** ([kit page](https://atlas-scientific.com/kits/dissolved-oxygen-kit/)):
EZO-DO circuit, lab-grade galvanic probe, electrolyte, Electrically Isolated EZO
Carrier. The EZO-DO circuit alone is $53.99, so a cheaper galvanic probe can cut the
cost.

## Recommendation when we pick this up

1. **DFRobot SEN0680:** it shares the existing RS485 bus at its own address, needs the
   least upkeep, and is accurate enough for a "DO low" alarm. Run the isolation test
   before putting it in a reservoir that already has the EC sensor.
2. **Airline pressure sensor:** if cost matters more, it covers most aeration
   failures for about $15.

## Implementation notes

- New module `esphome/packages/reservoir/do_dfrobot_rs485.yaml`, following the same
  pattern as `ec_dfrobot_rs485.yaml`: `modbus_controller`, DO sensor, fault and
  "DO low" problem sensors added to the bundle's status roll-up.
- Get the register map from DFRobot's Modbus protocol page for SEN0680 and record it
  under `docs/hardware/`, as was done for the SEN0707.
- Set a unique Modbus address before connecting it (`tools/dfrobot_rs485.py set-address`;
  check that SEN0680 uses the same address register as SEN0707 first).
