<div align="center">
    <a href="https://www.mirea.ru">
      <img src="https://www.mirea.ru/upload/medialibrary/205/yly02h0ioocdeega8ir1kbsstul6q9ws/new_logo.png" width="96" alt="РТУ МИРЭА">
    </a>
    <h1>MindTale</h1>
    <p><i>РТУ МИРЭА, команда ЭФБО-04-22</i></p>
    <p>
        <a href="https://t.me/Papajunn" target="_blank">Матвей Вишняков</a> <b>&middot;</b>
        <a href="https://t.me/lekichbh" target="_blank">Алексей Щелкунов</a> <b>&middot;</b>
        <a href="https://t.me/n1ddy" target="_blank">Кирилл Трунин</a> <b>&middot;</b>
    </p>
</div>

# MindTale

## 1 Клонирование репозитория и настройка VSCode

Для начала требуется склонировать репозиторий и открыть его.

```bash
# Клонирование репозитория с использованием SSH ключа
git clone https://github.com/Tr0ubad0ur/mind-tale-repository.git

# Открытие проекта в VSCode
code mind-tale-repository
```

Теперь требуется установить рекомендуемые расширения VSCode из файла [`.vscode/extensions.json`] (при открытии проекта появится всплывающее окно).

Далее требуется сделать новую ветку, либо использовать существующую согласно GitFlow процессу работы.

## 2 Установка pre-commit хуков

> [!note] Глоссарий
> *pre-commit хуки* — это скрипты, которые автоматически запускаются перед коммитом и проверяют/исправляют код (линтеры, форматирование и т.п.), чтобы в репозиторий попадал только корректный код.

```bash
# Установка pre-commit хуков
uv run pre-commit install
```

## 3 Создание виртуального окружения

```bash
# Установка менеджера пакетов UV
curl -LsSf https://astral.sh/uv/install.sh | sh
# powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" на Windows
```

```bash
# Создание виртуальной среды
uv venv

# Активация виртуальной среды
. .venv/bin/activate
# .venv\Scripts\activate на Windows

# Установка pre-commit хуков
uv run pre-commit install

# Установка зависимостей из requirements.txt
uv pip install -r requirements.txt
```

## 4 Использовать Swagger UI для теста

```bash
# Запуск сервера
uvicorn api.api:app --reload
```

После тестов сгенерированное изображение сохраняется в вашу локальную папку проекта в VSCode
