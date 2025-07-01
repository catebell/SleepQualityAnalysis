import os
import time as chronometer
import pandas as pd
import numpy as np

from plotting import plot_features

'''''
estimates sleep periods only using acc_dev_std
'''''

if __name__ == "__main__":

    # for file in os.listdir("csvs"):
    filename = "2022_03_25__CF0015DD8E0C52E75EFDF4C064108636"  # file[:-8]
    filepath = os.path.join("engineered_features", f"{filename}.csv")
    if not os.path.isfile(filepath):
        if not os.path.isdir(os.path.join("engineered_features")):
            os.mkdir("engineered_features")

        # PARAMETERS DEFINITION:

        # un-comment here and if-break later to define sub-period (ex. first night) for testing:
        end_time = pd.Timestamp(year=2022, month=3, day=26, hour=10, minute=00, second=0)

        # epoch for rolling window used to average the values and eliminate a bit of noise:
        epoch = "5s"

        # engineered features limits for sleep/wake detection:
        acc_dev_std_lim = 0.1

        # sliding windows to be used for calculations:
        window_sleep = pd.Timedelta(hours=1)  # we don't care if they occasionally move while asleep
        window_awake = pd.Timedelta(minutes=1)  # they move more frequently so stricter observation periods are needed
        window_current = window_awake  # we start hypothesizing they are awake
        window_slide_asleep = pd.Timedelta(minutes=1)
        window_slide_awake = pd.Timedelta(seconds=1)

        # intervals for sleep-wake detection:
        interval_for_asleep = pd.Timedelta(hours=1)  # if they keep almost still for this interval they're considered asleep
        interval_for_awake = pd.Timedelta(minutes=5)  # if there is movement for this interval they're considered awake

        # dataframes for extraction:
        column_names = ['datetime', 'x', 'y', 'z', 'light', 'temp']

        df = pd.DataFrame(columns=column_names)
        df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S.%f")
        df.set_index('datetime', inplace=True)

        current_day = None
        night_end = True
        start_extraction = None

        print("READING csv...")
        start = chronometer.time()

        for chunk in pd.read_csv(os.path.join("csvs", f"{filename}.csv.gz"),
                                 names=column_names, header=0, chunksize=10000, parse_dates=True):
            chunk.dropna()
            chunk['datetime'] = pd.to_datetime(chunk['datetime'], format="%Y-%m-%d %H:%M:%S.%f")

            # un-comment for testing (data up to end_time):
            #if chunk['datetime'].min() >= end_time:  # cut reading of file
            #    print(f"FINISHED in: {(chronometer.time() - start) / 60} minutes")
            #    break

            chunk.set_index('datetime', inplace=True)

            try:
                # use data from 21:00 till 9:00 + 1h so to compute correctly data till 9:00 (1h window):
                df_chunk = chunk.between_time("21:00", "10:00")

                if not df_chunk.empty:
                    # at 200Hz and by reading chunks of 10000 measurements, we'll never have different days in the same df_chunk
                    if night_end:
                        print("extracting night...")
                        start_extraction = chronometer.time()
                        current_day = df_chunk.index.min().date()

                    # if we extracted one complete night we do things, else continue extracting chunks:
                    if df_chunk.index.max() + pd.Timedelta(milliseconds=5) > (pd.Timestamp(year=current_day.year,
                                                                                            month=current_day.month,
                                                                                            day=current_day.day,
                                                                                            hour=10) + pd.Timedelta(days=1)):
                        print(f"extraction finished in: {(chronometer.time() - start_extraction) / 60} minutes")
                        night_end = True
                        df_chunk = df_chunk.sort_index()
                        df_chunk = df_chunk[df_chunk.index.notnull()]  # remove rows with null datetime (NaT)
                        df = pd.concat([df, df_chunk])  # add last chunk to current day df

                        print("\n")
                        print("----- DAY: " + str(current_day) + " -----")

                        # sub-sampling at 20Hz, 200Hz to have 1/20 of df rows -> compute new measurement every 20 measurements (0.1s)
                        print("resampling to 20Hz...")
                        start_resample = chronometer.time()
                        df = df.resample('100ms').mean()
                        print(f"FINISHED in: {(chronometer.time() - start_resample) / 60} minutes")

                        # average data with rolling window to eliminate noise:
                        df['x'] = df['x'].rolling(epoch).mean()  # ax
                        df['y'] = df['y'].rolling(epoch).mean()  # ay
                        df['z'] = df['z'].rolling(epoch).mean()  # az

                        df['temp'] = df['temp'].rolling(epoch).mean()
                        df['light'] = df['light'].rolling(epoch).mean()
                        # functions from Axivity documentation for light and temperature in correct measurement units:
                        df['light'] = 10 * (df['light'] / 341)
                        # df['temp'] = (df['temp'] - 171) / 3.142  # °C, but I think it's already converted?

                        # compute norm and angle for each measurement
                        df['norm'] = np.sqrt(np.square(df[['x', 'y', 'z']]).sum(axis=1))
                        df['angle'] = (np.arctan(df['z'] / np.sqrt(np.square(df[['x', 'y']]).sum(axis=1))) * 180 / np.pi)

                        # COORDINATE POLARI
                        print("computing polar coordinates...")
                        start_polar = chronometer.time()
                        # r = norm = distance from P = (x,y,z) to origin O
                        # theta = angle between axe x>0 and OQ (Q = P projection on xy)
                        df['theta'] = None
                        # fi = co-latitude, angle between axe z>0 and OP
                        df['fi'] = None

                        for index, row in df.iterrows():
                            if row['x'] != 0 or row['y'] != 0 or row['z'] != 0:
                                if row['x'] == 0:
                                    if row['y'] > 0:
                                        df.at[index, 'theta'] = np.pi / 2
                                    elif row['y'] < 0:
                                        df.at[index, 'theta'] = 3 * np.pi / 2
                                    elif row['y'] == 0:
                                        print("(x,y,z) = (0,0,...), theta not defined")
                                elif row['x'] > 0 and row['y'] >= 0:
                                    df.at[index, 'theta'] = np.arctan(row['y'] / row['x'])
                                elif row['x'] > 0 > row['y'] or row['x'] < 0 < row['y']:
                                    df.at[index, 'theta'] = np.arctan(row['y'] / row['x']) + 2 * np.pi
                                elif row['x'] < 0 and row['y'] <= 0:
                                    df.at[index, 'theta'] = np.arctan(row['y'] / row['x']) + np.pi

                                df.at[index, 'fi'] = np.arccos(row['z'] / row['norm'])
                            else:
                                print("x,y,z are (0,0,0), theta and fi not defined")

                        print(f"FINISHED in: {(chronometer.time() - start_polar) / 60} minutes")

                        df_windowed = pd.DataFrame(
                            columns=['datetime', 'acc_dev_std', 'ang_dev_std', 'activity'])  # df with new features
                        sleep_hours = []
                        awakenings = 0
                        awake = True
                        started_moving_at = None
                        stopped_moving_at = None
                        start_sleep_time = None
                        # start from datetime of first measurement in the df (datetime = index value):
                        start_time = df.index.min()

                        print("DETECTING SLEEP PERIODS...")
                        start = chronometer.time()

                        while start_time <= (df.index.max() - window_current):  # as long as we can compute a window of data
                            end_time = start_time + window_current
                            df_in_window = df[(df.index >= start_time) & (df.index < end_time)]  # select rows in window

                            # features computed for the current window of data
                            acc_dev_std = df_in_window['norm'].std()
                            ang_dev_std = df_in_window['angle'].std()
                            # if needed (then must be inserted in df_windowed, saved in c30 and plotted):
                            # norm = df_in_window.at[start_time, 'norm']
                            # angle = df_in_window.at[start_time, 'angle']

                            if awake:  # if was considered awake
                                start_time = start_time + window_slide_awake  # awakenings can be brief, window slides of fewer points
                                if acc_dev_std <= acc_dev_std_lim:  # -> maybe fell asleep
                                    # print(str(df_in_window.index.min()) + " (AWAKE) acc_dev_std <= limit --> MAYBE ASLEEP")
                                    if stopped_moving_at is None:  # was considered moving until now
                                        # print("they hadn't already stopped moving")
                                        stopped_moving_at = df_in_window.index.min()
                                        started_moving_at = None
                                    else:  # if already stopped moving
                                        # print("they had already stopped moving")
                                        # if been completely still for [interval_for_asleep] we consider they asleep
                                        if (df_in_window.index.min() - stopped_moving_at) >= interval_for_asleep:
                                            print("AWAKE --> ASLEEP: has not been moving from " +
                                                  str(stopped_moving_at) + " to " + str(df_in_window.index.min()))
                                            awake = False
                                            window_current = window_sleep  # change of window
                                            # add new row in df_windowed with associated features computed in the window
                                            df_windowed.loc[len(df_windowed.index)] = [df_in_window.index.min(),
                                                                                       acc_dev_std,
                                                                                       ang_dev_std, "Asleep"]
                                            start_sleep_time = df_in_window.index.min() - interval_for_asleep  # correction offset
                                            # past tot minutes of offset needs to be labelled correctly, "Awake" replaced with "Asleep"
                                            df_windowed['activity'] = df_windowed['activity'].mask(
                                                df_windowed['datetime'] > (df_in_window.index.min() - interval_for_asleep),
                                                "Asleep")
                                        else:  # not yet considerable sleeping
                                            # print("it's only been " + str(df_in_window.index.min() - stopped_moving_at) + " minutes")
                                            # add new row in df_windowed with associated features computed in the window
                                            df_windowed.loc[len(df_windowed.index)] = [df_in_window.index.min(),
                                                                                       acc_dev_std,
                                                                                       ang_dev_std, "Awake"]
                                else:  # was awake and is still considered awake
                                    # print("(AWAKE) acc_dev_std > limit --> ACTUALLY STILL AWAKE, reset stopped_moving_at")
                                    stopped_moving_at = None
                                    # add new row in df_windowed with associated features computed in the window
                                    df_windowed.loc[len(df_windowed.index)] = [df_in_window.index.min(), acc_dev_std,
                                                                               ang_dev_std,
                                                                               "Awake"]
                            else:  # if was considered asleep
                                start_time = start_time + window_slide_asleep  # sleep periods last longer, window slides of more points
                                if acc_dev_std > acc_dev_std_lim:  # maybe woke up
                                    # print(str(df_in_window.index.min()) + " (ASLEEP) acc_dev_std > limit --> MAYBE AWAKE")
                                    if started_moving_at is None:  # was not previously moving
                                        # print("they were not already moving")
                                        started_moving_at = df_in_window.index.min()
                                        stopped_moving_at = None
                                    else:  # if had already started moving
                                        # print("they had already started moving")
                                        # if been moving for [interval_for_awake] we consider they awake
                                        if (df_in_window.index.min() - started_moving_at) >= interval_for_awake:
                                            print("ASLEEP --> AWAKE: has been moving from " + str(started_moving_at) + " to " +
                                                  str(df_in_window.index.min()))
                                            awake = True
                                            awakenings += 1
                                            window_current = window_awake  # change of window
                                            # add new row in df_windowed with associated features computed in the window
                                            df_windowed.loc[len(df_windowed.index)] = [df_in_window.index.min(),
                                                                                       acc_dev_std,
                                                                                       ang_dev_std, "Awake"]
                                            end_sleep_time = df_in_window.index.min() - interval_for_awake  # with correction offset
                                            # past tot minutes of offset needs to be labelled correctly, "Asleep" replaced with "Awake"
                                            df_windowed['activity'] = df_windowed['activity'].mask(
                                                df_windowed['datetime'] > (df_in_window.index.min() - interval_for_awake),
                                                "Awake")
                                            sleep_hours.append(
                                                "[" + str(start_sleep_time) + " - " + str(end_sleep_time) + "]")
                                            start_sleep_time = None
                                        else:  # not yet considerable awake
                                            # print("it's only been " + str(df_in_window.index.min() - started_moving_at) + " minutes")
                                            # add new row in df_windowed with associated features computed in the window
                                            df_windowed.loc[len(df_windowed.index)] = [df_in_window.index.min(),
                                                                                       acc_dev_std,
                                                                                       ang_dev_std, "Asleep"]
                                else:  # was asleep and is still considered asleep
                                    # print("(ASLEEP) acc_dev_std <= limit --> ACTUALLY STILL ASLEEP, reset started_moving_at")
                                    started_moving_at = None
                                    # add new row in df_windowed with associated features computed in the window
                                    df_windowed.loc[len(df_windowed.index)] = [df_in_window.index.min(), acc_dev_std,
                                                                               ang_dev_std,
                                                                               "Asleep"]

                        # if still asleep after 09:00:
                        if start_sleep_time is not None and start_sleep_time <= pd.Timestamp(year=current_day.year,
                                                                                             month=current_day.month,
                                                                                             day=current_day.day,
                                                                                             hour=9) + pd.Timedelta(days=1):
                            sleep_hours.append("[" + str(start_sleep_time) + " - " + " ... ]")

                        print("awakenings: " + str(awakenings))
                        print("sleep_periods: " + str(sleep_hours))

                        df_windowed.set_index('datetime', inplace=True)
                        print(f"FINISHED in: {(chronometer.time() - start) / 60} minutes")

                        # saving csv to directory
                        print("SAVING TO engineered_features...")

                        c30 = df_windowed[['acc_dev_std', 'ang_dev_std', 'activity']]
                        if not os.path.isfile(filepath):
                            c30.to_csv(filepath)
                        else:
                            c30.to_csv(filepath, mode="a", header=False)

                        # RESET VARIABLES FOR NEXT DAY
                        sleep_hours = []  # reset for next day
                        df = pd.DataFrame(columns=column_names)
                        df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M:%S.%f")
                        df.set_index('datetime', inplace=True)
                        print(f"DONE")
                    else:
                        night_end = False
                        df_chunk = df_chunk.sort_index()
                        df_chunk = df_chunk[df_chunk.index.notnull()]  # remove rows with null datetime (NaT)
                        # df = pd.concat([df, df_chunk])
                        df = (df if df_chunk.empty
                                else df_chunk.copy() if df.empty
                                else pd.concat([df, df_chunk]))
                        continue
            except Exception as e:
                print("EXCEPTION: " + str(e))

    plot_features(filename)
