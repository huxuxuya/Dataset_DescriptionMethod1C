import os
import re
import json

def extract_methods_with_comments(file_path, exclusion_phrases):
    methods = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
        # Регулярное выражение для поиска комментариев и методов (функции или процедуры)
        pattern = re.compile(
            r'(?:^\/\/[^\n]*\n)*'  # Комментарии перед функцией/процедурой
            r'(Функция|Процедура)\s+([^\s(]+)\s*\(([^)]*)\)\s*'  # Тип, имя и параметры
            r'([\s\S]*?)'  # Тело функции/процедуры
            r'(КонецФункции|КонецПроцедуры)',  # Конец функции/процедуры
            re.MULTILINE | re.DOTALL
        )
        
        matches = pattern.findall(content)
        for match in matches:
            method_type, method_name, params, code_block, end_keyword = match
            
            # Извлекаем комментарии перед функцией/процедурой
            comment_lines = content.splitlines()
            start_index = content.find(match[0]) - 1
            comments = []
            
            # Ищем комментарии выше функции/процедуры с проверкой индекса
            while start_index >= 0 and start_index < len(comment_lines) and comment_lines[start_index].strip().startswith('//'):
                comments.insert(0, comment_lines[start_index].strip())  # Добавляем комментарий в начало списка
                start_index -= 1
            
            comment = '\n'.join(comments).strip()
            code_block = code_block.strip()
            
            # Проверяем, содержит ли комментарий или тело функции/процедуры любую из фраз-исключений
            if any(phrase in comment or phrase in code_block for phrase in exclusion_phrases):
                print(f"Метод {method_type} {method_name}({params}) исключен из-за наличия фразы-исключения: {comment}")
                continue
            
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
                print(f"Обрабатывается файл: {file_path}")
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
    
    print(f"Найдено методов: {len(methods)}")
    
    with open('output.json', 'w', encoding='utf-8') as json_file:
        json.dump(methods, json_file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()