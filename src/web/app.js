/**
 * EUR-Lex Trade Scraper Dashboard
 * Frontend JavaScript for dashboard interactivity
 */

class EURLexTradeScraperDashboard {
    constructor() {
        console.log('🇪🇺 Initializing EUR-Lex Trade Scraper Dashboard...');
        this.currentData = null;
        this.charts = {};
        this.autoHideTimeout = null;
        
        this.init();
    }
    
    async init() {
        console.log('🔧 Setting up event listeners...');
        this.setupEventListeners();
        
        console.log('📊 Loading initial dashboard data...');
        await this.loadDashboardData();
        
        console.log('✅ Dashboard initialization complete');
    }
    
    setupEventListeners() {
        // Scrape button
        const scrapeBtn = document.getElementById('scrapeBtn');
        if (scrapeBtn) {
            scrapeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.triggerScrape();
            });
        }
        
        // Export CSV button
        const exportBtn = document.getElementById('exportCsvBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportCsv();
            });
        }
        
        // Clear filters button
        const clearBtn = document.getElementById('clearFiltersBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.clearFilters();
            });
        }
        
        // Filter change listeners
        const filterElements = ['startDate', 'endDate', 'authorFilter', 'companyFilter', 'productFilter'];
        filterElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => this.applyFilters());
            }
        });
        
        // Search input with debouncing
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => this.applyFilters(), 300);
            });
        }
        
        // Sort dropdown
        const sortItems = document.querySelectorAll('[data-sort]');
        sortItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const sortBy = e.target.getAttribute('data-sort');
                this.sortResults(sortBy);
            });
        });
        
        console.log('✅ All event listeners set up successfully');
        
        // Show serverless notice if no data is available initially
        setTimeout(() => {
            if (this.currentData && this.currentData.statistics.total_documents === 0) {
                const notice = document.getElementById('serverlessNotice');
                if (notice) {
                    notice.style.display = 'block';
                }
            }
        }, 2000);
    }
    
    async loadDashboardData() {
        try {
            console.log('🌐 Fetching from /api/dashboard-data...');
            const response = await fetch('/api/dashboard-data');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            console.log('📡 Dashboard response:', response.status, response.statusText);
            
            const data = await response.json();
            console.log('📊 Dashboard data received:', data);
            
            this.currentData = data;
            console.log('💾 Stored data in currentData');
            
            console.log('🔄 Updating dashboard...');
            this.updateDashboard(data);
            
            console.log('📈 Initializing charts...');
            await this.initializeCharts(data);
            
            console.log('🔍 Loading filter options...');
            await this.loadFilterOptions();
            
            console.log('✅ Dashboard data loaded successfully');
            
        } catch (error) {
            console.error('❌ Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data: ' + error.message);
        }
    }
    
    updateDashboard(data) {
        try {
            // Update KPIs
            this.updateKPIs(data);
            
            // Update results table
            this.updateResultsTable(data.results || []);
            
            console.log('✅ Dashboard updated successfully');
        } catch (error) {
            console.error('❌ Error updating dashboard:', error);
        }
    }
    
    updateKPIs(data) {
        const stats = data.statistics || {};
        const results = this.currentData?.results || [];
        
        // Total documents
        const totalElement = document.getElementById('totalDocuments');
        if (totalElement) {
            totalElement.textContent = stats.total_documents || 0;
        }
        
        // This month's documents
        const todayElement = document.getElementById('todayDocuments');
        if (todayElement) {
            const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM
            const thisMonthDocs = results.filter(doc => 
                doc.publication_date && doc.publication_date.startsWith(currentMonth)
            ).length;
            todayElement.textContent = thisMonthDocs;
        }
        
        // Last scrape
        const lastScrapeElement = document.getElementById('lastScrape');
        const scrapeStatusElement = document.getElementById('scrapeStatus');
        
        if (stats.last_run) {
            if (lastScrapeElement) {
                lastScrapeElement.textContent = this.formatDateTime(stats.last_run);
            }
            if (scrapeStatusElement) {
                scrapeStatusElement.textContent = 'Complete';
            }
        } else {
            if (lastScrapeElement) {
                lastScrapeElement.textContent = 'Never';
            }
            if (scrapeStatusElement) {
                scrapeStatusElement.textContent = 'Idle';
            }
        }
        
        console.log('📊 KPIs updated');
    }
    
    updateResultsTable(results) {
        const tbody = document.getElementById('resultsTableBody');
        const showingCount = document.getElementById('showingCount');
        
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!results || results.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="10" class="text-center text-muted py-4">
                        <i class="ti ti-inbox icon mb-2"></i><br>
                        No documents found
                    </td>
                </tr>
            `;
            if (showingCount) showingCount.textContent = '0';
            return;
        }
        
        results.forEach(doc => {
            const row = this.createTableRow(doc);
            tbody.appendChild(row);
        });
        
        if (showingCount) {
            showingCount.textContent = results.length.toLocaleString();
        }
        
        console.log(`📋 Table updated with ${results.length} documents`);
    }
    
    createTableRow(doc) {
        const row = document.createElement('tr');
        
        // Format data
        const date = doc.publication_date || 'N/A';
        const title = doc.title || 'Untitled';
        const type = doc.form || 'N/A';
        const docNumber = doc.document_number || 'N/A';
        const author = doc.author || 'N/A';
        const companies = this.formatCompanies(doc.companies);
        const products = this.formatProducts(doc.products);
        const keywords = this.formatKeywordMatches(doc.match_details);
        const criteria = this.formatCriteria(doc.match_details);
        
        row.innerHTML = `
            <td>
                <span class="text-muted">${date}</span>
            </td>
            <td>
                <div class="text-truncate" style="max-width: 300px;" title="${title}">
                    ${title}
                </div>
            </td>
            <td>
                <span class="badge badge-outline text-blue">${type}</span>
            </td>
            <td>
                <code class="text-muted">${docNumber}</code>
            </td>
            <td>
                <span class="text-muted">${author}</span>
            </td>
            <td>${companies}</td>
            <td>${products}</td>
            <td>${keywords}</td>
            <td>${criteria}</td>
            <td>
                <div class="btn-list">
                    <button class="btn btn-sm btn-outline-primary" onclick="dashboard.showDocumentDetails('${docNumber}')">
                        <i class="ti ti-eye"></i> View
                    </button>
                    ${doc.eurlex_url ? `
                    <a href="${doc.eurlex_url}" target="_blank" class="btn btn-sm btn-outline-secondary">
                        <i class="ti ti-external-link"></i>
                    </a>
                    ` : ''}
                </div>
            </td>
        `;
        
        return row;
    }
    
    formatCompanies(companies) {
        if (!companies || companies.length === 0) return '<span class="text-muted">-</span>';
        
        const badges = companies.slice(0, 3).map(company => 
            `<span class="badge badge-outline text-green me-1">${company}</span>`
        ).join('');
        
        const extra = companies.length > 3 ? `<span class="text-muted">+${companies.length - 3}</span>` : '';
        
        return badges + extra;
    }
    
    formatProducts(products) {
        if (!products || products.length === 0) return '<span class="text-muted">-</span>';
        
        const badges = products.slice(0, 2).map(product => 
            `<span class="badge badge-outline text-orange me-1">${product}</span>`
        ).join('');
        
        const extra = products.length > 2 ? `<span class="text-muted">+${products.length - 2}</span>` : '';
        
        return badges + extra;
    }
    
    formatKeywordMatches(matchDetails) {
        if (!matchDetails) return '<span class="text-muted">-</span>';
        
        let html = '<div class="d-flex flex-column gap-1">';
        
        // Measures (Group A) - Blue badges
        if (matchDetails.measure_keywords && matchDetails.measure_keywords.length > 0) {
            const measures = matchDetails.measure_keywords.slice(0, 3); // Show max 3
            const extra = matchDetails.measure_keywords.length > 3 ? `+${matchDetails.measure_keywords.length - 3}` : '';
            html += '<div>';
            measures.forEach(keyword => {
                html += `<span class="badge badge-outline text-blue me-1" style="font-size: 0.65em;">${keyword}</span>`;
            });
            if (extra) html += `<span class="text-muted small">${extra}</span>`;
            html += '</div>';
        }
        
        // Products (Group B) - Orange badges  
        if (matchDetails.product_keywords && matchDetails.product_keywords.length > 0) {
            const products = matchDetails.product_keywords.slice(0, 3); // Show max 3
            const extra = matchDetails.product_keywords.length > 3 ? `+${matchDetails.product_keywords.length - 3}` : '';
            html += '<div>';
            products.forEach(keyword => {
                html += `<span class="badge badge-outline text-orange me-1" style="font-size: 0.65em;">${keyword}</span>`;
            });
            if (extra) html += `<span class="text-muted small">${extra}</span>`;
            html += '</div>';
        }
        
        // Places/Companies (Group C) - Green badges
        if (matchDetails.place_company_keywords && matchDetails.place_company_keywords.length > 0) {
            const places = matchDetails.place_company_keywords.slice(0, 3); // Show max 3
            const extra = matchDetails.place_company_keywords.length > 3 ? `+${matchDetails.place_company_keywords.length - 3}` : '';
            html += '<div>';
            places.forEach(keyword => {
                html += `<span class="badge badge-outline text-green me-1" style="font-size: 0.65em;">${keyword}</span>`;
            });
            if (extra) html += `<span class="text-muted small">${extra}</span>`;
            html += '</div>';
        }
        
        html += '</div>';
        
        // If no keywords matched, show fallback
        if (!matchDetails.measure_keywords?.length && 
            !matchDetails.product_keywords?.length && 
            !matchDetails.place_company_keywords?.length) {
            return '<span class="text-muted">No matches</span>';
        }
        
        return html;
    }
    
    formatCriteria(matchDetails) {
        if (!matchDetails) return '<span class="text-muted">-</span>';
        
        const groups = matchDetails.groups_matched || 0;
        const total = matchDetails.total_groups || 3;
        
        const color = groups === total ? 'text-green' : 'text-yellow';
        
        return `<span class="badge badge-outline ${color}">${groups}/${total} groups</span>`;
    }
    
    formatDateTime(isoString) {
        try {
            return new Date(isoString).toLocaleString();
        } catch {
            return isoString;
        }
    }
    
    async loadFilterOptions() {
        try {
            console.log('🌐 Fetching filter data from multiple endpoints...');
            
            const [authorsResp, companiesResp, productsResp] = await Promise.all([
                fetch('/api/authors'),
                fetch('/api/companies'),
                fetch('/api/products')
            ]);
            
            const authorsData = await authorsResp.json();
            const companiesData = await companiesResp.json();
            const productsData = await productsResp.json();
            
            console.log('📊 Filter data received:', {
                authors: authorsData.authors?.length || 0,
                companies: companiesData.companies?.length || 0,
                products: productsData.products?.length || 0
            });
            
            // Populate dropdowns
            this.populateSelect('authorFilter', authorsData.authors || []);
            this.populateSelect('companyFilter', companiesData.companies || []);
            this.populateSelect('productFilter', productsData.products || []);
            
            console.log('✅ Filter options loaded successfully');
            
        } catch (error) {
            console.error('❌ Error loading filter options:', error);
        }
    }
    
    populateSelect(selectId, options) {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        // Keep the first option (e.g., "All Authors")
        const firstOption = select.querySelector('option');
        select.innerHTML = '';
        if (firstOption) {
            select.appendChild(firstOption);
        }
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            select.appendChild(optionElement);
        });
    }
    
    async applyFilters() {
        if (!this.currentData) return;
        
        const filters = this.getFilters();
        console.log('🔍 Applying filters:', filters);
        
        let filtered = this.currentData.results || [];
        
        // Apply filters locally
        if (filters.start_date) {
            filtered = filtered.filter(doc => doc.publication_date >= filters.start_date);
        }
        
        if (filters.end_date) {
            filtered = filtered.filter(doc => doc.publication_date <= filters.end_date);
        }
        
        if (filters.author) {
            filtered = filtered.filter(doc => 
                doc.author && doc.author.toLowerCase().includes(filters.author.toLowerCase())
            );
        }
        
        if (filters.company) {
            filtered = filtered.filter(doc => 
                doc.companies && doc.companies.some(company => 
                    company.toLowerCase().includes(filters.company.toLowerCase())
                )
            );
        }
        
        if (filters.product) {
            filtered = filtered.filter(doc => 
                doc.products && doc.products.some(product => 
                    product.toLowerCase().includes(filters.product.toLowerCase())
                )
            );
        }
        
        if (filters.search) {
            const searchTerm = filters.search.toLowerCase();
            filtered = filtered.filter(doc => 
                (doc.title && doc.title.toLowerCase().includes(searchTerm)) ||
                (doc.text && doc.text.toLowerCase().includes(searchTerm))
            );
        }
        
        this.updateResultsTable(filtered);
        console.log(`🔍 Filtered ${this.currentData.results.length} -> ${filtered.length} documents`);
    }
    
    getFilters() {
        return {
            start_date: document.getElementById('startDate')?.value || '',
            end_date: document.getElementById('endDate')?.value || '',
            author: document.getElementById('authorFilter')?.value || '',
            company: document.getElementById('companyFilter')?.value || '',
            product: document.getElementById('productFilter')?.value || '',
            search: document.getElementById('searchInput')?.value || ''
        };
    }
    
    clearFilters() {
        console.log('🧹 Clearing all filters...');
        
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        document.getElementById('authorFilter').value = '';
        document.getElementById('companyFilter').value = '';
        document.getElementById('productFilter').value = '';
        document.getElementById('searchInput').value = '';
        
        // Reset to original data
        if (this.currentData) {
            this.updateResultsTable(this.currentData.results || []);
        }
        
        console.log('✅ Filters cleared');
    }
    
    sortResults(sortBy) {
        if (!this.currentData || !this.currentData.results) return;
        
        console.log(`📊 Sorting by: ${sortBy}`);
        
        const sorted = [...this.currentData.results].sort((a, b) => {
            let aVal = a[sortBy] || '';
            let bVal = b[sortBy] || '';
            
            // Handle date sorting
            if (sortBy === 'publication_date') {
                return new Date(bVal) - new Date(aVal); // Newest first
            }
            
            // Handle string sorting
            return aVal.toString().localeCompare(bVal.toString());
        });
        
        this.currentData.results = sorted;
        this.updateResultsTable(sorted);
    }
    
    async triggerScrape() {
        console.log('🔄 Triggering manual scrape...');
        
        const modal = new bootstrap.Modal(document.getElementById('scrapingModal'));
        modal.show();
        
        // Auto-hide after 30 seconds
        this.autoHideTimeout = setTimeout(() => {
            modal.hide();
        }, 30000);
        
        try {
            const response = await fetch('/api/scrape?force_current_year=true', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            // Clear timeout and hide modal
            clearTimeout(this.autoHideTimeout);
            modal.hide();
            
            if (result.status === 'success' || result.status === 'up_to_date') {
                // Show detailed success message with results
                let message = result.message;
                if (result.new_documents > 0) {
                    message += ` Found ${result.new_documents} new documents from ${result.from_date} to ${result.to_date}.`;
                }
                if (result.duration_seconds) {
                    message += ` Completed in ${result.duration_seconds.toFixed(1)}s.`;
                }
                
                this.showSuccess(message);
                
                // Try to reload dashboard data
                await this.loadDashboardData();
                
                // If still no data (Vercel serverless issue), show helpful message
                if (this.currentData && this.currentData.results.length === 0 && result.new_documents > 0) {
                    setTimeout(() => {
                        this.showSuccess(`✅ Scraping successful! Found ${result.new_documents} documents. Note: In serverless environments, data may not persist between requests. For full functionality, run locally.`);
                    }, 2000);
                }
            } else {
                this.showError(result.message || 'Scraping failed');
            }
            
        } catch (error) {
            clearTimeout(this.autoHideTimeout);
            modal.hide();
            console.error('❌ Scrape error:', error);
            this.showError('Failed to trigger scrape: ' + error.message);
        }
    }
    
    async exportCsv() {
        console.log('📥 Exporting CSV...');
        
        try {
            const filters = this.getFilters();
            const params = new URLSearchParams();
            
            Object.entries(filters).forEach(([key, value]) => {
                if (value) params.append(key, value);
            });
            
            const url = `/api/export/csv?${params.toString()}`;
            
            // Create temporary download link
            const link = document.createElement('a');
            link.href = url;
            link.download = `eurlex_trade_documents_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showSuccess('CSV export initiated');
            
        } catch (error) {
            console.error('❌ Export error:', error);
            this.showError('Failed to export CSV: ' + error.message);
        }
    }
    
    async showDocumentDetails(documentNumber) {
        console.log(`📄 Loading document details: ${documentNumber}`);
        
        try {
            const response = await fetch(`/api/documents/${documentNumber}`);
            
            if (!response.ok) {
                throw new Error('Failed to load document details');
            }
            
            const docData = await response.json();
            this.populateDocumentModal(docData);
            
            const modal = new bootstrap.Modal(document.getElementById('documentModal'));
            modal.show();
            
        } catch (error) {
            console.error('❌ Error loading document:', error);
            this.showError('Failed to load document details');
        }
    }
    
    populateDocumentModal(docData) {
        document.getElementById('modalTitle').textContent = `Raw Data: ${docData.title || 'Document Details'}`;
        
        const modalBody = document.getElementById('modalBody');
        modalBody.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h6 class="card-title mb-0">
                        <i class="ti ti-code me-2"></i>Complete Scraped Data (JSON)
                    </h6>
                </div>
                <div class="card-body p-0">
                    <pre class="bg-dark text-light p-3 m-0 rounded-0" style="max-height: 600px; overflow-y: auto; font-size: 0.875rem;"><code>${JSON.stringify(docData, null, 2)}</code></pre>
                </div>
            </div>
        `;
    }
    
    async initializeCharts(data) {
        try {
            // Timeline Chart
            await this.createTimelineChart(data.results || []);
            
            // Document Types Chart
            await this.createTypeChart(data.statistics || {});
            
            console.log('📈 Charts initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing charts:', error);
        }
    }
    
    async createTimelineChart(results) {
        const ctx = document.getElementById('timelineChart');
        if (!ctx) return;
        
        // Group by month
        const monthCounts = {};
        results.forEach(doc => {
            if (doc.publication_date) {
                const month = doc.publication_date.slice(0, 7); // YYYY-MM
                monthCounts[month] = (monthCounts[month] || 0) + 1;
            }
        });
        
        const sortedMonths = Object.keys(monthCounts).sort();
        const counts = sortedMonths.map(month => monthCounts[month]);
        
        if (this.charts.timeline) {
            this.charts.timeline.destroy();
        }
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedMonths,
                datasets: [{
                    label: 'Documents',
                    data: counts,
                    borderColor: '#206bc4',
                    backgroundColor: 'rgba(32, 107, 196, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    async createTypeChart(statistics) {
        const ctx = document.getElementById('typeChart');
        if (!ctx) return;
        
        const docTypes = statistics.document_types || {};
        const labels = Object.keys(docTypes).slice(0, 6); // Top 6
        const data = labels.map(label => docTypes[label]);
        
        if (this.charts.types) {
            this.charts.types.destroy();
        }
        
        this.charts.types = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#206bc4', '#79a6dc', '#a8cced', '#d7e8f7',
                        '#f8fafc', '#e5f3ff'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    showSuccess(message) {
        const toast = document.getElementById('successToast');
        const body = document.getElementById('successToastBody');
        
        if (body) body.textContent = message;
        if (toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }
    
    showError(message) {
        const toast = document.getElementById('errorToast');
        const body = document.getElementById('errorToastBody');
        
        if (body) body.textContent = message;
        if (toast) {
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new EURLexTradeScraperDashboard();
});
