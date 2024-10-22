import pytest
from unittest.mock import MagicMock
from zipfile import ZipFile
from main import execute_command  # Импортируйте вашу функцию execute_command

# Фикстура для создания zip-файла с виртуальной файловой системой
@pytest.fixture
def setup_fs(tmp_path):
    fs_path = tmp_path / "test_fs.zip"
    with ZipFile(fs_path, 'w') as myzip:
        myzip.writestr('example_dir/', '')  # Папка example_dir
        myzip.writestr('empty_dir/', '')     # Пустая папка empty_dir
        myzip.writestr('example_dir/hello.txt', 'Hello, world!')  # Файл внутри example_dir
    return str(fs_path)

# Фикстура для мокирования output_text
@pytest.fixture
def mock_output_text(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('main.output_text', mock)  # Подменяем output_text в вашем модуле
    return mock

# Тесты для команды ls
def test_ls_root(setup_fs, mock_output_text):
    global current_dir
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('ls')
        # Проверяем, что output_text.insert был вызван
        mock_output_text.insert.assert_called_once()
        output_content = mock_output_text.insert.call_args[0][1]
        assert 'example_dir' in output_content
        assert 'empty_dir' in output_content
        assert 'hello.txt' in output_content

def test_ls_empty_directory(setup_fs, mock_output_text):
    global current_dir
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('ls')
        output_content = mock_output_text.insert.call_args[0][1]
        assert 'hello.txt' in output_content  # Проверяем, что файл hello.txt присутствует

# Тесты для команды cd
def test_cd_to_existing_directory(setup_fs, mock_output_text):
    global current_dir
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('cd example_dir')
        assert current_dir == 'example_dir/'  # Проверяем, что текущее местоположение изменилось
        mock_output_text.insert.assert_called_once_with('end', '')

def test_cd_to_nonexistent_directory(setup_fs, mock_output_text):
    global current_dir
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('cd nonexistent_dir')
        assert current_dir == ''  # Проверяем, что текущее местоположение не изменилось
        output_content = mock_output_text.insert.call_args[0][1]
        assert "No such directory" in output_content

# Тесты для команды rmdir
def test_rmdir_empty_directory(setup_fs, mock_output_text):
    global current_dir
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('rmdir empty_dir')
        output_content = mock_output_text.insert.call_args[0][1]
        assert "Directory removed" in output_content  # Проверяем, что директория удалена

def test_rmdir_non_empty_directory(setup_fs, mock_output_text):
    global current_dir
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        myzip.writestr('example_dir/test_file.txt', 'This is a test file.')  # Создаем файл внутри example_dir
        execute_command('rmdir example_dir')
        output_content = mock_output_text.insert.call_args[0][1]
        assert "Directory not empty" in output_content  # Проверяем, что директория не удалена

# Тесты для команды exit
def test_exit_command(monkeypatch):
    mock_exit = MagicMock()
    monkeypatch.setattr('sys.exit', mock_exit)
    execute_command('exit')
    mock_exit.assert_called_once()  # Проверяем, что exit вызван один раз

def test_exit_no_message(monkeypatch):
    mock_exit = MagicMock()
    monkeypatch.setattr('sys.exit', mock_exit)
    output = execute_command('exit')
    assert output == ''  # Проверяем, что нет сообщения при выходе

# Тесты для команды clear
def test_clear_command(mock_output_text):
    execute_command('clear')
    mock_output_text.insert.assert_called_once_with('end', '')  # Проверяем, что метод insert был вызван

def test_clear_no_output(mock_output_text):
    execute_command('clear')
    mock_output_text.insert.assert_called_once()  # Проверяем, что insert вызван хотя бы один раз
