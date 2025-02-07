import os
import re
import json

def extract_methods_with_comments(file_path, exclusion_phrases):
    methods = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Регулярное выражение для поиска комментариев и методов (функции или процедуры)
        pattern = re.compile(r'(?:^\/\/.*\n)+?(Функция|Процедура)\s+(\w+)\s*\((.*?)\)(?:\s*Экспорт)?\s*\n(.*?)(КонецФункции|КонецПроцедуры)', re.DOTALL | re.MULTILINE)
        
        matches = pattern.findall(content)
        for match in matches:
            method_type, method_name, params, code_block, end_keyword = match
            # Удаляем лишние пробелы и переносы строк из комментария и кода метода
            comment_lines = content.splitlines()
            start_index = content.find(match[0]) - 1
            while start_index >= 0 and comment_lines[start_index].strip().startswith('//'):
                start_index -= 1
            start_index += 1
            
            comments = []
            for i in range(start_index, content.find(match[0])):
                comments.append(comment_lines[i])
            
            comment = '\n'.join(comments).strip()
            code_block = code_block.strip()
            
            # Проверяем, содержит ли комментарий любую из фраз-исключений
            if not any(phrase in comment for phrase in exclusion_phrases):
                conversation = {
                    "from": "user",
                    "value": f"{method_type} {method_name}({params})\n{code_block}"
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