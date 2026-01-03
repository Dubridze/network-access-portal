# Отладка проблемы: Пустая страница с надписью "Loading"

## 🔴 Проблема

После аутентификации в Keycloak пользователь видит пустую страницу с надписью **"Loading"**, которая никогда не исчезает.

## 🎯 Причины и решения

### 1. Keycloak не инициализирован в API Service ❌

**Проблема:** Метод `setKeycloakInstance()` никогда не вызывался, поэтому API запросы не содержали Bearer token.

**Решение:** ✅ **УЖЕ ИСПРАВЛЕНО**
- Обновлен `frontend/src/App.tsx` - теперь вызывает `setKeycloakInstance(keycloakInstance)` после инициализации
- Обновлен `frontend/src/services/api.ts` - добавлено логирование инициализации

### 2. Backend недоступен

**Проблема:** Frontend пытается обратиться к `http://localhost:8000`, но backend не запущен.

**Проверка:**
```bash
# Проверить статус контейнеров
docker-compose ps

# Должны быть в статусе "Up":
# - backend
# - frontend
# - db (postgres)
```

**Решение:**
```bash
# Если контейнер backend падает, посмотрите логи
docker-compose logs backend -f

# Перезапустите всё
docker-compose down
docker-compose up -d
```

### 3. Неверная конфигурация REACT_APP_API_URL

**Проблема:** Переменная окружения указывает на неправильный адрес backend.

**Проверка:**
```bash
# В браузере откройте консоль (F12) и проверьте логи
# Там должно быть:
# "Keycloak instance initialized in API service"
# "Initializing Keycloak with: { url: ..., realm: ... }"

# Если их нет, то Keycloak не инициализирован
```

**Решение:**
```bash
# Откройте .env файл и проверьте
REACT_APP_API_URL=http://localhost:8000  # ✅ Правильно (локально)
REACT_APP_API_URL=http://backend:8000    # ✅ Правильно (в Docker)
```

### 4. Dashboard пытается загрузить статистику, но API не работает

**Проблема:** Компонент Dashboard зависает на Loading, потому что запрос к `/api/admin/stats` падает.

**Решение:** ✅ **УЖЕ ИСПРАВЛЕНО**
- Обновлен `frontend/src/pages/Dashboard.tsx` с обработкой ошибок
- Теперь показывает пользователю ошибку вместо вечного Loading

### 5. CORS ошибки

**Проблема:** Frontend и backend на разных доменах/портах, и CORS не настроен.

**Проверка в браузере (F12 → Console):**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/admin/stats' 
from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Решение:**
Ensure backend CORS is configured correctly in `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Should include http://localhost:3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📋 Пошаговый процесс отладки

### Шаг 1: Проверьте консоль браузера (F12)

```javascript
// Откройте вкладку Console и ищите такие сообщения:

// ✅ Успешно:
// "Initializing Keycloak with: { url: ..., realm: ..., clientId: ... }"
// "Keycloak initialization successful, authenticated: true"
// "Keycloak instance initialized in API service"

// ❌ Ошибки:
// "Keycloak initialization failed: ..."
// "API Error: status: 404, url: http://localhost:8000/api/admin/stats"
// "Access to XMLHttpRequest blocked by CORS policy"
```

### Шаг 2: Проверьте вкладку Network

1. Откройте F12 → вкладка Network
2. Перезагрузите страницу
3. Ищите запросы к:
   - Keycloak: `http://localhost:8080/auth/realms/network-access/...`
   - Backend: `http://localhost:8000/api/admin/stats`
4. Проверьте статус ответа (200, 404, 500, и т.д.)

### Шаг 3: Проверьте Docker logs

```bash
# Frontend логи
docker-compose logs frontend -f

# Backend логи
docker-compose logs backend -f

# Keycloak логи
docker-compose logs keycloak -f

# Postgres логи
docker-compose logs db -f
```

### Шаг 4: Проверьте запуск контейнеров

```bash
docker-compose ps

# Ожидаемый результат:
# NAME                      STATUS
# network-access-portal-backend-1   Up (healthy)
# network-access-portal-frontend-1  Up
# network-access-portal-keycloak-1  Up (healthy)
# network-access-portal-db-1        Up (healthy)
```

## 🔧 Частые проблемы и решения

### Проблема: "Keycloak initialization failed"

```
Кaycloak недоступен по адресу http://localhost:8080
```

**Решение:**
```bash
# 1. Проверьте запущен ли Keycloak
docker-compose logs keycloak | tail -20

# 2. Дождитесь инициализации (может занять 30-60 секунд)
# 3. Проверьте .env файл:
REACT_APP_KEYCLOAK_URL=http://localhost:8080  # ✅ локально
REACT_APP_KEYCLOAK_URL=http://keycloak:8080   # ✅ в Docker

# 4. Перезапустите frontend
docker-compose restart frontend
```

### Проблема: "Failed to Load Statistics"

```
Backend не ответил на запрос /api/admin/stats
```

**Решение:**
```bash
# 1. Проверьте backend запущен
docker-compose ps backend

# 2. Проверьте логи backend
docker-compose logs backend -f

# 3. Проверьте здоров ли backend
curl -X GET http://localhost:8000/health

# 4. Проверьте REACT_APP_API_URL в .env
REACT_APP_API_URL=http://localhost:8000  # ✅ правильно

# 5. Перезапустите frontend
docker-compose restart frontend
```

### Проблема: "Access to XMLHttpRequest blocked by CORS"

```
backend не разрешает запросы с фронтенда
```

**Решение:**
Отредактируйте `backend/app/main.py` и убедитесь, что:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],  # Добавьте оба
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Тестирование API вручную

### Получить Bearer Token

```bash
# В браузере консоли выполните:
const token = window.localStorage.getItem('KEYCLOAK_TOKEN'); // Может быть разным в зависимости от версии
console.log(token);
```

### Тестировать API

```bash
# Замените TOKEN на настоящий токен
TOKEN="your-jwt-token"

# Проверить health
curl -X GET http://localhost:8000/health

# Получить статистику (требует аутентификации)
curl -X GET http://localhost:8000/api/admin/stats \
  -H "Authorization: Bearer $TOKEN"

# Получить мои заявки
curl -X GET http://localhost:8000/api/requests \
  -H "Authorization: Bearer $TOKEN"
```

## 📚 Полезные команды

```bash
# Полный перезапуск
docker-compose down
docker-compose up -d

# Очистить всё и начать с чистого листа
docker-compose down -v
rm -rf postgres_data
docker-compose up -d

# Просмотреть все логи в реальном времени
docker-compose logs -f

# Войти в контейнер backend для отладки
docker exec -it network-access-portal-backend-1 bash

# Войти в PostgreSQL
docker exec -it network-access-portal-db-1 psql -U network_user -d network_db
```

## 🔗 Важные URL для проверки

| Сервис | URL | Назначение |
|--------|-----|----------|
| Frontend | http://localhost:3000 | Веб-приложение |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Keycloak | http://localhost:8080 | Сервер аутентификации |
| Keycloak Admin | http://localhost:8080/admin | Админ-панель Keycloak |

## 📞 Нужна помощь?

Если проблема не решена:

1. **Включите все логи:**
   ```bash
   docker-compose logs -f > debug.log 2>&1
   ```

2. **Откройте Developer Tools (F12)** и сохраните скриншоты:
   - Console вкладка (все ошибки)
   - Network вкладка (все запросы)
   - Application → Local Storage (переменные)

3. **Проверьте файл `.env`** (убедитесь что копировали из `.env.example`)

4. **Очистите все кэши:** `docker-compose down -v && docker-compose up -d`
