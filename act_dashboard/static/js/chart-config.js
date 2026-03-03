/**
 * ACT DASHBOARD - CHART CONFIGURATION
 * Module 3: Google Ads Chart Design
 * Chat 55 | 2026-03-02
 * 
 * Purpose: Centralized Chart.js configuration and utility functions
 * Usage: Loaded globally in base_bootstrap.html
 */

// ============================================================================
// ACT COLOR PALETTE (from logo)
// ============================================================================

const ACT_COLORS = {
    GREEN:  '#34A853',  // 1st metric (inner circle)
    YELLOW: '#FBBC05',  // 2nd metric (middle ring)
    RED:    '#EA4335',  // 3rd metric (outer ring)
    BLUE:   '#4285F4'   // 4th metric (outermost ring)
};

// Fixed color array (colors assigned by index 0-3)
const FIXED_COLORS = [
    ACT_COLORS.GREEN,   // Index 0
    ACT_COLORS.YELLOW,  // Index 1
    ACT_COLORS.RED,     // Index 2
    ACT_COLORS.BLUE     // Index 3
];

// ============================================================================
// NORMALIZATION LOGIC
// ============================================================================

/**
 * Normalize data to 0-95% range for charts with 3+ metrics.
 * Prevents flat lines at top when combining metrics with different scales.
 * 
 * @param {number[]} rawData - Original metric values
 * @returns {number[]} - Normalized values (0-95 range)
 */
function normalizeData(rawData) {
    if (!rawData || rawData.length === 0) {
        return [];
    }
    
    const min = Math.min(...rawData);
    const max = Math.max(...rawData);
    const range = max - min;
    
    if (range > 0) {
        // Normalize to 0-95% (95% ceiling prevents flat lines)
        return rawData.map(v => ((v - min) / range) * 95);
    } else {
        // All values same → center at 47.5%
        return rawData.map(() => 47.5);
    }
}

// ============================================================================
// VALUE FORMATTING
// ============================================================================

/**
 * Format metric values for display in tooltips and cards.
 * 
 * @param {number} value - Metric value
 * @param {string} metricKey - Metric identifier (e.g., 'cost', 'ctr')
 * @returns {string} - Formatted string
 */
function formatMetricValue(value, metricKey) {
    if (value === null || value === undefined) {
        return 'N/A';
    }
    
    // Currency metrics
    if (['cost', 'avg_cpc', 'conv_value', 'cost_per_conv'].includes(metricKey)) {
        return '£' + value.toLocaleString('en-GB', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }
    
    // Percentage metrics
    if (['conv_rate', 'ctr'].includes(metricKey)) {
        return value.toFixed(2) + '%';
    }
    
    // ROAS (2 decimal places, no symbol)
    if (metricKey === 'roas') {
        return value.toFixed(2) + 'x';
    }
    
    // Count metrics (whole numbers)
    if (['impressions', 'clicks', 'conversions'].includes(metricKey)) {
        return value.toLocaleString('en-GB', {
            maximumFractionDigits: 0
        });
    }
    
    // Default: 2 decimal places
    return value.toLocaleString('en-GB', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// ============================================================================
// METRIC DISPLAY NAMES
// ============================================================================

const METRIC_LABELS = {
    'cost':          'Cost',
    'impressions':   'Impressions',
    'clicks':        'Clicks',
    'avg_cpc':       'Avg CPC',
    'conversions':   'Conversions',
    'conv_value':    'Conv. Value',
    'cost_per_conv': 'Cost/Conv.',
    'conv_rate':     'Conv. Rate',
    'ctr':           'CTR',
    'roas':          'ROAS'
};

/**
 * Get display label for a metric key.
 * 
 * @param {string} metricKey - Metric identifier
 * @returns {string} - Display label
 */
function getMetricLabel(metricKey) {
    return METRIC_LABELS[metricKey] || metricKey;
}

// ============================================================================
// CHART CONFIGURATION BUILDER
// ============================================================================

/**
 * Build Chart.js configuration for ACT dashboard charts.
 * 
 * @param {object} params - Configuration parameters
 * @param {string[]} params.dates - Date labels array
 * @param {string[]} params.visibleMetrics - Array of visible metric keys
 * @param {object} params.metricsData - Raw metric data (key -> array)
 * @param {object} params.originalData - Original (non-normalized) data for tooltips
 * @param {boolean} params.normalizeData - Whether to normalize (3+ metrics)
 * @param {boolean} params.showAxes - Whether to show axes (1-2 metrics)
 * @returns {object} - Chart.js configuration object
 */
function buildChartConfig(params) {
    const {
        dates,
        visibleMetrics,
        metricsData,
        originalData,
        normalizeData: shouldNormalize,
        showAxes
    } = params;
    
    // Build datasets with fixed colors
    const datasets = visibleMetrics.map((metricKey, index) => {
        const rawData = metricsData[metricKey] || [];
        const displayData = shouldNormalize ? normalizeData(rawData) : rawData;
        const color = FIXED_COLORS[index % FIXED_COLORS.length];
        
        return {
            label: getMetricLabel(metricKey),
            data: displayData,
            borderColor: color,
            backgroundColor: color + '0F',  // 6% opacity
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            pointStyle: 'line',  // Line indicators in tooltip
            tension: 0.3,
            yAxisID: 'y'  // All use same axis when normalized
        };
    });
    
    return {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false  // Using custom metric cards instead
                },
                tooltip: {
                    backgroundColor: '#ffffff',
                    titleColor: '#212529',
                    bodyColor: '#212529',
                    borderColor: '#e0e0e0',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    usePointStyle: true,  // Use line indicators
                    callbacks: {
                        label: function(context) {
                            const metricKey = visibleMetrics[context.datasetIndex];
                            const realValue = shouldNormalize 
                                ? originalData[metricKey][context.dataIndex]
                                : context.parsed.y;
                            
                            const label = context.dataset.label;
                            const formatted = formatMetricValue(realValue, metricKey);
                            
                            return label + ': ' + formatted;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        font: { size: 11 },
                        color: '#616161',
                        maxTicksLimit: 7
                    },
                    grid: { display: false }
                },
                y: {
                    display: showAxes,
                    ticks: {
                        font: { size: 11 },
                        color: '#616161',
                        display: showAxes
                    },
                    grid: {
                        display: !showAxes,  // Show grid when axes hidden
                        drawTicks: false,
                        color: '#e0e0e0',
                        borderDash: [2, 2]
                    },
                    title: { display: false }
                }
            }
        }
    };
}

// ============================================================================
// CHART INITIALIZATION
// ============================================================================

/**
 * Initialize or update a Chart.js instance with ACT styling.
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {object} chartData - Data object with dates and metrics
 * @param {string[]} visibleMetrics - Array of visible metric keys
 * @returns {Chart} - Chart.js instance
 */
function initACTChart(canvasId, chartData, visibleMetrics) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`[initACTChart] Canvas not found: ${canvasId}`);
        return null;
    }
    
    const ctx = canvas.getContext('2d');
    
    // Destroy existing chart if present
    if (window[`${canvasId}_instance`]) {
        window[`${canvasId}_instance`].destroy();
    }
    
    // Determine normalization and axes visibility
    const shouldNormalize = visibleMetrics.length >= 3;
    const showAxes = visibleMetrics.length <= 2;
    
    // Store original data for tooltips
    const originalData = {};
    visibleMetrics.forEach(key => {
        originalData[key] = chartData.metrics[key] || [];
    });
    
    // Build config
    const config = buildChartConfig({
        dates: chartData.dates || [],
        visibleMetrics: visibleMetrics,
        metricsData: chartData.metrics || {},
        originalData: originalData,
        normalizeData: shouldNormalize,
        showAxes: showAxes
    });
    
    // Create chart
    const chart = new Chart(ctx, config);
    window[`${canvasId}_instance`] = chart;
    
    return chart;
}

// ============================================================================
// EXPORT FOR MODULE USE (if using modules)
// ============================================================================

// For use in modules:
// export { ACT_COLORS, FIXED_COLORS, normalizeData, formatMetricValue, 
//          getMetricLabel, buildChartConfig, initACTChart };

console.log('[chart-config.js] Loaded - ACT Chart utilities ready');
