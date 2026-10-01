# Control logic

Everything here runs on the node and keeps working without Home Assistant or Wi-Fi.

## Auto top-off

Source: [`topoff_pump.yaml`](../esphome/packages/reservoir/topoff_pump.yaml)

Every 30 s the node starts a fill if **all** of these are true:

- auto top-off is on
- the water is below the low switch (held for 30 s, so the bubbling surface doesn't
  trigger it)
- the level switches agree with each other (no level fault)
- the top-off tank is not low
- the floor leak probe is dry
- no top-off fault is latched
- the daily fill limit hasn't been reached

A fill runs the pump until the high switch sees water, the tank runs low or a leak
appears, or the **max fill time** passes. Ending on the time limit means the pump, the
line or a switch has failed, so it **latches a fault**: auto top-off stays off,
across reboots, until someone presses "reset top-off fault".

## pH-down dosing

Source: [`ph_down_dosing.yaml`](../esphome/packages/reservoir/ph_down_dosing.yaml)

Every 60 s the node doses once if **all** of these are true:

- auto pH dosing is on
- the pH reading is valid (no pH sensor fault)
- pH > target + deadband
- the mix time has passed since the last dose **and** since the last top-off
- the top-off pump is off and the floor is dry
- the hourly and daily dose limits haven't been reached

A dose runs the peristaltic pump for the configured dose time. After that the
mix time must pass before the next dose, so pH creeps toward target in small steps.

There is no pH-up pump. Overshooting below target just stops dosing, and the pH-out-of-
range alarm fires if it goes too far.

## Safety layers

| Layer | Where | What it does |
|---|---|---|
| Boot state | every pump switch | `restore_mode: ALWAYS_OFF`. Pumps are off after any reset. |
| Pump watchdog | every pump switch | A script stops the pump after a fixed maximum on-time, whatever started it. pH-down: 15 s. Top-off: max fill time + 10 s. |
| Mix lockout | dosing | No dose until one mix time after boot, after the last dose and after the last top-off |
| Rate limits | dosing, top-off | Per-hour and per-day counters |
| Latched fault | top-off | A timed-out fill disables top-off until a person resets it. Stored in flash. |
| Interlocks | dosing, top-off | Leak probe, top-off tank level, level-switch agreement |
| No self-reboot | node base | `reboot_timeout: 0s` for API and Wi-Fi, because a reboot clears the rate-limit counters |

## What survives a reboot

| Survives (flash) | Resets (RAM) |
|---|---|
| Crop profile and all setpoints | Hourly and daily dose counts |
| Auto top-off and auto dosing on/off | Daily fill count |
| Top-off fault latch | Mix-time timers (restart from boot, which delays dosing) |
| EC offset | |

## Alarms

Each reservoir has these problem sensors, rolled up into `<res_name> status` and
`<res_name> needs attention`:

| Alarm | Trips when | Delay |
|---|---|---|
| pH sensor fault | No valid pH reading for 5 min | none |
| pH out of range | pH more than the alarm band from target | 10 min |
| pH dosing limit reached | Daily dose limit hit. Usually means the pH-down bottle is empty or the probe is failing. | none |
| EC sensor fault | No valid EC reading for 5 min | none |
| EC out of range | EC outside the profile's low/high limits | 10 min |
| water too warm | Water above the temperature limit (default 24 °C / 75 °F) | 10 min |
| level sensor fault | High switch wet while low switch dry | 1 min |
| water low | Below the low switch for 30 min (top-off isn't keeping up) | 30 min |
| top-off problem | Fault latched, or daily fill limit reached | none |

Node-level: `Top-off tank low`, `Floor leak`, and `Status` (online/offline, seen by
Home Assistant).

## Commissioning

Turn the automation on one piece at a time:

1. Calibrate pH and check EC against a handheld meter ([calibration.md](calibration.md)).
2. Measure the pH-down pump's flow and pick a dose time that adds about 1 ml of diluted
   pH-down.
3. Turn on **auto top-off**. Watch a few fills, then compare how long each one takes
   with the max fill time. The max should be about twice a normal fill.
4. Turn on **auto pH dosing** with the defaults (1 s dose, 10 min mix, 2 per hour,
   12 per day). Watch the logs for a day and adjust the dose time so each dose moves
   pH by about 0.05-0.1.
