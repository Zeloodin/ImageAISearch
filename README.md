# Документация к коду

## Введение

Приложение, реализованное в данном коде, предназначено для поиска изображений с использованием текстовых запросов и изображений в качестве входных данных. Оно использует библиотеку CLIP для извлечения векторных представлений изображений и текстов, что позволяет находить схожие изображения на основе введенных пользователем критериев. Этот код реализует графический интерфейс пользователя (GUI) с помощью PySimpleGUI и использует асинхронные вызовы для повышения отзывчивости приложения.

## Структура кода

### Импортируемые библиотеки 

Код начинается с импорта необходимых библиотек. Вот список основных импортируемых библиотек:

- **os**: для работы с файловой системой.
- **shutil**: для высокоуровневых операций с файлами.
- **pathlib**: для удобной работы с путями.
- **PySimpleGUI**: для создания GUI.
- **torch**: библиотека для работы с нейронными сетями.
- **clip**: модуль для работы с моделями CLIP.
- **re**: для работы с регулярными выражениями.
- **time**: для работы с временем и ожиданиями.
- **keyboard**: для обработки горячих клавиш.
- **asyncio**: для асинхронного выполнения задач.
- **core**: пользовательская библиотека, которая содержит дополнительные функции и классы для работы с изображениями.


## Глобальные переменные в `variables.py`

- `PKL_FILE_PATH`: Путь к файлу для сохранения/загрузки данных в формате Pickle.
- `JSON_FILE_PATH`: Путь к файлу для сохранения/загрузки данных в формате JSON.
- `TEMP_VAL`: Временный список для хранения значений.
- `EMPTY_LIST`: Пустой список.
- `IMG_SUP_EXTS`: Поддерживаемые расширения изображений.


### Объявление класса `Main_gui_image_search`

#### Основной класс

Класс `Main_gui_image_search` отвечает за создание основного графического интерфейса приложения.

##### Конструктор `__init__`

- Инициализирует элементы интерфейса и устанавливает начальные значения.
- Загружает список изображений и векторные представления из JSON- и PKL-файлов.
- Устанавливает обработчики горячих клавиш для завершения работы приложения.
- Создает основные элементы интерфейса и запускает поток для обновления информации о количестве изображений.

##### Методы

1. **update_counts**: обновляет счетчик изображений, отображаемых в GUI.
2. **_build_search_frame**: строит элементы поиска текста и изображений.
3. **_build_folder_multiline_list_frame**: строит элементы для выбора папок.
4. **_build_make_folder_list_frame**: создает элементы для начала сборки изображений и отображает счетчики.
5. **_build_cleanup_images_find_frame**: создает элементы для управления временными файлами.
6. **read_event**: считывает события из элементов интерфейса.
7. **close**: закрывает окно приложения.
8. **process_event**: обрабатывает различные события интерфейса (нажатия кнопок, изменения и т.д.).

### Объявление класса `Generate_clip_features`

#### Основной класс для обработки изображений

Класс `Generate_clip_features` отвечает за загрузку изображений, извлечение их векторных представлений и выполнение поиска на основе CLIP.

##### Конструктор `__init__`

- Инициализирует переменные для хранения путей к файлам и настроек обработки изображений.
- Создает экземпляр `Folder_make_list` для работы с папками изображений.

##### Методы

1. **folder_make_list**: добавляет папки для поиска изображений.
2. **find_image_list**: находит изображения в указанных папках и сохраняет их в списке.
3. **create_clip_image_features**: создает векторные представления для изображений, используя модель CLIP.
4. **get_features**: извлекает векторные представления для одного изображения.
5. **searcher_clip**: выполняет поиск изображений по тексту или изображению путем поиска похожих векторных представлений.

### Дополнительные классы и функции

- **Folder_make_list**: класс, который управляет списками папок для поиска изображений и их фильтрацией.
- **filter_str_list**: функция, фильтрующая строки для работы с массивами.
- **isdir_makefolder**: проверяет, существует ли папка, и создает ее, если нет.
- **mini_translator**: переводит текст с использованием Google Translator.
-  

## Настройка параметров приложения

1. **Пути к файлам**:
    - **К пути JSON и PKL файлов**: Значения по умолчанию для этих файлов определены в переменных `JSON_FILE_PATH` и `PKL_FILE_PATH` (можете изменить их в начале кода, чтобы указать свои пути).
    - Эти файлы используются для хранения списка изображений и их векторных представлений соответственно.
    - Для изменения пути к этим файлам откройте секцию кода, где эти переменные объявлены и присвойте им новые значения.

2. **Форматы изображений**:
    - Поддерживаемые форматы изображений определяются в переменной `IMG_FILE_TYPES` и включают такие форматы, как `.png`, `.jpg`, `.jpeg`, `.gif`, и т.д.
    - Вы можете изменить или добавить новые форматы, отредактировав массив `IMG_FILE_TYPES`. Убедитесь, что форматы совместимы с используемыми библиотеками.

3. **Параметры поиска**:
    - В интерфейсе пользователя есть опции для ввода количества изображений, которые необходимо вернуть в результатах поиска:
        - Поле **"Показать"** позволяет указать количество найденных изображений. Значение должно быть целым числом, по умолчанию — 10.
        - Пользователь может изменить это значение на любое желаемое количество.

4. **Параметры фильтрации**:
    - В интерфейсе есть чекбокс **"Автоматически удалять найденные изображения"**, который определяет, стоит ли очищать результаты поиска после каждой новой операции поиска.
    - Если чекбокс активен, временные результаты будут очищены.

5. **Пути к папкам**:
    - Для сбора изображений пользователю необходимо указать пути к папкам.
    - Для добавления положительных папок (папок, в которых нужно искать изображения), используйте кнопку **"Выбрать папку"** под **"Список папок"**.
    - Для добавления негативных папок (которые не нужно обрабатывать) используйте кнопку **"Выбрать папку"** под **"Негативный список папок"**.


## Подробные инструкции по использованию различных функций GUI

1. **Ввод текстового запроса**:
    - Выберите вкладку *"Текст"*
    - В поле ввода *"Введите описание текста"* вы можете ввести текстовый запрос для поиска изображений.
    - После ввода текста нажмите кнопку **"Поиск по описанию"**, чтобы инициировать поиск по базе данных.

2. **Поиск изображения**:
    - Выберите вкладку *"Картинки"*
    - В поле ввода *"Введите путь к картинке"* можно ввести путь к изображению для поиска или использовать кнопку **"Выбрать картинку"** для выбора изображения через диалоговое окно.
    - Чтобы выполнить поиск по выбранному изображению, нажмите кнопку **"Поиск по картинке"**.

3. **Добавление папок**:
    - Для добавления положительных и негативных папок:
        - Выберите папку с изображениями, нажав на соответствующий элемент, и папка будет добавлена в соответствующее многострочное поле.
    - Если хотите добавить несколько папок, повторите процесс для каждой папки.

4. **Сканирование папок**:
    - Нажмите кнопку **"Сканировать"** для начала процесса сбора изображений из указанных положительных папок.
    - В процессе сбора данные о количестве найденных изображений будут отображаться в соответствующих полях.

5. **Поиск результатов**:
    - После завершения поиска вы можете видеть количество найденных изображений и общее количество изображений в базе данных.
    - Для просмотра результатов откройте результаты через интерфейс, кликнув по нужной кнопке (например, **"Показать результат"**).

6. **Обучение модели**:
    - Для начала обучения модели, используйте кнопку **"Обучить"**. Приложение начнет процесс обучения на основании собранных изображений.
    - Прогресс обучения будет отображаться в интерфейсе.

7. **Правый клик**:
    - В многострочных списках (например, списках папок) можно использовать правый клик для доступа к дополнительным командам, таким как вырезать, копировать и вставить, а также удалять выделенные строки.

Эти инструкции должны помочь пользователю правильно настроить параметры приложения и эффективно использовать функции интерфейса для поиска изображений.

# Проблемы и улучшения

## Известные проблемы и недостатки

1. **Производительность**
   - При обработке большой базы изображений время отклика приложения может увеличиваться, особенно если используются изображения высокого разрешения.
   - Решение: оптимизация обработки изображений (например, уменьшение разрешения перед извлечением признаков).

2. **Память**
   - Приложение может потреблять значительное количество оперативной памяти при загрузке большого числа изображений и векторных представлений в память.
   - Решение: реализация ленивой загрузки изображений и оптимизация использования памяти с учётом кеширования.

3. **Проблемы с путями к файлам**
   - На некоторых системах могут возникать проблемы с относительными путями, особенно в Windows.
   - Решение: добавить функцию для автоматического преобразования путей и валидации существования файлов.

4. **Обработка исключений**
   - В коде недостаточно обработки исключений, что может привести к аварийному завершению программы при возникновении ошибок (например, неверные пути или недоступность файлов).
   - Решение: улучшение обработки ошибок и информирование пользователя о проблемах с удобным интерфейсом для последующих действий.

5. **Модульность**
   - Текущий код может быть трудным для поддержки из-за его структуры и недостаточной модульности.
   - Решение: рефакторинг кода с целью повышения модульности и упрощения тестирования.

## Возможные планы по улучшению

1. **Оптимизация производительности**
   - Реализовать параллельную обработку изображений, чтобы использовать многоядерные процессоры для повышения скорости.
   - Добавить использование графических процессоров (GPU) для ускорения извлечения признаков с использованием библиотеки PyTorch.

2. **Расширение функциональности**
   - Добавить возможность поиска по метаданным изображений (например, по тегам или описаниям).
   - Реализовать функциональность по добавлению и управлению пользовательскими тегами для изображений.

3. **Интерфейс пользователя**
   - Улучшение дизайна интерфейса для более интуитивного взаимодействия с пользователем.
   - Добавить возможность настройки темы и стиля приложения.
   - Включить интерактивные визуализации результатов поиска для улучшения работы с данными.

4. **Поддержка других форматов и методов обработки**
   - Расширить поддержку дополнительных форматов изображений (например, TIFF).
   - Интеграция с другими архитектурами нейронных сетей для извлечения признаков (например, ResNet, EfficientNet).

5. **Документация и тестирование**
   - Написание более подробной документации по коду с примерами использования и настройками.
   - Разработка юнит-тестов для ключевых функций приложения с целью повышения надежности и предотвращения регрессий.

6. **Улучшение обработки ошибок**
   - Реализация более детальной и пользовательской обработки ошибок с предоставлением четких инструкций о том, как их устранить.
   - Включение логирования ошибок для дальнейшего анализа и устранения неполадок.

Эти проблемы и планы по улучшению могут помочь в развитии и оптимизации приложения, улучшая его производительность, удобство использования и функциональность в будущем.

## Заключение

Этот код представляет собой мощное приложение для поиска изображений на основе текста и изображений. Он использует несколько внешних библиотек и предоставляет пользователю интуитивный интерфейс для выполнения запросов. Код охватывает множество аспектов: от обработки изображений до асинхронного выполнения задач, что делает его полезным инструментом для поиска и обработки изображений.























