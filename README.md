# MagicWorld — Hidden Object: уровень 1

Проект Godot 4.4.1 для Android. Полная папка проекта для сборки находится в архиве `gamegro_tropical_cove_level1 (1).zip`.

## Сборка Android
GitHub Actions workflow **Build Android APK** распаковывает загруженный архив, устанавливает Godot 4.4.1 и Android SDK, импортирует проект и экспортирует debug APK. APK публикуется как артефакт `MagicWorld-Android-debug`.

Workflow запускается при push в `main` и `feature/**`, а также вручную через Actions.

## Проверка
Успешная сборка подтверждается только после завершения всех шагов workflow и появления APK-артефакта.