import pytesseract
from PIL import Image
import re
from datetime import datetime
from dateutil import parser
import os

class OCRService:
    def __init__(self):
        # Konfiguration für deutsche Texterkennung
        self.tesseract_config = '--oem 3 --psm 6 -l deu+eng'
    
    def extract_text_from_image(self, image_path):
        """Extrahiert Text aus einem Bild mit Tesseract OCR"""
        try:
            image = Image.open(image_path)
            # Konvertiere zu RGB falls nötig
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # OCR durchführen
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            return text
        except Exception as e:
            raise Exception(f"Fehler bei der OCR-Verarbeitung: {str(e)}")
    
    def parse_investment_document(self, text):
        """Parst den extrahierten Text und sucht nach Investitionsdaten"""
        result = {
            'symbol': None,
            'company_name': None,
            'purchase_date': None,
            'purchase_price': None,
            'quantity': None,
            'total_value': None,
            'confidence': 0
        }
        
        # Text normalisieren
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Suche nach Aktien-/ETF-Symbol (z.B. AAPL, MSFT, etc.)
        symbol_patterns = [
            r'\b([A-Z]{2,5})\b',  # 2-5 Großbuchstaben
            r'Symbol[:\s]+([A-Z]{2,5})',
            r'Ticker[:\s]+([A-Z]{2,5})',
            r'WKN[:\s]+([A-Z0-9]{6})',  # Deutsche WKN
            r'ISIN[:\s]+([A-Z]{2}[A-Z0-9]{10})'  # ISIN
        ]
        
        for pattern in symbol_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['symbol'] = match.group(1).upper()
                result['confidence'] += 20
                break
        
        # Suche nach Firmenname
        company_patterns = [
            r'(?:Unternehmen|Company|Firma)[:\s]+([A-Za-z\s&.,]+?)(?:\s|$)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:AG|GmbH|Inc|Corp|Ltd|SE|SA))?)',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Nimm den längsten gefundenen Namen
                result['company_name'] = max(matches, key=len).strip()
                result['confidence'] += 15
                break
        
        # Suche nach Datum
        date_patterns = [
            r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})',  # DD.MM.YYYY oder DD/MM/YYYY
            r'(\d{2,4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD
            r'(?:Datum|Date|Kauf|Purchase)[:\s]+(\d{1,2}[./]\d{1,2}[./]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for date_str in matches:
                    try:
                        # Versuche verschiedene Datumsformate zu parsen
                        parsed_date = parser.parse(date_str, dayfirst=True)
                        result['purchase_date'] = parsed_date.date()
                        result['confidence'] += 25
                        break
                    except:
                        continue
                if result['purchase_date']:
                    break
        
        # Suche nach Preis
        price_patterns = [
            r'(?:Preis|Price|Kurs|Rate)[:\s]*([0-9]+[,.]?[0-9]*)\s*(?:€|EUR|USD|\$)',
            r'([0-9]+[,.]?[0-9]*)\s*(?:€|EUR|USD|\$)',
            r'(?:Stück|Piece|Unit)[:\s]*([0-9]+[,.]?[0-9]*)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    price_str = matches[0].replace(',', '.')
                    result['purchase_price'] = float(price_str)
                    result['confidence'] += 20
                    break
                except:
                    continue
        
        # Suche nach Menge/Anzahl
        quantity_patterns = [
            r'(?:Anzahl|Quantity|Stück|Shares|Menge)[:\s]*([0-9]+[,.]?[0-9]*)',
            r'([0-9]+[,.]?[0-9]*)\s*(?:Stück|Shares|St\.)',
        ]
        
        for pattern in quantity_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    quantity_str = matches[0].replace(',', '.')
                    result['quantity'] = float(quantity_str)
                    result['confidence'] += 20
                    break
                except:
                    continue
        
        # Berechne Gesamtwert falls Preis und Menge vorhanden
        if result['purchase_price'] and result['quantity']:
            result['total_value'] = result['purchase_price'] * result['quantity']
        
        # Suche nach Gesamtwert als Fallback
        if not result['total_value']:
            total_patterns = [
                r'(?:Gesamt|Total|Summe)[:\s]*([0-9]+[,.]?[0-9]*)\s*(?:€|EUR|USD|\$)',
                r'(?:Betrag|Amount)[:\s]*([0-9]+[,.]?[0-9]*)\s*(?:€|EUR|USD|\$)',
            ]
            
            for pattern in total_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        total_str = matches[0].replace(',', '.')
                        result['total_value'] = float(total_str)
                        result['confidence'] += 10
                        break
                    except:
                        continue
        
        return result
    
    def process_investment_document(self, image_path):
        """Vollständige Verarbeitung eines Investitionsbelegs"""
        try:
            # Text extrahieren
            text = self.extract_text_from_image(image_path)
            
            # Investitionsdaten parsen
            parsed_data = self.parse_investment_document(text)
            
            return {
                'success': True,
                'extracted_text': text,
                'parsed_data': parsed_data,
                'message': f'Dokument erfolgreich verarbeitet (Vertrauen: {parsed_data["confidence"]}%)'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Fehler bei der Dokumentenverarbeitung'
            }

