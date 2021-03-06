import pandas as pd
from datetime import datetime, timedelta, time
from features_utils import splitOvernightEpisodes, splitMultiSegmentEpisodes

battery_data = pd.read_csv(snakemake.input[0], parse_dates=["local_start_date_time", "local_end_date_time", "local_start_date", "local_end_date"])
day_segment = snakemake.params["day_segment"]
features = snakemake.params["features"]

if battery_data.empty:
    battery_features = pd.DataFrame(columns=["local_date"] + ["battery_" + day_segment + "_" + x for x in features])
else:
    battery_data = splitOvernightEpisodes(battery_data, ["battery_diff"], [])

    if day_segment != "daily":
        battery_data = splitMultiSegmentEpisodes(battery_data, day_segment, ["battery_diff"])

    battery_data["battery_consumption_rate"] = battery_data["battery_diff"] / battery_data["time_diff"]

    # for battery_data_discharge:
    battery_data_discharge = battery_data[battery_data["battery_diff"] > 0]
    battery_discharge_features = pd.DataFrame()
    if "countdischarge" in features:
        battery_discharge_features["battery_"+day_segment+"_countdischarge"] = battery_data_discharge.groupby(["local_start_date"])["local_start_date"].count()
    if "sumdurationdischarge" in features:
        battery_discharge_features["battery_"+day_segment+"_sumdurationdischarge"] = battery_data_discharge.groupby(["local_start_date"])["time_diff"].sum()
    if "avgconsumptionrate" in features:
        battery_discharge_features["battery_"+day_segment+"_avgconsumptionrate"] = battery_data_discharge.groupby(["local_start_date"])["battery_consumption_rate"].mean()
    if "maxconsumptionrate" in features:
        battery_discharge_features["battery_"+day_segment+"_maxconsumptionrate"] = battery_data_discharge.groupby(["local_start_date"])["battery_consumption_rate"].max()

    # for battery_data_charge:
    battery_data_charge = battery_data[battery_data["battery_diff"] <= 0]
    battery_charge_features = pd.DataFrame()
    if "countcharge" in features:
        battery_charge_features["battery_"+day_segment+"_countcharge"] = battery_data_charge.groupby(["local_start_date"])["local_start_date"].count()
    if "sumdurationcharge" in features:
        battery_charge_features["battery_"+day_segment+"_sumdurationcharge"] = battery_data_charge.groupby(["local_start_date"])["time_diff"].sum()

    # combine discharge features and charge features; fill the missing values with ZERO
    battery_features = pd.concat([battery_discharge_features, battery_charge_features], axis=1, sort=True).fillna(0)
    battery_features.index.rename("local_date", inplace=True)
battery_features.to_csv(snakemake.output[0], index=True)