import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional

class MarketDataService:
    def __init__(self, api_key: str = None):
        # Finnhub API - kostenlos mit 60 Anfragen/Minute
        self.finnhub_api_key = api_key or "demo"  # Demo-Key für Tests
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.1  # Etwas mehr als 1 Sekunde für 60 req/min
        
    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Macht eine API-Anfrage mit Rate Limiting"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            params['token'] = self.finnhub_api_key
            response = requests.get(url, params=params, timeout=10)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Holt den aktuellen Kurs für ein Symbol"""
        url = f"{self.finnhub_base_url}/quote"
        params = {'symbol': symbol}
        
        data = self._make_request(url, params)
        if data and 'c' in data:
            return float(data['c'])  # 'c' ist der aktuelle Preis
        return None
    
    def get_historical_data(self, symbol: str, days: int = 365) -> Optional[List[Dict]]:
        """Holt historische Kursdaten für ein Symbol"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = f"{self.finnhub_base_url}/stock/candle"
        params = {
            'symbol': symbol,
            'resolution': 'D',  # Tägliche Daten
            'from': int(start_date.timestamp()),
            'to': int(end_date.timestamp())
        }
        
        data = self._make_request(url, params)
        if data and data.get('s') == 'ok':
            # Konvertiere zu Liste von Dictionaries
            historical_data = []
            for i in range(len(data['t'])):
                historical_data.append({
                    'date': datetime.fromtimestamp(data['t'][i]).strftime('%Y-%m-%d'),
                    'open': data['o'][i],
                    'high': data['h'][i],
                    'low': data['l'][i],
                    'close': data['c'][i],
                    'volume': data['v'][i]
                })
            return historical_data
        return None
    
    def search_symbol(self, query: str) -> List[Dict]:
        """Sucht nach Aktien-/ETF-Symbolen"""
        url = f"{self.finnhub_base_url}/search"
        params = {'q': query}
        
        data = self._make_request(url, params)
        if data and 'result' in data:
            return data['result'][:10]  # Limitiere auf 10 Ergebnisse
        return []
    
    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """Holt Unternehmensinformationen"""
        url = f"{self.finnhub_base_url}/stock/profile2"
        params = {'symbol': symbol}
        
        data = self._make_request(url, params)
        return data if data else None
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, float]:
        """Holt aktuelle Kurse für mehrere Symbole"""
        quotes = {}
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                quotes[symbol] = price
            # Kleine Pause zwischen Anfragen
            time.sleep(0.1)
        return quotes
    
    def get_etf_suggestions(self) -> List[Dict]:
        """Gibt eine Liste beliebter ETFs für Vergleiche zurück"""
        popular_etfs = [
            {'symbol': 'SPY', 'name': 'SPDR S&P 500 ETF Trust', 'description': 'S&P 500 Index'},
            {'symbol': 'QQQ', 'name': 'Invesco QQQ Trust', 'description': 'NASDAQ-100 Index'},
            {'symbol': 'VTI', 'name': 'Vanguard Total Stock Market ETF', 'description': 'Total Stock Market'},
            {'symbol': 'IVV', 'name': 'iShares Core S&P 500 ETF', 'description': 'S&P 500 Index'},
            {'symbol': 'VEA', 'name': 'Vanguard FTSE Developed Markets ETF', 'description': 'International Developed Markets'},
            {'symbol': 'VWO', 'name': 'Vanguard FTSE Emerging Markets ETF', 'description': 'Emerging Markets'},
            {'symbol': 'BND', 'name': 'Vanguard Total Bond Market ETF', 'description': 'Total Bond Market'},
            {'symbol': 'GLD', 'name': 'SPDR Gold Shares', 'description': 'Gold'},
            {'symbol': 'VNQ', 'name': 'Vanguard Real Estate ETF', 'description': 'Real Estate Investment Trusts'},
            {'symbol': 'EFA', 'name': 'iShares MSCI EAFE ETF', 'description': 'Europe, Australasia, Far East'}
        ]
        return popular_etfs
    
    def calculate_performance(self, historical_data: List[Dict], investment_date: str, investment_amount: float) -> Dict:
        """Berechnet die Performance seit einem bestimmten Investitionsdatum"""
        if not historical_data:
            return None
        
        # Finde den Kurs am nächsten verfügbaren Datum zum Investitionsdatum
        investment_datetime = datetime.strptime(investment_date, '%Y-%m-%d')
        
        closest_data = None
        min_diff = float('inf')
        
        for data_point in historical_data:
            data_date = datetime.strptime(data_point['date'], '%Y-%m-%d')
            diff = abs((data_date - investment_datetime).days)
            if diff < min_diff:
                min_diff = diff
                closest_data = data_point
        
        if not closest_data:
            return None
        
        # Aktueller Kurs (letzter Datenpunkt)
        current_data = historical_data[-1]
        
        initial_price = closest_data['close']
        current_price = current_data['close']
        
        # Berechne Performance
        shares = investment_amount / initial_price
        current_value = shares * current_price
        profit_loss = current_value - investment_amount
        profit_loss_percent = (profit_loss / investment_amount) * 100
        
        return {
            'initial_price': initial_price,
            'current_price': current_price,
            'initial_investment': investment_amount,
            'current_value': current_value,
            'profit_loss': profit_loss,
            'profit_loss_percent': profit_loss_percent,
            'shares': shares,
            'investment_date': closest_data['date'],
            'current_date': current_data['date']
        }

# Alpha Vantage als Fallback (falls Finnhub nicht verfügbar)
class AlphaVantageService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "demo"
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.min_request_interval = 12  # 5 Anfragen pro Minute = 12 Sekunden zwischen Anfragen
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Macht eine API-Anfrage mit Rate Limiting"""
        try:
            # Rate limiting für Alpha Vantage (5 req/min)
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            params['apikey'] = self.api_key
            response = requests.get(self.base_url, params=params, timeout=15)
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Alpha Vantage API Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Alpha Vantage request error: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Holt den aktuellen Kurs über Alpha Vantage"""
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }
        
        data = self._make_request(params)
        if data and 'Global Quote' in data:
            price_str = data['Global Quote'].get('05. price', '0')
            try:
                return float(price_str)
            except:
                return None
        return None

