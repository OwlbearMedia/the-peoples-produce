# Decision log

Decisions already made and why. Revisit one only when its reasoning stops holding.
Add new entries at the bottom.

## 1. Start fresh rather than fork Hydro0x01

[Hydro0x01](https://github.com/40rbidd3n/Hydro0x01) is built around analog sensors and
one device per system, with a large custom backend (Fastify, Postgres, InfluxDB,
React). Multiple analog pH/EC probes in one reservoir interfere with each other, and we
want one controller to run several reservoirs.

## 2. ESPHome and Home Assistant instead of custom firmware

ESPHome already supports the sensors we use (Atlas EZO, Modbus, SHT4x, GPIO), runs
logic on the device and supports OTA updates. Home Assistant provides the shared
dashboard, history, phone alerts and setpoint controls. Custom firmware and a custom UI
would cost a lot of upkeep for no gain at this scale.

## 3. One node per location, many reservoirs per node

Reservoirs next to each other share one ESP32. A system in another room gets its own
node. This keeps cable runs short and lets each location work on its own.

## 4. Hybrid sensors: isolated Atlas pH, RS485 DFRobot EC

- **pH:** Atlas Scientific EZO-pH on the Electrically Isolated EZO Carrier (Atlas pH
  kit, about $175). pH is the reading most easily skewed by other probes, so it gets
  the isolation.
- **EC:** DFRobot SEN0707 RS485 EC sensor, K=10, 10-20000 µS/cm ($159). It is the one
  non-isolated probe in the reservoir and includes a water temperature sensor that also
  drives the pH temperature compensation.

Rejected options:
- DFRobot Gravity analog EC: its practical range tops out around 2000 µS/cm, too low
  for fruiting tomatoes (2500-3500 µS/cm).
- DFRobot K=1 RS485 EC (SEN0706): 1-2000 µS/cm, too low for the same reason.
- All-Atlas (about $375 per reservoir): better EC accuracy (±2% of reading vs ±0.2
  mS/cm), but costs more. Reasonable upgrade later.
- All-DFRobot RS485 (about $288 per reservoir): their documentation says nothing about
  isolation, and two non-isolated probes in one reservoir break design rule 3.

## 5. Automate pH-down only, add nutrients by hand

Tomatoes in DWC mostly push pH up, so pH-down is the dosing that pays off. Nutrients
are topped up by hand at reservoir changes for now; EC is monitored and alarmed.
Nutrient A/B dosing is on the [roadmap](roadmap.md).

## 6. Auto top-off with plain water and an air gap

Fruiting tomatoes drink a large share of a 5 gal reservoir per day, so top-off is what
keeps the reservoir stable. Fill lines end above the water surface. The air gap breaks
the conductive path between reservoirs that share a top-off tank and prevents
back-siphoning.

## 7. Rate limits are RAM counters, not wall-clock based

Hourly and daily dose and fill limits count from boot, so they work without a clock or
network. Because a reboot resets them, nodes never reboot themselves when they lose
the network.

## 8. Air pump health via a power-monitoring smart plug

The air pump runs on mains, which stays out of the node enclosure (design rule 5). A
smart plug with power metering lets Home Assistant alert when the pump stops drawing
power. An inline air pressure sensor on the node is a possible later upgrade.
