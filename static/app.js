class DashboardApp {
    constructor() {
        this.currentReportId = 'storyboard';
        this.reports = [];
        this.currentChat = null;
        this.init();
    }

    async init() {
        await this.loadReports();
        this.renderSidebar();
        this.showStoryboard();
        this.setupDragAndDrop();
    }

    async loadReports() {
        try {
            const response = await fetch('/api/reports');
            const data = await response.json();
            this.reports = data.reports;
        } catch (error) {
            console.error('Error loading reports:', error);
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
        
        const content = `
            <div class="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700 max-w-7xl mx-auto">
                <h2 class="text-3xl font-bold text-white mb-2">AI Macroeconomic Storyboard</h2>
                <p class="text-gray-400 mb-6">Generate a high-level narrative with synthesized charts to see the bigger picture across all economic reports.</p>
                
                <div id="storyboard-content" class="text-center py-8">
                    <button onclick="app.generateStoryboard()" class="bg-green-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center justify-center mx-auto text-lg">
                        <i class="fa-solid fa-wand-magic-sparkles mr-3"></i>Generate Storyboard
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('content-area').innerHTML = content;
    }

    async generateStoryboard() {
        const button = document.querySelector('#storyboard-content button');
        const originalHtml = button.innerHTML;
        button.innerHTML = `${this.getSpinner()} Synthesizing reports and building visualizations...`;
        button.disabled = true;

        try {
            const response = await fetch('/api/generate-storyboard', { method: 'POST' });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const storyboard = await response.json();
            
            const storyboardHtml = `
                <div class="mt-4 grid grid-cols-1 lg:grid-cols-5 gap-8">
                    <div class="lg:col-span-3">
                        <h3 class="text-2xl font-bold text-white mb-4 border-b border-gray-600 pb-2">Synthesized Narrative</h3>
                        <div class="prose-custom max-w-none text-gray-300">
                            ${marked.parse(storyboard.narrative)}
                        </div>
                    </div>
                    <div class="lg:col-span-2 flex flex-col gap-8">
                        <h3 class="text-2xl font-bold text-white mb-0 border-b border-gray-600 pb-2">Synthesized Visualizations</h3>
                        <div id="storyboard-charts">
                            ${storyboard.charts.length > 0 ? '' : '<div class="bg-gray-700/50 p-4 rounded-lg text-center text-gray-400"><p>The AI did not generate specific visualizations for this synthesis.</p></div>'}
                        </div>
                    </div>
                </div>
                <div class="text-center mt-12">
                    <button onclick="app.generateStoryboard()" class="bg-gray-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-500 transition-all duration-200 flex items-center justify-center mx-auto">
                        <i class="fa-solid fa-arrows-rotate mr-2"></i>Regenerate Storyboard
                    </button>
                </div>
            `;
            
            document.getElementById('storyboard-content').innerHTML = storyboardHtml;
            
            // Render charts
            if (storyboard.charts.length > 0) {
                this.renderCharts(storyboard.charts, 'storyboard-charts');
            }
            
            this.showNotification('Storyboard generated successfully!', 'success');
        } catch (error) {
            console.error('Error generating storyboard:', error);
            document.getElementById('storyboard-content').innerHTML = `
                <p class="text-red-400 bg-red-900/50 p-3 rounded-md">An error occurred while generating the storyboard: ${error.message}</p>
                <div class="text-center mt-4">
                    <button onclick="app.generateStoryboard()" class="bg-green-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-green-700">
                        <i class="fa-solid fa-wand-magic-sparkles mr-3"></i>Try Again
                    </button>
                </div>
            `;
            this.showNotification('Failed to generate storyboard', 'error');
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
                    <p>Some files failed to process:</p>
                    <ul class="text-sm mt-2 text-left max-w-lg mx-auto">
                        ${result.errors.map(err => `<li class="mb-1">• ${err}</li>`).join('')}
                    </ul>
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

    speakText(text) {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop any ongoing speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';
            utterance.rate = 0.9;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
        } else {
            this.showNotification('Text-to-speech not supported in your browser', 'info');
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
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new DashboardApp();
});