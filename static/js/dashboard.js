/**
 * Goldman Sachs Equity Research Dashboard
 * Full-featured with Plotly interactive charts
 */

let currentData = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initialized');
    fetchStockData();
    
    const input = document.getElementById('tickerInput');
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') fetchStockData();
        });
    }
});

async function fetchStockData() {
    const tickerInput = document.getElementById('tickerInput');
    if (!tickerInput) return;
    
    const ticker = tickerInput.value.trim().toUpperCase();
    if (!ticker) return;
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('content').style.display = 'none';
    
    // Update loading steps
    updateLoadingStep(1);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker: ticker })
        });
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            document.getElementById('loading').style.display = 'none';
            return;
        }
        
        currentData = data;
        updateDashboard(data);
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('content').style.display = 'block';
        
    } catch (err) {
        console.error('Fetch error:', err);
        alert('Failed to fetch data: ' + err.message);
        document.getElementById('loading').style.display = 'none';
    }
}

function updateLoadingStep(step) {
    const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
    for (let i = 0; i < steps.length; i++) {
        const el = document.getElementById(steps[i]);
        if (el && i < step) {
            el.style.color = 'var(--positive)';
        }
    }
}

function updateDashboard(data) {
    console.log('Updating dashboard...');
    
    // Update API Status
    const fredStatus = document.getElementById('fredStatus');
    if (fredStatus) {
        if (data.fred_available) {
            fredStatus.innerHTML = '✓ FRED API Connected';
            fredStatus.style.color = 'var(--positive)';
        } else {
            fredStatus.innerHTML = '⚠ FRED API: Add Key';
            fredStatus.style.color = 'var(--warning)';
        }
    }
    
    // Price Section
    document.getElementById('currentPrice').innerHTML = `$${data.current_price.toFixed(2)} <span>USD</span>`;
    const changeHtml = data.change_pct >= 0 
        ? `<div class="change-positive"><i class="fas fa-arrow-up"></i> +${data.change_pct.toFixed(2)}% ($${data.change_abs.toFixed(2)})</div>`
        : `<div class="change-negative"><i class="fas fa-arrow-down"></i> ${data.change_pct.toFixed(2)}% ($${data.change_abs.toFixed(2)})</div>`;
    document.getElementById('changeBadge').innerHTML = changeHtml;
    document.getElementById('tickerName').innerHTML = `${data.ticker} | NASDAQ`;
    document.getElementById('recommendation').innerHTML = data.rating;
    
    // Metrics Row
    let metricsHtml = '';
    for (let m of data.metrics_row) {
        metricsHtml += `<div class="metric-card"><div class="metric-label">${m.label}</div><div class="metric-value">${m.value}</div></div>`;
    }
    document.getElementById('metricsRow').innerHTML = metricsHtml;
    
    // KPI Grid
    let kpiHtml = '';
    for (let k of data.kpi_grid) {
        kpiHtml += `<div class="kpi-item"><div class="kpi-title">${k.title}</div><div class="kpi-number">${k.value}</div><div class="kpi-sub">${k.sub}</div></div>`;
    }
    document.getElementById('kpiGrid').innerHTML = kpiHtml;
    
    // Macro Strip
    if (data.macro_summary) {
        const macro = data.macro_summary;
        document.getElementById('macroGdp').innerHTML = macro.gdp_growth ? `${macro.gdp_growth >= 0 ? '+' : ''}${macro.gdp_growth}%` : '--';
        document.getElementById('macroInflation').innerHTML = macro.inflation_rate ? `${macro.inflation_rate}%` : '--';
        document.getElementById('macroFedRate').innerHTML = macro.fed_rate ? `${macro.fed_rate}%` : '--';
        document.getElementById('macroUnemployment').innerHTML = macro.unemployment ? `${macro.unemployment}%` : '--';
        document.getElementById('macroTreasury').innerHTML = macro.treasury_rate ? `${macro.treasury_rate}%` : '--';
    }
    
    // AI Analysis
    document.getElementById('thesisText').innerHTML = data.thesis;
    document.getElementById('ratingBox').innerHTML = `
        <div class="rating-label">GS RATING</div>
        <div class="rating-value">${data.rating}</div>
        <div class="rating-detail">Target: $${data.price_target} | +${data.upside_pct}%</div>
    `;
    
    const sentimentColor = data.sentiment_score >= 0.3 ? 'var(--positive)' : (data.sentiment_score <= -0.3 ? 'var(--negative)' : 'var(--neutral)');
    document.getElementById('sentimentBox').innerHTML = `
        <div class="sentiment-label">MARKET SENTIMENT</div>
        <div class="sentiment-value" style="color: ${sentimentColor}">${data.sentiment_label}</div>
        <div class="sentiment-detail">Score: ${(data.sentiment_score * 100).toFixed(0)}/100</div>
    `;
    
    const quality = data.earnings_quality || { quality_rating: 'Excellent', quality_score: 85 };
    document.getElementById('qualityBox').innerHTML = `
        <div class="quality-label">EARNINGS QUALITY</div>
        <div class="quality-value">${quality.quality_rating}</div>
        <div class="quality-detail">Score: ${quality.quality_score}/100</div>
    `;
    
    // Risks & Catalysts
    let risksHtml = '';
    for (let r of data.risks) {
        risksHtml += `<li><i class="fas fa-circle" style="font-size:0.35rem; margin-right:8px; color:var(--negative);"></i>${r}</li>`;
    }
    document.getElementById('risksList').innerHTML = risksHtml;
    
    let catsHtml = '';
    for (let c of data.catalysts) {
        catsHtml += `<li><i class="fas fa-circle" style="font-size:0.35rem; margin-right:8px; color:var(--positive);"></i>${c}</li>`;
    }
    document.getElementById('catalystsList').innerHTML = catsHtml;
    
    // Technical Summary
    const tech = data.technical_outlook || { outlook: 'Bullish', rsi: 55, rsi_signal: 'Neutral', support: 0, resistance: 0, momentum: 'Positive' };
    document.getElementById('technicalSummary').innerHTML = `
        <div class="tech-item"><div class="tech-label">Technical Outlook</div><div class="tech-value">${tech.outlook}</div></div>
        <div class="tech-item"><div class="tech-label">RSI (14)</div><div class="tech-value">${tech.rsi} (${tech.rsi_signal})</div></div>
        <div class="tech-item"><div class="tech-label">Support / Resistance</div><div class="tech-value">$${tech.support} / $${tech.resistance}</div></div>
        <div class="tech-item"><div class="tech-label">Momentum</div><div class="tech-value">${tech.momentum}</div></div>
    `;
    
    // Peer Table
    if (data.peers && data.peers.length) {
        let peerHtml = '<tbody>';
        for (let p of data.peers) {
            const perfClass = p.ytd_perf >= 0 ? 'positive-text' : 'negative-text';
            peerHtml += `
                <tr>
                    <td><strong>${p.company}</strong></td>
                    <td>${p.ticker}</td>
                    <td>${p.mkt_cap}</td>
                    <td>${p.pe_ntm}x</td>
                    <td class="${perfClass}">${p.ytd_perf >= 0 ? '+' : ''}${p.ytd_perf}%</td>
                </tr>
            `;
        }
        peerHtml += '</tbody>';
        document.querySelector('#peerTable tbody').innerHTML = peerHtml;
    }
    
    // Render Charts
    renderChart('priceChartDiv', data.price_chart_json);
    renderChart('techChartDiv', data.tech_chart_json);
    renderChart('returnsChartDiv', data.returns_chart_json);
    renderChart('peerChartDiv', data.peer_chart_json);
    
    // Timestamp
    document.getElementById('timestamp').innerHTML = `<i class="far fa-clock"></i> ${data.timestamp}`;
}

function renderChart(elementId, chartJson) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    if (!chartJson) {
        element.innerHTML = '<div class="error">No chart data available</div>';
        return;
    }
    
    try {
        let chartData;
        if (typeof chartJson === 'string') {
            chartData = JSON.parse(chartJson);
        } else {
            chartData = chartJson;
        }
        
        if (chartData.error) {
            element.innerHTML = `<div class="error">Chart error: ${chartData.error}</div>`;
            return;
        }
        
        if (chartData.data && chartData.layout) {
            Plotly.newPlot(elementId, chartData.data, chartData.layout, {
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['lasso2d', 'select2d']
            });
            console.log(`Chart rendered: ${elementId}`);
        } else {
            element.innerHTML = '<div class="error">Invalid chart data format</div>';
        }
    } catch (e) {
        console.error(`Error rendering ${elementId}:`, e);
        element.innerHTML = `<div class="error">Failed to load chart: ${e.message}</div>`;
    }
}

function resetChart(chartId) {
    const element = document.getElementById(chartId);
    if (element && element.data) {
        Plotly.relayout(chartId, {
            'xaxis.range': null,
            'yaxis.range': null,
            'xaxis.autorange': true,
            'yaxis.autorange': true
        });
    }
}