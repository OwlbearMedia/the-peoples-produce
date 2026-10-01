# Crop profiles

Each reservoir has a crop profile select. Choosing a profile writes its pH target and
EC limits into that reservoir's setpoints. Setpoints can then be tuned by hand. The
profile select keeps showing the last profile applied, even after hand tuning.

The source of truth is the `set_action` lambda in
[`core.yaml`](../esphome/packages/reservoir/core.yaml). Keep this table in step with it.

| Profile | pH target | EC low (mS/cm) | EC high (mS/cm) | Use for |
|---|---|---|---|---|
| Seedling | 6.0 | 0.6 | 1.2 | Seedlings and clones until established |
| Tomato - vegetative | 6.0 | 1.8 | 2.5 | Before first flower truss |
| Tomato - fruiting | 6.0 | 2.5 | 3.5 | Flowering and fruit set onward |
| Pepper | 6.0 | 1.8 | 2.8 | Sweet and hot peppers |
| Brassica | 6.3 | 2.5 | 3.2 | Broccoli, Brussels sprouts, cabbage, kale |

Not set by profiles (shared defaults, change by hand): pH dosing deadband 0.15, pH
alarm band 0.5, water temperature limit 24 °C.

These are starting points drawn from commonly published hydroponic charts. Check them
against your nutrient maker's feed chart and adjust from how the plants look.

## Adding a profile

1. Add the option to `options:` and a matching `else if` line in the `set_action`
   lambda in `core.yaml`.
2. Add a row to the table above.
3. Validate (`tools/validate.sh`) and flash.
