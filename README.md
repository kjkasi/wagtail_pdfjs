# Wagtail + PDF.js: презентации с PDF-аннотациями

Минимальный рабочий demo-проект: редактор загружает PDF в Wagtail, а публичная HTML-страница отображает текущий слайд через Mozilla PDF.js и выводит текст PDF-аннотаций рядом обычным HTML. Встроенный PDF viewer браузера и `<iframe>` не используются.

## Стек

- Python 3.12+
- Django 5.2.17 LTS
- Wagtail 7.3.4 LTS
- `pdfjs-dist` 6.3.289
- SQLite, vanilla JavaScript, HTML/CSS

## Быстрый запуск

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
npm run build
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install
npm run build
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте:

- Wagtail Admin: <http://127.0.0.1:8000/admin/>
- сайт: <http://127.0.0.1:8000/>

`npm run build` копирует `pdf.mjs` и `pdf.worker.mjs` из установленного `pdfjs-dist` в `presentation/static/pdfjs/`. Собранные файлы также включены в репозиторий, поэтому для запуска уже скачанной версии demo npm не обязателен. Он нужен для обновления/воспроизводимой пересборки PDF.js.

## Создание презентации

1. Войдите в `/admin/`.
2. Откройте **Pages → Home** и выберите **Add child page**.
3. Выберите **Presentation page**.
4. Задайте заголовок.
5. В поле **Pdf** выберите существующий документ либо загрузите PDF.
6. Нажмите **Publish**.
7. Откройте опубликованную страницу через кнопку просмотра или по её URL.

Разрешена загрузка только документов с расширением PDF (`WAGTAILDOCS_EXTENSIONS` в `config/settings/base.py`). Ограничение demo — 10 МБ.

## Как устроен проект

```text
config/                         Django/Wagtail settings, URLs, base template
home/                           корневая HomePage
presentation/
├── models.py                   PresentationPage и связь с wagtaildocs.Document
├── migrations/0001_initial.py
├── templates/presentation/
│   └── presentation_page.html HTML viewer, canvas, sidebar, controls
├── static/presentation/
│   ├── presentation.css        responsive layout 70/30 и mobile layout
│   └── presentation.js         PDF.js render, navigation, annotations
├── static/pdfjs/
│   ├── pdf.mjs
│   └── pdf.worker.mjs
└── tests.py
scripts/copy-pdfjs.mjs          локальная сборка/copy step
```

### Передача PDF URL

Шаблон передаёт URL через экранируемый Django HTML-атрибут:

```html
<div id="pdf-viewer" data-pdf-url="{{ page.pdf.url }}">
```

JavaScript получает его через `viewer.dataset.pdfUrl`. URL не конкатенируется в исполняемый JavaScript.

### PDF.js и аннотации

`presentation/static/presentation/presentation.js`:

1. динамически импортирует локальный `pdf.mjs`;
2. задаёт локальный `GlobalWorkerOptions.workerSrc`;
3. загружает документ через `getDocument()`;
4. получает страницу через `pdf.getPage(pageNumber)`;
5. параллельно выполняет `page.render(...)` и `page.getAnnotations({ intent: "display" })`;
6. извлекает текст функцией `getAnnotationText(annotation)`.

Основное актуальное поле PDF.js 6 — `annotation.contentsObj.str`. Есть безопасные fallback-проверки для строковых `contents` и `content`, чтобы код не зависел от единственного представления данных. Показываются все аннотации с непустым текстовым содержимым, включая Text/Sticky Note и FreeText, если PDF.js возвращает `contents`.

Текст аннотаций считается недоверенным. Он добавляется только через `textContent`, никогда через `innerHTML`. Поэтому содержимое PDF не может внедрить HTML/JavaScript. Переносы строк сохраняются CSS-правилом `white-space: pre-wrap`.

Отрисовка учитывает `devicePixelRatio`; CSS-размер canvas остаётся размером контейнера, а физический bitmap увеличивается для HiDPI. При смене страницы и resize используется generation token. Результат старого асинхронного render не заменит более новый слайд или его комментарии.

## Проверка кириллицы

В workspace нет тестового PDF. Создайте его в PowerPoint с экспортом annotations либо в Okular:

1. Откройте PDF в Okular.
2. Нажмите `F6`.
3. Выберите **Висящая заметка / Pop-up Note**.
4. Добавьте текст:

   ```text
   adasd
   asd
   пиф
   ```

5. Сохраните PDF, загрузите его через Wagtail Admin и опубликуйте `PresentationPage`.
6. Проверьте Chrome/Chromium и Firefox: слайд должен быть нарисован в canvas, а три строки — показаны в sidebar.

Если на слайде несколько текстовых аннотаций, выводятся все. Если их нет, sidebar показывает: **«Для этого слайда нет комментариев.»**

## Проверки

```bash
python manage.py migrate
python manage.py check
python manage.py test
npm run build
```

Тесты проверяют связь `PresentationPage` с документом, успешный frontend render, наличие URL документа в безопасном data-атрибуте и отсутствие iframe.

## Обновление PDF.js

1. Обновите фиксированную версию в `package.json`, например `npm install --save-dev pdfjs-dist@VERSION`.
2. Выполните `npm run build`.
3. Проверьте release notes PDF.js, особенно структуру объектов annotation и требования worker.
4. Выполните Django tests и ручную проверку PDF с кириллицей.
5. Зафиксируйте `package.json`, `package-lock.json`, `pdf.mjs` и `pdf.worker.mjs`.

## Ограничения demo

- Нет серверной индексации аннотаций и PyMuPDF; annotations читаются только браузером.
- Нет поиска, zoom, thumbnails и annotation layer — это намеренно простой fit-to-width viewer.
- Автотест браузера с реальным PowerPoint/Okular PDF не включён; требуется описанная ручная проверка.
- Для production нужно настроить production storage/web server для media/static, HTTPS, allowed hosts и ограничения доступа к документам.
