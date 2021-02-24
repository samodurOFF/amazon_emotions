import pandas as pd
from create_chart import create_scatter, create_line, area_max


def calculate_median_timestamp(path):
    df = pd.read_csv(path)
    df_median = pd.DataFrame()

    for i in set(df['episode'].to_list()):
        df_episodes = df.loc[df['episode'] == i].copy()
        for j in sorted(set(df_episodes['timestamps'].to_list())):
            df_timestamps = df_episodes.loc[df_episodes['timestamps'] == j].copy()
            df_median = df_median.append(
                df_timestamps[['happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
                               'confused']].median(), ignore_index=True)
            df_median.at[len(df_median) - 1, 'episode'] = i
            df_median.at[len(df_median) - 1, 'timestamps'] = j

    df_median = df_median[['timestamps', 'episode', 'happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised',
                           'calm', 'confused']].sort_values(by=['timestamps'])
    df_median = df_median.reset_index(drop=True)

    return df_median


def calculate_max_timestamp(path):
    df = pd.read_csv(path)
    df_max = pd.DataFrame()

    for i in set(df['episode'].to_list()):
        df_episodes = df.loc[df['episode'] == i].copy()
        for j in sorted(set(df_episodes['timestamps'].to_list())):
            df_timestamps = df_episodes.loc[df_episodes['timestamps'] == j].copy()
            df_max = df_max.append(
                df_timestamps[['happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
                               'confused']].max(), ignore_index=True)
            df_max.at[len(df_max) - 1, 'episode'] = i
            df_max.at[len(df_max) - 1, 'timestamps'] = j

    df_max = df_max[['timestamps', 'episode', 'happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised',
                     'calm', 'confused']].sort_values(by=['timestamps'])
    df_max = df_max.reset_index(drop=True)

    return df_max


def calculate_max_episode(path):
    df = pd.read_csv(path)
    df_max = pd.DataFrame()
    for i in set(df['episode'].to_list()):
        df_episodes = df.loc[df['episode'] == i].copy().reset_index(drop=True)
        df_max = df_max.append(
            df_episodes[['happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
                         'confused']].max(), ignore_index=True)
        df_max.at[len(df_max) - 1, 'episode'] = i
        df_max.at[len(df_max) - 1, 'timestamps'] = df_episodes.at[0, 'timestamps']

    df_max = df_max[
        ['timestamps', 'episode', 'happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
         'confused']].sort_values(by=['timestamps'])
    df_max = df_max.reset_index(drop=True)

    return df_max


def calculate_median_episode(path):
    df = pd.read_csv(path)
    df_median = pd.DataFrame()
    for i in set(df['episode'].to_list()):
        df_episodes = df.loc[df['episode'] == i].copy().reset_index(drop=True)
        df_median = df_median.append(
            df_episodes[['happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
                         'confused']].median(), ignore_index=True)
        df_median.at[len(df_median) - 1, 'episode'] = i
        df_median.at[len(df_median) - 1, 'timestamps'] = df_episodes.at[0, 'timestamps']

    df_median = df_median[
        ['timestamps', 'episode', 'happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
         'confused']].sort_values(by=['timestamps'])
    df_median = df_median.reset_index(drop=True)

    return df_median


def resp_max_episode(path):
    df = pd.read_csv(path)
    resp_list = []
    for i in set(df['user_id'].to_list()):
        df_max = pd.DataFrame()
        df_by_user = df.loc[df['user_id'] == i].copy()
        for j in set(df_by_user['episode'].to_list()):
            df_episodes = df_by_user.loc[df_by_user['episode'] == j].copy().reset_index(drop=True)
            df_max = df_max.append(
                df_episodes[['happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
                             'confused']].max(), ignore_index=True)
            df_max.at[len(df_max) - 1, 'episode'] = j
            df_max.at[len(df_max) - 1, 'user_id'] = i
            df_max.at[len(df_max) - 1, 'timestamps'] = df_episodes.at[0, 'timestamps']
        else:
            df_max = df_max[
                ['user_id', 'timestamps', 'episode', 'happy', 'angry', 'fear', 'disgusted', 'sad', 'surprised', 'calm',
                 'confused']].sort_values(by=['timestamps'])
            df_max = df_max.reset_index(drop=True)
            resp_list.append(df_max)

    return resp_list


def write_to_excel(df, writer, sheet_name, startrow=0, startcol=0):
    workbook = writer.book
    sheet_names = workbook.sheetnames
    if 'Sheet' in sheet_names:
        workbook.remove(workbook.worksheets[0])
        worksheet = workbook.create_sheet(sheet_name)
    elif sheet_name not in workbook.sheetnames:
        worksheet = workbook.create_sheet(sheet_name)
    else:
        worksheet = workbook[sheet_name]

    writer.sheets[sheet_name] = worksheet
    df.to_excel(writer, index=False, sheet_name=sheet_name, startrow=startrow, startcol=startcol)

    if 'timestamps' in sheet_name:
        create_scatter(df, workbook, sheet_name)
    elif sheet_name == 'max_episode':
        area_max(df, workbook, sheet_name)
    else:
        create_line(df, workbook, sheet_name, startcol=startcol)


def create_excel(path_to_csv, path_to_excel):
    df_median = calculate_median_timestamp(path_to_csv)
    df_max = calculate_max_timestamp(path_to_csv)
    df_median_episode = calculate_median_episode(path_to_csv)
    df_max_episode = calculate_max_episode(path_to_csv)
    # print(df_median)
    # print(df_max)
    # print(df_median_episode)
    # print(df_max_episode)

    writer = pd.ExcelWriter(path_to_excel, engine='openpyxl')

    write_to_excel(df_median, writer, 'median_timestamps')
    write_to_excel(df_max, writer, 'max_timestamps')
    write_to_excel(df_median_episode, writer, 'median_episode')
    write_to_excel(df_max_episode, writer, 'max_episode')
    startrow = 0
    startcol = 0
    for i in resp_max_episode(path_to_csv):
        write_to_excel(i, writer, 'max_by_resp', startrow=startrow, startcol=startcol)
        startcol += i.shape[1] + 1

    writer.save()


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.options.display.max_rows = None
    pd.set_option('display.width', 300)

    path_to_csv = 'D:/YandexDisk/PYTHON/Amazon/jsons/FINAL.csv'
    path_to_excel = 'D:/YandexDisk/PYTHON/Amazon/jsons/FINAL.xlsx'

    create_excel(path_to_csv, path_to_excel)
