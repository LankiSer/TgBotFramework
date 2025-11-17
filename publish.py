"""
Скрипт для автоматической публикации TgFramework на PyPI
"""

import subprocess
import sys
import os
import shutil

def run_command(cmd, check=True):
    """Выполнить команду"""
    print(f"Выполняется: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check)
    return result

def clean_build():
    """Очистить предыдущие сборки"""
    print("Очистка предыдущих сборок...")
    dirs_to_remove = ["build", "dist"]
    files_to_remove = ["*.egg-info"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Удалено: {dir_name}/")
    
    # Удаление egg-info
    for item in os.listdir("."):
        if item.endswith(".egg-info"):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"  Удалено: {item}/")

def build_package():
    """Собрать пакет"""
    print("\nСборка пакета...")
    try:
        run_command("python -m build")
        print("  ✓ Пакет собран успешно")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Ошибка при сборке: {e}")
        sys.exit(1)

def check_package():
    """Проверить пакет"""
    print("\nПроверка пакета...")
    try:
        run_command("python -m twine check dist/*")
        print("  ✓ Пакет проверен успешно")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Ошибка при проверке: {e}")
        sys.exit(1)

def upload_package(repository="pypi"):
    """Загрузить пакет на PyPI"""
    print(f"\nПубликация на {repository.upper()}...")
    
    if repository == "test":
        cmd = "python -m twine upload --repository testpypi dist/*"
        print("  URL: https://test.pypi.org/")
    else:
        cmd = "python -m twine upload dist/*"
        print("  URL: https://pypi.org/")
    
    print("\nВведите учетные данные:")
    print("  Username: __token__")
    print("  Password: ваш токен API (начинается с pypi-)")
    
    try:
        run_command(cmd)
        print(f"  ✓ Пакет загружен на {repository.upper()}")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Ошибка при загрузке: {e}")
        sys.exit(1)

def main():
    """Главная функция"""
    print("=" * 60)
    print("Публикация TgFramework на PyPI")
    print("=" * 60)
    
    # Определяем репозиторий
    repository = "pypi"
    if len(sys.argv) > 1:
        if sys.argv[1] in ["test", "testpypi"]:
            repository = "test"
        elif sys.argv[1] in ["pypi", "prod", "production"]:
            repository = "pypi"
        else:
            print(f"Неизвестный аргумент: {sys.argv[1]}")
            print("Использование: python publish.py [test|pypi]")
            sys.exit(1)
    
    # Проверка установленных инструментов
    print("\nПроверка инструментов...")
    try:
        import build
        import twine
        print("  ✓ build и twine установлены")
    except ImportError:
        print("  ✗ Необходимо установить build и twine:")
        print("    pip install --upgrade build twine")
        sys.exit(1)
    
    # Основные шаги
    clean_build()
    build_package()
    check_package()
    
    # Подтверждение перед загрузкой
    print("\n" + "=" * 60)
    response = input(f"Загрузить на {repository.upper()}? (y/n): ")
    if response.lower() != 'y':
        print("Отменено.")
        sys.exit(0)
    
    upload_package(repository)
    
    print("\n" + "=" * 60)
    print("✓ Готово!")
    print("=" * 60)
    
    if repository == "test":
        print("\nПроверьте установку:")
        print("  pip install --index-url https://test.pypi.org/simple/ tgframework-bot")
    else:
        print("\nПроверьте установку:")
        print("  pip install tgframework-bot")
        print("\nПроверьте страницу:")
        print("  https://pypi.org/project/tgframework-bot/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nОтменено пользователем.")
        sys.exit(1)

