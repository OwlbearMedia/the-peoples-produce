# Safety

Water, electricity and acid in one place. These rules aren't optional.

## Electrical

- **The node switches only 12 V DC.** Mains loads (air pumps, chillers, heaters,
  lights) go on off-the-shelf smart plugs, never through relays in the node enclosure.
- **GFCI:** everything near the reservoirs plugs into a GFCI-protected outlet or a GFCI
  adapter, including the 12 V supply.
- **Enclosure:** mount it above the highest water level, keep it closed, bring cables
  in through glands from below, and give every cable a drip loop.
- **Fusing:** put an inline fuse (about 3 A) on the 12 V supply's output.

## Water

- **Overflow:** top-off has a max fill time, a daily fill limit, a latched fault and a
  leak interlock ([control-logic.md](control-logic.md)). Put the leak probe at the
  lowest point under the reservoirs.
- **Siphoning:** keep the top-off tank lower than the fill line's outlet, and end the
  line above the water surface (an air gap).
- **Tubing:** use clips on barbed fittings. A popped line drains a tank onto the floor.

## Chemicals

- pH-down is usually phosphoric or nitric acid. Wear gloves and eye protection when
  mixing it.
- Dilute it (about 1:10) in a labeled bottle. Diluting gives finer dosing and makes a
  pump failure less dangerous.
- When diluting, always add acid to water, never water to acid.
- Keep the dosing bottle in a tray that can hold a spill.

## Firmware

Rules for anyone changing the firmware, human or AI:

- Never change a pump's `restore_mode` from `ALWAYS_OFF`.
- Never remove or lengthen a pump watchdog without a written reason in the commit.
- Never re-enable automatic reboots (`reboot_timeout`) on the API or Wi-Fi.
- New automatic actions default off and come with rate limits.
- Bench-test with the pump outlets in a cup before letting new logic touch a reservoir.
