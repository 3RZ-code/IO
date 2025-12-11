# Alarm Alert - Nasłuchiwanie Zmian w Bazie Danych

## 📚 Spis Treści
1. [Wprowadzenie](#wprowadzenie)
2. [Teoria Django Signals](#teoria-django-signals)
3. [Metody Nasłuchiwania Zmian](#metody-nasłuchiwania-zmian)
4. [Praktyczny Przykład: Zmiana Roli Użytkownika](#praktyczny-przykład-zmiana-roli-użytkownika)
5. [Implementacja Krok po Kroku](#implementacja-krok-po-kroku)
6. [Zaawansowane Techniki](#zaawansowane-techniki)
7. [Najlepsze Praktyki](#najlepsze-praktyki)

---

## 🎯 Wprowadzenie

Ten dokument wyjaśnia **jak nasłuchiwać zmian w bazie danych Django** i automatycznie reagować na nie (np. tworząc Alert). 

**Przykład użycia:** Gdy ktoś zmieni rolę użytkownika z `'user'` na `'admin'`, system automatycznie utworzy Alert informujący o tej zmianie.

---

## 🔔 Teoria Django Signals

### Co to są Signals?

**Signals** to mechanizm Django, który pozwala na **nasłuchiwanie określonych zdarzeń** w aplikacji i wykonywanie kodu w odpowiedzi na nie.

### Typy Signals w Django

#### 1. **pre_save** 
- Wywoływany **PRZED** zapisaniem obiektu do bazy
- Możesz modyfikować dane przed zapisem
- **Nie masz jeszcze** zapisanego obiektu w bazie

#### 2. **post_save**
- Wywoływany **PO** zapisaniu obiektu do bazy
- Obiekt już istnieje w bazie
- Idealny do tworzenia powiązanych obiektów (np. Alert)

#### 3. **pre_delete**
- Wywoływany **PRZED** usunięciem obiektu
- Możesz jeszcze odczytać dane przed usunięciem

#### 4. **post_delete**
- Wywoływany **PO** usunięciu obiektu
- Obiekt już nie istnieje w bazie

#### 5. **m2m_changed**
- Dla relacji Many-to-Many
- Wywoływany gdy dodajesz/usuwasz powiązania

---

## 🛠️ Metody Nasłuchiwania Zmian

### Metoda 1: Django Signals (REKOMENDOWANA)

**Zalety:**
- ✅ Oddziela logikę od modeli
- ✅ Łatwe do testowania
- ✅ Można wyłączyć w testach
- ✅ Działa dla wszystkich sposobów zapisu (admin, API, shell)

**Wady:**
- ⚠️ Trzeba pamiętać o rejestracji w `apps.py`

### Metoda 2: Override metody `save()` w modelu

**Zalety:**
- ✅ Wszystko w jednym miejscu
- ✅ Łatwe do zrozumienia

**Wady:**
- ⚠️ Nie działa dla `bulk_update()`, `update()`
- ⚠️ Miesza logikę biznesową z modelem

### Metoda 3: Override w Serializerze/ViewSet

**Zalety:**
- ✅ Kontrola nad konkretnymi endpointami

**Wady:**
- ⚠️ Działa tylko dla API
- ⚠️ Nie działa dla admin panelu

---

## 💡 Praktyczny Przykład: Zmiana Roli Użytkownika

### Scenariusz

Chcemy **wykryć**, gdy ktoś zmieni rolę użytkownika (np. z `'user'` na `'admin'`) i **automatycznie utworzyć Alert**.

### Krok 1: Utworzenie Signal Handlera

Stwórz plik `backend/alarm_alert/signals.py`:

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from security.models import User
from alarm_alert.models import Alert
from django.utils import timezone


@receiver(pre_save, sender=User)
def detect_user_role_change(sender, instance, **kwargs):
    """
    Wykrywa zmianę roli użytkownika PRZED zapisem.
    Zapisuje starą wartość w instancji, żeby porównać w post_save.
    """
    if instance.pk:  # Tylko dla istniejących użytkowników (nie dla nowych)
        try:
            old_user = User.objects.get(pk=instance.pk)
            instance._old_role = old_user.role  # Zapisz starą rolę w instancji
        except User.DoesNotExist:
            instance._old_role = None
    else:
        instance._old_role = None  # Nowy użytkownik


@receiver(post_save, sender=User)
def create_alert_on_role_change(sender, instance, created, **kwargs):
    """
    Tworzy Alert PO zapisaniu, jeśli rola się zmieniła.
    """
    # Pomiń dla nowych użytkowników
    if created:
        return
    
    # Sprawdź czy rola się zmieniła
    old_role = getattr(instance, '_old_role', None)
    if old_role is None:
        return
    
    if old_role != instance.role:
        # ROLA SIĘ ZMIENIŁA! Utwórz Alert
        
        # Określ severity na podstawie zmiany
        if instance.role == 'admin' and old_role != 'admin':
            severity = 'critical'  # Podniesienie do admina = krytyczne
            message = f"⚠️ KRYTYCZNA ZMIANA: Użytkownik {instance.username} otrzymał rolę administratora!"
        elif old_role == 'admin' and instance.role != 'admin':
            severity = 'warning'  # Odebranie admina = ostrzeżenie
            message = f"⚠️ OSTRZEŻENIE: Użytkownik {instance.username} stracił rolę administratora!"
        else:
            severity = 'info'
            message = f"ℹ️ Zmiana roli użytkownika {instance.username}: {old_role} → {instance.role}"
        
        # Utwórz Alert
        Alert.objects.create(
            user_id=instance.id,  # UUID jako integer (może wymagać zmiany typu)
            timestamp=timezone.now(),
            source='security',
            category='system',
            severity=severity,
            message=message,
            details=f"Zmiana roli użytkownika:\n"
                   f"- Użytkownik: {instance.username} (ID: {instance.id})\n"
                   f"- Poprzednia rola: {old_role}\n"
                   f"- Nowa rola: {instance.role}\n"
                   f"- Zmiana wykonana: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            status='open',
            visible_for='admin'  # Tylko admini widzą zmiany ról
        )
```

### Krok 2: Rejestracja Signals w apps.py

Zaktualizuj `backend/alarm_alert/apps.py`:

```python
from django.apps import AppConfig


class AlarmAlertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarm_alert'
    
    def ready(self):
        """
        Metoda ready() jest wywoływana gdy aplikacja jest gotowa.
        Tutaj rejestrujemy nasze signals.
        """
        import alarm_alert.signals  # Import signals, żeby się zarejestrowały
```

### Krok 3: Upewnij się, że aplikacja jest załadowana

W `backend/IO/settings.py` sprawdź, czy `alarm_alert` jest w `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... inne aplikacje
    'alarm_alert',
    # ...
]
```

---

## 📝 Implementacja Krok po Kroku

### Krok 1: Utwórz plik signals.py

```bash
# W katalogu backend/alarm_alert/
touch signals.py
```

### Krok 2: Napisz handler dla zmiany roli

Skopiuj kod z sekcji "Praktyczny Przykład" powyżej.

### Krok 3: Zaktualizuj apps.py

Dodaj metodę `ready()` jak pokazano wyżej.

### Krok 4: Przetestuj

```python
# W Django shell (python manage.py shell)
from security.models import User

# Pobierz użytkownika
user = User.objects.first()

# Zmień rolę
user.role = 'admin'
user.save()  # To wywoła signal i utworzy Alert!

# Sprawdź czy Alert został utworzony
from alarm_alert.models import Alert
alerts = Alert.objects.filter(user_id=user.id)
print(alerts)
```

---

## 🎓 Zaawansowane Techniki

### 1. Wykrywanie Zmiany Dowolnego Pola

Jeśli chcesz wykrywać zmiany **dowolnego pola**, nie tylko `role`:

```python
@receiver(pre_save, sender=User)
def save_old_values(sender, instance, **kwargs):
    """Zapisuje wszystkie stare wartości przed zapisem."""
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            instance._old_values = {
                'role': old_instance.role,
                'email': old_instance.email,
                'is_active': old_instance.is_active,
                # ... inne pola
            }
        except User.DoesNotExist:
            instance._old_values = {}


@receiver(post_save, sender=User)
def detect_any_field_change(sender, instance, created, **kwargs):
    """Wykrywa zmianę dowolnego pola."""
    if created:
        return
    
    old_values = getattr(instance, '_old_values', {})
    if not old_values:
        return
    
    changed_fields = []
    for field_name, old_value in old_values.items():
        new_value = getattr(instance, field_name)
        if old_value != new_value:
            changed_fields.append({
                'field': field_name,
                'old': old_value,
                'new': new_value
            })
    
    if changed_fields:
        # Utwórz Alert z listą zmian
        Alert.objects.create(
            user_id=instance.id,
            source='security',
            category='system',
            severity='info',
            message=f"Zmiana danych użytkownika {instance.username}",
            details=f"Zmienione pola: {', '.join([c['field'] for c in changed_fields])}",
            visible_for='admin'
        )
```

### 2. Wykrywanie Zmian w Bulk Operations

Domyślnie signals **NIE działają** dla `bulk_update()` i `update()`. 

**Rozwiązanie:** Override w Managerze lub QuerySet:

```python
# W security/models.py
from django.db import models

class UserQuerySet(models.QuerySet):
    def update(self, **kwargs):
        """Override update() żeby wywołać signals."""
        # Pobierz stare wartości przed update
        old_instances = {obj.pk: obj for obj in self}
        
        # Wykonaj update
        result = super().update(**kwargs)
        
        # Wywołaj signals ręcznie
        for pk, old_instance in old_instances.items():
            try:
                new_instance = self.model.objects.get(pk=pk)
                # Wywołaj post_save signal ręcznie
                from django.db.models.signals import post_save
                post_save.send(sender=self.model, instance=new_instance, created=False)
            except self.model.DoesNotExist:
                pass
        
        return result

class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

# W modelu User:
class User(AbstractUser):
    objects = UserManager()
    # ... reszta kodu
```

### 3. Wykrywanie Kto Wykonał Zmianę

Jeśli chcesz wiedzieć **kto** zmienił rolę (np. który admin):

```python
@receiver(post_save, sender=User)
def track_who_changed_role(sender, instance, created, **kwargs):
    """Śledzi kto zmienił rolę użytkownika."""
    if created:
        return
    
    old_role = getattr(instance, '_old_role', None)
    if old_role is None or old_role == instance.role:
        return
    
    # Pobierz aktualnie zalogowanego użytkownika (jeśli dostępny)
    # UWAGA: To wymaga przekazania request.user przez context
    # Lepsze rozwiązanie: użyj django-auditlog lub podobnej biblioteki
    
    # Alternatywnie: zapisz w details informację o czasie zmiany
    Alert.objects.create(
        user_id=instance.id,
        source='security',
        category='system',
        severity='warning',
        message=f"Zmiana roli: {old_role} → {instance.role}",
        details=f"Użytkownik: {instance.username}\n"
               f"Zmiana wykonana: {timezone.now()}",
        visible_for='admin'
    )
```

---

## ✅ Najlepsze Praktyki

### 1. **Zawsze używaj `pre_save` do zapisania starych wartości**

```python
@receiver(pre_save, sender=User)
def save_old_role(sender, instance, **kwargs):
    if instance.pk:
        old = User.objects.get(pk=instance.pk)
        instance._old_role = old.role  # Zapisz w instancji
```

### 2. **Sprawdzaj czy obiekt istnieje (`if instance.pk`)**

```python
if instance.pk:  # Tylko dla istniejących obiektów
    # ... kod
else:
    return  # Nowy obiekt, nie ma starej wartości
```

### 3. **Używaj `created` flag w `post_save`**

```python
@receiver(post_save, sender=User)
def handler(sender, instance, created, **kwargs):
    if created:
        return  # Nowy obiekt, nie ma zmian
    # ... sprawdź zmiany
```

### 4. **Nie wykonuj ciężkich operacji w signals**

Signals są synchroniczne - jeśli zrobisz tam ciężką operację, spowolni to zapis.

**Złe:**
```python
@receiver(post_save, sender=User)
def send_email(sender, instance, **kwargs):
    # Ciężka operacja - spowolni zapis!
    send_complex_email(instance)  # Może trwać sekundy
```

**Dobre:**
```python
@receiver(post_save, sender=User)
def queue_email(sender, instance, **kwargs):
    # Dodaj do kolejki - szybkie
    from celery import shared_task
    send_email_task.delay(instance.id)  # Asynchroniczne
```

### 5. **Testuj swoje signals**

```python
# tests.py
from django.test import TestCase
from security.models import User
from alarm_alert.models import Alert

class UserRoleChangeSignalTest(TestCase):
    def test_role_change_creates_alert(self):
        user = User.objects.create(username='test', email='test@test.com', role='user')
        
        # Zmień rolę
        user.role = 'admin'
        user.save()
        
        # Sprawdź czy Alert został utworzony
        alerts = Alert.objects.filter(user_id=user.id)
        self.assertEqual(alerts.count(), 1)
        self.assertEqual(alerts.first().severity, 'critical')
```

---

## 🚀 Szybki Start - Gotowy Kod

### Plik: `backend/alarm_alert/signals.py`

```python
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from security.models import User
from alarm_alert.models import Alert
from django.utils import timezone


@receiver(pre_save, sender=User)
def detect_user_role_change(sender, instance, **kwargs):
    """Zapisuje starą rolę przed zapisem."""
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            instance._old_role = old_user.role
        except User.DoesNotExist:
            instance._old_role = None
    else:
        instance._old_role = None


@receiver(post_save, sender=User)
def create_alert_on_role_change(sender, instance, created, **kwargs):
    """Tworzy Alert gdy rola się zmieni."""
    if created:
        return
    
    old_role = getattr(instance, '_old_role', None)
    if old_role is None or old_role == instance.role:
        return
    
    # Określ severity
    if instance.role == 'admin' and old_role != 'admin':
        severity = 'critical'
        message = f"⚠️ KRYTYCZNA ZMIANA: {instance.username} otrzymał rolę administratora!"
    elif old_role == 'admin' and instance.role != 'admin':
        severity = 'warning'
        message = f"⚠️ OSTRZEŻENIE: {instance.username} stracił rolę administratora!"
    else:
        severity = 'info'
        message = f"ℹ️ Zmiana roli: {instance.username} ({old_role} → {instance.role})"
    
    Alert.objects.create(
        user_id=str(instance.id),  # UUID jako string (dostosuj do typu w modelu)
        timestamp=timezone.now(),
        source='security',
        category='system',
        severity=severity,
        message=message,
        details=f"Użytkownik: {instance.username}\n"
               f"Poprzednia rola: {old_role}\n"
               f"Nowa rola: {instance.role}\n"
               f"Czas: {timezone.now()}",
        status='open',
        visible_for='admin'
    )
```

### Plik: `backend/alarm_alert/apps.py`

```python
from django.apps import AppConfig


class AlarmAlertConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarm_alert'
    
    def ready(self):
        import alarm_alert.signals
```

---

## 📖 Podsumowanie

1. **Signals** to mechanizm Django do nasłuchiwania zdarzeń
2. **pre_save** - zapisz stare wartości przed zapisem
3. **post_save** - sprawdź zmiany i utwórz Alert po zapisie
4. **Rejestracja** - w metodzie `ready()` w `apps.py`
5. **Testowanie** - zawsze testuj swoje signals

**Gotowe!** Teraz każda zmiana roli użytkownika automatycznie utworzy Alert w systemie! 🎉

