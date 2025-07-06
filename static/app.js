// DashboardApp: Main class for the economic insights dashboard
class DashboardApp {
    /**
     * Constructor initializes app state, loads cached key actors, and starts the app.
     */
    constructor() {
        this.currentReportId = 'storyboard'; // Track which section is active
        this.reports = []; // All loaded reports
        this.currentChat = null; // Current chat state
        this.cachedKeyActors = null; // Store latest AI-generated key actors
        // Speech synthesis for read-aloud
        this.speechSynthesis = window.speechSynthesis;
        this.speechUtterance = null;
        this.isSpeaking = false;
        // Try to load cached key actors from localStorage
        const storedActors = localStorage.getItem('cachedKeyActors');
        if (storedActors) {
            try {
                this.cachedKeyActors = JSON.parse(storedActors);
            } catch (e) {
                this.cachedKeyActors = null;
            }
        }
        this.init();
    }

    /**
     * Initialize the dashboard: load reports, render sidebar, show storyboard, and setup drag-and-drop.
     */
    async init() {
        try {
            await this.loadReports();
            this.renderSidebar();
            this.showStoryboard();
            this.setupDragAndDrop();
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showNotification('Failed to initialize application', 'error');
        }
    }

    async loadReports() {
        try {
            const response = await fetch('/api/reports');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            this.reports = data.reports || [];
        } catch (error) {
            console.error('Error loading reports:', error);
            this.reports = []; // Set empty array as fallback
            this.showNotification('Failed to load reports', 'error');
        }
    }

    renderSidebar() {
        const reportsNav = document.getElementById('reports-nav');
        reportsNav.innerHTML = this.reports.map(report => `
            <button onclick="app.showReport('${report.id}')" class="sidebar-btn" id="report-${report.id}">
                <i class="fa-solid fa-file-lines w-6 h-6"></i>
                <span class="font-medium">${report.title}</span>
            </button>
        `).join('');
    }

    updateSidebarSelection(selectedId) {
        // Remove active class from all buttons
        document.querySelectorAll('.sidebar-btn').forEach(btn => {
            btn.className = 'sidebar-btn';
        });
        
        // Add active class to selected button
        const selectedBtn = document.getElementById(`${selectedId}-btn`) || 
                           document.getElementById(`report-${selectedId}`);
        if (selectedBtn) {
            selectedBtn.className = 'sidebar-btn bg-blue-600 text-white shadow-lg';
        }
    }

    showStoryboard() {
        this.currentReportId = 'storyboard';
        this.updateSidebarSelection('storyboard');
        
        // Initial card UI for storyboard
        const content = `
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700 max-w-5xl mx-auto">
                <h2 class="text-3xl font-bold text-white mb-2">AI Macroeconomic Storyboard</h2>
                <p class="text-gray-400 mb-6">Generate a high-level narrative with synthesized charts and AI analysis to see the bigger picture across all economic reports.</p>
                <div id="storyboard-content" class="text-center py-8">
                    <button onclick="app.generateStoryboard()" class="bg-green-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center justify-center mx-auto text-lg">
                        <i class="fa-solid fa-wand-magic-sparkles mr-3"></i> Generate Storyboard
                    </button>
                </div>
            </div>
        `;
        document.getElementById('content-area').innerHTML = content;
    }

    async generateStoryboard() {
        const contentDiv = document.getElementById('storyboard-content');
        contentDiv.innerHTML = `${this.getSpinner()} Generating AI Storyboard...`;
        try {
            const response = await fetch('/api/generate-storyboard', { method: 'POST' });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            // Cache key actors if present
            if (data.keyActors && Array.isArray(data.keyActors) && data.keyActors.length > 0) {
                this.cachedKeyActors = data.keyActors;
                localStorage.setItem('cachedKeyActors', JSON.stringify(data.keyActors));
                // If Key Actors tab is active, re-render it
                if (this.currentReportId === 'key_actors') {
                    this.showKeyActors();
                }
            }
            // Build the storyboard sections
            let html = '';
            // 1. The Singularity Thesis
            html += `
                <div class="bg-gray-900/80 border border-gray-700 rounded-lg p-6 mb-8 shadow-lg">
                    <h3 class="text-2xl font-bold text-green-400 mb-2">The Singularity Thesis</h3>
                    <div class="text-xl text-white font-semibold mb-2">${data.title}</div>
                    <div class="text-gray-300 text-lg">${marked.parse(data.narrative)}</div>
                </div>
            `;
            // 2. Inter-Report Relationships
            html += `
                <div class="bg-gray-900/80 border border-gray-700 rounded-lg p-6 mb-8 shadow-lg">
                    <h3 class="text-2xl font-bold text-blue-400 mb-4">Inter-Report Relationships</h3>
                    <div id="relationship-graph" class="mb-2"></div>
                    <div class="text-gray-300 text-sm">This graph shows the most critical connections between reports supporting the singularity thesis.</div>
                </div>
            `;
            // 3. Synthesized Visualizations
            if (data.charts && data.charts.length > 0) {
                html += `
                    <div class="bg-gray-900/80 border border-gray-700 rounded-lg p-6 mb-8 shadow-lg">
                        <h3 class="text-2xl font-bold text-purple-400 mb-4">Synthesized Visualizations</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            ${data.charts.map((chart, i) => `
                                <div class="bg-gray-800 border border-gray-700 rounded-lg p-4">
                                    <div class="font-bold text-white mb-2">${chart.title}</div>
                                    <div class="text-gray-400 text-sm mb-2">${chart.description || ''}</div>
                                    <div id="storyboard-chart-${i}" class="h-64"></div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
            // 4. AI Introspection: The 'Why'
            html += `
                <div class="bg-gray-900/80 border border-gray-700 rounded-lg p-6 mb-8 shadow-lg">
                    <h3 class="text-2xl font-bold text-yellow-400 mb-2">AI Introspection: The 'Why'</h3>
                    <div class="prose prose-invert max-w-none text-gray-200">${data.introspection && data.introspection.trim() ? marked.parse(data.introspection) : '<span class="italic text-gray-400">No introspection provided by AI.</span>'}</div>
                </div>
            `;
            // 5. AI Retrospection: The 'What If'
            html += `
                <div class="bg-gray-900/80 border border-gray-700 rounded-lg p-6 mb-8 shadow-lg">
                    <h3 class="text-2xl font-bold text-pink-400 mb-2">AI Retrospection: The 'What If'</h3>
                    <div class="prose prose-invert max-w-none text-gray-200">${data.retrospection && data.retrospection.trim() ? marked.parse(data.retrospection) : '<span class="italic text-gray-400">No retrospection provided by AI.</span>'}</div>
                </div>
            `;
            // 6. Key Actors in the Narrative (styled as grid of cards)
            const defaultKeyActors = [
                { name: "Policymakers (Federal/State/Municipal)", description: "Responsible for creating incentives, regulations, and investment frameworks to guide structural transformations and address social inequalities.", icon: "fa-solid fa-landmark" },
                { name: "German Households", description: "Experience the direct effects of economic stagnation, climate costs (heating, transport), and social policies (care burden, health access).", icon: "fa-solid fa-users" },
                { name: "German Industry", description: "Faces challenges adapting to higher energy costs, international competition, and the need to decarbonize while maintaining competitiveness.", icon: "fa-solid fa-industry" },
                { name: "Energy Sector", description: "Navigating the shift from fossil fuels to renewables, requiring massive investment in generation, grids, and network decommissioning.", icon: "fa-solid fa-bolt" },
                { name: "Property Owners / Landlords", description: "Key decision-makers for building renovations and investments in heating systems, influenced by financing, standards, and tenancy laws.", icon: "fa-solid fa-building" },
                { name: "European Central Bank (ECB)", description: "Sets monetary policy influencing financing conditions, inflation, and overall economic stability in the Euro Area, including Germany.", icon: "fa-solid fa-euro-sign" }
            ];
            const keyActors = (data.keyActors && Array.isArray(data.keyActors) && data.keyActors.length > 0) ? data.keyActors : defaultKeyActors;
            html += `
                <div class="bg-gray-900/80 border border-gray-700 rounded-lg p-6 mb-8 shadow-lg">
                    <h3 class="text-2xl font-bold text-green-400 mb-4">Key Actors in the Narrative</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        ${keyActors.map(actor => `
                            <div class="bg-gray-800 border border-gray-700 rounded-lg p-5 flex flex-col justify-between items-center shadow-lg">
                                <div class="text-5xl mb-3"><i class="${actor.icon} text-green-400"></i></div>
                                <div class="font-bold text-white text-lg mb-1 text-center">${actor.name}</div>
                                <div class="text-gray-300 text-center text-sm">${actor.description}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            // Render all
            contentDiv.innerHTML = html;
            // Render charts
            if (data.charts && data.charts.length > 0) {
                data.charts.forEach((chart, i) => {
                    this.renderPlotlyChart(chart, `storyboard-chart-${i}`);
                });
            }
            // Render relationship graph (placeholder for now)
            if (data.relationshipGraph) {
                this.renderRelationshipGraph(data.relationshipGraph, 'relationship-graph');
            }
        } catch (error) {
            contentDiv.innerHTML = `<div class="text-red-400 text-center p-6">An error occurred while generating the storyboard: ${error.message}</div>`;
        }
    }

    showAddReport() {
        this.currentReportId = 'add_report';
        this.updateSidebarSelection('add-report');
        
        const content = `
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700 max-w-4xl mx-auto">
                <h2 class="text-3xl font-bold text-white mb-2">Create Dashboards from PDFs</h2>
                <p class="text-gray-400 mb-6">
                    Upload one or more PDF reports. The AI will read them, extract key findings, generate charts, and create a new interactive dashboard for each file.
                </p>

                <form id="upload-form" onsubmit="app.handleUpload(event)">
                    <div id="drop-zone" class="file-upload-area relative w-full min-h-64 border-2 border-dashed border-gray-600 rounded-lg p-4 flex flex-col justify-center items-center text-center cursor-pointer">
                        <input type="file" id="pdf-upload" class="hidden" accept="application/pdf" multiple>
                        <div class="text-center" onclick="document.getElementById('pdf-upload').click()">
                            <i class="fa-solid fa-cloud-arrow-up text-5xl text-gray-500 mb-4"></i>
                            <p class="text-gray-300">
                                <span class="font-semibold text-blue-400">Click to upload</span> or drag and drop PDF files here.
                            </p>
                            <p class="text-xs text-gray-500 mt-1">Multiple files are supported (Max 50MB each)</p>
                        </div>
                        <div id="selected-files" class="hidden w-full text-left mt-4"></div>
                    </div>

                    <div id="upload-error" class="hidden text-red-400 mt-4 text-center"></div>
                    
                    <div class="mt-6 text-center">
                        <button type="submit" disabled class="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-500 transition-all duration-200 flex items-center justify-center mx-auto text-lg" id="upload-btn">
                            <i class="fa-solid fa-microchip-ai mr-3"></i>Analyze PDFs & Generate Dashboards
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.getElementById('content-area').innerHTML = content;
        this.setupFileUpload();
    }

    setupFileUpload() {
        const fileInput = document.getElementById('pdf-upload');
        const uploadBtn = document.getElementById('upload-btn');
        const dropZone = document.getElementById('drop-zone');
        let selectedFiles = [];

        fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            selectedFiles = files.filter(f => f.type === 'application/pdf');
            this.updateFileDisplay(selectedFiles);
            uploadBtn.disabled = selectedFiles.length === 0;
        });

        // Setup drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files);
            const pdfFiles = files.filter(f => f.type === 'application/pdf');
            
            if (pdfFiles.length !== files.length) {
                this.showNotification('Some files were ignored (only PDFs are supported)', 'info');
            }
            
            selectedFiles = [...selectedFiles, ...pdfFiles];
            this.updateFileDisplay(selectedFiles);
            uploadBtn.disabled = selectedFiles.length === 0;
            
            // Update file input
            const dt = new DataTransfer();
            selectedFiles.forEach(file => dt.items.add(file));
            fileInput.files = dt.files;
        });
    }

    updateFileDisplay(files) {
        const container = document.getElementById('selected-files');
        if (files.length === 0) {
            container.classList.add('hidden');
            return;
        }

        container.classList.remove('hidden');
        container.innerHTML = `
            <h4 class="font-semibold text-gray-300 mb-2">Selected Files:</h4>
            <ul class="space-y-2 max-h-48 overflow-y-auto">
                ${files.map((file, index) => `
                    <li class="bg-gray-700 p-2 rounded-md flex justify-between items-center text-sm">
                        <div class="flex items-center gap-2 overflow-hidden">
                            <i class="fa-solid fa-file-pdf text-red-400 flex-shrink-0"></i>
                            <span class="text-gray-200 truncate" title="${file.name}">${file.name}</span>
                            <span class="text-gray-500 text-xs">(${this.formatFileSize(file.size)})</span>
                        </div>
                        <button type="button" onclick="app.removeFile(${index})" class="text-gray-400 hover:text-white">
                            <i class="fa-solid fa-times-circle"></i>
                        </button>
                    </li>
                `).join('')}
            </ul>
        `;
    }

    removeFile(index) {
        const fileInput = document.getElementById('pdf-upload');
        const files = Array.from(fileInput.files);
        files.splice(index, 1);
        
        const dt = new DataTransfer();
        files.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
        
        this.updateFileDisplay(files);
        document.getElementById('upload-btn').disabled = files.length === 0;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async handleUpload(event) {
        event.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('pdf-upload');
        const files = Array.from(fileInput.files);
        
        if (files.length === 0) return;

        files.forEach(file => formData.append('files', file));

        const uploadBtn = document.getElementById('upload-btn');
        const originalHtml = uploadBtn.innerHTML;
        uploadBtn.innerHTML = `${this.getSpinner()} Processing ${files.length} file(s)...`;
        uploadBtn.disabled = true;

        try {
            const response = await fetch('/api/reports/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.reports.length > 0) {
                await this.loadReports();
                this.renderSidebar();
                // Show the first uploaded report
                this.showReport(result.reports[0].id);
                this.showNotification(`Successfully processed ${result.success_count} file(s)!`, 'success');
            }
            
            if (result.errors.length > 0) {
                const errorHtml = `
                    <div class="bg-yellow-900/50 border border-yellow-600 rounded-lg p-4">
                        <h4 class="text-yellow-400 font-semibold mb-2">Some files failed to process:</h4>
                        <div class="text-sm text-yellow-200 space-y-2">
                            ${result.errors.map(err => {
                                // Extract filename and error message for better formatting
                                const parts = err.split(': ');
                                const filename = parts[0];
                                const errorMsg = parts.slice(1).join(': ');
                                return `
                                    <div class="border-l-2 border-yellow-500 pl-3">
                                        <div class="font-medium text-yellow-300">${filename}</div>
                                        <div class="text-yellow-200">${errorMsg}</div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                        <div class="mt-3 text-xs text-yellow-300">
                            <strong>Common solutions:</strong>
                            <ul class="mt-1 list-disc list-inside space-y-1">
                                <li>Ensure the PDF contains selectable text (not just images)</li>
                                <li>Check that the PDF is not password-protected</li>
                                <li>Try with a different PDF file</li>
                                <li>Contact support if the issue persists</li>
                            </ul>
                        </div>
                    </div>
                `;
                document.getElementById('upload-error').innerHTML = errorHtml;
                document.getElementById('upload-error').classList.remove('hidden');
                this.showNotification(`${result.errors.length} file(s) failed to process`, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            document.getElementById('upload-error').innerHTML = 'An error occurred during upload. Please try again.';
            document.getElementById('upload-error').classList.remove('hidden');
            this.showNotification('Upload failed', 'error');
        } finally {
            uploadBtn.innerHTML = originalHtml;
            uploadBtn.disabled = false;
        }
    }

    showReport(reportId) {
        this.currentReportId = reportId;
        this.updateSidebarSelection(reportId);
        
        const report = this.reports.find(r => r.id === reportId);
        if (!report) return;

        const content = `
            <div class="grid grid-cols-1 xl:grid-cols-2 gap-4 w-full overflow-y-auto">
                <div class="flex flex-col space-y-6 overflow-y-auto pr-2">
                    <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700">
                        <div class="flex justify-between items-start mb-3">
                            <h2 class="text-2xl font-bold text-white">${report.title}</h2>
                            <button onclick="app.deleteReport('${reportId}')" class="text-gray-400 hover:text-red-400 transition-colors" title="Delete Report">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>
                        <p class="text-gray-300 mb-4">${report.summary}</p>
                        <div class="border-t border-gray-700 pt-4">
                            <h3 class="text-md font-semibold text-gray-200 mb-2">Key Findings:</h3>
                            <ul class="list-disc list-inside space-y-1 text-gray-400">
                                ${report.keyFindings.map(finding => `<li>${finding}</li>`).join('')}
                            </ul>
                        </div>
                        ${report.created_at ? `<div class="border-t border-gray-700 pt-4 mt-4 text-xs text-gray-500">Created: ${new Date(report.created_at).toLocaleDateString()}</div>` : ''}
                    </div>
                    
                    <div id="report-charts">
                        <!-- Charts will be rendered here -->
                    </div>
                </div>
                
                <div class="flex flex-col space-y-6 overflow-y-auto pr-2">
                    <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700">
                        <h2 class="text-2xl font-bold text-white mb-4">AI-Powered Narrative</h2>
                        
                        <div id="narrative-content" class="text-center py-8">
                            <p class="text-gray-400 mb-4">Click the button to generate an AI-powered analysis and discover the story behind the data.</p>
                            <button onclick="app.generateNarrative('${reportId}')" class="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center justify-center mx-auto">
                                <i class="fa-solid fa-wand-magic-sparkles mr-2"></i>Generate Analysis
                            </button>
                        </div>
                    </div>
                    
                    <div id="chat-container">
                        <!-- Chat will be rendered here -->
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('content-area').innerHTML = content;
        
        // Render charts
        this.renderCharts(report.charts, 'report-charts');
        
        // Setup chat
        this.setupChat(reportId);
    }

    async deleteReport(reportId) {
        if (!confirm('Are you sure you want to delete this report? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/reports/${reportId}`, { method: 'DELETE' });
            
            if (response.ok) {
                await this.loadReports();
                this.renderSidebar();
                this.showStoryboard();
                this.showNotification('Report deleted successfully', 'success');
            } else {
                throw new Error('Failed to delete report');
            }
        } catch (error) {
            console.error('Error deleting report:', error);
            this.showNotification('Failed to delete report', 'error');
        }
    }

    renderCharts(charts, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        charts.forEach((chart, index) => {
            const chartDiv = document.createElement('div');
            chartDiv.className = 'chart-container p-4';
            chartDiv.innerHTML = `
                <h3 class="text-lg font-bold text-white mb-2">${chart.title}</h3>
                <p class="text-sm text-gray-400 mb-4">${chart.description}</p>
                <div id="chart-${containerId}-${index}" style="width: 100%; height: 300px;"></div>
            `;
            container.appendChild(chartDiv);
            
            // Render chart with Plotly
            this.renderPlotlyChart(chart, `chart-${containerId}-${index}`);
        });
    }

    renderPlotlyChart(chartConfig, elementId) {
        try {
            // Ensure Plotly is available
            if (typeof Plotly === 'undefined') {
                console.error('Plotly is not loaded');
                document.getElementById(elementId).innerHTML = '<div class="text-red-400 text-center p-4">Chart library not available</div>';
                return;
            }

            let traces = [];
            let layout = {
                title: '',
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(31, 41, 55, 1)',
                font: { color: '#ffffff', family: 'Arial, sans-serif' },
                margin: { l: 60, r: 50, t: 20, b: 60 },
                showlegend: chartConfig.dataKeys.length > 1,
                legend: {
                    orientation: 'h',
                    y: -0.2,
                    x: 0.5,
                    xanchor: 'center'
                }
            };

        if (chartConfig.type === 'bar') {
            layout.xaxis = { color: '#9CA3AF', gridcolor: '#374151' };
            layout.yaxis = { color: '#9CA3AF', gridcolor: '#374151' };
            
            chartConfig.dataKeys.forEach(key => {
                traces.push({
                    x: chartConfig.data.map(d => d[chartConfig.xAxisKey]),
                    y: chartConfig.data.map(d => d[key.key]),
                    type: 'bar',
                    name: key.name || key.key,
                    marker: { color: key.color }
                });
            });
        } else if (chartConfig.type === 'line') {
            layout.xaxis = { color: '#9CA3AF', gridcolor: '#374151' };
            layout.yaxis = { color: '#9CA3AF', gridcolor: '#374151' };
            
            chartConfig.dataKeys.forEach(key => {
                traces.push({
                    x: chartConfig.data.map(d => d[chartConfig.xAxisKey]),
                    y: chartConfig.data.map(d => d[key.key]),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: key.name || key.key,
                    line: { color: key.color, width: 3 },
                    marker: { size: 6 }
                });
            });
        } else if (chartConfig.type === 'pie') {
            const dataKey = chartConfig.dataKeys[0]?.key || 'value';
            traces.push({
                values: chartConfig.data.map(d => d[dataKey]),
                labels: chartConfig.data.map(d => d[chartConfig.xAxisKey]),
                type: 'pie',
                marker: {
                    colors: chartConfig.data.map((_, index) => 
                        chartConfig.dataKeys[index % chartConfig.dataKeys.length]?.color || '#8884d8'
                    )
                },
                textinfo: 'label+percent',
                textfont: { color: '#ffffff' }
            });
            layout.showlegend = false;
        }

        Plotly.newPlot(elementId, traces, layout, { 
            responsive: true,
            displayModeBar: false
        });
        } catch (error) {
            console.error('Error rendering chart:', error);
            document.getElementById(elementId).innerHTML = '<div class="text-red-400 text-center p-4">Failed to render chart</div>';
        }
    }

    async generateNarrative(reportId) {
        const button = document.querySelector('#narrative-content button');
        const originalHtml = button.innerHTML;
        button.innerHTML = `${this.getSpinner()} Generating...`;
        button.disabled = true;

        try {
            const response = await fetch(`/api/generate-narrative/${reportId}`, { method: 'POST' });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            document.getElementById('narrative-content').innerHTML = `
                <div class="prose-custom max-w-none text-gray-300 text-left">
                    ${marked.parse(data.narrative)}
                </div>
            `;
            
            this.showNotification('Narrative generated successfully!', 'success');
        } catch (error) {
            console.error('Error generating narrative:', error);
            document.getElementById('narrative-content').innerHTML = `
                <p class="text-red-400">Error generating narrative: ${error.message}</p>
                <button onclick="app.generateNarrative('${reportId}')" class="bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700 mt-4">
                    <i class="fa-solid fa-wand-magic-sparkles mr-2"></i>Try Again
                </button>
            `;
            this.showNotification('Failed to generate narrative', 'error');
        }
    }

    setupChat(reportId) {
        const chatHtml = `
            <div class="bg-gray-800 p-4 rounded-lg shadow-xl border border-gray-700 flex flex-col h-[450px]">
                <h3 class="text-lg font-bold text-white mb-2 flex justify-between items-center">
                    <span>AI Chatbot</span>
                    <i class="fa-solid fa-robot text-blue-400"></i>
                </h3>
                <div id="chat-messages" class="flex-grow overflow-y-auto mb-4 pr-2 space-y-4">
                    <div class="flex justify-start">
                        <div class="p-3 rounded-lg bg-gray-700 text-gray-200 max-w-sm md:max-w-md">
                            <p>Hello! I'm ready to answer your questions about this report.</p>
                        </div>
                    </div>
                </div>
                <div class="mb-2 flex flex-wrap gap-2">
                    <button onclick="app.sendQuickMessage('Summarize the key findings.')" class="bg-gray-600 hover:bg-gray-500 text-xs px-2 py-1 rounded-full transition-colors">Summarize Findings</button>
                    <button onclick="app.sendQuickMessage('What are the interconnections with other sectors?')" class="bg-gray-600 hover:bg-gray-500 text-xs px-2 py-1 rounded-full transition-colors">Explain Connections</button>
                    <button onclick="app.sendQuickMessage('What are the policy implications?')" class="bg-gray-600 hover:bg-gray-500 text-xs px-2 py-1 rounded-full transition-colors">Policy Impact</button>
                </div>
                <form onsubmit="app.sendChatMessage(event, '${reportId}')" class="flex space-x-2">
                    <input type="text" id="chat-input" placeholder="Ask a question..." class="flex-grow bg-gray-900 border border-gray-600 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white">
                    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                        <i class="fa-solid fa-paper-plane"></i>
                    </button>
                </form>
            </div>
        `;
        
        document.getElementById('chat-container').innerHTML = chatHtml;
    }

    async sendChatMessage(event, reportId) {
        event.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message) return;
        
        this.addChatMessage('user', message);
        input.value = '';
        
        // Add loading message
        const loadingId = this.addChatMessage('model', `${this.getSpinner()} Thinking...`);
        
        try {
            const formData = new FormData();
            formData.append('message', message);
            
            const response = await fetch(`/api/chat/${reportId}`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Remove loading message and add real response
            document.getElementById(loadingId).remove();
            this.addChatMessage('model', data.response);
        } catch (error) {
            console.error('Chat error:', error);
            document.getElementById(loadingId).remove();
            this.addChatMessage('model', `Sorry, I encountered an error: ${error.message}`);
        }
    }

    async sendQuickMessage(message) {
        const chatInput = document.getElementById('chat-input');
        if (!chatInput) return;
        
        chatInput.value = message;
        
        // Trigger form submission
        const form = chatInput.closest('form');
        if (form) {
            const event = new Event('submit', { bubbles: true, cancelable: true });
            form.dispatchEvent(event);
        }
    }

    addChatMessage(role, content) {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;
        
        const messageId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
        
        const isHtml = content.includes('<') || content.includes('animate-spin');
        
        messageDiv.innerHTML = `
            <div class="p-3 rounded-lg max-w-sm md:max-w-md ${role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'}">
                ${isHtml ? content : `<div class="prose-custom prose-sm max-w-none">${marked.parse(content)}</div>`}
                ${role === 'model' && !isHtml ? `
                    <button onclick="app.speakText(\`${content.replace(/`/g, '\\`').replace(/\$/g, '\\$')}\`)" class="mt-2 text-xs text-blue-300 hover:text-blue-200 transition-colors">
                        <i class="fa-solid fa-volume-high mr-1"></i> Read aloud
                    </button>
                ` : ''}
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        return messageId;
    }

    /**
     * Read aloud the given text using browser SpeechSynthesis.
     * @param {string} text - The text to read aloud.
     */
    readAloud(text) {
        if (!text) return;
        this.stopAloud();
        this.speechUtterance = new window.SpeechSynthesisUtterance(text);
        this.speechUtterance.onend = () => { this.isSpeaking = false; this.updateChatReadButtons(); };
        this.speechUtterance.onerror = () => { this.isSpeaking = false; this.updateChatReadButtons(); };
        this.isSpeaking = true;
        this.speechSynthesis.speak(this.speechUtterance);
        this.updateChatReadButtons();
    }

    /**
     * Stop any ongoing speech synthesis.
     */
    stopAloud() {
        if (this.speechSynthesis.speaking) {
            this.speechSynthesis.cancel();
        }
        this.isSpeaking = false;
        this.updateChatReadButtons();
    }

    /**
     * Enable/disable Read/Stop buttons based on speaking state.
     */
    updateChatReadButtons() {
        const readBtn = document.getElementById('chat-read-btn');
        const stopBtn = document.getElementById('chat-stop-btn');
        if (readBtn) readBtn.disabled = this.isSpeaking;
        if (stopBtn) stopBtn.disabled = !this.isSpeaking;
    }

    /**
     * Render a chat message (AI or user) with optional read-aloud controls.
     * @param {string} message - The message content.
     * @param {boolean} isUser - True if user message, false if AI.
     * @returns {string} - HTML for the message.
     */
    renderChatMessage(message, isUser) {
        // ... existing code ...
        // Add Read and Stop buttons for AI messages
        if (!isUser) {
            return `
                <div class="chat-message ai-message">
                    <div class="chat-message-content">${marked.parse(message)}</div>
                    <div class="flex gap-2 mt-2">
                        <button id="chat-read-btn" class="bg-green-700 text-white px-3 py-1 rounded hover:bg-green-800" onclick="app.readAloud(this.previousElementSibling.textContent)">🔊 Read</button>
                        <button id="chat-stop-btn" class="bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700" onclick="app.stopAloud()" disabled>⏹ Stop</button>
                    </div>
                </div>
            `;
        } else {
            return `<div class="chat-message user-message"><div class="chat-message-content">${marked.parse(message)}</div></div>`;
        }
    }

    async showStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            const statsModal = `
                <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onclick="this.remove()">
                    <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700 max-w-md w-full mx-4" onclick="event.stopPropagation()">
                        <h3 class="text-xl font-bold text-white mb-4">Database Statistics</h3>
                        <div class="space-y-2 text-gray-300">
                            <p><strong>Total Reports:</strong> ${stats.total_reports}</p>
                            <p><strong>Database Size:</strong> ${stats.database_size_mb.toFixed(2)} MB</p>
                            <p><strong>Database Path:</strong> ${stats.database_path}</p>
                        </div>
                        <div class="mt-6 text-center">
                            <button onclick="this.closest('.fixed').remove()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', statsModal);
        } catch (error) {
            console.error('Error fetching stats:', error);
            this.showNotification('Failed to fetch database statistics', 'error');
        }
    }

    async backupDatabase() {
        try {
            const response = await fetch('/api/backup', { method: 'POST' });
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(`Database backup created: ${result.message}`, 'success');
            } else {
                throw new Error(result.detail || 'Backup failed');
            }
        } catch (error) {
            console.error('Error creating backup:', error);
            this.showNotification('Failed to create database backup', 'error');
        }
    }

    setupDragAndDrop() {
        // Prevent default drag behaviors on the document
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
    }

    showNotification(message, type = 'info') {
        const notificationContainer = document.getElementById('notifications');
        if (!notificationContainer) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button onclick="this.closest('.notification').remove()" class="ml-4 text-white hover:text-gray-300">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>
        `;
        
        notificationContainer.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    getSpinner() {
        return document.getElementById('spinner-template').innerHTML;
    }

    showKeyActors() {
        this.currentReportId = 'key_actors';
        this.updateSidebarSelection('key-actors');

        // Use cachedKeyActors if available, otherwise try to load from localStorage, otherwise aggregate from reports
        let actors = this.cachedKeyActors;
        if (!actors) {
            const storedActors = localStorage.getItem('cachedKeyActors');
            if (storedActors) {
                try {
                    actors = JSON.parse(storedActors);
                    this.cachedKeyActors = actors;
                } catch (e) {
                    actors = null;
                }
            }
        }
        if (!actors) {
            // Aggregate all key actors from all reports (fallback)
            const actorsMap = {};
            this.reports.forEach(report => {
                if (report.actors && Array.isArray(report.actors)) {
                    report.actors.forEach(actor => {
                        if (!actorsMap[actor.name]) {
                            actorsMap[actor.name] = { ...actor, reports: [] };
                        }
                        actorsMap[actor.name].reports.push(report);
                    });
                }
            });
            actors = Object.values(actorsMap);
        }

        const content = `
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700 max-w-5xl mx-auto">
                <h2 class="text-3xl font-bold text-white mb-2">Germany's Stalled Engine: Navigating Triple Structural Friction: Key Actors</h2>
                <p class="text-gray-400 mb-6">Identified by the AI as the central figures in the synthesized macroeconomic narrative.</p>
                <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    ${actors && actors.length > 0 ? actors.map(actor => `
                        <div class="bg-gray-700/60 border border-gray-600 rounded-lg p-5 flex flex-col justify-between shadow-lg">
                            <div class="text-5xl mb-3"><i class="${actor.icon || 'fa-solid fa-user-group'} text-green-400"></i></div>
                            <div class="font-bold text-white text-lg mb-1 text-center">${actor.name}</div>
                            <div class="text-gray-300 text-center text-sm">${actor.description}</div>
                        </div>
                    `).join('') : '<div class="text-gray-400 col-span-full text-center">No key actors found in the reports.</div>'}
                </div>
            </div>
        `;
        document.getElementById('content-area').innerHTML = content;
    }

    showHighlightsTimeline() {
        this.currentReportId = 'highlights_timeline';
        this.updateSidebarSelection('highlights-timeline');
        
        // Show loading spinner
        document.getElementById('content-area').innerHTML = `
            <div class="flex justify-center items-center h-64">
                ${this.getSpinner()} Loading timeline...
            </div>
        `;
        
        fetch('/api/timeline')
            .then(res => res.json())
            .then(data => {
                const timeline = data.timeline || [];
                const timelineHtml = `
                    <div class="max-w-4xl mx-auto">
                        <h2 class="text-3xl font-bold text-white mb-8 text-center">Report Highlights Timeline</h2>
                        <div class="relative border-l-2 border-blue-800 pl-8">
                            ${timeline.length > 0 ? timeline.map((item, idx) => `
                                <div class="mb-10 relative">
                                    <div class="absolute -left-4 top-1 w-3 h-3 bg-blue-400 rounded-full border-2 border-blue-800"></div>
                                    <div class="bg-gray-800 rounded-lg shadow-md p-6">
                                        <h3 class="text-xl font-bold text-white mb-2">${item.title}</h3>
                                        <p class="text-gray-300 mb-2">${item.summary}</p>
                                        <button onclick="app.showReport('${item.id}')" class="text-blue-400 hover:underline font-semibold text-sm">View Full Report &rarr;</button>
                                    </div>
                                </div>
                            `).join('') : '<div class="text-gray-400 text-center">No highlights found.</div>'}
                        </div>
                    </div>
                `;
                document.getElementById('content-area').innerHTML = timelineHtml;
            })
            .catch(err => {
                document.getElementById('content-area').innerHTML = `<div class="text-red-400 text-center p-6">Failed to load highlights timeline.</div>`;
                this.showNotification('Failed to load highlights timeline', 'error');
            });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Ensure crypto.randomUUID is available before initializing
        if (typeof crypto === 'undefined' || !crypto.randomUUID) {
            console.warn('crypto.randomUUID not available, using fallback');
            if (typeof crypto === 'undefined') {
                window.crypto = {};
            }
            if (!crypto.randomUUID) {
                crypto.randomUUID = function() {
                    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        var r = Math.random() * 16 | 0;
                        var v = c == 'x' ? r : (r & 0x3 | 0x8);
                        return v.toString(16);
                    });
                };
            }
        }
        
        window.app = new DashboardApp();
    } catch (error) {
        console.error('Failed to initialize DashboardApp:', error);
        // Show user-friendly error message
        const errorDiv = document.createElement('div');
        errorDiv.innerHTML = `
            <div class="fixed inset-0 bg-red-900 bg-opacity-90 flex items-center justify-center z-50">
                <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-red-600 max-w-md mx-4">
                    <h3 class="text-xl font-bold text-red-400 mb-4">Application Error</h3>
                    <p class="text-gray-300 mb-4">Failed to initialize the dashboard application. Please refresh the page or contact support if the problem persists.</p>
                    <div class="text-center">
                        <button onclick="location.reload()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                            Refresh Page
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(errorDiv);
    }
});