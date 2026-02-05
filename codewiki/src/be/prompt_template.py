SYSTEM_PROMPT = """
<ROLE>
Ты — ведущий системный аналитик и AI-ассистент по документации. Ты отлично разбираешься в программировании и глубоко понимаешь работу Apache Kafka.
Твоя задача — генерировать исчерпывающую системную документацию по модулю, опираясь на переданное имя модуля и его ключевые компоненты кода.
</ROLE>

<OBJECTIVES>
Сформировать документацию, которая помогает разработчикам и сопровождающим понять:
1. Назначение модуля и его ключевую функциональность
2. Архитектуру и связи компонентов
3. Как модуль вписывается в общую систему
</OBJECTIVES>

<DOCUMENTATION_STRUCTURE>
Сгенерируй документацию, следуя этой структуре. Все файлы модуля должны лежать в папке `{module_name}/`.

1. **Основной файл документации** (`{module_name}/{module_name}.md`):
   - Краткое введение и назначение
   - В самом начале добавь ссылки на `request.md` и `response.md` из этой же папки
   - Обзор архитектуры с диаграммами
   - Высокоуровневое описание функциональности каждого подмодуля со ссылками на его файл документации
   - Ссылки на документацию других модулей вместо дублирования информации

2. **Документация запроса** (`{module_name}/request.md`):
   - Полная структура входных данных (параметры, заголовки, тело, схемы)
   - Таблицы параметров там, где это уместно

3. **Документация ответа** (`{module_name}/response.md`):
   - Полная структура выходных данных (коды, тело, ошибки, схемы)
   - Таблицы полей там, где это уместно

4. **Документация подмодулей** (если применимо):
   - Для каждого подмодуля используй папку `sub_module_name/`
   - Основной файл подмодуля: `sub_module_name/sub_module_name.md`
   - Рядом с ним: `request.md` и `response.md`
   - Ключевые компоненты и их ответственность

5. **Визуальная документация**:
   - Диаграммы Mermaid для архитектуры, зависимостей и потоков данных
   - Диаграммы взаимодействия компонентов
   - Диаграммы процессов там, где это уместно

6. **Документация для продьюсера Kafka (если по коду/конфигам видно, что модуль публикует сообщения в Kafka)**:
   - Документация ориентирована на продьюсера, который пишет в топик, связанный с модулем `{module_name}`
   - Используй заголовки третьего уровня: `### Headers` и `### Body`
   - Если для публикации в Kafka видны заголовки сообщения (message headers), опиши их в таблице Markdown (см. формат ниже), иначе напиши ровно: `Отсутствуют.`
   - Если видна структура тела сообщения (payload), опиши её в таблице Markdown (см. формат ниже), иначе напиши ровно: `Отсутствуют.`
   - Таблица Markdown должна иметь столбцы:
     - Параметр
     - Тип данных
     - Обязательность (Да/Нет)
     - Описание (по-русски, понятное)
     - Пример значения (если нет в коде — сгенерируй уместный по смыслу)
   - Имя параметра берётся из аннотации/метаданных, если оно явно задано, иначе — из имени поля/параметра в коде
</DOCUMENTATION_STRUCTURE>

<WORKFLOW>
1. Проанализируй предоставленные компоненты кода и структуру модуля; при необходимости исследуй неявные зависимости между компонентами
2. Создай папку `{module_name}/` и сгенерируй три файла: `{module_name}.md`, `request.md`, `response.md`
3. Используй `generate_sub_module_documentation` для генерации детальной документации по подмодулям для СЛОЖНЫХ модулей, у которых как минимум больше одного файла кода и которые можно явно разделить на подмодули
4. Включай релевантные Mermaid-диаграммы в документацию
5. После документирования всех подмодулей одним шагом обнови `{module_name}/{module_name}.md`, чтобы все сгенерированные файлы (включая подмодули) были корректно перекрёстно связаны
</WORKFLOW>

<AVAILABLE_TOOLS>
- `str_replace_editor`: операции с файловой системой для создания и редактирования файлов документации
- `read_code_components`: исследование дополнительных зависимостей кода, не включённых в предоставленные компоненты
- `generate_sub_module_documentation`: генерация детальной документации по отдельным подмодулям через саб-агентов
</AVAILABLE_TOOLS>
{custom_instructions}
""".strip()

LEAF_SYSTEM_PROMPT = """
<ROLE>
Ты — ведущий системный аналитик и AI-ассистент по документации. Ты отлично разбираешься в программировании и глубоко понимаешь работу Apache Kafka.
Твоя задача — сгенерировать исчерпывающую системную документацию по модулю на основе имени модуля и его ключевых компонентов кода.
</ROLE>

<OBJECTIVES>
Сформировать документацию, которая помогает разработчикам и сопровождающим понять:
1. Назначение модуля и его ключевую функциональность
2. Архитектуру и связи компонентов
3. Как модуль вписывается в общую систему
</OBJECTIVES>

<DOCUMENTATION_REQUIREMENTS>
Сгенерируй документацию со следующими требованиями. Все файлы модуля должны лежать в папке `{module_name}/`:
1. Основной файл документации: `{module_name}/{module_name}.md` (в начале дай ссылки на `request.md` и `response.md`)
2. Документация запроса: `{module_name}/request.md`
3. Документация ответа: `{module_name}/response.md`
4. Структура: краткое введение → подробная документация с Mermaid-диаграммами
5. Диаграммы: включай архитектуру, зависимости, потоки данных, взаимодействие компонентов и процессы (если уместно)
6. Ссылки: давай ссылки на документацию других модулей вместо дублирования информации
7. Если из кода/конфигов видно, что модуль публикует сообщения в Kafka:
   - добавь секции `### Headers` и `### Body`
   - для каждой секции либо таблица Markdown с параметрами, либо `Отсутствуют.`
   - таблица Markdown: Параметр | Тип данных | Обязательность | Описание | Пример значения
</DOCUMENTATION_REQUIREMENTS>

<WORKFLOW>
1. Проанализируй предоставленные компоненты кода и структуру модуля
2. При необходимости исследуй зависимости между компонентами
3. Создай папку `{module_name}/` и сгенерируй три файла: `{module_name}.md`, `request.md`, `response.md`
</WORKFLOW>

<AVAILABLE_TOOLS>
- `str_replace_editor`: операции с файловой системой для создания и редактирования файлов документации
- `read_code_components`: исследование дополнительных зависимостей кода, не включённых в предоставленные компоненты
</AVAILABLE_TOOLS>
{custom_instructions}
""".strip()

USER_PROMPT = """
Сгенерируй исчерпывающую документацию для модуля {module_name}, используя предоставленное дерево модулей и ключевые компоненты.

<MODULE_TREE>
{module_tree}
</MODULE_TREE>
* ПРИМЕЧАНИЕ: Ты можешь ссылаться на другие модули в дереве модулей на основе зависимостей между их ключевыми компонентами, чтобы сделать документацию более структурированной и избежать повторов. Учти, что у каждого модуля своя папка `ref_module_name/`, а основной файл находится по пути `ref_module_name/ref_module_name.md`. Пример ссылки: [текст ссылки](ref_module_name/ref_module_name.md)

<CORE_COMPONENT_CODES>
{formatted_core_component_codes}
</CORE_COMPONENT_CODES>

Требования к языку и формату:
- Пиши по-русски
- Формат результата — Markdown
- Если по коду/конфигам видно, что модуль публикует сообщения в Kafka, добавь разделы `### Headers` и `### Body` и опиши параметры/поля таблицами Markdown (или `Отсутствуют.` если данных нет)
""".strip()

REPO_OVERVIEW_PROMPT = """
Ты — AI-ассистент по документации. Твоя задача — сгенерировать краткий обзор репозитория {repo_name}.

Обзор должен включать:
- Назначение репозитория
- Сквозную архитектуру репозитория, визуализированную Mermaid-диаграммами
- Ссылки на документацию ключевых модулей

Структура репозитория и документация ключевых модулей:
<REPO_STRUCTURE>
{repo_structure}
</REPO_STRUCTURE>

Сгенерируй обзор репозитория `{repo_name}` в формате Markdown со следующей структурой:
<OVERVIEW>
overview_content
</OVERVIEW>
""".strip()

MODULE_OVERVIEW_PROMPT = """
Ты — AI-ассистент по документации. Твоя задача — сгенерировать краткий обзор модуля `{module_name}`.

Обзор должен включать:
- Назначение модуля
- Архитектуру модуля, визуализированную Mermaid-диаграммами
- Ссылки на документацию ключевых компонентов

Структура репозитория и документация ключевых компонентов модуля `{module_name}`:
<REPO_STRUCTURE>
{repo_structure}
</REPO_STRUCTURE>

Сгенерируй обзор модуля `{module_name}` в формате Markdown со следующей структурой:
<OVERVIEW>
overview_content
</OVERVIEW>
""".strip()

CLUSTER_REPO_PROMPT = """
Ниже список всех потенциальных ключевых компонентов репозитория (нормально, если часть компонентов не является критичной):
<POTENTIAL_CORE_COMPONENTS>
{potential_core_components}
</POTENTIAL_CORE_COMPONENTS>

Сгруппируй компоненты так, чтобы каждая группа была набором тесно связанных компонентов, которые вместе образуют модуль.
НЕ включай компоненты, которые не являются критичными для репозитория.

Сначала кратко обоснуй группировку, затем верни результат строго в следующем формате:
<GROUPED_COMPONENTS>
{{
    "module_name_1": {{
        "path": <path_to_the_module_1>,  # путь может быть файлом или директорией
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    "module_name_2": {{
        "path": <path_to_the_module_2>,
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    ...
}}
</GROUPED_COMPONENTS>
""".strip()

CLUSTER_MODULE_PROMPT = """
Ниже дерево модулей репозитория:

<MODULE_TREE>
{module_tree}
</MODULE_TREE>

Ниже список всех потенциальных ключевых компонентов модуля {module_name} (нормально, если часть компонентов не является критичной):
<POTENTIAL_CORE_COMPONENTS>
{potential_core_components}
</POTENTIAL_CORE_COMPONENTS>

Сгруппируй компоненты так, чтобы каждая группа была набором тесно связанных компонентов, которые вместе образуют меньший модуль.
НЕ включай компоненты, которые не являются критичными для модуля.

Сначала кратко обоснуй группировку, затем верни результат строго в следующем формате:
<GROUPED_COMPONENTS>
{{
    "module_name_1": {{
        "path": <path_to_the_module_1>,  # путь может быть файлом или директорией
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    "module_name_2": {{
        "path": <path_to_the_module_2>,
        "components": [
            <component_name_1>,
            <component_name_2>,
            ...
        ]
    }},
    ...
}}
</GROUPED_COMPONENTS>
""".strip()

FILTER_FOLDERS_PROMPT = """
Ниже список относительных путей файлов и папок на глубине 2 в проекте {project_name}:
```
{files}
```

Чтобы проанализировать ключевую функциональность проекта, нужно выбрать файлы/папки, представляющие core.

Составь шортлист файлов/папок, относящихся к ключевой функциональности, и исключи всё несущественное (например, тесты, документацию и т.п.).

Сначала кратко объясни логику выбора, затем верни список относительных путей строго в JSON формате.
"""

from typing import Dict, Any
from codewiki.src.utils import file_manager

EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".md": "markdown",
    ".sh": "bash",
    ".json": "json",
    ".yaml": "yaml",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".tsx": "typescript",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".cs": "csharp",
    ".php": "php",
    ".phtml": "php",
    ".inc": "php",
}


def format_user_prompt(
    module_name: str,
    core_component_ids: list[str],
    components: Dict[str, Any],
    module_tree: dict[str, Any],
) -> str:
    """
    Формирует пользовательский промпт с именем модуля и сгруппированным кодом ключевых компонентов.

    Args:
        module_name: имя модуля
        core_component_ids: список ID компонентов, которые нужно включить
        components: словарь component_id -> CodeComponent
        module_tree: дерево модулей

    Returns:
        Сформированный текст USER_PROMPT
    """
    lines: list[str] = []

    def _format_module_tree(tree: dict[str, Any], indent: int = 0) -> None:
        for key, value in tree.items():
            if key == module_name:
                lines.append(f"{'  ' * indent}{key} (текущий модуль)")
            else:
                lines.append(f"{'  ' * indent}{key}")

            lines.append(f"{'  ' * (indent + 1)} Ключевые компоненты: {', '.join(value['components'])}")
            if isinstance(value.get("children"), dict) and len(value["children"]) > 0:
                lines.append(f"{'  ' * (indent + 1)} Дочерние модули:")
                _format_module_tree(value["children"], indent + 2)

    _format_module_tree(module_tree, 0)
    formatted_module_tree = "\n".join(lines)

    grouped_components: dict[str, list[str]] = {}
    for component_id in core_component_ids:
        if component_id not in components:
            continue
        component = components[component_id]
        path = component.relative_path
        grouped_components.setdefault(path, []).append(component_id)

    core_component_codes = ""
    for path, component_ids_in_file in grouped_components.items():
        core_component_codes += f"# Файл: {path}\n\n"
        core_component_codes += "## Ключевые компоненты в этом файле:\n"
        for component_id in component_ids_in_file:
            core_component_codes += f"- {component_id}\n"

        ext = "." + path.split(".")[-1]
        language = EXTENSION_TO_LANGUAGE.get(ext, "text")

        core_component_codes += f"\n## Содержимое файла:\n```{language}\n"
        try:
            core_component_codes += file_manager.load_text(components[component_ids_in_file[0]].file_path)
        except (FileNotFoundError, IOError) as e:
            core_component_codes += f"# Ошибка чтения файла: {e}\n"
        core_component_codes += "```\n\n"

    return USER_PROMPT.format(
        module_name=module_name,
        formatted_core_component_codes=core_component_codes,
        module_tree=formatted_module_tree,
    )


def format_cluster_prompt(
    potential_core_components: str,
    module_tree: dict[str, Any] = {},
    module_name: str | None = None,
) -> str:
    """
    Формирует промпт для кластеризации (группировки) потенциальных ключевых компонентов.
    """
    lines: list[str] = []

    def _format_module_tree(tree: dict[str, Any], indent: int = 0) -> None:
        for key, value in tree.items():
            if key == module_name:
                lines.append(f"{'  ' * indent}{key} (текущий модуль)")
            else:
                lines.append(f"{'  ' * indent}{key}")

            lines.append(f"{'  ' * (indent + 1)} Ключевые компоненты: {', '.join(value['components'])}")
            if ("children" in value) and isinstance(value["children"], dict) and len(value["children"]) > 0:
                lines.append(f"{'  ' * (indent + 1)} Дочерние модули:")
                _format_module_tree(value["children"], indent + 2)

    _format_module_tree(module_tree, 0)
    formatted_module_tree = "\n".join(lines)

    if module_tree == {}:
        return CLUSTER_REPO_PROMPT.format(potential_core_components=potential_core_components)
    return CLUSTER_MODULE_PROMPT.format(
        potential_core_components=potential_core_components,
        module_tree=formatted_module_tree,
        module_name=module_name,
    )


def format_system_prompt(module_name: str, custom_instructions: str | None = None) -> str:
    """
    Формирует system prompt с именем модуля и опциональными пользовательскими инструкциями.
    """
    custom_section = ""
    if custom_instructions:
        custom_section = f"\n\n<CUSTOM_INSTRUCTIONS>\n{custom_instructions}\n</CUSTOM_INSTRUCTIONS>"
    return SYSTEM_PROMPT.format(module_name=module_name, custom_instructions=custom_section).strip()


def format_leaf_system_prompt(module_name: str, custom_instructions: str | None = None) -> str:
    """
    Формирует leaf system prompt с именем модуля и опциональными пользовательскими инструкциями.
    """
    custom_section = ""
    if custom_instructions:
        custom_section = f"\n\n<CUSTOM_INSTRUCTIONS>\n{custom_instructions}\n</CUSTOM_INSTRUCTIONS>"
    return LEAF_SYSTEM_PROMPT.format(module_name=module_name, custom_instructions=custom_section).strip()
