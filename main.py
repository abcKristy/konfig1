import os
import csv
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime


# Функция для чтения конфигурационного файла и извлечения параметров
def read_config(config_path):
    tree = ET.parse(config_path)
    root = tree.getroot()
    computer_name = root.find('user_name').text
    fs_path = root.find('fs_path').text
    log_path = root.find('log_path').text
    return computer_name, fs_path, log_path


# Функция для записи в лог-файл
def write_log(log_path, command, output):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, 'a', newline='') as log_file:
        writer = csv.writer(log_file)
        writer.writerow([timestamp, command, output.strip()])


# Функция выполнения команды
def execute_command(command):
    global current_dir

    if command == 'clear':
        output_text.delete('1.0', tk.END)
        return ""

    output = ""

    if command == 'ls':
        output = ""
        if current_dir:
            for name in myzip.namelist():
                if name.startswith(current_dir + '/') and '/' not in name[len(current_dir):].strip('/'):
                    relative_name = name[len(current_dir):].strip('/')
                    output += relative_name + "\n"
        else:
            output = "\n".join(myzip.namelist()) + "\n"


    elif command.startswith('cd '):
        path = command.split(maxsplit=1)[1]
        for part in path.split('/'):
            if part == '...':
                current_dir = '/'.join(current_dir.strip('/').split('/')[:-1]) or ''
            else:
                new_path = (current_dir + '/' + part).strip('/')
                if new_path in myzip.namelist() or any(name.startswith(new_path + '/') for name in myzip.namelist()):
                    current_dir = new_path
                else:
                    output = f"No such directory: {part}\n"
                    break  # Stop processing on first invalid directory

    elif command == 'exit':
        root.destroy()
        return ""

    elif command == 'date':
        now = datetime.now()
        output = f"Now is: {now}\n";

    elif command.startswith('rmdir '):
        # Удаление папки
        path = command.split(maxsplit=1)[1]
        full_path = (current_dir + path).strip('/') + '/'

        # Проверяем, существует ли директория
        if full_path not in myzip.namelist():
            output = f"No such directory: {path}\n"
        else:
            # Проверяем, есть ли содержимое в директории
            has_content = any(item.startswith(full_path) and item != full_path for item in myzip.namelist())

            if has_content:
                output = f"Directory not empty: {path}\n"
            else:
                # Удаляем директорию, создавая новый zip без неё
                temp_zip_path = "temp_fs.zip"
                with ZipFile(temp_zip_path, 'w') as temp_zip:
                    for item in myzip.namelist():
                        if not item.startswith(full_path):
                            temp_zip.writestr(item, myzip.read(item))

                # Убедитесь, что myzip закрыт перед заменой
                myzip.close()  # Закрываем оригинальный zip перед заменой

                os.replace(temp_zip_path, fs_path)
                output = f"Directory {path} removed\n"

    elif command.startswith('mkdir '):
        new_directory = command.split(maxsplit=1)[1]
        output = f"new_directory is {new_directory}\n";
        myzip.mkdir(new_directory);

    else:
        output = f"Unknown command: {command}\n"

    output_text.insert(tk.END, f"{output}")
    return output


# Функция для обработки ввода команды
def on_command_enter(event=None):
    command = command_entry.get()
    command_entry.delete(0, tk.END)
    output_text.insert(tk.END, f"{computer_name}$ {command}\n")
    output = execute_command(command)
    write_log(log_path, command, output)


# Чтение конфигурационного файла
config_path = "config.xml"
computer_name, fs_path, log_path = read_config(config_path)

# Открытие виртуальной файловой системы
with ZipFile(fs_path, 'a') as myzip:
    current_dir = ""
    # Настройка GUI с использованием tkinter
    root = tk.Tk()
    root.title("Shell Emulator")

    command_frame = tk.Frame(root)
    command_frame.pack(padx=10, pady=5)
    user_label = tk.Label(command_frame, text=f"{computer_name}$ ", anchor='w')
    user_label.pack(side=tk.LEFT)

    command_entry = tk.Entry(command_frame, width=90)
    command_entry.pack(side=tk.LEFT, padx=(5, 0))
    command_entry.bind('<Return>', on_command_enter)

    output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=30)
    output_text.pack(padx=10, pady=10)

    root.protocol("WM_DELETE_WINDOW", lambda: execute_command("exit"))
    # Запуск главного цикла приложения
    root.mainloop()
