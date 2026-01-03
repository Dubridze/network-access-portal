# Быстрое исправление (Quick Fix)

## Ошибка
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "idx_created_at" already exists
```

## Одна команда для исправления:

```bash
# 1. Перестартуйте и очистите
cd network-access-portal
docker-compose down -v
git pull origin main
docker-compose up -d
```

**Выбрано:** то есть удаляется вся база и персональные данные!

## Не хотите терять данные?

Прочтите [BUGFIX_DUPLICATE_INDEXES.md](./BUGFIX_DUPLICATE_INDEXES.md) → «Способ 2»
