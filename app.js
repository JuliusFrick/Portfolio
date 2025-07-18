// Portfolio Manager JavaScript

class PortfolioManager {
    constructor() {
        this.apiBase = '/api';
        this.portfolio = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadPortfolio();
        this.setDefaultDate();
    }

    setupEventListeners() {
        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        fileInput.addEventListener('change', (e) => this.handleFileUpload(e));

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.uploadFile(files[0]);
            }
        });

        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });

        // Manual entry form
        document.getElementById('manualEntryForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.addManualEntry();
        });
    }

    setDefaultDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('manualDate').value = today;
        document.getElementById('comparisonStartDate').value = today;
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
            await this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        const uploadArea = document.getElementById('uploadArea');
        const resultDiv = document.getElementById('uploadResult');
        
        // Show processing state
        uploadArea.classList.add('processing');
        uploadArea.innerHTML = `
            <div class="upload-icon"><div class="loading"></div></div>
            <div class="upload-text">Dokument wird verarbeitet...</div>
        `;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${this.apiBase}/portfolio/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', result.message);
                
                // Show OCR results
                if (result.parsed_data) {
                    this.displayOCRResult(result.parsed_data, result.auto_created);
                }

                // Reload portfolio if entry was auto-created
                if (result.auto_created) {
                    await this.loadPortfolio();
                }
            } else {
                this.showAlert('error', result.error || 'Upload fehlgeschlagen');
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Upload');
            console.error('Upload error:', error);
        } finally {
            // Reset upload area
            uploadArea.classList.remove('processing');
            uploadArea.innerHTML = `
                <div class="upload-icon">📁</div>
                <div class="upload-text">
                    Investitionsbeleg hier ablegen oder klicken zum Auswählen
                </div>
                <div style="font-size: 0.9rem; color: #a0aec0;">
                    Unterstützte Formate: PNG, JPG, PDF
                </div>
            `;
            
            // Clear file input
            document.getElementById('fileInput').value = '';
        }
    }

    displayOCRResult(parsedData, autoCreated) {
        const resultDiv = document.getElementById('uploadResult');
        
        const confidenceClass = parsedData.confidence >= 70 ? 'confidence-high' : 
                               parsedData.confidence >= 40 ? 'confidence-medium' : 'confidence-low';
        
        const confidenceText = parsedData.confidence >= 70 ? 'Hoch' : 
                              parsedData.confidence >= 40 ? 'Mittel' : 'Niedrig';

        resultDiv.innerHTML = `
            <div class="ocr-result">
                <h4>OCR-Ergebnis 
                    <span class="ocr-confidence ${confidenceClass}">
                        Vertrauen: ${confidenceText} (${parsedData.confidence}%)
                    </span>
                </h4>
                <div style="margin-top: 15px;">
                    <strong>Erkannte Daten:</strong><br>
                    Symbol: ${parsedData.symbol || 'Nicht erkannt'}<br>
                    Firma: ${parsedData.company_name || 'Nicht erkannt'}<br>
                    Datum: ${parsedData.purchase_date || 'Nicht erkannt'}<br>
                    Preis: ${parsedData.purchase_price ? '€' + parsedData.purchase_price : 'Nicht erkannt'}<br>
                    Menge: ${parsedData.quantity || 'Nicht erkannt'}
                </div>
                ${autoCreated ? 
                    '<div class="alert alert-success" style="margin-top: 15px;">Portfolio-Eintrag wurde automatisch erstellt!</div>' :
                    '<div class="alert alert-info" style="margin-top: 15px;">Vertrauen zu niedrig für automatische Erstellung. Bitte manuell hinzufügen.</div>'
                }
            </div>
        `;
    }

    async addManualEntry() {
        const formData = {
            symbol: document.getElementById('manualSymbol').value.trim().toUpperCase(),
            company_name: document.getElementById('manualCompany').value.trim() || null,
            purchase_date: document.getElementById('manualDate').value,
            purchase_price: parseFloat(document.getElementById('manualPrice').value),
            quantity: parseFloat(document.getElementById('manualQuantity').value)
        };

        try {
            const response = await fetch(`${this.apiBase}/portfolio`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', 'Position erfolgreich hinzugefügt');
                document.getElementById('manualEntryForm').reset();
                this.setDefaultDate();
                await this.loadPortfolio();
            } else {
                this.showAlert('error', result.error || 'Fehler beim Hinzufügen');
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Hinzufügen');
            console.error('Add entry error:', error);
        }
    }

    async loadPortfolio() {
        try {
            const response = await fetch(`${this.apiBase}/portfolio`);
            const result = await response.json();

            if (result.success) {
                this.portfolio = result.data;
                this.displayPortfolio();
                await this.loadPortfolioStats();
            } else {
                this.showAlert('error', 'Fehler beim Laden des Portfolios');
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Laden');
            console.error('Load portfolio error:', error);
        }
    }

    async loadPortfolioStats() {
        try {
            const response = await fetch(`${this.apiBase}/portfolio/stats`);
            const result = await response.json();

            if (result.success) {
                const stats = result.data;
                document.getElementById('totalEntries').textContent = stats.total_entries;
                document.getElementById('totalInvested').textContent = `€${stats.total_invested.toFixed(2)}`;
                document.getElementById('currentValue').textContent = `€${stats.current_value.toFixed(2)}`;
                
                const profitLossElement = document.getElementById('totalProfitLoss');
                profitLossElement.textContent = `€${stats.total_profit_loss.toFixed(2)} (${stats.total_profit_loss_percent.toFixed(2)}%)`;
                profitLossElement.className = `stat-value ${stats.total_profit_loss >= 0 ? 'profit' : 'loss'}`;
            }

        } catch (error) {
            console.error('Load stats error:', error);
        }
    }

    displayPortfolio() {
        const contentDiv = document.getElementById('portfolioContent');

        if (this.portfolio.length === 0) {
            contentDiv.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📈</div>
                    <h3>Noch keine Investitionen</h3>
                    <p>Laden Sie einen Investitionsbeleg hoch oder fügen Sie manuell eine Position hinzu.</p>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <table class="portfolio-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Firma</th>
                        <th>Kaufdatum</th>
                        <th>Kaufpreis</th>
                        <th>Menge</th>
                        <th>Investiert</th>
                        <th>Aktueller Kurs</th>
                        <th>Aktueller Wert</th>
                        <th>Gewinn/Verlust</th>
                        <th>Aktionen</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.portfolio.map(entry => this.renderPortfolioRow(entry)).join('')}
                </tbody>
            </table>
        `;

        contentDiv.innerHTML = tableHTML;
    }

    renderPortfolioRow(entry) {
        const profitLoss = entry.profit_loss || 0;
        const profitLossPercent = entry.profit_loss_percent || 0;
        const profitLossClass = profitLoss >= 0 ? 'profit' : 'loss';
        const profitLossSymbol = profitLoss >= 0 ? '+' : '';

        return `
            <tr>
                <td><strong>${entry.symbol}</strong></td>
                <td>${entry.company_name || '-'}</td>
                <td>${new Date(entry.purchase_date).toLocaleDateString('de-DE')}</td>
                <td>€${entry.purchase_price.toFixed(2)}</td>
                <td>${entry.quantity}</td>
                <td>€${entry.total_value.toFixed(2)}</td>
                <td>${entry.current_price ? '€' + entry.current_price.toFixed(2) : '-'}</td>
                <td>${entry.current_value ? '€' + entry.current_value.toFixed(2) : '-'}</td>
                <td class="${profitLossClass}">
                    ${entry.current_value ? 
                        `${profitLossSymbol}€${profitLoss.toFixed(2)} (${profitLossSymbol}${profitLossPercent.toFixed(2)}%)` : 
                        '-'
                    }
                </td>
                <td>
                    <button class="btn btn-danger" style="padding: 5px 10px; font-size: 0.8rem;" 
                            onclick="portfolioManager.deleteEntry(${entry.id})">
                        Löschen
                    </button>
                </td>
            </tr>
        `;
    }

    async deleteEntry(entryId) {
        if (!confirm('Möchten Sie diesen Eintrag wirklich löschen?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/portfolio/${entryId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', 'Eintrag gelöscht');
                await this.loadPortfolio();
            } else {
                this.showAlert('error', result.error || 'Fehler beim Löschen');
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Löschen');
            console.error('Delete entry error:', error);
        }
    }

    async updateAllPrices() {
        const button = document.getElementById('updatePricesBtn');
        const originalText = button.textContent;
        
        button.disabled = true;
        button.innerHTML = '<div class="loading" style="width: 16px; height: 16px;"></div> Aktualisiere...';

        try {
            const response = await fetch(`${this.apiBase}/market/portfolio/update`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', result.message);
                await this.loadPortfolio();
            } else {
                this.showAlert('error', result.error || 'Fehler beim Aktualisieren');
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Aktualisieren');
            console.error('Update prices error:', error);
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }

    async clearPortfolio() {
        if (!confirm('Möchten Sie wirklich das gesamte Portfolio löschen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/portfolio/clear`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showAlert('success', 'Portfolio geleert');
                await this.loadPortfolio();
            } else {
                this.showAlert('error', result.error || 'Fehler beim Leeren');
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Leeren');
            console.error('Clear portfolio error:', error);
        }
    }

    async compareWithETF() {
        const etfSymbol = document.getElementById('etfSelect').value;
        const startDate = document.getElementById('comparisonStartDate').value;
        const button = document.getElementById('compareBtn');
        const resultDiv = document.getElementById('comparisonResult');

        if (!startDate) {
            this.showAlert('error', 'Bitte wählen Sie ein Startdatum');
            return;
        }

        if (this.portfolio.length === 0) {
            this.showAlert('error', 'Portfolio ist leer');
            return;
        }

        button.disabled = true;
        button.innerHTML = '<div class="loading" style="width: 16px; height: 16px;"></div> Vergleiche...';

        try {
            const response = await fetch(`${this.apiBase}/market/compare`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    etf_symbol: etfSymbol,
                    start_date: startDate
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayComparison(result.data);
            } else {
                this.showAlert('error', result.error || 'Fehler beim Vergleich');
                resultDiv.innerHTML = '';
            }

        } catch (error) {
            this.showAlert('error', 'Netzwerkfehler beim Vergleich');
            console.error('Compare error:', error);
            resultDiv.innerHTML = '';
        } finally {
            button.disabled = false;
            button.textContent = 'Vergleichen';
        }
    }

    displayComparison(data) {
        const resultDiv = document.getElementById('comparisonResult');
        const portfolio = data.portfolio;
        const etf = data.etf;
        const comparison = data.comparison;

        const portfolioClass = portfolio.profit_loss >= 0 ? 'profit' : 'loss';
        const etfClass = etf.performance.profit_loss >= 0 ? 'profit' : 'loss';
        const winnerClass = comparison.portfolio_outperforms ? 'profit' : 'loss';

        resultDiv.innerHTML = `
            <div class="comparison-result">
                <div class="performance-card">
                    <h3>📊 Ihr Portfolio</h3>
                    <div class="performance-metric">
                        <span>Investiert:</span>
                        <span>€${portfolio.initial_value.toFixed(2)}</span>
                    </div>
                    <div class="performance-metric">
                        <span>Aktueller Wert:</span>
                        <span>€${portfolio.current_value.toFixed(2)}</span>
                    </div>
                    <div class="performance-metric">
                        <span>Gewinn/Verlust:</span>
                        <span class="${portfolioClass}">
                            €${portfolio.profit_loss.toFixed(2)} (${portfolio.profit_loss_percent.toFixed(2)}%)
                        </span>
                    </div>
                </div>

                <div class="performance-card">
                    <h3>📈 ${etf.symbol} ETF</h3>
                    <div class="performance-metric">
                        <span>Investiert:</span>
                        <span>€${etf.performance.initial_investment.toFixed(2)}</span>
                    </div>
                    <div class="performance-metric">
                        <span>Aktueller Wert:</span>
                        <span>€${etf.performance.current_value.toFixed(2)}</span>
                    </div>
                    <div class="performance-metric">
                        <span>Gewinn/Verlust:</span>
                        <span class="${etfClass}">
                            €${etf.performance.profit_loss.toFixed(2)} (${etf.performance.profit_loss_percent.toFixed(2)}%)
                        </span>
                    </div>
                </div>
            </div>

            <div class="alert ${comparison.portfolio_outperforms ? 'alert-success' : 'alert-info'}" style="margin-top: 20px;">
                <strong>Ergebnis:</strong> 
                ${comparison.portfolio_outperforms ? 
                    `Ihr Portfolio übertrifft den ${etf.symbol} ETF um ${comparison.difference_percent.toFixed(2)} Prozentpunkte! 🎉` :
                    `Der ${etf.symbol} ETF übertrifft Ihr Portfolio um ${Math.abs(comparison.difference_percent).toFixed(2)} Prozentpunkte.`
                }
            </div>
        `;
    }

    showAlert(type, message) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        });

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        // Insert at the top of the container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    }
}

// Initialize the portfolio manager when the page loads
let portfolioManager;
document.addEventListener('DOMContentLoaded', () => {
    portfolioManager = new PortfolioManager();
});

// Global functions for inline event handlers
function updateAllPrices() {
    portfolioManager.updateAllPrices();
}

function clearPortfolio() {
    portfolioManager.clearPortfolio();
}

function compareWithETF() {
    portfolioManager.compareWithETF();
}

