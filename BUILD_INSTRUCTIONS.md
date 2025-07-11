# 🔨 Instrukcja Budowania TaskMaster BugTracker jako .EXE

## 📋 Przygotowanie środowiska

### 1. Sprawdź wersję Pythona
```bash
python --version
```
Wymagany Python 3.8 lub nowszy.

### 2. Utwórz wirtualne środowisko (zalecane)
```bash
# W katalogu projektu
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Zainstaluj PyInstaller
```bash
pip install pyinstaller==6.3.0
```

Opcjonalnie (dla lepszej kompresji i ikon):
```bash
pip install pillow==10.1.0
```

## 🎨 Przygotowanie ikon (opcjonalne)

### 1. Utwórz folder assets
```bash
mkdir assets
```

### 2. Dodaj ikonę
- Nazwa: `icon.ico`
- Rozmiar: 256x256 pikseli (zawierająca też 48x48, 32x32, 16x16)
- Format: ICO dla Windows
- Umieść w: `assets/icon.ico`

Możesz użyć narzędzi online do konwersji PNG → ICO.

## 🚀 Budowanie aplikacji

### Metoda 1: Podstawowa (szybka)

```bash
pyinstaller --onefile --windowed --name="TaskMaster BugTracker" main.py
```

### Metoda 2: Z ikoną i optymalizacją

```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico --name="TaskMaster BugTracker" main.py
```

### Metoda 3: Zaawansowana (używając pliku .spec)

1. **Utwórz plik taskmaster.spec** (już utworzony powyżej)

2. **Dostosuj plik version_info.txt** z informacjami o Twojej firmie

3. **Buduj używając spec:**
```bash
pyinstaller taskmaster.spec
```

## 📦 Dodatkowe opcje PyInstaller

### Optymalizacja rozmiaru
```bash
pyinstaller --onefile --windowed \
    --name="TaskMaster BugTracker" \
    --icon=assets/icon.ico \
    --exclude-module matplotlib \
    --exclude-module numpy \
    --exclude-module pandas \
    --exclude-module PIL \
    --exclude-module scipy \
    --upx-dir=C:\upx \  # Jeśli masz UPX zainstalowany
    main.py
```

### Debugowanie (jeśli są problemy)
```bash
pyinstaller --onefile --console --debug=all --name="TaskMaster BugTracker" main.py
```

## 📁 Struktura po budowaniu

```
taskmaster-bugtracker/
├── build/              # Pliki tymczasowe (można usunąć)
├── dist/               # Tu znajdziesz gotowy plik .exe
│   └── TaskMaster BugTracker.exe
├── TaskMaster BugTracker.spec  # Plik konfiguracji
└── [pozostałe pliki projektu]
```

## 🖥️ Instalacja na pulpicie

### 1. Kopiowanie pliku .exe
```bash
# Znajdź plik
cd dist

# Skopiuj na pulpit (Windows)
copy "TaskMaster BugTracker.exe" "%USERPROFILE%\Desktop\"
```

### 2. Tworzenie skrótu (opcjonalnie)
1. Kliknij prawym na `TaskMaster BugTracker.exe`
2. Wybierz "Utwórz skrót"
3. Przenieś skrót na pulpit
4. Opcjonalnie zmień ikonę skrótu

## 🛠️ Rozwiązywanie problemów

### Problem: "Failed to execute script"
**Rozwiązanie:**
```bash
# Buduj z konsolą aby zobaczyć błędy
pyinstaller --onefile --console --name="TaskMaster BugTracker" main.py
```

### Problem: Brakujące moduły
**Rozwiązanie:** Dodaj do hidden imports w .spec:
```python
hiddenimports=['nazwa_modulu'],
```

### Problem: Antywirus blokuje
**Rozwiązanie:**
1. Dodaj folder `dist` do wyjątków antywirusa
2. Podpisz aplikację cyfrowo (zaawansowane)

### Problem: Duży rozmiar pliku
**Rozwiązanie:**
1. Użyj UPX:
```bash
# Pobierz UPX: https://upx.github.io/
pyinstaller --upx-dir=C:\upx taskmaster.spec
```

2. Exclude niepotrzebne moduły:
```bash
pyinstaller --exclude-module nazwa_modulu main.py
```

## 🔒 Podpisywanie cyfrowe (opcjonalne)

Dla Windows (wymaga certyfikatu):
```bash
signtool sign /f certyfikat.pfx /p hasło /t http://timestamp.digicert.com "dist\TaskMaster BugTracker.exe"
```

## 📝 Checklist przed dystrybucją

- [ ] Test na czystym systemie Windows
- [ ] Sprawdź czy wszystkie funkcje działają
- [ ] Zweryfikuj tworzenie bazy danych
- [ ] Test logowania (admin/admin123)
- [ ] Sprawdź skalowanie na różnych rozdzielczościach
- [ ] Skanuj antywirusem
- [ ] Utwórz kopię zapasową

## 🚢 Dystrybucja

### Opcja 1: Prosty plik .exe
- Rozmiar: ~15-25 MB
- Wystarczy skopiować i uruchomić
- Baza danych tworzona automatycznie

### Opcja 2: Installer (zaawansowane)
Użyj NSIS lub Inno Setup:
```ini
[Setup]
AppName=TaskMaster BugTracker
AppVersion=2.0.0
DefaultDirName={pf}\TaskMaster
DefaultGroupName=TaskMaster
OutputBaseFilename=TaskMasterSetup
```

### Opcja 3: Portable ZIP
```bash
# Utwórz folder
mkdir TaskMaster-Portable

# Skopiuj exe
copy "dist\TaskMaster BugTracker.exe" TaskMaster-Portable\

# Utwórz README
echo "Run 'TaskMaster BugTracker.exe' to start" > TaskMaster-Portable\README.txt

# Spakuj
powershell Compress-Archive -Path TaskMaster-Portable -DestinationPath TaskMaster-Portable-v2.0.0.zip
```

## 📊 Finalne kroki

1. **Test końcowy:**
    - Uruchom .exe z pulpitu
    - Zaloguj się (admin/admin123)
    - Utwórz testowy bug
    - Zamknij i uruchom ponownie
    - Sprawdź czy dane się zachowały

2. **Dokumentacja użytkownika:**
    - Utwórz `QUICK_START.pdf`
    - Dodaj zrzuty ekranu
    - Opisz pierwsze kroki

3. **Wsparcie:**
    - Przygotuj FAQ
    - Utwórz email wsparcia
    - Rozważ utworzenie strony Wiki

## ✅ Gotowe!

Twój plik `TaskMaster BugTracker.exe` jest gotowy do użycia.
Aplikacja jest w pełni samodzielna i nie wymaga instalacji Pythona na docelowym komputerze.

---

💡 **Wskazówka:** Zapisz tę instrukcję jako `BUILD_INSTRUCTIONS.md` w katalogu projektu dla przyszłych buildów.