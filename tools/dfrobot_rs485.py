# /// script
# requires-python = ">=3.10"
# dependencies = ["pyserial>=3.5"]
# ///
"""Bench tool for DFRobot RS485 water sensors (SEN0707 EC) through a USB-RS485 adapter.

Use it to read a sensor, change its Modbus address before putting a second sensor on
the same bus, or run the one-point EC calibration. Connect one sensor at a time when
changing addresses. Register map: docs/hardware/dfrobot-sen0707.md

    uv run tools/dfrobot_rs485.py --port /dev/tty.usbserial-XXXX read
    uv run tools/dfrobot_rs485.py --port /dev/tty.usbserial-XXXX set-address 2
    uv run tools/dfrobot_rs485.py --port /dev/tty.usbserial-XXXX calibrate-ec 1413
"""

from __future__ import annotations

import argparse
import struct
import sys

REG_EC = 0x0000
REG_DEVICE_ADDRESS = 0x07D0
REG_EC_CALIBRATION = 0x0110
EC_CALIBRATION_MODE = 0x0004  # first word of the calibration write, per DFRobot's docs


def crc16_modbus(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return struct.pack("<H", crc)


def frame(pdu: bytes) -> bytes:
    return pdu + crc16_modbus(pdu)


def read_holding(address: int, start: int, count: int) -> bytes:
    return frame(struct.pack(">BBHH", address, 0x03, start, count))


def write_single(address: int, register: int, value: int) -> bytes:
    return frame(struct.pack(">BBHH", address, 0x06, register, value))


def write_multiple(address: int, register: int, values: list[int]) -> bytes:
    pdu = struct.pack(">BBHHB", address, 0x10, register, len(values), 2 * len(values))
    return frame(pdu + b"".join(struct.pack(">H", v) for v in values))


def transact(port, request: bytes, response_len: int) -> bytes:
    port.reset_input_buffer()
    port.write(request)
    response = port.read(response_len)
    if len(response) < 5:
        sys.exit(f"No response ({response.hex(' ') or 'nothing'}). Check wiring, address and baud.")
    if response[1] & 0x80:
        sys.exit(f"Modbus exception code {response[2]}")
    if len(response) != response_len or crc16_modbus(response[:-2]) != response[-2:]:
        sys.exit(f"Bad response: {response.hex(' ')}")
    return response


def cmd_read(port, args) -> None:
    response = transact(port, read_holding(args.address, REG_EC, 4), 5 + 2 * 4)
    ec, temp, salinity, tds = struct.unpack(">4H", response[3:11])
    print(f"EC:          {ec} uS/cm ({ec / 1000:.2f} mS/cm)")
    print(f"Temperature: {temp / 10:.1f} C")
    print(f"Salinity:    {salinity} ppm")
    print(f"TDS:         {tds} ppm")


def cmd_set_address(port, args) -> None:
    if not 1 <= args.new_address <= 254:
        sys.exit("Address must be 1-254")
    transact(port, write_single(args.address, REG_DEVICE_ADDRESS, args.new_address), 8)
    print(f"Address changed {args.address} -> {args.new_address}. Power-cycle the sensor, then "
          f"check it with: read --address {args.new_address}")


def cmd_calibrate_ec(port, args) -> None:
    print(f"Calibrating at {args.standard} uS/cm. The probe must be in that standard solution.")
    request = write_multiple(args.address, REG_EC_CALIBRATION, [EC_CALIBRATION_MODE, args.standard])
    transact(port, request, 8)
    print("Calibration accepted. Rinse the probe and confirm with: read")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", required=True, help="serial port of the USB-RS485 adapter")
    parser.add_argument("--baud", type=int, default=4800, help="default: 4800 (factory setting)")
    parser.add_argument("--address", type=int, default=1, help="current Modbus address (default: 1)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("read", help="read EC, temperature, salinity and TDS")
    p = sub.add_parser("set-address", help="change the sensor's Modbus address")
    p.add_argument("new_address", type=int)
    p = sub.add_parser("calibrate-ec", help="one-point EC calibration in a standard solution")
    p.add_argument("standard", type=int, nargs="?", default=1413, help="uS/cm (default: 1413)")
    args = parser.parse_args()

    import serial  # imported here so the frame helpers can be tested without pyserial

    with serial.Serial(args.port, args.baud, bytesize=8, parity="N", stopbits=1, timeout=1) as port:
        {"read": cmd_read, "set-address": cmd_set_address, "calibrate-ec": cmd_calibrate_ec}[args.command](port, args)


if __name__ == "__main__":
    main()
