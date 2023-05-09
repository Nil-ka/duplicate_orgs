# Сравнение строк (имен из ORGANIZ_CL)
# Nilka 06.05.2023
from thefuzz import fuzz 
from pathlib import Path
import re
import time

 
MATCH_CONST = 90



def clear_symbols(origin_name):  
    """ Очистка строки от символов  """
    regex = re.compile('[\{\}\<\>\+\[\]*\$\.\^\'\\\\"№#«»()?!@%:;=/-]')
    clear_name = re.sub(',',' ', origin_name)   # заменяем ',' на ' '
    clear_name = regex.sub('',clear_name)       # удаляем все небуквенные и нечисловые символы
    clear_name = " ".join(clear_name.split())   # удаляем лишние пробелы и табуляции
    return clear_name

def read_data(filename):    
    """ Считываем строки в database"""
    lines_readed = 0
    database = {} 
    # { НОМЕР_СТРОКИ: [
    # 0-ISN_NODE, 
    # 1-"CLASSIF_NAME", 
    # 2-"CLASSIF_NAME без спецсимволов", 
    # 3-ISN_NODE самого похожего имени организации, 
    # 4-самое похожее "CLASSIF_NAME" организации,
    # 5-СТЕПЕНЬ_ПОХОЖЕСТИ
    # ] }
    with open(filename, 'r') as f:
        for line in f:
            cols = line.split('|')
            origin_name = re.sub('\n','', cols[-1]) 
            origin_clear_name = clear_symbols(origin_name)
            database[lines_readed] = [int(cols[0]), origin_name, origin_clear_name, 0, '', 0] # Формируем запись
            lines_readed += 1
            if lines_readed%500 == 0:
                print(f'Импортировано {lines_readed} записей')
    print(f'Файл обработан, всего {lines_readed} записей')
    return database
    
     
def process_names(database, out_file):    
    print('Начата обработка записей')
    list_mathed_value = []
    names_count = len(database.keys())
    names_matched = 0
    for key, value in database.items():
        matched_key = 0
        matched_name = ''
        max_match_value = 0
        clear_name_origin = value[2]
        
        for i in range(key + 1, names_count):            
            clear_name_matching = database[i][2]
            match_value = fuzz.partial_token_sort_ratio(clear_name_origin, clear_name_matching)
            if max_match_value < match_value >= MATCH_CONST: # Получаем степень сходства сравнителем partial_token_set_ratio, если нашли более похожее - записываем
                matched_name = clear_name_matching
                max_match_value = match_value
                matched_key = i
        
        if max_match_value > 0:
            list_mathed_value.append(max_match_value)
            database[key][3] = database[matched_key][0]
            database[key][4] = matched_name
            database[key][5] = max_match_value
            print(f'ISN: {database[key][0]}; CLASSI_NAME: {database[key][1]}; MATCHED_ISN: {database[matched_key][0]}; MATCHED_NAME: {matched_name}; MATCH: {max_match_value}', file=out_file)
        names_matched += 1
        if names_matched%10 == 0:
                print(f'Сравнено {names_matched} слов, осталось {names_count-names_matched}, {int(100*names_matched/names_count)}%')
    print(f'Всего количество записей: {names_count}')
    print(f'Всего записей со схожестью {MATCH_CONST}: {len(list_mathed_value)}')
    print(f'Средняя схожесть: {sum(list_mathed_value)/len(list_mathed_value)}')

my_database = read_data('C:\Prog\Python\Low\Сравнение строк\In\expdata_2000.csv')
p = Path('C:\Prog\Python\Low\Сравнение строк\Out')
out_files_cnt = len(list(p.glob('out*.txt'))) + 1 
out_file = open(f'C:\Prog\Python\Low\Сравнение строк\Out\out_{out_files_cnt}.txt','w')
tic = time.perf_counter()
process_names(my_database,out_file)
toc = time.perf_counter()
out_file.close()
print(f'Время вычислений : {toc-tic}')





    

