from flask import Blueprint, jsonify, request
from src.models.portfolio import PortfolioEntry
from src.services.market_data_service import MarketDataService
from datetime import datetime, timedelta
import json

charts_bp = Blueprint('charts', __name__)
market_service = MarketDataService()

@charts_bp.route('/charts/portfolio/allocation', methods=['GET'])
def get_portfolio_allocation():
    """Gibt die Portfolio-Allokation für Pie-Chart zurück"""
    try:
        entries = PortfolioEntry.query.all()
        
        if not entries:
            return jsonify({
                'success': False,
                'error': 'Keine Portfolio-Einträge vorhanden'
            }), 404
        
        # Berechne Allokation basierend auf aktuellem Wert oder Investitionswert
        allocation_data = []
        total_value = 0
        
        for entry in entries:
            value = entry.current_value if entry.current_value else entry.total_value
            total_value += value
            
            allocation_data.append({
                'symbol': entry.symbol,
                'company_name': entry.company_name,
                'value': value,
                'quantity': entry.quantity
            })
        
        # Berechne Prozentanteile
        for item in allocation_data:
            item['percentage'] = (item['value'] / total_value * 100) if total_value > 0 else 0
        
        # Sortiere nach Wert (absteigend)
        allocation_data.sort(key=lambda x: x['value'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': allocation_data,
            'total_value': total_value
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@charts_bp.route('/charts/portfolio/performance', methods=['GET'])
def get_portfolio_performance():
    """Gibt Portfolio-Performance über Zeit zurück"""
    try:
        entries = PortfolioEntry.query.all()
        
        if not entries:
            return jsonify({
                'success': False,
                'error': 'Keine Portfolio-Einträge vorhanden'
            }), 404
        
        # Sammle alle Symbole und deren historische Daten
        symbols = list(set(entry.symbol for entry in entries))
        performance_data = []
        
        # Bestimme Zeitraum (letzten 6 Monate oder seit ältestem Kauf)
        oldest_date = min(entry.purchase_date for entry in entries)
        start_date = max(oldest_date, (datetime.now() - timedelta(days=180)).date())
        
        # Hole historische Daten für alle Symbole
        historical_data = {}
        for symbol in symbols:
            hist_data = market_service.get_historical_data(symbol, 180)
            if hist_data:
                historical_data[symbol] = {item['date']: item['close'] for item in hist_data}
        
        # Berechne Portfolio-Wert für jeden Tag
        current_date = start_date
        end_date = datetime.now().date()
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_value = 0
            daily_invested = 0
            
            for entry in entries:
                # Nur Einträge berücksichtigen, die bereits gekauft wurden
                if entry.purchase_date <= current_date:
                    daily_invested += entry.total_value
                    
                    # Aktueller Wert basierend auf historischem Kurs
                    if entry.symbol in historical_data and date_str in historical_data[entry.symbol]:
                        current_price = historical_data[entry.symbol][date_str]
                        daily_value += entry.quantity * current_price
                    else:
                        # Fallback: Verwende Kaufpreis wenn kein historischer Kurs verfügbar
                        daily_value += entry.total_value
            
            if daily_invested > 0:  # Nur Tage mit Investitionen
                performance_data.append({
                    'date': date_str,
                    'portfolio_value': daily_value,
                    'invested_value': daily_invested,
                    'profit_loss': daily_value - daily_invested,
                    'profit_loss_percent': ((daily_value - daily_invested) / daily_invested * 100) if daily_invested > 0 else 0
                })
            
            current_date += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'data': performance_data,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@charts_bp.route('/charts/portfolio/vs-etf/<etf_symbol>', methods=['GET'])
def get_portfolio_vs_etf_chart(etf_symbol):
    """Vergleicht Portfolio-Performance mit ETF über Zeit"""
    try:
        entries = PortfolioEntry.query.all()
        
        if not entries:
            return jsonify({
                'success': False,
                'error': 'Keine Portfolio-Einträge vorhanden'
            }), 404
        
        etf_symbol = etf_symbol.upper()
        days = int(request.args.get('days', 180))
        
        # Hole ETF historische Daten
        etf_historical = market_service.get_historical_data(etf_symbol, days)
        if not etf_historical:
            return jsonify({
                'success': False,
                'error': f'Keine historischen Daten für {etf_symbol} verfügbar'
            }), 404
        
        # Portfolio historische Performance (vereinfacht)
        portfolio_symbols = list(set(entry.symbol for entry in entries))
        portfolio_historical = {}
        
        for symbol in portfolio_symbols:
            hist_data = market_service.get_historical_data(symbol, days)
            if hist_data:
                portfolio_historical[symbol] = {item['date']: item['close'] for item in hist_data}
        
        # Berechne vergleichende Performance
        comparison_data = []
        total_invested = sum(entry.total_value for entry in entries)
        
        # ETF Startpreis für Normalisierung
        etf_start_price = etf_historical[0]['close']
        
        for etf_data in etf_historical:
            date_str = etf_data['date']
            
            # ETF Performance (normalisiert auf 100)
            etf_performance = (etf_data['close'] / etf_start_price) * 100
            
            # Portfolio Performance für dieses Datum
            portfolio_value = 0
            for entry in entries:
                if entry.symbol in portfolio_historical and date_str in portfolio_historical[entry.symbol]:
                    current_price = portfolio_historical[entry.symbol][date_str]
                    portfolio_value += entry.quantity * current_price
                else:
                    # Fallback
                    portfolio_value += entry.total_value
            
            portfolio_performance = (portfolio_value / total_invested) * 100 if total_invested > 0 else 100
            
            comparison_data.append({
                'date': date_str,
                'portfolio_performance': portfolio_performance,
                'etf_performance': etf_performance,
                'portfolio_value': portfolio_value,
                'etf_value': (etf_data['close'] / etf_start_price) * total_invested
            })
        
        return jsonify({
            'success': True,
            'data': comparison_data,
            'etf_symbol': etf_symbol,
            'total_invested': total_invested
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@charts_bp.route('/charts/portfolio/profit-loss', methods=['GET'])
def get_profit_loss_chart():
    """Gibt Gewinn/Verlust-Daten für jede Position zurück"""
    try:
        entries = PortfolioEntry.query.all()
        
        if not entries:
            return jsonify({
                'success': False,
                'error': 'Keine Portfolio-Einträge vorhanden'
            }), 404
        
        profit_loss_data = []
        
        for entry in entries:
            if entry.current_value:
                profit_loss = entry.current_value - entry.total_value
                profit_loss_percent = (profit_loss / entry.total_value * 100) if entry.total_value > 0 else 0
                
                profit_loss_data.append({
                    'symbol': entry.symbol,
                    'company_name': entry.company_name,
                    'invested': entry.total_value,
                    'current_value': entry.current_value,
                    'profit_loss': profit_loss,
                    'profit_loss_percent': profit_loss_percent,
                    'quantity': entry.quantity
                })
        
        # Sortiere nach Gewinn/Verlust
        profit_loss_data.sort(key=lambda x: x['profit_loss'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': profit_loss_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@charts_bp.route('/charts/market/trending', methods=['GET'])
def get_trending_stocks():
    """Gibt Trending-Aktien zurück (Mock-Daten für Demo)"""
    try:
        # In einer echten Anwendung würde man hier echte Trending-Daten von der API holen
        trending_stocks = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'change_percent': 2.5},
            {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'change_percent': 1.8},
            {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'change_percent': -0.5},
            {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'change_percent': 3.2},
            {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'change_percent': -2.1},
            {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'change_percent': 4.7},
            {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'change_percent': 1.2},
            {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'change_percent': -1.8}
        ]
        
        return jsonify({
            'success': True,
            'data': trending_stocks
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

