# Network Access Portal

Портал для управления заявками на открытие сетевых доступов

## ⚠️ Важно: Исправление ошибки базы данных

Если вы получили ошибку при старте приложения:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateTable) relation "idx_created_at" already exists
```

**Этот баг был исправлен!** Читайте [BUGFIX_DUPLICATE_INDEXES.md](./BUGFIX_DUPLICATE_INDEXES.md) для подробных инструкций по исправлению.

## Функционал

- Аутентификация через Keycloak (OAuth2/OIDC)
- Ролевая модель: Администратор, Согласующий, Пользователь
- Управление заявками (CRUD)
- Шаги согласования: На рассмотрении → Одобрено/Отклонено
- Поддержка протоколов, IP адресов и портов
- Комфортный поиск по имени, номеру заявки, IP
- Модерный дизайн с Material-UI
- Аудит действий пользователей
- Кастомизация веб-интерфейса
- Docker контейнеры

## Технологии

### Бэкэнд
- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Keycloak (OAuth2/OIDC)
- Pydantic
- python-jose (JWT)
- python-multipart

### Фронтенд
- React 18
- TypeScript
- Material-UI v5
- Axios
- React Router v6
- React Query
- Keycloak JS

## Директория

```
network-access-portal/
├── backend/              # Python бэкэнд
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── crud.py
│   │   ├── utils.py
│   │   ├── audit.py
│   │   ├── routes/
│   │   │   ├── requests.py
│   │   │   ├── users.py
│   │   │   ├── audit.py
│   │   │   ├── admin.py
│   │   │   ├── config.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
├── frontend/             # React фронтенд
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── theme/
│   │   ├── App.tsx
│   │   ├── index.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
├── postgres-init/        # SQL скрипты инициализации БД
│   ├── 01-init.sql
│   ├── 02-fix-duplicate-indexes.sql
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── BUGFIX_DUPLICATE_INDEXES.md  # Документация по исправлению бага
```

## Поднятие работы

### Пререквизиты

- Docker и Docker Compose
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Keycloak 20+

### Конфигурация

1. Клонируйте репозиторий
```bash
git clone https://github.com/Dubridze/network-access-portal.git
cd network-access-portal
```

2. Настройте окружение (скопируйте .env.example в .env и адаптируйте параметры)
```bash
cp .env.example .env
```

3. Поднимите сервисы
```bash
docker-compose up -d
```

4. Посетите портал
```
http://localhost:3000
```

## API Документация

```
http://localhost:8000/docs
```

## Устранение неполадок

### Ошибка при старте: DuplicateTable
См. [BUGFIX_DUPLICATE_INDEXES.md](./BUGFIX_DUPLICATE_INDEXES.md) для решения проблемы с индексами БД.

### Проблемы с Keycloak
- Убедитесь, что Keycloak запущен и доступен
- Проверьте конфигурацию в `.env` файле
- Убедитесь, что realm и client настроены правильно

### Проблемы с подключением к БД
```bash
# Проверьте статус контейнера
docker-compose ps

# Посмотрите логи
docker-compose logs db
```

## Лицензия

MIT
