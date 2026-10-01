# DFRobot SEN0707 RS485 EC sensor (K=10)

Source: [DFRobot wiki SEN0707](https://wiki.dfrobot.com/sen0707/) and its
[Modbus protocol page](https://wiki.dfrobot.com/sen0707/docs/23337).

## Specs

| | |
|---|---|
| EC range | 10-20000 µS/cm, 1 µS/cm resolution |
| EC accuracy | ±1% full scale (±200 µS/cm) |
| Temperature | -20 to 60 °C, ±0.5 °C, built-in compensation |
| Supply | 10-30 V DC, 0.4 W |
| Interface | RS485 Modbus RTU, 8N1 |
| Defaults | address 1, 4800 baud |
| Cable | 5 m |
| Isolation | Not documented; treat as non-isolated |

## Wire colors

| Color | Signal |
|---|---|
| Brown | V+ (12 V on our nodes) |
| Black | GND |
| Yellow | RS485 A |
| Blue | RS485 B |

## Registers

| Address | Meaning | Type | Scaling | Access |
|---|---|---|---|---|
| 0x0000 | EC | uint16 | µS/cm | R |
| 0x0001 | Temperature | uint16 | ×10 °C | R |
| 0x0002 | Salinity | uint16 | ppm | R |
| 0x0003 | TDS | uint16 | ppm | R |
| 0x0050 | Temperature deviation | int16 | ×10 | R/W |
| 0x0051 | EC deviation | uint16 | µS/cm | R/W |
| 0x0052-0x0053 | EC temperature compensation coefficient | float, big-endian | default 0.02 | R/W |
| 0x0054-0x0055 | Electrode constant | float, big-endian | | R/W |
| 0x0110-0x0111 | EC calibration | 2 × uint16 | see below | W (0x10) |
| 0x07D0 | Device address | uint16 | 1-254 | R/W |
| 0x07D1 | Baud rate | uint16 | 0=2400, 1=4800, 2=9600, 3=19200, 4=38400, 5=57600, 6=115200, 7=1200 | R/W |

Reads use function 0x03 or 0x04. Single writes use 0x06, multi-register writes 0x10.

## Example frames (from DFRobot)

- Change address 1 → 2: `01 06 07 D0 00 02 08 86`
- Change baud to 9600: `01 06 07 D1 00 02 59 46`
- Calibrate at 1413 µS/cm: `01 10 01 10 00 02 04 00 04 05 85 7C 01`
  (writes `0x0004`, then the standard's value in µS/cm)

[`tools/dfrobot_rs485.py`](../../tools/dfrobot_rs485.py) builds these frames and is
tested against the examples above.
