# 🚀 TaskMaster BugTracker - Szybki Start

## 🎯 Budowanie aplikacji .exe w 3 krokach

### Krok 1: Otwórz terminal w folderze projektu
- W IntelliJ IDEA: `View → Tool Windows → Terminal`
- Lub: Otwórz Command Prompt/PowerShell w folderze projektu

### Krok 2: Uruchom skrypt budowania
```bash
# Windows:
./build.bat

# Linux/Mac:
chmod +x build.sh
./build.sh
```

### Krok 3: Gotowe!
- Plik .exe znajdziesz w folderze `dist/`
- Skrypt zapyta czy skopiować na pulpit

## 🔧 Budowanie ręczne (jeśli skrypt nie działa)

### 1. Zainstaluj PyInstaller
```bash
pip install pyinstaller
```

### 2. Zbuduj aplikację
```bash
pyinstaller --onefile --windowed --name="TaskMaster BugTracker" main.py
```

### 3. Znajdź plik .exe
- Lokalizacja: `dist/TaskMaster BugTracker.exe`
- Skopiuj na pulpit

## 📱 Pierwsze uruchomienie

1. **Uruchom** `TaskMaster BugTracker.exe`
2. **Zaloguj się:**
    - Login: `admin`
    - Hasło: `admin123`
3. **Gotowe!** Możesz tworzyć projekty i zgłaszać bugi

## ❓ Problemy?

### "Windows chronił komputer"
- Kliknij "Więcej informacji"
- Wybierz "Uruchom mimo to"

### Aplikacja się nie uruchamia
- Sprawdź folder `%APPDATA%\TaskMaster`
- Usuń `taskmaster.db` aby zresetować

### Brak modułu przy budowaniu
```bash
pip install -r requirements.txt
```

## 📞 Wsparcie

- Email: support@taskmaster.example.com
- Dokumentacja: [README.md](README.md)

---
**TaskMaster BugTracker v2.0.0** - Bug Tracker dla Money Mentor AI