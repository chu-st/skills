# What's new

## 0.4.0 — полный цикл и работа с разногласиями

- **Два независимых выбора:** две/три модели и короткий/полный цикл. Старые
  профили сохраняют короткий цикл, пока пользователь не выберет другой.
- **Полный цикл исследования:** независимые ответы, взаимная критика, авторские
  доработки, разбор существенных разногласий, общий проект, независимая проверка
  одной версии и проверенный итог. Для готового материала — ревью, исправление
  назначенным автором и заключительная проверка.
- **Разногласия превращаются в проверку или явный выбор.** Модели формулируют
  конкурирующие позиции, условия пересмотра и различающую проверку; для планов
  ищут варианты по целям пользователя. Третья помогает проверять и улучшать
  варианты, не получает решающего голоса. Число обменов ограничено.
- **Обычные формулировки:** «прогони», «исследуй», «сделай работу двумя/тремя
  моделями». Сравнение моделей как продуктов само по себе не вызывает прогон.
  «Полный» не означает «три», а разовый запрос не меняет постоянные настройки.
- **Настройка через диалог:** показать состав, поменять роли местами, сохранить
  предпочтения или проверить доступ. Агент работает с файлом сам и показывает
  понятную сводку ролей, способов доступа и реальных наблюдений.
- **Безопасное изменение профиля:** необязательный помощник получил
  `update --from-file` с проверкой и резервной копией, а `plan` — `--cycle`.
  Чтение старых профилей ничего не переписывает. Явное обновление проекта не
  затрагивает личный профиль, если файла проекта ещё нет.
- **Явный выбор модели:** доступный вариант Pro передаётся в выбранный способ
  запуска явно. Если сервис не сообщает имя ответившей модели, оно остаётся
  непроверенным; успешный ответ и подтверждённая идентичность различаются.

Метод не обещает прироста точности от дополнительных раундов. Проверки и
ограничения описаны в [отчёте выпуска](docs/validation.md).
Процедура доработана в реальном обмене Codex, Claude Fable и ответами через
Antigravity с явно выбранным Gemini Pro. Локально проходят 50 автоматических
тестов; ограничения подтверждения моделей указаны в отчёте.

**English:** Participant count and cycle depth are independent. Full investigation
adds mutual critique, author revisions, bounded disagreement resolution, a common
draft and independent closing checks. Existing artifacts use reviews and a
designated author's revision. Conversational routing and setup preserve temporary
choices, product selections and old profiles. The helper supports explicit backed-up
updates and cycle overrides. Model selection remains distinct from identity evidence.

## 0.3.1 — исправления после ревью Claude Fable

- **Текущий агент как оркестратор:** `plan --host-file` принимает сведения о текущем
  приложении и модели, когда оркестратор не задан. Сохранённая или явно выбранная
  роль не подменяется; помощник не угадывает модель.
- **Проектный профиль создаётся в указанном проекте.** `init --project` больше не
  перенаправляется переменной `CHUST_REVIEW_CONFIG`. Приоритеты чтения прежние.
- **Уточнён протокол:** агент может передавать материалы выбранному оркестратору и
  хранить ответы, не становясь дополнительным участником анализа. Проверка выбора
  моделей явно отделена от проверки их фактической идентичности при запуске.
- **Понятнее ошибка неизвестной схемы.** Новый номер версии распознаётся до проверки
  набора полей.

Изменения основаны на реальном ревью модели, которую провайдер сообщил как
`claude-fable-5-1`. Два существенных замечания воспроизведены. Добавлены пять тестов,
всего — 42. Объём ревью и ограничения — в [отчёте](docs/validation.md).

**English:** A real Claude Fable review exposed two reproducible gaps. The plan
helper now accepts a known current host for an unspecified orchestrator, without
replacing selected roles. Explicit project creation now outranks the environment
profile selector; read precedence is unchanged. Relay responsibilities, runtime
identity checks, and future-schema diagnostics are clearer. Five regression tests
were added. The model reviewed the original four core files, not the patched
release; it did not run tests. No live three-model experiment is claimed.

## 0.3.0

### По-русски

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

### English

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
