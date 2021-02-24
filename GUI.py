from datetime import datetime
import PySimpleGUI as sg
import os
import sqlite3 as sl

from create_excel import create_excel
from test_analyse import unite_func, parse_youtube
import subprocess


def runCommand(cmd, timeout=None):
    """ run shell command
	@param cmd: command to execute
	@param timeout: timeout for command execution
	@return: (return code from command, command output)
	"""
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''

    out, err = p.communicate()
    p.wait(timeout)

    return (out, err)


def Launcher():
    sg.ChangeLookAndFeel('LightGreen')

    layout = [
        [sg.T('Папка с json файлами'), sg.In(key='dir', size=(40, 1)), sg.FolderBrowse()],
        [sg.T('URL видео'), sg.In(key='url', size=(40, 1)), ],
        [sg.T('Фильтр значений'), sg.In(default_text=10, key='filter', size=(40, 1)), ],
        # [sg.Frame('LOG', layout=[[sg.Output(size=(65, 15))]])],
        [sg.ReadFormButton('Начать', bind_return_key=True),
         sg.SimpleButton('Quit', button_color=('white', 'firebrick3')), ]]

    window = sg.Window('JSON to CSV and DB GUI',
                       auto_size_text=False,
                       auto_size_buttons=False,
                       default_element_size=(20, 1,),
                       # text_justification='right',
                       )

    window.Layout(layout)

    # ---===--- Loop taking in user input --- #
    while True:
        try:
            (button, values) = window.Read()
            # print(button)
            # print(values)
            if button in ('Quit', None):
                break  # exit button clicked

            source_dir = values['dir']  # запись введенного начения директории в переменную
            files = os.listdir(source_dir)  # список всех файлов в директории
            json_files = [file for file in files if '.json' in file]  # список всех файлов с расширением .json
            url = values['url']  # запись введенного начения адреса видео в переменную
            filter = float(values['filter'])  # запись введенного значения фильтрации в переменную
            export_to_csv = f'{source_dir}/FINAL.csv'  # файл для сохранения в формате .csv
            export_to_db = f'{source_dir}/FINAL.db'  # файл для сохранения в формате.db
            path_to_excel = f'{source_dir}/FINAL.xlsx' # файл для сохранения в формате .xlsx


            if button == 'Начать':
                if not source_dir:
                    sg.PopupError('Укажите папку с json файлами')
                elif not files:
                    sg.PopupError('Папку пуста')
                elif not json_files:
                    sg.PopupError('В папке нет json файлов')
                elif not url:
                    sg.PopupError('Укажите url')
                elif not filter:
                    sg.PopupError('Укажите фильтр значений')
                else:
                    try:  # файлы создаются при каждом запуске скрипта, а предидущие версии удаляются
                        os.remove(export_to_csv)
                        os.remove(export_to_db)
                    except FileNotFoundError:
                        pass
                    print(f'Папка с json файлами: {source_dir}')
                    print(f'Адрес видео: {url}')
                    print(f'Параметр для фильтрации: {filter}')
                    print(f'{"_" * 200}')
                    print(f'Обнаружено {len(json_files)} json файлов')
                    episodes = parse_youtube(url)
                    print(f'Получены эпизоды с временными метками: {episodes}')
                    print(f'{"_" * 200}')

                    for file in json_files:  # для каждого json файла в папке
                        try:
                            print(f'\nФайл на обработке: {file}')
                            df = unite_func(source_dir, file, episodes, filter)  # получить dataframe
                            print('Файл успешно обработан')
                            print(f'Запись в csv: {export_to_csv}')
                            df.to_csv(export_to_csv, index=False, header=not os.path.exists(export_to_csv),
                                      mode='a' if os.path.exists(export_to_csv) else 'a')
                            print(f'Запись в DB: {export_to_db}')
                            con = sl.connect(export_to_db)
                            df.to_sql('frame_of_emotions', con, if_exists='append', index=False)
                            con.commit()
                            con.close()
                        except Exception as inner_error:
                            print(f'Произошла ошибка:\n{inner_error}')
                    else:
                        print(f'\nВсе файлы были успешно обработаны!')
                        print(f'\nСоздание Excel и построение графиков.')
                        create_excel(export_to_csv, path_to_excel)
                        print(f'DONE!\nПроверьте папку {source_dir}')
                        sg.PopupOK(f'    DONE!    ')
        except Exception as error:
            sg.PopupError(f'Произошла ошибка:\n{error}')


if __name__ == '__main__':
    trial_period = 7  # через сколько дней программа перестанет работать
    initial_date = '20.02.2021'
    date_start = datetime.strptime(initial_date, "%d.%m.%Y")
    date_stop = datetime.now()
    difference = (date_stop - date_start).days
    # print(difference)
    if difference > trial_period:
        sg.PopupError('Пробный период закончился!')
    else:
        Launcher()
