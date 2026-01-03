# Исправление ошибки DuplicateTable: relation "idx_created_at" already exists

## Описание проблемы

При запуске приложения возникает ошибка:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "idx_created_at" already exists
```

## Причина

В файле `backend/app/models.py` были определены индексы с одинаковыми именами в разных таблицах:

**До исправления:**
```python
# В таблице AccessRequest
Index('idx_created_at', 'created_at')
Index('idx_user_id', 'user_id')
Index('idx_status', 'status')
Index('idx_approver_id', 'approver_id')

# В таблице AuditLog
Index('idx_created_at', 'created_at')  # ❌ Конфликт!
Index('idx_user_id', 'user_id')        # ❌ Конфликт!
Index('idx_access_request_id', 'access_request_id')
Index('idx_action', 'action')

# В таблице Configuration
Index('idx_key', 'key')
```

SQLAlchemy создаёт индексы с использованием **глобального пространства имён** для всей базы данных. Когда несколько таблиц используют одинаковые имена индексов, происходит конфликт.

## Решение

### Было
```python
Index('idx_created_at', 'created_at')      # Неправильно
Index('idx_user_id', 'user_id')            # Неправильно
Index('idx_status', 'status')              # Неправильно
```

### Стало
```python
Index('idx_access_requests_created_at', 'created_at')      # ✅ Уникально
Index('idx_access_requests_user_id', 'user_id')            # ✅ Уникально
Index('idx_access_requests_status', 'status')              # ✅ Уникально
Index('idx_audit_logs_created_at', 'created_at')           # ✅ Уникально
Index('idx_audit_logs_user_id', 'user_id')                 # ✅ Уникально
Index('idx_users_keycloak_id', 'keycloak_id')              # ✅ Уникально
```

## Как это исправить

### Способ 1: Для новых установок

1. Обновите код из GitHub (исправление уже включено в `models.py`)
2. Убедитесь, что БД пуста или используйте чистую базу данных
3. Запустите приложение:

```bash
docker-compose up -d
```

### Способ 2: Для существующих установок с БД

#### Вариант A: Полная переинициализация (самый простой)

```bash
# Остановить контейнеры
docker-compose down

# Удалить volume с БД
docker volume rm network-access-portal_postgres_data

# Обновить код
git pull origin main

# Перезапустить
docker-compose up -d
```

#### Вариант B: Сохранить данные, исправить БД

```bash
# 1. Остановить приложение
docker-compose down

# 2. Подключиться к PostgreSQL
docker-compose up -d db  # Запустить только БД

# 3. Выполнить скрипт исправления
docker exec network-access-portal-db psql -U network_user -d network_db -f /docker-entrypoint-initdb.d/02-fix-duplicate-indexes.sql

# 4. Обновить код
git pull origin main

# 5. Запустить приложение
docker-compose up -d
```

#### Вариант C: Ручное исправление через psql

```bash
# Подключиться к базе данных
docker exec -it network-access-portal-db psql -U network_user -d network_db

# Выполнить команды в psql:
DROP INDEX IF EXISTS idx_created_at CASCADE;
DROP INDEX IF EXISTS idx_user_id CASCADE;
DROP INDEX IF EXISTS idx_status CASCADE;
DROP INDEX IF EXISTS idx_approver_id CASCADE;
DROP INDEX IF EXISTS idx_access_request_id CASCADE;
DROP INDEX IF EXISTS idx_action CASCADE;
DROP INDEX IF EXISTS idx_key CASCADE;

# Выход из psql
\q

# Перезапустить приложение
docker-compose restart backend
```

## Как избежать подобных ошибок

### Правила именования индексов в SQLAlchemy

1. **Всегда используйте уникальные имена индексов** - добавляйте префикс с названием таблицы
2. **Используйте соглашение об именовании:**
   ```python
   Index('idx_{table}_{column}', 'column')
   ```

3. **Пример правильного кода:**
   ```python
   class AccessRequest(Base):
       __tablename__ = "access_requests"
       __table_args__ = (
           Index('idx_access_requests_user_id', 'user_id'),
           Index('idx_access_requests_status', 'status'),
           Index('idx_access_requests_created_at', 'created_at'),
       )
   
   class AuditLog(Base):
       __tablename__ = "audit_logs"
       __table_args__ = (
           Index('idx_audit_logs_user_id', 'user_id'),      # ✅ Другое имя
           Index('idx_audit_logs_created_at', 'created_at'), # ✅ Другое имя
       )
   ```

## Что было изменено

### 1. `backend/app/models.py`
- Переименованы все индексы с уникальными префиксами таблиц
- Добавлены новые индексы для улучшения производительности поиска

### 2. `postgres-init/02-fix-duplicate-indexes.sql`
- Создан скрипт для удаления старых конфликтующих индексов
- Новые индексы будут созданы автоматически при запуске приложения

## Проверка исправления

### Проверить, что индексы созданы правильно:

```bash
# Подключиться к БД
docker exec -it network-access-portal-db psql -U network_user -d network_db

# Просмотреть все индексы
\d access_requests
\d audit_logs
\d users

# Или через SQL запрос
SELECT indexname FROM pg_indexes WHERE tablename IN ('access_requests', 'audit_logs', 'users', 'configurations') ORDER BY indexname;
```

Все индексы должны иметь уникальные имена с префиксами таблиц.

## Дополнительная информация

- **SQLAlchemy документация по индексам**: https://docs.sqlalchemy.org/en/20/core/indexes.html
- **PostgreSQL документация по индексам**: https://www.postgresql.org/docs/current/indexes.html
