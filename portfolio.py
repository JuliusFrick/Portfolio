from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from src.models.portfolio import PortfolioEntry, db
from src.services.ocr_service import OCRService

portfolio_bp = Blueprint('portfolio', __name__)

# Erlaubte Dateierweiterungen für Upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@portfolio_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Gibt alle Portfolio-Einträge zurück"""
    try:
        entries = PortfolioEntry.query.all()
        return jsonify({
            'success': True,
            'data': [entry.to_dict() for entry in entries],
            'total_entries': len(entries)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio_bp.route('/portfolio', methods=['POST'])
def add_portfolio_entry():
    """Fügt einen neuen Portfolio-Eintrag hinzu"""
    try:
        data = request.json
        
        # Validierung der erforderlichen Felder
        required_fields = ['symbol', 'purchase_date', 'purchase_price', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Feld "{field}" ist erforderlich'
                }), 400
        
        # Datum parsen
        try:
            purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Ungültiges Datumsformat. Verwenden Sie YYYY-MM-DD'
            }), 400
        
        # Portfolio-Eintrag erstellen
        entry = PortfolioEntry(
            symbol=data['symbol'],
            purchase_date=purchase_date,
            purchase_price=float(data['purchase_price']),
            quantity=float(data['quantity']),
            company_name=data.get('company_name')
        )
        
        db.session.add(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': entry.to_dict(),
            'message': 'Portfolio-Eintrag erfolgreich hinzugefügt'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio_bp.route('/portfolio/<int:entry_id>', methods=['DELETE'])
def delete_portfolio_entry(entry_id):
    """Löscht einen Portfolio-Eintrag"""
    try:
        entry = PortfolioEntry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio-Eintrag erfolgreich gelöscht'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio_bp.route('/portfolio/upload', methods=['POST'])
def upload_investment_document():
    """Upload und OCR-Verarbeitung von Investitionsbelegen"""
    try:
        # Prüfe ob eine Datei hochgeladen wurde
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Keine Datei hochgeladen'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Keine Datei ausgewählt'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Dateityp nicht erlaubt. Erlaubte Typen: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Sichere Dateinamen erstellen
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        
        # Upload-Verzeichnis erstellen falls nicht vorhanden
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Datei speichern
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # OCR-Verarbeitung
        ocr_service = OCRService()
        result = ocr_service.process_investment_document(file_path)
        
        # Datei nach Verarbeitung löschen (optional)
        try:
            os.remove(file_path)
        except:
            pass
        
        if not result['success']:
            return jsonify(result), 500
        
        # Automatisch Portfolio-Eintrag erstellen falls genügend Daten vorhanden
        parsed_data = result['parsed_data']
        auto_created = False
        
        if (parsed_data['symbol'] and 
            parsed_data['purchase_date'] and 
            parsed_data['purchase_price'] and 
            parsed_data['quantity'] and
            parsed_data['confidence'] >= 60):  # Mindestvertrauen von 60%
            
            try:
                entry = PortfolioEntry(
                    symbol=parsed_data['symbol'],
                    purchase_date=parsed_data['purchase_date'],
                    purchase_price=parsed_data['purchase_price'],
                    quantity=parsed_data['quantity'],
                    company_name=parsed_data['company_name']
                )
                
                db.session.add(entry)
                db.session.commit()
                
                result['auto_created_entry'] = entry.to_dict()
                result['message'] += ' - Portfolio-Eintrag automatisch erstellt'
                auto_created = True
                
            except Exception as e:
                db.session.rollback()
                result['auto_creation_error'] = str(e)
        
        result['auto_created'] = auto_created
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Fehler beim Upload'
        }), 500

@portfolio_bp.route('/portfolio/clear', methods=['DELETE'])
def clear_portfolio():
    """Löscht alle Portfolio-Einträge"""
    try:
        PortfolioEntry.query.delete()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Portfolio erfolgreich geleert'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@portfolio_bp.route('/portfolio/stats', methods=['GET'])
def get_portfolio_stats():
    """Gibt Portfolio-Statistiken zurück"""
    try:
        entries = PortfolioEntry.query.all()
        
        if not entries:
            return jsonify({
                'success': True,
                'data': {
                    'total_entries': 0,
                    'total_invested': 0,
                    'current_value': 0,
                    'total_profit_loss': 0,
                    'total_profit_loss_percent': 0
                }
            })
        
        total_invested = sum(entry.total_value for entry in entries)
        current_value = sum(entry.current_value for entry in entries if entry.current_value)
        total_profit_loss = current_value - total_invested if current_value else 0
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_entries': len(entries),
                'total_invested': round(total_invested, 2),
                'current_value': round(current_value, 2) if current_value else 0,
                'total_profit_loss': round(total_profit_loss, 2),
                'total_profit_loss_percent': round(total_profit_loss_percent, 2)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

