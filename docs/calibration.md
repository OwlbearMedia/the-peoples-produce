# Calibration and sensor setup

## EZO-pH: switch to I2C mode (once)

EZO circuits ship in UART mode (LED green). The firmware needs I2C mode (LED blue).

**Reservoir A (default address 99), no tools needed:**

1. Disconnect power from the EZO.
2. Connect the EZO's **PGND** pin to its **TX** pin with a jumper.
3. Reconnect power. The LED changes from green to blue.
4. Remove the jumper.

**Reservoir B or later (non-default address):** use a 3.3 V USB-to-serial adapter on
the EZO's TX/RX pins, 9600 baud, and send `I2C,49` followed by Enter (carriage return).
The EZO switches to I2C mode at address 49 and reboots. Use the address listed for
that reservoir in [hardware/dwc-node.md](hardware/dwc-node.md#i2c-and-modbus-addresses).

After connecting, check the node's boot log: the I2C scan should list the address.

## pH calibration

Calibrate when new, then every 1-2 months. Rinse the probe with RO or distilled water
between buffers. Let each reading settle for 1-2 minutes before pressing the button.

1. Probe in **pH 7.00** buffer → press `<reservoir> pH calibrate mid (7.00)`.
   This clears any earlier calibration, so always do it first.
2. Probe in **pH 4.00** buffer → press `<reservoir> pH calibrate low (4.00)`.
3. Optional: probe in **pH 10.00** buffer → press `<reservoir> pH calibrate high (10.00)`.
   Our range is 5.5-6.5, so the two-point calibration (7 and 4) matters most.

Turn **auto pH dosing off** while calibrating. Readings are wildly off target while the
probe sits in buffer, and with the probe out of the reservoir the dosing would be
working blind.

## EC check and correction

The SEN0707 is factory calibrated. Its rated accuracy is ±0.2 mS/cm.

- **Routine check (monthly):** compare the node's reading with a calibrated handheld
  EC pen in the reservoir. Set `<reservoir> EC offset` to the difference
  (handheld − node).
- **Recalibration:** with the probe in 1413 µS/cm standard solution and connected to a
  laptop through a USB-RS485 adapter (not to the node):

  ```bash
  uv run tools/dfrobot_rs485.py --port /dev/tty.usbserial-XXXX calibrate-ec 1413
  ```

  Then reset the EC offset to 0.

## Changing a DFRobot sensor's Modbus address

Every sensor on the RS485 bus needs its own address. Before connecting Reservoir B's
EC sensor, connect **only that sensor** to a USB-RS485 adapter and run:

```bash
uv run tools/dfrobot_rs485.py --port /dev/tty.usbserial-XXXX set-address 2
```

Power-cycle it and confirm with `--address 2 read`.

## Dosing pump flow

1. Put the pH-down line's outlet in a measuring cup or syringe.
2. Press `<reservoir> prime pH-down pump (3 s)` a few times and measure the total.
3. ml per second = volume ÷ (3 × presses).
4. Set `<reservoir> pH-down dose time` so one dose is about 1 ml of diluted pH-down,
   then tune from how far each dose moves the pH.
