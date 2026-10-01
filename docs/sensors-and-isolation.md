# Sensors and isolation

## Why isolation matters

A pH probe measures a millivolt-level signal against its own reference electrode. An
EC probe pushes an excitation current through the water. When both probes' circuits
share the controller's ground, the nutrient solution connects them: EC current flows
through the pH circuit and the pH reading drifts or jumps. Submersible pumps and
heaters add more noise the same way.

The problem is not analog vs. digital. It is **galvanic isolation**.

## The rule

**At most one non-isolated probe per body of water.** Every other probe in that water
needs an isolated front end, meaning its power and signal are both isolated from the
controller.

Things that do not touch the water electrically don't count: non-contact capacitive
level switches, Hall-effect flow sensors, and peristaltic pumps (the tubing is an
insulator).

Watch for hidden water paths between reservoirs. A tube full of water from a shared
top-off tank connects the reservoirs electrically. That's why fill lines end above the
water surface (an air gap).

## Current sensor choices (per reservoir)

| Measurement | Part | Interface | Isolated | Notes |
|---|---|---|---|---|
| pH | Atlas Scientific pH kit: EZO-pH, lab-grade probe, Electrically Isolated EZO Carrier | I2C | Yes | About $175. Ships in UART mode; switch it to I2C first ([calibration.md](calibration.md)). |
| EC and water temperature | DFRobot SEN0707 RS485 EC, K=10, 10-20000 µS/cm | RS485 Modbus RTU | Assume not | $159. The one non-isolated probe. Accuracy ±1% of full scale = ±0.2 mS/cm. [Register map](hardware/dfrobot-sen0707.md). |
| Level | XKC-Y25-NPN non-contact capacitive switch ×2 | GPIO | n/a | Stuck to the outside of the bucket. |

Per node: SHT40/SHT45 air temperature and humidity (I2C), one XKC-Y25 on the top-off
tank, a floor leak probe.

The reasoning and rejected alternatives are in [decisions.md](decisions.md#4-hybrid-sensors-isolated-atlas-ph-rs485-dfrobot-ec).

## Testing whether a probe is isolated

Manufacturers often don't say. To check:

1. Power the sensor from its normal supply and put the probe in salty water.
2. Put a bare wire in the same water.
3. Measure resistance between the sensor's supply GND and the bare wire.

A reading in the kΩ range means the probe's circuit is connected to the water: not
isolated. Megaohms or open circuit means it is isolated (or at least very weakly
coupled).

If the DFRobot EC sensor turns out to be isolated, the DFRobot RS485 pH sensor
(SEN0708, $129) becomes an option for the cheaper path.

## Symptoms of an isolation problem

- pH reading shifts when the EC sensor polls or a pump turns on.
- pH reads correctly in a cup of buffer but wrong in the reservoir.
- Readings differ depending on whether other reservoirs' probes are connected.
