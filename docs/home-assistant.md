# Home Assistant

Home Assistant is the hub: one dashboard for every node, history, alerts and
setpoint changes. It doesn't run any control loops ([architecture.md](architecture.md#design-rules)).

## Adding a node

After a node's first flash it shows up under **Settings → Devices & services** as a
discovered ESPHome device. Add it and enter the `api_encryption_key` from
`esphome/secrets.yaml`.

Entity IDs combine the node's friendly name and the entity name. For `dwc-1`
("DWC 1"):

| Entity | ID |
|---|---|
| Reservoir A pH | `sensor.dwc_1_reservoir_a_ph` |
| Reservoir A EC | `sensor.dwc_1_reservoir_a_ec` |
| Reservoir A status | `sensor.dwc_1_reservoir_a_status` |
| Reservoir A needs attention | `binary_sensor.dwc_1_reservoir_a_needs_attention` |
| Top-off tank low | `binary_sensor.dwc_1_top_off_tank_low` |
| Floor leak | `binary_sensor.dwc_1_floor_leak` |
| Node online | `binary_sensor.dwc_1_status` |

Check the actual IDs on the device page; Home Assistant may adjust them.

## Dashboard

A good layout per reservoir:

- A tile for the **status** text
- pH and EC history graphs over 24 h, with the target and limits visible
- Water temperature and level switches
- A collapsed section with the config entities: crop profile, setpoints, automation
  switches, calibration and reset buttons

## Alerts

The node decides what counts as a problem; Home Assistant only delivers the
message. Example automation (replace `notify.notify` with your phone's notify action):

```yaml
alias: Hydroponics - notify on problems
mode: queued
triggers:
  - trigger: state
    entity_id:
      - binary_sensor.dwc_1_reservoir_a_needs_attention
      - binary_sensor.dwc_1_top_off_tank_low
      - binary_sensor.dwc_1_floor_leak
    to: "on"
  - trigger: state
    entity_id: binary_sensor.dwc_1_status
    to: "off"
    for: "00:05:00"
  - trigger: numeric_state
    entity_id: sensor.air_pump_plug_power   # your smart plug's power sensor
    below: 2
    for: "00:02:00"
actions:
  - action: notify.notify
    data:
      title: "Hydroponics: {{ trigger.to_state.name }}"
      message: >-
        {% if trigger.entity_id.endswith('_needs_attention') %}
          {{ states(trigger.entity_id
               | replace('binary_sensor.', 'sensor.')
               | replace('_needs_attention', '_status')) }}
        {% else %}
          {{ trigger.to_state.name }} is {{ trigger.to_state.state }}
        {% endif %}
```

When adding a reservoir or node, add its `needs attention`, `status` and node-level
entities to the triggers.

## Air pump monitoring

The DWC air pump runs on mains, so it plugs into a power-monitoring smart plug rather
than the node ([decisions.md](decisions.md#8-air-pump-health-via-a-power-monitoring-smart-plug)).
Note the pump's normal wattage, then set the alert threshold a bit below it. A dead
air pump can kill DWC roots within hours, so this alert matters.
