# What's new — 0.3.0

## По-русски

**Один скилл для двух- и трёхмодельной проверки.** Имя `dual-model-review`
сохранено: переустанавливать его под новым именем не нужно.

- **Три настраиваемые роли:** оркестратор ведёт работу и собирает итог; вторая
  модель участвует в обычной проверке; третья добавляется в трёхмодельном режиме.
  Пользователь сам выбирает поставщиков, приложения и модели.
- **Режим настройки внутри скилла.** Достаточно попросить «настрой мои модели».
  Предпочтения сохраняются отдельно от пакета и переживают обновления. Необязательный
  `configure.py` создаёт профиль, проверяет его и показывает состав участников.
- **Два участника по умолчанию.** Наличие третьей в настройках само по себе её не
  запускает. Можно сохранить три как обычный режим или менять число в каждом запросе.
- **Предсказуемые приоритеты.** Разовый запрос важнее сохранённых ролей; явный файл
  важнее переменной окружения, проектного и личного профиля. Выбранные профили не
  смешиваются. Изменение роли не наследует модель от предыдущего поставщика.
- **Независимое участие третьей.** Она получает исходное задание до чужих ответов.
  Если подключена позже для разбора готового спора, это явно обозначается как ревью.
  Решения принимаются по проверяемым основаниям, без голосования большинства.
- **Честный учёт неполного запуска.** При недоступной модели сохраняются полученные
  ответы, но три запрошенных участника не превращаются молча в двух. Успешный
  вызов, проверка имени модели и качество результата учитываются отдельно.
- **Gemini и другие модели:** доступный инструмент выбранного приложения, явно
  настроенный универсальный CLI-адаптер или ручной перенос между чатами. Встроенного
  Gemini-адаптера и автоматического подключения аккаунтов этот выпуск не добавляет.
- **Совместимость:** прежние команды `peer.py`, квитанции и двухмодельные запросы
  сохранены. Обновлены задания без установки, инструкция и описание плагина.

Пример личной конфигурации: **Claude Fable → ChatGPT → Gemini**. Этот порядок
не навязывается другим пользователям и не зашит в публичные настройки.

Проверки и их ограничения описаны в [отчёте о валидации](docs/validation.md).
Инструкции: [настройка](docs/install.md), [формат профиля](skills/dual-model-review/references/configuration.md).

## English

The existing `dual-model-review` skill now supports two or three real participants:
a configurable orchestrator, regular second model, and optional third. No provider
is mandatory. Setup is a mode of the same skill; preferences live outside the
installation. The optional standard-library `configure.py` helper initializes,
validates, and resolves profiles without calling models.

Two remains the fallback count. Task choices override saved preferences; profile
files are selected by explicit path, environment, project, then user scope without
implicit merging. Replacing a role replaces its whole record. Explicit same-provider
choices are allowed for distinct models; duplicate underlying models do not count.

Third peers receive a neutral first brief. Late informed reviews are labelled as
such; evidence, not majority voting, resolves disagreements. Missing access or
unverified identities leave the requested roster incomplete while preserving useful
partial results. Products and roles are never silently substituted.

Gemini and other providers work through available tools, an explicitly configured
generic CLI adapter, or manual handoff. There is no bundled native Gemini adapter
or account provisioning. Existing invocation names, `peer.py` commands, and receipt
formats remain compatible. See [validation](docs/validation.md) for tested scope.
