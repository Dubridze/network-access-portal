# Network Access Portal

Портал для управления заявками на открытие сетевых доступов

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
├── backend/              # Пытон бэкэнд
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
│   │   ├── migrations/
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
├── docker-compose.yml
├─┠─ .env.example
├── .gitignore
├── README.md
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

2. Настройте воружение (copy .env.example to .env и адаптируйте параметры)
```bash
cp .env.example .env
```

3. Подняте сервисы
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

## Лицензия

MIT
