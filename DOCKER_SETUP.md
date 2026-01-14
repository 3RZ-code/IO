# Aplikacja IO - Docker Setup

## Uruchomienie całej aplikacji z Dockerem

### 1. Upewnij się że masz .env w katalogu `backend/`

```bash
cd /home/issu3/Studia/IO
cat backend/.env
```

### 2. Uruchom docker-compose z głównego katalogu projektu

```bash
cd /home/issu3/Studia/IO
docker-compose up --build
```

**Lub bez budowania (jeśli obrazy już istnieją):**
```bash
docker-compose up
```

### 3. Aplikacja będzie dostępna pod:

- **Frontend (React):** http://localhost:3000
- **Backend (Django):** http://localhost:6543
- **Database (PostgreSQL):** localhost:5432

---

## Flagi przydatne

```bash
# Uruchom w tle (detached mode)
docker-compose up -d --build

# Zatrzymaj kontenery
docker-compose down

# Zatrzymaj i usuń wolumeny (baza danych)
docker-compose down -v

# Wyświetl logi wszystkich serwisów
docker-compose logs -f

# Logi tylko backendu
docker-compose logs -f api

# Logi tylko frontendu
docker-compose logs -f frontend
```

---

## Jeśli masz problemy

**Problem: Port już zajęty**
```bash
# Zmień port w docker-compose.yml
# Zmień "3000:3000" na "3001:3000" na przykład
```

**Problem: Błędy budowania**
```bash
# Przebuduj bez cache
docker-compose up --build --no-cache
```

**Problem: Baza danych nieużyteczna**
```bash
# Usuń i stwórz nową
docker-compose down -v
docker-compose up --build
```
