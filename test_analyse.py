import re
import json
import pandas as pd
import requests
from statistics import median


def create_df(dir, file_name):
    print()
    final_list = []
    with open(f'{dir}/{file_name}', 'r') as file:
        string = file.read()  # читаем строку
        new_string = re.sub("\s*\n\s*", ' ', string.strip())  # удаляем лишние символы
        my_dic = json.loads(new_string)  # создаем словарь
        needed_list = my_dic['Faces']  # получаем лист со словарями, где ключи "Timestamp" и "Face"
        for i in needed_list:  # проходим по каждому элементу списка
            template = {'user_id': file_name, 'timestamps': '', 'episode': '', 'happy': '', 'angry': '', 'fear': '',
                        'disgusted': '', 'sad': '', 'surprised': '', 'calm': ''}  # шаблон строки для будущего DataFrame
            for j in i:  # прохом по ключам каждого словаря. В каждом словаре ключей всего два: "Timestamp" и "Face"
                if j == "Timestamp":
                    time_stamp = 0.5 * round(
                        i[j] / 1000 / 0.5)  # округляем значение Timestamp до длижайшего, крантного 0,5
                    if time_stamp in [time['timestamps'] for time in
                                      final_list]:  # True, если timestamp уже в final_list
                        break
                    else:
                        template['timestamps'] = time_stamp  # добавление timestamp в template
                else:
                    face_dict = i[j]
                    for x in face_dict:  # проходы по словарю Face
                        if x == 'Emotions':  # находим список с эмоциями
                            emotions_list = face_dict[x]  # список с эмоциями. Элементы списка – словарь с эмоциями
                            for y in emotions_list:  # проход по ключам слоавря эмоций.Ключи Type и Confidence
                                template[y['Type'].lower()] = y['Confidence']  # добавление в template
                            else:
                                final_list.append(template)  # добавление в final_list
    df = pd.DataFrame(final_list)
    return df


def parse_youtube(url):
    video = requests.get(url).text  # получение инфтомации со страницы в текстовом виде
    episodes = {}
    match = re.search(r'shortDescription":"Timecodes:\\n(.+?)","isCrawlable', video).group(1)  # поиск информации
    timecodes = str(match).split('\\n')  # получение списка
    for i in timecodes:  # цикл для получения словаря, где ключи – таймкоды, а значения – названия эпизодов
        i_list = i.replace(" ", "").split('-')
        time_code = i_list[0]
        episode = i_list[1]
        time_code_list = time_code.split(':')
        seconds = int(time_code_list[0]) * 60 + int(time_code_list[1])
        episodes[seconds] = episode
    else:
        return episodes


def insert_episodes(df, episodes):  # вставка эпизодов в предварительный dataframe
    for row in range(len(df)):
        timestamp = float(df.at[row, 'timestamps'])
        for time_code in episodes:
            episode = episodes[time_code]
            if float(time_code) <= timestamp:
                df.at[row, 'episode'] = episode
    else:
        return df


def baseline_correction(df):  # коррекция по baseline
    for column in list(df.columns):
        if column not in ('user_id', 'timestamps', 'episode'):
            median_list = []
            for row in range(len(df)):  # в каждой строке в dataframe
                timestamp = float(df.at[row, 'timestamps'])  # считается timestamp
                if timestamp <= 10:  # первые 10 секунд
                    median_list.append(df.at[row, column])  # значения эмоций записываются в список
                else:  # после того, как счетчик цикла перескочит 10 секунд
                    median_emotion = median(median_list)  # вычисляется медиана
                    df.at[row, column] = df.at[row, column] - median_emotion  # и вычитается из значения эмоции
                    if df.at[row, column] < 0:  # если после корректировки по baseline значение эмоции < 0
                        df.at[row, column] = 0  # то присваивается 0
    else:
        return df


def filter_emotions(df, filter_emotion):  # фильтрация по эмоциям
    start_episodes = set(df['episode'].to_list())
    rows_for_delete = []
    for row in range(len(df)):
        for column in list(df.columns):
            if column not in ('user_id', 'timestamps', 'episode'):
                if df.at[row, column] < filter_emotion:  # если все эмоции в timestamp < filter_emotion, то
                    continue
                else:
                    break
        else:
            rows_for_delete.append(row)  # timestamp помещается в список на удаление
    else:
        df.drop(rows_for_delete, inplace=True)  # удаление всех timestamp, где все эмоции < filter_emotion
        finish_episodes = set(df['episode'].to_list())
        if len(finish_episodes) == 0:
            print(f'ВНИМАНИЕ! После фильтрации DataFrame оказался пустой!')
        elif len(finish_episodes) == len(start_episodes):
            pass
        else:
            print(
                f'ВНИМАНИЕ! После фильтрации DataFrame эпизоды {start_episodes.symmetric_difference(finish_episodes)} были удалены!')
        return df


def unite_func(dir, file_name, episodes, filter_emotion, ):
    df = create_df(dir, file_name)
    # print(len(df), df)
    df = insert_episodes(df, episodes)
    # print(len(df), df)
    df = baseline_correction(df)
    # print(len(df), df)
    return filter_emotions(df, filter_emotion)


if __name__ == '__main__':
    pd.set_option('display.max_columns', None)
    pd.options.display.max_rows = None
    pd.set_option('display.width', 200)

    # file_name = 'jsons/2ec6dd23-7b28-4dbd-ac42-d107e053b894_LYRcCJ5KqRU.mp4.json'
    url = 'https://www.youtube.com/watch?v=LYRcCJ5KqRU&feature=youtu.be&ab_channel=AnnaLeoshko'
    filter_emotion = 10
    # df = unite_func('jsons', '49c81c8a-cc69-4afe-8917-5380bee22107_LYRcCJ5KqRU.mp4.json', url, filter_emotion)
    df = create_df('jsons', '2ec6dd23-7b28-4dbd-ac42-d107e053b894_LYRcCJ5KqRU.mp4.json')
    episodes = parse_youtube(url)
    df = insert_episodes(df, episodes)
    df = baseline_correction(df)
    print(df)
    df = filter_emotions(df, filter_emotion)
    print(df)
