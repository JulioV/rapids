import pandas as pd
import numpy as np

def getActivityEpisodes(acc_minute, activity_type):
    col_name = ["nonexertional_episodes", "exertional_episodes"][activity_type]
    
    # rebuild local date time for resampling
    acc_minute["local_datetime"] = pd.to_datetime(acc_minute["local_date"].dt.strftime("%Y-%m-%d") + \
                                        " " + acc_minute["local_hour"].apply(str) + ":" + acc_minute["local_minute"].apply(str) + ":00")
    # resample the data into 1 minute bins
    resampled_acc_minute = pd.DataFrame(acc_minute.resample("1T", on="local_datetime")["isexertionalactivity"].sum())

    if activity_type == 0:
        resampled_acc_minute["isexertionalactivity"] = resampled_acc_minute["isexertionalactivity"] * (-1) + 1

    # get the longest episode of exertional/non-exertional activity given as consecutive one minute periods
    resampled_acc_minute['consecutive'] = resampled_acc_minute["isexertionalactivity"].groupby((resampled_acc_minute["isexertionalactivity"] != resampled_acc_minute["isexertionalactivity"].shift()).cumsum()).transform('size') * resampled_acc_minute["isexertionalactivity"]
    longest_activity_episodes = resampled_acc_minute.groupby(pd.Grouper(freq='D'))[["consecutive"]].max().rename(columns = {"consecutive": col_name})

    # get the count of exertional/non-exertional activity episodes
    resampled_acc_minute_shift = resampled_acc_minute.loc[resampled_acc_minute["consecutive"].shift() != resampled_acc_minute["consecutive"]]
    count_activity_episodes = resampled_acc_minute_shift.groupby(pd.Grouper(freq='D'))[["consecutive"]].apply(lambda x: np.count_nonzero(x)).to_frame(name = col_name)

    return longest_activity_episodes, count_activity_episodes

def dropRowsWithCertainThreshold(data, threshold):
    data_grouped = data.groupby(["local_date", "local_hour", "local_minute"]).count()
    drop_dates = data_grouped[data_grouped["timestamp"] == threshold].index
    data.set_index(["local_date", "local_hour", "local_minute"], inplace = True)
    if not drop_dates.empty:
        data.drop(drop_dates, axis = 0, inplace = True)
    return data.reset_index()


acc_data = pd.read_csv(snakemake.input[0], parse_dates=["local_date_time", "local_date"])
day_segment = snakemake.params["day_segment"]
features = snakemake.params["features"]

acc_features = pd.DataFrame(columns=["local_date"] + ["acc_" + day_segment + "_" + x for x in features])
if not acc_data.empty:
    if day_segment != "daily":
        acc_data = acc_data[acc_data["local_day_segment"] == day_segment]
    if not acc_data.empty:
        acc_features = pd.DataFrame()        
        # get magnitude related features: magnitude = sqrt(x^2+y^2+z^2)
        acc_data["magnitude"] = (acc_data["double_values_0"] ** 2 + acc_data["double_values_1"] ** 2 + acc_data["double_values_2"] ** 2).apply(np.sqrt)
        if "maxmagnitude" in features:
            acc_features["acc_" + day_segment + "_maxmagnitude"] = acc_data.groupby(["local_date"])["magnitude"].max()
        if "minmagnitude" in features:
            acc_features["acc_" + day_segment + "_minmagnitude"] = acc_data.groupby(["local_date"])["magnitude"].min()
        if "avgmagnitude" in features:
            acc_features["acc_" + day_segment + "_avgmagnitude"] = acc_data.groupby(["local_date"])["magnitude"].mean()
        if "medianmagnitude" in features:
            acc_features["acc_" + day_segment + "_medianmagnitude"] = acc_data.groupby(["local_date"])["magnitude"].median()
        if "stdmagnitude" in features:
            acc_features["acc_" + day_segment + "_stdmagnitude"] = acc_data.groupby(["local_date"])["magnitude"].std()
        
        # get extertional activity features
        # reference: https://jamanetwork.com/journals/jamasurgery/fullarticle/2753807

        # drop rows where we only have one row per minute (no variance) 
        acc_data = dropRowsWithCertainThreshold(acc_data, 1)
        if not acc_data.empty:
            # check if the participant performs exertional activity for each minute
            acc_minute = pd.DataFrame()
            acc_minute["isexertionalactivity"] = (acc_data.groupby(["local_date", "local_hour", "local_minute"])["double_values_0"].var() + acc_data.groupby(["local_date", "local_hour", "local_minute"])["double_values_1"].var() + acc_data.groupby(["local_date", "local_hour", "local_minute"])["double_values_2"].var()).apply(lambda x: 1 if x > 0.15 * (9.807 ** 2) else 0)
            acc_minute.reset_index(inplace=True)

            if "ratioexertionalactivityepisodes" in features:
                acc_features["acc_" + day_segment + "_ratioexertionalactivityepisodes"] = acc_minute.groupby(["local_date"])["isexertionalactivity"].sum()/acc_minute.groupby(["local_date"])["isexertionalactivity"].count()
            if "sumexertionalactivityepisodes" in features:
                acc_features["acc_" + day_segment + "_sumexertionalactivityepisodes"] = acc_minute.groupby(["local_date"])["isexertionalactivity"].sum()
            
            longest_exertionalactivity_episodes, count_exertionalactivity_episodes = getActivityEpisodes(acc_minute, 1)
            longest_nonexertionalactivity_episodes, count_nonexertionalactivity_episodes = getActivityEpisodes(acc_minute, 0)
            if "longestexertionalactivityepisode" in features:
                acc_features["acc_" + day_segment + "_longestexertionalactivityepisode"] = longest_exertionalactivity_episodes["exertional_episodes"]
            if "longestnonexertionalactivityepisode" in features:
                acc_features["acc_" + day_segment + "_longestnonexertionalactivityepisode"] = longest_nonexertionalactivity_episodes["nonexertional_episodes"]
            if "countexertionalactivityepisodes" in features:
                acc_features["acc_" + day_segment + "_countexertionalactivityepisodes"] = count_exertionalactivity_episodes["exertional_episodes"]
            if "countnonexertionalactivityepisodes" in features:
                acc_features["acc_" + day_segment + "_countnonexertionalactivityepisodes"] = count_nonexertionalactivity_episodes["nonexertional_episodes"]
        
        acc_features = acc_features.reset_index()

acc_features.to_csv(snakemake.output[0], index=False)