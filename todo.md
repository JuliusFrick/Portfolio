# Portfolio Management Website - Todo Liste

## Phase 1: API-Recherche für Aktien- und ETF-Daten ✓
- [x] Alpha Vantage API untersucht - kostenlos mit 25 Anfragen/Tag
- [x] Finnhub API untersucht - kostenlos mit 60 Anfragen/Minute
- [x] Beide APIs bieten Aktien- und ETF-Daten

## Phase 2: Flask-Anwendung erstellen und grundlegende Struktur aufbauen
- [x] Flask-App mit manus-create-flask-app erstellen
- [x] Grundlegende Projektstruktur einrichten
- [x] CORS-Unterstützung hinzufügen (flask-cors installiert)
- [ ] API-Konfiguration für Finnhub/Alpha Vantage
- [x] OCR-Abhängigkeiten installiert (pytesseract, tesseract-ocr)

## Phase 3: OCR-Funktionalität für Investitionsbelege implementieren
- [x] OCR-Bibliothek (Tesseract/pytesseract) installieren
- [x] Upload-Funktionalität für Bilder/PDFs
- [x] OCR-Verarbeitung für Aktienname, Kaufdatum, Kaufpreis, Menge
- [x] Datenextraktion und -validierung
- [x] OCR-Service erstellt mit deutschen und englischen Mustern

## Phase 4: Portfolio-Datenmodell und -verwaltung entwickeln
- [x] Portfolio-Datenstruktur definieren
- [x] In-Memory-Speicher (Session-basiert) - SQLite Datenbank verwendet
- [x] CRUD-Operationen für Portfolio-Einträge
- [x] API-Integration für aktuelle Kursdaten (Finnhub + Alpha Vantage Fallback)
- [x] Market Data Service mit Rate Limiting implementiert

## Phase 5: Frontend für Upload und Portfolio-Anzeige erstellen
- [x] HTML-Templates für Upload-Seite
- [x] Portfolio-Übersichtsseite
- [x] Responsive Design
- [x] JavaScript für interaktive Funktionen
- [x] Drag & Drop Upload-Funktionalität
- [x] Manuelle Eingabe-Formulare
- [x] Portfolio-Statistiken und Tabelle

## Phase 6: Datenvisualisierung und Performance-Vergleich implementieren
- [x] Chart.js oder ähnliche Bibliothek integrieren
- [x] Portfolio-Performance-Charts
- [x] ETF-Vergleichsfunktionalität
- [x] Historische Datenvisualisierung
- [x] Portfolio-Allokation Pie Chart
- [x] Gewinn/Verlust Bar Chart
- [x] Performance-Zeitreihen-Diagramm
- [x] Portfolio vs ETF Vergleichsdiag## Phase 7: Anwendung testen und optimieren
- [x] Lokale Tests durchführen
- [x] Frontend-Funktionalität testen
- [x] Backend-API-Endpunkte testen
- [x] Datenbank-Integration testen
- [x] Portfolio-Management testen
- [x] Charts und Visualisierungen testen
- [x] Responsive Design testen
- [x] Fehlerbehandlung überprüfense 8: Ergebnisse präsentieren und Deployment-Option anbieten
- [ ] Dokumentation erstellen
- [ ] Demo-Daten vorbereiten
- [ ] Deployment-Option anbieten

