import pandas as pd
import numpy as np
import scipy.stats as stats

#Read csv into a pandas dataframe
data = pd.read_csv(snakemake.input[0])
column = ['local_date_time','count','most_common_activity','number_unique_activities','activity_change_count']
finalDataset = pd.DataFrame(columns=column)
finalDataset.set_index('local_date_time',inplace=True)

if data.empty:
    finalDataset.to_csv(snakemake.output[0])

else:
    #Resampling each of the required features as a pandas series
    data.local_date_time = pd.to_datetime(data.local_date_time)
    resampledData = data.set_index(data.local_date_time)
    resampledData = resampledData[~resampledData.index.duplicated()]
    resampledData.rename_axis('time',axis='columns',inplace=True)
    resampledData.drop(columns=['local_date_time'],inplace=True)

    #Finding count grouped by day
    count = pd.DataFrame()
    count = resampledData['activity_type'].resample('D').count()
    count = count.rename(columns={"activity_type":"count"})

    #Finding most common activity of the day
    mostCommonActivity = pd.DataFrame()
    mostCommonActivity = resampledData['activity_type'].resample('D').apply(lambda x:stats.mode(x)[0])
    mostCommonActivity = mostCommonActivity.rename(columns={'activity_type':'most_common_activity'})

    #finding different number of activities during a day
    uniqueActivities = pd.DataFrame()
    # countChanges = resampledData.to_period('D').groupby(resampledData.index)['activity_type'].value_counts()
    uniqueActivities = resampledData['activity_type'].resample('D').nunique()
    
    #finding Number of times activity changed
    resampledData['activity_type_shift'] = resampledData['activity_type'].shift()
    resampledData['activity_type_shift'].fillna(resampledData['activity_type'].head(1),inplace=True)
    #resampledData['different_activity'] = resampledData['activity_type'].apply(lambda x: 0 if resampledData['activity_type'] == resampledData['activity_type_shift'] else 1, axis=1)
    resampledData['different_activity']=np.where(resampledData['activity_type']!=resampledData['activity_type_shift'],1,0)
    countChanges = pd.DataFrame()
    countChanges = resampledData['different_activity'].resample('D').sum()

    #Concatenating all the processed data only, no other sensor data is added here for simplicity
    finalDataset = pd.DataFrame()
    finalDataset = pd.concat([count,mostCommonActivity,uniqueActivities,countChanges],axis=1)
    finalDataset.rename(columns={0:"count",1:'most_common_activity','activity_type':'number_unique_activities','different_activity':'activity_change_count'},inplace = True)

    #Export final dataframe with extracted features to respective PID
    finalDataset.to_csv(snakemake.output[0])

