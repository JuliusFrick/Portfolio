# Portfolio Manager - OCR-basierte Investitionsverwaltung

Eine moderne Flask-basierte Webanwendung zur Verwaltung von Investitionsportfolios mit OCR-Funktionalität für Investitionsbelege und umfassenden Visualisierungen.

## 🚀 Features

### Core-Funktionalitäten
- **📄 OCR-Integration**: Automatische Erkennung von Investitionsdaten aus Belegen (PNG, JPG, PDF)
- **💼 Portfolio-Management**: Verwaltung von Aktien und ETF-Positionen
- **📊 Datenvisualisierung**: Interaktive Charts und Diagramme
- **📈 Performance-Tracking**: Echtzeit-Kursdaten und Gewinn/Verlust-Analyse
- **⚖️ ETF-Vergleich**: Vergleich der Portfolio-Performance mit beliebten ETFs

### Technische Features
- **🎨 Responsive Design**: Optimiert für Desktop und Mobile
- **🔄 Drag & Drop Upload**: Intuitive Datei-Upload-Funktionalität
- **🌐 API-Integration**: Finnhub (primär) + Alpha Vantage (fallback)
- **💾 Session-basiert**: Portfolio wird bei Neustart automatisch gelöscht
- **🔒 Keine Account-Verwaltung**: Einfache Nutzung ohne Registrierung

## 🛠️ Technologie-Stack

### Backend
- **Flask**: Web-Framework
- **SQLAlchemy**: ORM für Datenbankoperationen
- **Tesseract OCR**: Texterkennung aus Dokumenten
- **Requests**: HTTP-Client für API-Aufrufe

### Frontend
- **HTML5/CSS3**: Moderne Webstandards
- **JavaScript (ES6+)**: Interaktive Funktionalitäten
- **Chart.js**: Datenvisualisierung
- **Responsive Design**: Mobile-first Ansatz

### Datenbank
- **SQLite**: Leichtgewichtige Datenbank für lokale Entwicklung

## 📋 Installation und Setup

### Voraussetzungen
```bash
# System-Abhängigkeiten installieren
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
```

### Installation
```bash
# Repository klonen
git clone <repository-url>
cd portfolio_manager

# Virtuelle Umgebung aktivieren
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Konfiguration
1. **API-Schlüssel einrichten** (optional für Demo):
   - Finnhub: https://finnhub.io/register
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key

2. **Umgebungsvariablen setzen**:
   ```bash
   export FINNHUB_API_KEY="your_finnhub_key"
   export ALPHA_VANTAGE_API_KEY="your_alpha_vantage_key"
   ```

### Anwendung starten
```bash
python src/main.py
```

Die Anwendung ist dann verfügbar unter: http://127.0.0.1:5000

## 📖 Nutzung

### 1. Portfolio-Einträge hinzufügen

#### Manuell
1. Navigieren Sie zum Bereich "Oder manuell hinzufügen"
2. Füllen Sie die Felder aus:
   - **Symbol/Ticker**: z.B. AAPL, MSFT
   - **Firmenname**: Optional
   - **Kaufdatum**: Datum des Kaufs
   - **Kaufpreis**: Preis pro Aktie in Euro
   - **Anzahl**: Anzahl der gekauften Aktien
3. Klicken Sie auf "Hinzufügen"

#### Per OCR-Upload
1. Klicken Sie auf "Datei auswählen" oder ziehen Sie eine Datei in den Upload-Bereich
2. Unterstützte Formate: PNG, JPG, PDF
3. Die OCR-Engine erkennt automatisch:
   - Aktien-Symbol
   - Firmenname
   - Kaufdatum
   - Kaufpreis
   - Anzahl der Aktien
4. Bei hohem Vertrauen wird der Eintrag automatisch erstellt

### 2. Portfolio verwalten
- **Kurse aktualisieren**: Holt aktuelle Marktdaten
- **Portfolio leeren**: Löscht alle Einträge
- **Einzelne Einträge löschen**: Über die Tabelle

### 3. Visualisierungen nutzen
Klicken Sie auf "📈 Zu den Visualisierungen" für:
- **Portfolio-Allokation**: Pie Chart der Verteilung
- **Gewinn/Verlust**: Bar Chart pro Position
- **Performance über Zeit**: Zeitreihen-Diagramm
- **ETF-Vergleich**: Vergleich mit beliebten ETFs

### 4. ETF-Vergleich
1. Wählen Sie einen ETF aus der Dropdown-Liste
2. Setzen Sie ein Startdatum für den Vergleich
3. Klicken Sie auf "Vergleichen"
4. Sehen Sie die Performance-Unterschiede in Echtzeit

## 🔧 API-Integration

### Finnhub API (Primär)
- **Kostenlos**: 60 Aufrufe/Minute
- **Daten**: Aktien, ETFs, Echtzeit-Kurse
- **Dokumentation**: https://finnhub.io/docs/api

### Alpha Vantage API (Fallback)
- **Kostenlos**: 5 Aufrufe/Minute
- **Daten**: Aktien, ETFs, historische Daten
- **Dokumentation**: https://www.alphavantage.co/documentation/

## 📊 Unterstützte Visualisierungen

### Portfolio-Allokation
- **Typ**: Doughnut Chart
- **Zeigt**: Prozentuale Verteilung der Investitionen
- **Features**: Hover-Effekte, Legende

### Gewinn/Verlust pro Position
- **Typ**: Bar Chart
- **Zeigt**: Absolute Gewinn/Verlust-Werte
- **Features**: Farbkodierung (Grün/Rot)

### Portfolio-Performance über Zeit
- **Typ**: Line Chart
- **Zeigt**: Entwicklung des Portfolio-Werts
- **Features**: Vergleich mit investiertem Betrag

### ETF-Vergleich
- **Typ**: Multi-Line Chart
- **Zeigt**: Performance-Vergleich in Prozent
- **Features**: Interaktive Zeitraum-Auswahl

## 🔍 OCR-Funktionalität

### Unterstützte Formate
- **PNG**: Portable Network Graphics
- **JPG/JPEG**: Joint Photographic Experts Group
- **PDF**: Portable Document Format
- **GIF, BMP, TIFF**: Weitere Bildformate

### Erkennungsgenauigkeit
- **Hoch (>70%)**: Automatische Erstellung
- **Mittel (40-70%)**: Manuelle Überprüfung empfohlen
- **Niedrig (<40%)**: Manuelle Eingabe erforderlich

### Optimierung für deutsche und englische Belege
- Tesseract mit deutschen und englischen Sprachpaketen
- Regex-Muster für typische Belegformate
- Intelligente Datenextraktion und -validierung

## 🚀 Deployment-Optionen

### Lokale Entwicklung
```bash
python src/main.py
# Verfügbar unter http://127.0.0.1:5000
```

### Produktions-Deployment
Die Anwendung kann mit verschiedenen WSGI-Servern deployed werden:

#### Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```


---

**Entwickelt mit ❤️ für moderne Portfolio-Verwaltung**

