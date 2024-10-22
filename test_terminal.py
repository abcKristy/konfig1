import pytest
from unittest.mock import MagicMock, patch
from zipfile import ZipFile
from main import execute_command  # Импортируйте вашу функцию execute_command

# Фикстура для создания zip-файла с виртуальной файловой системой
@pytest.fixture
def setup_fs(tmp_path):
    fs_path = tmp_path / "test_fs.zip"
    with ZipFile(fs_path, 'w') as myzip:
        myzip.writestr('example_dir/', '')
        myzip.writestr('example_dir/hello.txt', 'Hello, world!')
        myzip.writestr('empty_dir/', '')
    return str(fs_path)

# Фикстура для мокирования output_text
@pytest.fixture
def mock_output_text(monkeypatch):
    mock = MagicMock()
    # Подменяем output_text в вашем модуле на мок-объект
    monkeypatch.setattr('main.output_text', mock)
    return mock

# Пример теста команды ls
def test_ls_root(setup_fs, mock_output_text):
    global current_dir, myzip
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('ls')
        # Проверяем, что output_text.insert был вызван хотя бы раз
        mock_output_text.insert.assert_called_once()
        # Проверяем, что 'example_dir' и 'empty_dir' были в выводе
        output_content = mock_output_text.insert.call_args[0][1]  # Получаем текст, который был передан в insert
        assert 'example_dir' in output_content
        assert 'empty_dir' in output_content

# Пример теста команды cd к существующей директории
def test_cd_to_existing_directory(setup_fs, mock_output_text):
    global current_dir, myzip
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('cd example_dir')
        # Проверяем, что текущее местоположение изменилось
        assert current_dir == 'example_dir/'
        # Проверяем, что не было сообщений об ошибке при переходе в директорию
        mock_output_text.insert.assert_called_once_with('end', '')

# Пример теста команды cd к несуществующей директории
def test_cd_to_nonexistent_directory(setup_fs, mock_output_text):
    global current_dir, myzip
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('cd nonexistent_dir')
        # Проверяем, что текущее местоположение не изменилось
        assert current_dir == ''
        # Проверяем, что был вызван вывод сообщения об ошибке
        output_content = mock_output_text.insert.call_args[0][1]
        assert "No such directory" in output_content

# Пример теста команды rmdir для удаления пустой директории
def test_rmdir_empty_directory(setup_fs, mock_output_text):
    global current_dir, myzip
    current_dir = ''
    with ZipFile(setup_fs, 'a') as myzip:
        execute_command('rmdir empty_dir')
        # Проверяем, что была попытка удалить директорию
        mock_output_text.insert.assert_called_once()
        output_content = mock_output_text.insert.call_args[0][1]
        assert "Directory removed" in output_content

# Пример теста команды exit
def test_exit_command(monkeypatch):
    # Здесь мы просто проверим, что команда exit вызывает системный выход
    mock_exit = MagicMock()
    monkeypatch.setattr('sys.exit', mock_exit)
    execute_command('exit')
    mock_exit.assert_called_once()

# Пример теста команды clear
def test_clear_command(mock_output_text):
    execute_command('clear')
    # Проверяем, что output_text.insert был вызван с соответствующим сообщением
    mock_output_text.insert.assert_called_once_with('end', '')
