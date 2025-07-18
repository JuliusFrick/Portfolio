from flask import Blueprint, jsonify, request
from src.services.market_data_service import MarketDataService, AlphaVantageService
from src.models.portfolio import PortfolioEntry, db
from datetime import datetime

market_data_bp = Blueprint('market_data', __name__)

# Initialisiere Market Data Services
finnhub_service = MarketDataService()
alpha_vantage_service = AlphaVantageService()

@market_data_bp.route('/market/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    """Holt den aktuellen Kurs für ein Symbol"""
    try:
        symbol = symbol.upper()
        
        # Versuche zuerst Finnhub
        price = finnhub_service.get_current_price(symbol)
        
        # Fallback zu Alpha Vantage falls Finnhub nicht funktioniert
        if price is None:
            price = alpha_vantage_service.get_current_price(symbol)
        
        if price is None:
            return jsonify({
                'success': False,
                'error': f'Kurs für Symbol {symbol} nicht gefunden'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@market_data_bp.route('/market/search', methods=['GET'])
def search_symbols():
    """Sucht nach Aktien-/ETF-Symbolen"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Suchbegriff erforderlich'
            }), 400
        
        results = finnhub_service.search_symbol(query)
        
        return jsonify({
            'success': True,
            'data': results,
            'query': query
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@market_data_bp.route('/market/profile/<symbol>', methods=['GET'])
def get_company_profile(symbol):
    """Holt Unternehmensinformationen"""
    try:
        symbol = symbol.upper()
        profile = finnhub_service.get_company_profile(symbol)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': f'Profil für Symbol {symbol} nicht gefunden'
            }), 404
        
        return jsonify({
            'success': True,
            'data': profile
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@market_data_bp.route('/market/historical/<symbol>', methods=['GET'])
def get_historical_data(symbol):
    """Holt historische Kursdaten"""
    try:
        symbol = symbol.upper()
        days = int(request.args.get('days', 365))
        
        historical_data = finnhub_service.get_historical_data(symbol, days)
        
        if not historical_data:
            return jsonify({
                'success': False,
                'error': f'Historische Daten für Symbol {symbol} nicht gefunden'
            }), 404
        
        return jsonify({
            'success': True,
            'data': historical_data,
            'symbol': symbol,
            'days': days
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@market_data_bp.route('/market/etfs', methods=['GET'])
def get_etf_suggestions():
    """Gibt beliebte ETFs für Vergleiche zurück"""
    try:
        etfs = finnhub_service.get_etf_suggestions()
        
        return jsonify({
            'success': True,
            'data': etfs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@market_data_bp.route('/market/portfolio/update', methods=['POST'])
def update_portfolio_prices():
    """Aktualisiert die Kurse aller Portfolio-Einträge"""
    try:
        entries = PortfolioEntry.query.all()
        
        if not entries:
            return jsonify({
                'success': True,
                'message': 'Keine Portfolio-Einträge zum Aktualisieren',
                'updated_count': 0
            })
        
        # Sammle alle Symbole
        symbols = list(set(entry.symbol for entry in entries))
        
        # Hole aktuelle Kurse
        quotes = finnhub_service.get_multiple_quotes(symbols)
        
        updated_count = 0
        for entry in entries:
            if entry.symbol in quotes:
                entry.update_current_price(quotes[entry.symbol])
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{updated_count} von {len(entries)} Einträgen aktualisiert',
            'updated_count': updated_count,
            'total_entries': len(entries)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@market_data_bp.route('/market/compare', methods=['POST'])
def compare_with_etf():
    """Vergleicht Portfolio-Performance mit ETF"""
    try:
        data = request.json
        etf_symbol = data.get('etf_symbol', 'SPY').upper()
        start_date = data.get('start_date')
        
        if not start_date:
            return jsonify({
                'success': False,
                'error': 'Startdatum erforderlich'
            }), 400
        
        # Portfolio-Performance berechnen
        entries = PortfolioEntry.query.all()
        if not entries:
            return jsonify({
                'success': False,
                'error': 'Keine Portfolio-Einträge vorhanden'
            }), 400
        
        # Gesamtinvestition und aktueller Wert
        total_invested = sum(entry.total_value for entry in entries)
        total_current = sum(entry.current_value for entry in entries if entry.current_value)
        
        if total_current == 0:
            return jsonify({
                'success': False,
                'error': 'Portfolio-Kurse müssen zuerst aktualisiert werden'
            }), 400
        
        portfolio_performance = {
            'initial_value': total_invested,
            'current_value': total_current,
            'profit_loss': total_current - total_invested,
            'profit_loss_percent': ((total_current - total_invested) / total_invested) * 100
        }
        
        # ETF-Performance berechnen
        etf_historical = finnhub_service.get_historical_data(etf_symbol, 365)
        if not etf_historical:
            return jsonify({
                'success': False,
                'error': f'Historische Daten für ETF {etf_symbol} nicht verfügbar'
            }), 404
        
        etf_performance = finnhub_service.calculate_performance(
            etf_historical, start_date, total_invested
        )
        
        if not etf_performance:
            return jsonify({
                'success': False,
                'error': 'ETF-Performance konnte nicht berechnet werden'
            }), 500
        
        # Vergleich
        comparison = {
            'portfolio': portfolio_performance,
            'etf': {
                'symbol': etf_symbol,
                'performance': etf_performance
            },
            'comparison': {
                'portfolio_outperforms': portfolio_performance['profit_loss_percent'] > etf_performance['profit_loss_percent'],
                'difference_percent': portfolio_performance['profit_loss_percent'] - etf_performance['profit_loss_percent']
            }
        }
        
        return jsonify({
            'success': True,
            'data': comparison
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

