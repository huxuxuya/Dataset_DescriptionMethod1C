import os
import re
import json

def extract_methods_with_comments(file_path, exclusion_phrases):
    methods = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

        pattern_debug = re.compile(r'((?:^\/\/.*\n)+)(Функция|Процедура)',  re.MULTILINE)
       # pattern_debug = re.compile(r'((^\/\/.*\n)+?)(?=Функция|Процедура)', re.MULTILINE)
        matches_debug = pattern_debug.findall(content)
        for match_debug in matches_debug:
            debug_comment, method_type = match_debug
            print(debug_comment)
            print('---------------')
            print(method_type)  # Это будет "Функция" или "Процедура"

        # Регулярное выражение для поиска комментариев и методов (функции или процедуры)
        pattern = re.compile(r'((?:^\/\/.*\n)+)(Функция|Процедура)\s+(.*?)\n(.*[\s\S]*?)(КонецФункции|КонецПроцедуры)', re.MULTILINE)
        
        matches = pattern.findall(content)
        for match in matches:
            comment, method_type, method_name, code_block, end_keyword = match
            # Удаляем лишние пробелы и переносы строк из комментария и кода метода
            comment = comment.strip()
            code_block = code_block.strip()
            
            # Проверяем, содержит ли комментарий любую из фраз-исключений
            if not any(phrase in comment for phrase in exclusion_phrases):
                conversation = {
                    "from": "user",
                    "value": f"{method_type} {method_name}\n{code_block}"
                }
                
                assistant_comment = {
                    "from": "assistant",
                    "value": comment
                }
                
                methods.append({
                    "id": f"identity_{len(methods)}",
                    "conversations": [conversation, assistant_comment]
                })
    
    return methods

def process_directory(directory, exclusion_phrases):
    all_methods = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.bsl'):
                file_path = os.path.join(root, file)
                methods = extract_methods_with_comments(file_path, exclusion_phrases)
                all_methods.extend(methods)
    
    return all_methods

def main():
    directory = 'C:\\Projects\\1С src bases\\ssl_3_1\\src\\cf\\CommonModules\\АвтономнаяРаботаСлужебный\\'  # Укажите путь к каталогу
    exclusion_phrases = [
        "Для внутреннего использования",
        "Не использовать напрямую",
        "Внутренняя функция"
        # Добавьте другие фразы-исключения по необходимости
    ]
    
    methods = process_directory(directory, exclusion_phrases)
    
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(methods, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()