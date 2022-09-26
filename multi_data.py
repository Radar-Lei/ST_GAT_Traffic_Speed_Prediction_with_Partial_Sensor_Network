import glob
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET

def sort_df(speed_df, sensor_df):
    speed_df = speed_df.groupby('detector_id').agg({'detector_id':'first', 'speed': 'mean'})
    speed_df = speed_df.reindex(index=sensor_df.AID_ID_Number)
    return speed_df.reset_index(drop=True).values[:,1].reshape(1,-1)

def load_speed_data(params):
    path, sensors_id_array, sensors_gpd, num_intervals= params
    sensor_data_1day = glob.glob(path + "./*.xml")
    ndarray_1day = []
    if num_intervals > 0:
        sensor_data_1day = sensor_data_1day[0:1]

    for file_name in sensor_data_1day:
        try:
            tree = ET.parse(file_name)
            root = tree.getroot()
            rows = []
            df_cols = ["detector_id","period_from", "period_to", "direction", "lane_id", "speed"]

            for each_period in root[1]:
                period_from = each_period.find("period_from").text if each_period is not None else None
                period_to = each_period.find("period_to").text 
                for each_detector in each_period.find("detectors"):
                    detector_id = each_detector.find("detector_id").text if each_detector is not None else None
                    if detector_id not in sensors_id_array:
                        continue
                    direction = each_detector.find("direction").text
                    for each_lane in each_detector.find("lanes"):
                        lane_id = each_lane.find("lane_id").text
                        speed = float(each_lane.find("speed").text)
                        rows.append({"detector_id": detector_id,"period_from": period_from, "period_to": period_to, "direction": direction, "lane_id": lane_id, "speed": speed})
        except:
            pass
        if num_intervals > 0:
            return pd.DataFrame(rows)

        df_1interval = pd.DataFrame(rows)
        array_1interval = sort_df(df_1interval, sensors_gpd)
        ndarray_1day.append(array_1interval)

    ndarray_1day = np.concatenate(ndarray_1day, axis = 0)
    ndarray_1day[ndarray_1day==0] = np.nan
    
    return np.round(ndarray_1day.astype(np.double),2)