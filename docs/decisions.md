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

## 9. Our own sourced crop database

No maintained open database of hydroponic crop targets exists. OpenFarm shut down in
April 2025 and never had EC/pH data, Growstuff has no EC/pH, and a GitHub dataset we
found was unlicensed and covered 8 crops. Published values often disagree: Oklahoma
State's HLA-6722 puts peppers at EC 0.8-1.8, while other sources say 2.0-3.5. A 2024
HortScience study says tomato recommendations are inconsistent too.

So [`crops/crops.yaml`](../crops/crops.yaml) records what each source says, the range
chosen and why, and a confidence level. No single source is the default; crops whose
sources conflict are kept out of the firmware until resolved. A generator builds the
firmware's profile select from the file, so selecting a crop stays on the node and
works offline. Rules: [crop-profiles.md](crop-profiles.md#research-rules).

## 10. Dissolved oxygen deferred

A DO sensor would directly check DWC aeration, but costs $199-355 per reservoir. The
smart-plug power check covers a dead air pump for now. Findings and a recommended
part are in [research/dissolved-oxygen.md](research/dissolved-oxygen.md).

## 11. One repo growing into general open-source firmware

The long-term aim is open-source firmware for automated hydroponic systems, including
ones sold as finished products. Rather than keep this repo about one household's
systems and extract a general project later, this repo grows in that direction:

- The firmware is already split into generic parts (packages, crop database, tools,
  most docs) and parts specific to one build (node configs like `esphome/dwc-1.yaml`
  and `docs/hardware/`). Keep it that way: anything only true of one physical build
  goes in its node config or hardware doc.
- The first builds stay in the repo as prototypes and reference designs.
- Material that isn't meant to be open, such as product or furniture designs and
  business documents, lives outside this repo.
- Tagged releases become the stable points that builds pin to. Commercial ESPHome
  devices typically use `dashboard_import` to pull their config from a public repo at
  a tagged version, which fits this model.

Extracting later was rejected: it splits the history, breaks links, and means
maintaining two copies of the docs while it happens.

A product would eventually need things a home build doesn't, such as an on-device UI
for buyers without Home Assistant, a custom PCB, and certification (listed power
supplies, FCC Part 15). Those are for later and shouldn't shape the code yet, beyond
keeping control on the node.

## 12. GPL-3.0-or-later

Relicensed from MIT on 2026-09-30, while there was a single author. The intent:
anyone, including competitors, may use and sell what they build with this project,
but nobody can take it and close it off. MIT allows closed derivatives; the GPL
requires distributed versions to stay open under the same terms.

- **Matches ESPHome.** ESPHome's C++ runtime is GPLv3 (its Python tooling is MIT), so
  firmware built from this repo already ships under GPLv3.
- **Devices stay hackable.** For consumer devices, GPLv3 requires sellers to let owners
  install modified firmware. That applies to us too if we sell devices; ESPHome's OTA
  and USB flashing already make it possible.
- **"Or later"** keeps the project compatible with future GPL versions.
- The license covers the whole repository, including the crop database and docs.
- Versions published under MIT before the change remain available under MIT to anyone
  who obtained them. Everything from this change on is GPL.
- Contributions are accepted under the same license.

