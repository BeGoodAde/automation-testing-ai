// Data Analysis Practice with GitHub Copilot
// Let's analyze sales data and create visualizations

// Import required libraries for data analysis
// pandas for data manipulation, matplotlib for visualization
// numpy for numerical operations

// Sample sales data structure:
// - date: transaction date
// - product: product name
// - category: product category
// - quantity: items sold
// - price: unit price
// - revenue: total revenue

const salesData = [
    { date: '2024-01-01', product: 'Laptop', category: 'Electronics', quantity: 2, price: 999.99, revenue: 1999.98 },
    { date: '2024-01-02', product: 'Coffee Mug', category: 'Home', quantity: 5, price: 12.99, revenue: 64.95 },
    { date: '2024-01-03', product: 'Smartphone', category: 'Electronics', quantity: 1, price: 799.99, revenue: 799.99 },
    // Add more sample data...
];

class DataAnalyzer {
    constructor(data) {
        this.data = data;
    }
    
    // Calculate total revenue across all products
    calculateTotalRevenue() {
        return this.data.reduce((total, item) => total + item.revenue, 0);
    }
    
    // Find top selling products by quantity
    getTopSellingProducts(limit = 5) {
        const productSales = {};
        
        // Group by product and sum quantities
        this.data.forEach(item => {
            if (productSales[item.product]) {
                productSales[item.product] += item.quantity;
            } else {
                productSales[item.product] = item.quantity;
            }
        });
        
        // Convert to array and sort by quantity
        return Object.entries(productSales)
            .map(([product, quantity]) => ({ product, quantity }))
            .sort((a, b) => b.quantity - a.quantity)
            .slice(0, limit);
    }
    
    // Calculate average order value
    calculateAverageOrderValue() {
        if (this.data.length === 0) return 0;
        const totalRevenue = this.calculateTotalRevenue();
        return totalRevenue / this.data.length;
    }
    
    // Group sales by category and calculate totals
    getSalesByCategory() {
        const categoryTotals = {};
        
        this.data.forEach(item => {
            if (categoryTotals[item.category]) {
                categoryTotals[item.category].revenue += item.revenue;
                categoryTotals[item.category].quantity += item.quantity;
                categoryTotals[item.category].orders += 1;
            } else {
                categoryTotals[item.category] = {
                    revenue: item.revenue,
                    quantity: item.quantity,
                    orders: 1
                };
            }
        });
        
        return categoryTotals;
    }
    
    // Find sales trends by date
    getSalesTrends() {
        const dailySales = {};
        
        this.data.forEach(item => {
            const date = item.date;
            if (dailySales[date]) {
                dailySales[date] += item.revenue;
            } else {
                dailySales[date] = item.revenue;
            }
        });
        
        // Convert to array and sort by date
        return Object.entries(dailySales)
            .map(([date, revenue]) => ({ date, revenue }))
            .sort((a, b) => new Date(a.date) - new Date(b.date));
    }
    
    // Calculate monthly growth rate
    calculateMonthlyGrowthRate() {
        const monthlySales = {};
        
        // Group by month
        this.data.forEach(item => {
            const month = item.date.substring(0, 7); // YYYY-MM format
            if (monthlySales[month]) {
                monthlySales[month] += item.revenue;
            } else {
                monthlySales[month] = item.revenue;
            }
        });
        
        // Calculate growth rates
        const months = Object.keys(monthlySales).sort();
        const growthRates = [];
        
        for (let i = 1; i < months.length; i++) {
            const currentMonth = months[i];
            const previousMonth = months[i - 1];
            const growthRate = ((monthlySales[currentMonth] - monthlySales[previousMonth]) / monthlySales[previousMonth]) * 100;
            
            growthRates.push({
                month: currentMonth,
                growthRate: Math.round(growthRate * 100) / 100
            });
        }
        
        return growthRates;
    }
    
    // Identify best performing product categories
    getBestPerformingCategories() {
        const categoryData = this.getSalesByCategory();
        
        return Object.entries(categoryData)
            .map(([category, data]) => ({
                category,
                revenue: data.revenue,
                quantity: data.quantity,
                orders: data.orders,
                averageOrderValue: data.revenue / data.orders
            }))
            .sort((a, b) => b.revenue - a.revenue);
    }
    
    // Generate summary statistics
    generateSummaryStatistics() {
        const totalRevenue = this.calculateTotalRevenue();
        const avgOrderValue = this.calculateAverageOrderValue();
        const totalOrders = this.data.length;
        const totalQuantity = this.data.reduce((sum, item) => sum + item.quantity, 0);
        const topProducts = this.getTopSellingProducts(3);
        const categoryBreakdown = this.getSalesByCategory();
        
        return {
            overview: {
                totalRevenue: Math.round(totalRevenue * 100) / 100,
                totalOrders,
                averageOrderValue: Math.round(avgOrderValue * 100) / 100,
                totalQuantitySold: totalQuantity
            },
            topProducts,
            categoryBreakdown,
            dateRange: {
                startDate: Math.min(...this.data.map(item => new Date(item.date))),
                endDate: Math.max(...this.data.map(item => new Date(item.date)))
            }
        };
    }
}

// Create test data for analysis
function generateSampleData(numberOfRecords = 100) {
    const products = [
        { name: 'Laptop', category: 'Electronics', basePrice: 999.99 },
        { name: 'Smartphone', category: 'Electronics', basePrice: 799.99 },
        { name: 'Headphones', category: 'Electronics', basePrice: 199.99 },
        { name: 'Coffee Mug', category: 'Home', basePrice: 12.99 },
        { name: 'Desk Chair', category: 'Home', basePrice: 249.99 },
        { name: 'Plant Pot', category: 'Home', basePrice: 24.99 },
        { name: 'Running Shoes', category: 'Sports', basePrice: 129.99 },
        { name: 'Yoga Mat', category: 'Sports', basePrice: 39.99 },
        { name: 'Water Bottle', category: 'Sports', basePrice: 19.99 },
        { name: 'Novel Book', category: 'Books', basePrice: 15.99 },
        { name: 'Cookbook', category: 'Books', basePrice: 24.99 },
        { name: 'Magazine', category: 'Books', basePrice: 4.99 }
    ];
    
    const sampleData = [];
    const startDate = new Date('2024-01-01');
    const endDate = new Date('2024-12-31');
    
    for (let i = 0; i < numberOfRecords; i++) {
        // Random date between start and end
        const randomTime = startDate.getTime() + Math.random() * (endDate.getTime() - startDate.getTime());
        const randomDate = new Date(randomTime).toISOString().split('T')[0];
        
        // Random product
        const randomProduct = products[Math.floor(Math.random() * products.length)];
        
        // Random quantity (1-5 items, weighted toward 1-2)
        const quantities = [1, 1, 1, 2, 2, 3, 4, 5];
        const quantity = quantities[Math.floor(Math.random() * quantities.length)];
        
        // Price with some variation (±20%)
        const priceVariation = 0.8 + Math.random() * 0.4; // 0.8 to 1.2
        const price = Math.round(randomProduct.basePrice * priceVariation * 100) / 100;
        
        // Calculate revenue
        const revenue = Math.round(price * quantity * 100) / 100;
        
        sampleData.push({
            date: randomDate,
            product: randomProduct.name,
            category: randomProduct.category,
            quantity: quantity,
            price: price,
            revenue: revenue
        });
    }
    
    // Sort by date
    return sampleData.sort((a, b) => new Date(a.date) - new Date(b.date));
}

// Data visualization functions
class DataVisualizer {
    constructor(analyzer) {
        this.analyzer = analyzer;
    }
    
    // Create bar chart for sales by category
    createCategoryBarChart() {
        const categoryData = this.analyzer.getSalesByCategory();
        const chartData = {
            type: 'bar',
            title: 'Sales Revenue by Category',
            categories: Object.keys(categoryData),
            values: Object.values(categoryData).map(cat => cat.revenue),
            colors: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
        };
        
        console.log('📊 Bar Chart - Sales by Category:');
        chartData.categories.forEach((category, index) => {
            const revenue = chartData.values[index];
            const bar = '█'.repeat(Math.ceil(revenue / 200)); // Scale bars
            console.log(`${category.padEnd(12)} | ${bar} $${revenue.toFixed(2)}`);
        });
        
        return chartData;
    }
    
    // Generate line chart for sales trends over time
    createSalesTrendChart() {
        const trendsData = this.analyzer.getSalesTrends();
        const chartData = {
            type: 'line',
            title: 'Sales Trends Over Time',
            xAxis: trendsData.map(item => item.date),
            yAxis: trendsData.map(item => item.revenue),
            trend: this.calculateTrendDirection(trendsData)
        };
        
        console.log('\n📈 Line Chart - Sales Trends:');
        console.log(`Date Range: ${chartData.xAxis[0]} to ${chartData.xAxis[chartData.xAxis.length - 1]}`);
        console.log(`Trend Direction: ${chartData.trend}`);
        console.log(`Peak Sales Day: ${this.findPeakSalesDay(trendsData)}`);
        
        return chartData;
    }
    
    // Create pie chart for product distribution
    createProductDistributionChart() {
        const topProducts = this.analyzer.getTopSellingProducts(6);
        const totalQuantity = topProducts.reduce((sum, product) => sum + product.quantity, 0);
        
        const chartData = {
            type: 'pie',
            title: 'Product Distribution by Quantity Sold',
            segments: topProducts.map(product => ({
                label: product.product,
                value: product.quantity,
                percentage: Math.round((product.quantity / totalQuantity) * 100)
            }))
        };
        
        console.log('\n🥧 Pie Chart - Product Distribution:');
        chartData.segments.forEach(segment => {
            const slice = '●'.repeat(Math.ceil(segment.percentage / 5));
            console.log(`${segment.label.padEnd(15)} | ${slice} ${segment.percentage}% (${segment.value} units)`);
        });
        
        return chartData;
    }
    
    // Generate scatter plot for price vs quantity analysis
    createPriceQuantityScatterPlot() {
        const scatterData = this.analyzer.data.map(item => ({
            x: item.price,
            y: item.quantity,
            category: item.category,
            product: item.product
        }));
        
        const chartData = {
            type: 'scatter',
            title: 'Price vs Quantity Analysis',
            points: scatterData,
            correlation: this.calculateCorrelation(scatterData)
        };
        
        console.log('\n📊 Scatter Plot - Price vs Quantity:');
        console.log(`Correlation: ${chartData.correlation.toFixed(3)}`);
        console.log(`Relationship: ${this.interpretCorrelation(chartData.correlation)}`);
        
        // Group by price ranges for display
        const priceRanges = this.groupByPriceRanges(scatterData);
        Object.entries(priceRanges).forEach(([range, items]) => {
            const avgQuantity = items.reduce((sum, item) => sum + item.y, 0) / items.length;
            console.log(`${range.padEnd(15)} | Avg Quantity: ${avgQuantity.toFixed(1)}`);
        });
        
        return chartData;
    }
    
    // Helper methods for chart calculations
    calculateTrendDirection(trendsData) {
        if (trendsData.length < 2) return 'Insufficient data';
        
        const firstHalf = trendsData.slice(0, Math.floor(trendsData.length / 2));
        const secondHalf = trendsData.slice(Math.floor(trendsData.length / 2));
        
        const firstAvg = firstHalf.reduce((sum, item) => sum + item.revenue, 0) / firstHalf.length;
        const secondAvg = secondHalf.reduce((sum, item) => sum + item.revenue, 0) / secondHalf.length;
        
        if (secondAvg > firstAvg * 1.1) return '📈 Upward';
        if (secondAvg < firstAvg * 0.9) return '📉 Downward';
        return '➡️ Stable';
    }
    
    findPeakSalesDay(trendsData) {
        const peak = trendsData.reduce((max, current) => 
            current.revenue > max.revenue ? current : max
        );
        return `${peak.date} ($${peak.revenue.toFixed(2)})`;
    }
    
    calculateCorrelation(data) {
        const n = data.length;
        const sumX = data.reduce((sum, point) => sum + point.x, 0);
        const sumY = data.reduce((sum, point) => sum + point.y, 0);
        const sumXY = data.reduce((sum, point) => sum + (point.x * point.y), 0);
        const sumX2 = data.reduce((sum, point) => sum + (point.x * point.x), 0);
        const sumY2 = data.reduce((sum, point) => sum + (point.y * point.y), 0);
        
        const numerator = n * sumXY - sumX * sumY;
        const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
        
        return denominator === 0 ? 0 : numerator / denominator;
    }
    
    interpretCorrelation(correlation) {
        const abs = Math.abs(correlation);
        if (abs >= 0.7) return 'Strong correlation';
        if (abs >= 0.5) return 'Moderate correlation';
        if (abs >= 0.3) return 'Weak correlation';
        return 'No significant correlation';
    }
    
    groupByPriceRanges(data) {
        const ranges = {
            '$0-50': [],
            '$51-100': [],
            '$101-250': [],
            '$251-500': [],
            '$501+': []
        };
        
        data.forEach(point => {
            if (point.x <= 50) ranges['$0-50'].push(point);
            else if (point.x <= 100) ranges['$51-100'].push(point);
            else if (point.x <= 250) ranges['$101-250'].push(point);
            else if (point.x <= 500) ranges['$251-500'].push(point);
            else ranges['$501+'].push(point);
        });
        
        return ranges;
    }
}

// Main analysis workflow
function runAnalysis() {
    console.log('🚀 Starting Data Analysis with GitHub Copilot');
    console.log('=' * 60);
    
    // Load data
    console.log('\n📁 Loading sample data...');
    const sampleData = generateSampleData(150); // Generate 150 sample records
    console.log(`✅ Generated ${sampleData.length} sample records`);
    
    // Clean and validate data
    console.log('\n🧹 Cleaning and validating data...');
    const validData = sampleData.filter(item => 
        item.price > 0 && 
        item.quantity > 0 && 
        item.revenue > 0 &&
        item.date && 
        item.product && 
        item.category
    );
    console.log(`✅ Validated ${validData.length} records (removed ${sampleData.length - validData.length} invalid)`);
    
    // Perform analysis
    console.log('\n📊 Performing data analysis...');
    const analyzer = new DataAnalyzer(validData);
    const stats = analyzer.generateSummaryStatistics();
    
    // Display key metrics
    console.log('\n📈 KEY BUSINESS METRICS:');
    console.log(`Total Revenue: $${stats.overview.totalRevenue.toLocaleString()}`);
    console.log(`Total Orders: ${stats.overview.totalOrders.toLocaleString()}`);
    console.log(`Average Order Value: $${stats.overview.averageOrderValue}`);
    console.log(`Total Items Sold: ${stats.overview.totalQuantitySold.toLocaleString()}`);
    
    console.log('\n🏆 TOP SELLING PRODUCTS:');
    stats.topProducts.forEach((product, index) => {
        console.log(`${index + 1}. ${product.product} - ${product.quantity} units sold`);
    });
    
    console.log('\n🎯 SALES BY CATEGORY:');
    Object.entries(stats.categoryBreakdown).forEach(([category, data]) => {
        console.log(`${category}: $${data.revenue.toFixed(2)} revenue (${data.orders} orders)`);
    });
    
    // Generate visualizations
    console.log('\n🎨 Generating visualizations...');
    const visualizer = new DataVisualizer(analyzer);
    
    visualizer.createCategoryBarChart();
    visualizer.createSalesTrendChart();
    visualizer.createProductDistributionChart();
    visualizer.createPriceQuantityScatterPlot();
    
    // Calculate growth metrics
    console.log('\n📈 GROWTH ANALYSIS:');
    const growthRates = analyzer.calculateMonthlyGrowthRate();
    if (growthRates.length > 0) {
        growthRates.forEach(month => {
            const trend = month.growthRate > 0 ? '📈' : '📉';
            console.log(`${month.month}: ${trend} ${month.growthRate}% growth`);
        });
    } else {
        console.log('Insufficient data for growth analysis (need multiple months)');
    }
    
    // Export results
    console.log('\n💾 Exporting results...');
    const results = {
        timestamp: new Date().toISOString(),
        summary: stats,
        rawData: validData,
        analysis: {
            totalRecords: validData.length,
            dateRange: `${stats.dateRange.startDate} to ${stats.dateRange.endDate}`,
            categories: Object.keys(stats.categoryBreakdown),
            topPerformers: stats.topProducts
        }
    };
    
    console.log('✅ Analysis complete! Results ready for export.');
    console.log('\n🎯 RECOMMENDATIONS:');
    generateRecommendations(analyzer);
    
    return results;
}

// Generate business recommendations based on analysis
function generateRecommendations(analyzer) {
    const categoryData = analyzer.getBestPerformingCategories();
    const topProducts = analyzer.getTopSellingProducts(3);
    const avgOrderValue = analyzer.calculateAverageOrderValue();
    
    console.log('\n💡 Based on the analysis, here are key recommendations:');
    
    // Revenue recommendations
    const topCategory = categoryData[0];
    console.log(`1. 🎯 Focus on ${topCategory.category} - your highest revenue category ($${topCategory.revenue.toFixed(2)})`);
    
    // Product recommendations
    console.log(`2. 📦 Stock up on ${topProducts[0].product} - your bestselling product (${topProducts[0].quantity} units sold)`);
    
    // Pricing recommendations
    if (avgOrderValue < 100) {
        console.log(`3. 💰 Consider bundle deals to increase average order value (currently $${avgOrderValue.toFixed(2)})`);
    } else {
        console.log(`3. ✅ Good average order value of $${avgOrderValue.toFixed(2)} - maintain current pricing strategy`);
    }
    
    // Category diversification
    if (categoryData.length < 4) {
        console.log('4. 🌱 Consider expanding into new product categories for diversification');
    } else {
        console.log('4. ✅ Good category diversification - monitor performance across all categories');
    }
    
    console.log('\n🚀 Ready to implement these insights for business growth!');
}

module.exports = { DataAnalyzer, DataVisualizer, generateSampleData, runAnalysis };

// ========== ADVANCED ANALYTICS METHODS ==========
// Practice these with GitHub Copilot!

// Calculate customer lifetime value from repeat purchases
function calculateCustomerLifetimeValue(data) {
    const customerMetrics = {};
    
    // Group transactions by customer (simulate customer IDs)
    data.forEach(item => {
        // Create customer ID based on product preference pattern
        const customerId = `CUST_${item.product.slice(0, 3)}_${item.date.slice(-2)}`;
        
        if (!customerMetrics[customerId]) {
            customerMetrics[customerId] = {
                totalRevenue: 0,
                orderCount: 0,
                firstPurchase: item.date,
                lastPurchase: item.date,
                avgOrderValue: 0,
                daysBetweenOrders: 0
            };
        }
        
        customerMetrics[customerId].totalRevenue += item.revenue;
        customerMetrics[customerId].orderCount += 1;
        customerMetrics[customerId].lastPurchase = item.date;
    });
    
    // Calculate CLV for each customer
    const clvResults = Object.entries(customerMetrics).map(([customerId, metrics]) => {
        const daysBetween = Math.max(1, (new Date(metrics.lastPurchase) - new Date(metrics.firstPurchase)) / (1000 * 60 * 60 * 24));
        const avgOrderValue = metrics.totalRevenue / metrics.orderCount;
        const purchaseFrequency = metrics.orderCount / Math.max(1, daysBetween / 30); // orders per month
        const customerLifespan = Math.max(3, daysBetween / 30); // months
        
        const clv = avgOrderValue * purchaseFrequency * customerLifespan;
        
        return {
            customerId,
            clv: Math.round(clv * 100) / 100,
            totalRevenue: metrics.totalRevenue,
            orderCount: metrics.orderCount,
            avgOrderValue: Math.round(avgOrderValue * 100) / 100,
            lifespanMonths: Math.round(customerLifespan * 10) / 10
        };
    });
    
    // Sort by CLV descending
    return clvResults.sort((a, b) => b.clv - a.clv);
}

// Find seasonal trends in product categories
function findSeasonalTrends(data) {
    const seasonalData = {
        'Q1 (Jan-Mar)': { months: ['01', '02', '03'], categories: {} },
        'Q2 (Apr-Jun)': { months: ['04', '05', '06'], categories: {} },
        'Q3 (Jul-Sep)': { months: ['07', '08', '09'], categories: {} },
        'Q4 (Oct-Dec)': { months: ['10', '11', '12'], categories: {} }
    };
    
    // Group sales by quarter and category
    data.forEach(item => {
        const month = item.date.substring(5, 7);
        
        Object.entries(seasonalData).forEach(([quarter, quarterData]) => {
            if (quarterData.months.includes(month)) {
                if (!quarterData.categories[item.category]) {
                    quarterData.categories[item.category] = {
                        revenue: 0,
                        quantity: 0,
                        orders: 0
                    };
                }
                quarterData.categories[item.category].revenue += item.revenue;
                quarterData.categories[item.category].quantity += item.quantity;
                quarterData.categories[item.category].orders += 1;
            }
        });
    });
    
    // Calculate seasonal performance
    const trends = {};
    Object.entries(seasonalData).forEach(([quarter, quarterData]) => {
        trends[quarter] = Object.entries(quarterData.categories)
            .map(([category, data]) => ({
                category,
                revenue: Math.round(data.revenue * 100) / 100,
                quantity: data.quantity,
                orders: data.orders,
                avgOrderValue: Math.round((data.revenue / data.orders) * 100) / 100
            }))
            .sort((a, b) => b.revenue - a.revenue);
    });
    
    return trends;
}

// Identify products with declining sales
function identifyDecliningProducts(data) {
    const monthlyProductSales = {};
    
    // Group by month and product
    data.forEach(item => {
        const month = item.date.substring(0, 7); // YYYY-MM
        const key = `${month}_${item.product}`;
        
        if (!monthlyProductSales[key]) {
            monthlyProductSales[key] = {
                month,
                product: item.product,
                category: item.category,
                revenue: 0,
                quantity: 0
            };
        }
        
        monthlyProductSales[key].revenue += item.revenue;
        monthlyProductSales[key].quantity += item.quantity;
    });
    
    // Convert to array and group by product
    const productTrends = {};
    Object.values(monthlyProductSales).forEach(item => {
        if (!productTrends[item.product]) {
            productTrends[item.product] = [];
        }
        productTrends[item.product].push(item);
    });
    
    // Analyze trends for each product
    const decliningProducts = [];
    Object.entries(productTrends).forEach(([product, monthlyData]) => {
        if (monthlyData.length >= 3) { // Need at least 3 months of data
            monthlyData.sort((a, b) => a.month.localeCompare(b.month));
            
            // Calculate trend using linear regression
            const n = monthlyData.length;
            const xValues = monthlyData.map((_, index) => index + 1);
            const yValues = monthlyData.map(item => item.revenue);
            
            const sumX = xValues.reduce((sum, x) => sum + x, 0);
            const sumY = yValues.reduce((sum, y) => sum + y, 0);
            const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
            const sumX2 = xValues.reduce((sum, x) => sum + x * x, 0);
            
            const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
            const avgRevenue = sumY / n;
            const percentDecline = (slope / avgRevenue) * 100;
            
            if (slope < 0 && percentDecline < -10) { // Declining by more than 10%
                decliningProducts.push({
                    product,
                    category: monthlyData[0].category,
                    trendSlope: Math.round(slope * 100) / 100,
                    percentDecline: Math.round(percentDecline * 100) / 100,
                    avgMonthlyRevenue: Math.round(avgRevenue * 100) / 100,
                    monthsAnalyzed: n
                });
            }
        }
    });
    
    return decliningProducts.sort((a, b) => a.percentDecline - b.percentDecline);
}

// Calculate profit margins by category
function calculateProfitMargins(data) {
    // Simulate cost data (typically would come from inventory system)
    const costRatios = {
        'Electronics': 0.65, // 65% of selling price is cost
        'Home': 0.45,
        'Sports': 0.55,
        'Books': 0.40
    };
    
    const categoryMetrics = {};
    
    data.forEach(item => {
        const costRatio = costRatios[item.category] || 0.50;
        const cost = item.revenue * costRatio;
        const profit = item.revenue - cost;
        const margin = (profit / item.revenue) * 100;
        
        if (!categoryMetrics[item.category]) {
            categoryMetrics[item.category] = {
                totalRevenue: 0,
                totalCost: 0,
                totalProfit: 0,
                orderCount: 0
            };
        }
        
        categoryMetrics[item.category].totalRevenue += item.revenue;
        categoryMetrics[item.category].totalCost += cost;
        categoryMetrics[item.category].totalProfit += profit;
        categoryMetrics[item.category].orderCount += 1;
    });
    
    return Object.entries(categoryMetrics).map(([category, metrics]) => ({
        category,
        totalRevenue: Math.round(metrics.totalRevenue * 100) / 100,
        totalCost: Math.round(metrics.totalCost * 100) / 100,
        totalProfit: Math.round(metrics.totalProfit * 100) / 100,
        profitMargin: Math.round((metrics.totalProfit / metrics.totalRevenue) * 10000) / 100,
        avgProfitPerOrder: Math.round((metrics.totalProfit / metrics.orderCount) * 100) / 100
    })).sort((a, b) => b.profitMargin - a.profitMargin);
}

// Generate forecasts for next quarter
function generateQuarterlyForecast(data) {
    const monthlyTotals = {};
    
    // Group data by month
    data.forEach(item => {
        const month = item.date.substring(0, 7);
        if (!monthlyTotals[month]) {
            monthlyTotals[month] = 0;
        }
        monthlyTotals[month] += item.revenue;
    });
    
    const months = Object.keys(monthlyTotals).sort();
    const revenues = months.map(month => monthlyTotals[month]);
    
    if (revenues.length < 3) {
        return { error: 'Insufficient data for forecasting (need at least 3 months)' };
    }
    
    // Simple linear trend forecasting
    const n = revenues.length;
    const xValues = revenues.map((_, index) => index + 1);
    const yValues = revenues;
    
    const sumX = xValues.reduce((sum, x) => sum + x, 0);
    const sumY = yValues.reduce((sum, y) => sum + y, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * yValues[i], 0);
    const sumX2 = xValues.reduce((sum, x) => sum + x * x, 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // Forecast next 3 months
    const forecasts = [];
    for (let i = 1; i <= 3; i++) {
        const nextX = n + i;
        const forecast = slope * nextX + intercept;
        forecasts.push({
            month: `Month +${i}`,
            forecastRevenue: Math.round(Math.max(0, forecast) * 100) / 100
        });
    }
    
    const quarterlyForecast = forecasts.reduce((sum, f) => sum + f.forecastRevenue, 0);
    const currentQuarterlyAvg = revenues.slice(-3).reduce((sum, r) => sum + r, 0);
    const growthRate = ((quarterlyForecast - currentQuarterlyAvg) / currentQuarterlyAvg) * 100;
    
    return {
        monthlyForecasts: forecasts,
        quarterlyTotal: Math.round(quarterlyForecast * 100) / 100,
        expectedGrowthRate: Math.round(growthRate * 100) / 100,
        confidence: revenues.length >= 6 ? 'High' : 'Medium',
        trendDirection: slope > 0 ? 'Upward' : 'Downward'
    };
}

// Find correlation between price and sales volume
function findPriceVolumeCorrelation(data) {
    // Group by price ranges and calculate average volume
    const priceRanges = {
        '$0-25': { prices: [], volumes: [], count: 0 },
        '$26-50': { prices: [], volumes: [], count: 0 },
        '$51-100': { prices: [], volumes: [], count: 0 },
        '$101-250': { prices: [], volumes: [], count: 0 },
        '$251-500': { prices: [], volumes: [], count: 0 },
        '$501+': { prices: [], volumes: [], count: 0 }
    };
    
    data.forEach(item => {
        const price = item.price;
        const volume = item.quantity;
        
        if (price <= 25) {
            priceRanges['$0-25'].prices.push(price);
            priceRanges['$0-25'].volumes.push(volume);
            priceRanges['$0-25'].count++;
        } else if (price <= 50) {
            priceRanges['$26-50'].prices.push(price);
            priceRanges['$26-50'].volumes.push(volume);
            priceRanges['$26-50'].count++;
        } else if (price <= 100) {
            priceRanges['$51-100'].prices.push(price);
            priceRanges['$51-100'].volumes.push(volume);
            priceRanges['$51-100'].count++;
        } else if (price <= 250) {
            priceRanges['$101-250'].prices.push(price);
            priceRanges['$101-250'].volumes.push(volume);
            priceRanges['$101-250'].count++;
        } else if (price <= 500) {
            priceRanges['$251-500'].prices.push(price);
            priceRanges['$251-500'].volumes.push(volume);
            priceRanges['$251-500'].count++;
        } else {
            priceRanges['$501+'].prices.push(price);
            priceRanges['$501+'].volumes.push(volume);
            priceRanges['$501+'].count++;
        }
    });
    
    // Calculate correlation coefficient
    const allPrices = data.map(item => item.price);
    const allVolumes = data.map(item => item.quantity);
    
    const n = allPrices.length;
    const sumX = allPrices.reduce((sum, price) => sum + price, 0);
    const sumY = allVolumes.reduce((sum, volume) => sum + volume, 0);
    const sumXY = allPrices.reduce((sum, price, i) => sum + price * allVolumes[i], 0);
    const sumX2 = allPrices.reduce((sum, price) => sum + price * price, 0);
    const sumY2 = allVolumes.reduce((sum, volume) => sum + volume * volume, 0);
    
    const correlation = (n * sumXY - sumX * sumY) / 
        Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
    
    // Analyze price ranges
    const rangeAnalysis = Object.entries(priceRanges).map(([range, data]) => {
        if (data.count === 0) return { range, avgPrice: 0, avgVolume: 0, count: 0 };
        
        const avgPrice = data.prices.reduce((sum, p) => sum + p, 0) / data.count;
        const avgVolume = data.volumes.reduce((sum, v) => sum + v, 0) / data.count;
        
        return {
            range,
            avgPrice: Math.round(avgPrice * 100) / 100,
            avgVolume: Math.round(avgVolume * 100) / 100,
            count: data.count
        };
    }).filter(item => item.count > 0);
    
    return {
        overallCorrelation: Math.round(correlation * 1000) / 1000,
        correlationStrength: Math.abs(correlation) >= 0.7 ? 'Strong' : 
                           Math.abs(correlation) >= 0.5 ? 'Moderate' : 
                           Math.abs(correlation) >= 0.3 ? 'Weak' : 'None',
        correlationDirection: correlation > 0 ? 'Positive' : 'Negative',
        priceRangeAnalysis: rangeAnalysis
    };
}

// Create cohort analysis for customer retention
function createCohortAnalysis(data) {
    // Simulate customer cohorts based on first purchase month
    const customerCohorts = {};
    const customerFirstPurchase = {};
    
    // Identify first purchase for each customer
    data.forEach(item => {
        const customerId = `CUST_${item.product.slice(0, 3)}_${item.date.slice(-2)}`;
        const purchaseMonth = item.date.substring(0, 7);
        
        if (!customerFirstPurchase[customerId]) {
            customerFirstPurchase[customerId] = purchaseMonth;
        } else if (purchaseMonth < customerFirstPurchase[customerId]) {
            customerFirstPurchase[customerId] = purchaseMonth;
        }
    });
    
    // Group customers into cohorts by first purchase month
    Object.entries(customerFirstPurchase).forEach(([customerId, firstMonth]) => {
        if (!customerCohorts[firstMonth]) {
            customerCohorts[firstMonth] = new Set();
        }
        customerCohorts[firstMonth].add(customerId);
    });
    
    // Track retention for each cohort
    const cohortAnalysis = Object.entries(customerCohorts).map(([cohortMonth, customers]) => {
        const cohortSize = customers.size;
        const retentionData = {};
        
        // Check retention in subsequent months
        data.forEach(item => {
            const customerId = `CUST_${item.product.slice(0, 3)}_${item.date.slice(-2)}`;
            const purchaseMonth = item.date.substring(0, 7);
            
            if (customers.has(customerId) && purchaseMonth >= cohortMonth) {
                if (!retentionData[purchaseMonth]) {
                    retentionData[purchaseMonth] = new Set();
                }
                retentionData[purchaseMonth].add(customerId);
            }
        });
        
        // Calculate retention percentages
        const retentionRates = Object.entries(retentionData).map(([month, activeCustomers]) => ({
            month,
            activeCustomers: activeCustomers.size,
            retentionRate: Math.round((activeCustomers.size / cohortSize) * 10000) / 100
        })).sort((a, b) => a.month.localeCompare(b.month));
        
        return {
            cohortMonth,
            cohortSize,
            retentionByMonth: retentionRates
        };
    }).sort((a, b) => a.cohortMonth.localeCompare(b.cohortMonth));
    
    return cohortAnalysis;
}

// Test function to run all advanced analytics
function runAdvancedAnalytics() {
    console.log('\n🔬 ADVANCED ANALYTICS DEMO');
    console.log('=' * 50);
    
    // Generate sample data
    const sampleData = generateSampleData(200);
    
    console.log('\n💰 Customer Lifetime Value Analysis:');
    const clvData = calculateCustomerLifetimeValue(sampleData);
    clvData.slice(0, 5).forEach((customer, index) => {
        console.log(`${index + 1}. ${customer.customerId}: CLV $${customer.clv} (${customer.orderCount} orders)`);
    });
    
    console.log('\n🌟 Seasonal Trends Analysis:');
    const seasonalTrends = findSeasonalTrends(sampleData);
    Object.entries(seasonalTrends).forEach(([quarter, categories]) => {
        console.log(`${quarter}:`);
        categories.slice(0, 2).forEach(cat => {
            console.log(`  ${cat.category}: $${cat.revenue} revenue`);
        });
    });
    
    console.log('\n📉 Declining Products:');
    const decliningProducts = identifyDecliningProducts(sampleData);
    if (decliningProducts.length > 0) {
        decliningProducts.slice(0, 3).forEach(product => {
            console.log(`  ${product.product}: ${product.percentDecline}% decline`);
        });
    } else {
        console.log('  No significantly declining products found');
    }
    
    console.log('\n💹 Profit Margins by Category:');
    const profitMargins = calculateProfitMargins(sampleData);
    profitMargins.forEach(category => {
        console.log(`  ${category.category}: ${category.profitMargin}% margin`);
    });
    
    console.log('\n🔮 Quarterly Forecast:');
    const forecast = generateQuarterlyForecast(sampleData);
    if (!forecast.error) {
        console.log(`  Next Quarter: $${forecast.quarterlyTotal} (${forecast.expectedGrowthRate}% growth)`);
        console.log(`  Trend: ${forecast.trendDirection} | Confidence: ${forecast.confidence}`);
    } else {
        console.log(`  ${forecast.error}`);
    }
    
    console.log('\n📊 Price-Volume Correlation:');
    const correlation = findPriceVolumeCorrelation(sampleData);
    console.log(`  Correlation: ${correlation.overallCorrelation} (${correlation.correlationStrength})`);
    console.log(`  Direction: ${correlation.correlationDirection}`);
    
    console.log('\n👥 Cohort Retention Analysis:');
    const cohorts = createCohortAnalysis(sampleData);
    cohorts.slice(0, 3).forEach(cohort => {
        const firstMonth = cohort.retentionByMonth[0];
        const retention = firstMonth ? firstMonth.retentionRate : 0;
        console.log(`  ${cohort.cohortMonth}: ${cohort.cohortSize} customers (${retention}% retention)`);
    });
    
    console.log('\n✨ Advanced analytics complete!');
}

// Test function to run EXPERT-LEVEL analytics
function runExpertAnalytics() {
    console.log('\n🎯 EXPERT-LEVEL ANALYTICS DEMO');
    console.log('=' * 60);
    
    // Generate larger dataset for more comprehensive analysis
    const expertData = generateSampleData(300);
    
    console.log('\n💼 Marketing ROI Analysis:');
    const marketingROI = calculateMarketingROI(expertData);
    marketingROI.slice(0, 3).forEach(campaign => {
        console.log(`  ${campaign.campaignName}: ${campaign.roi}% ROI (${campaign.profitability})`);
        console.log(`    Revenue: $${campaign.revenue} | Cost: $${campaign.cost} | Orders: ${campaign.orders}`);
    });
    
    console.log('\n🎁 Product Bundling Opportunities:');
    const bundling = identifyBundlingOpportunities(expertData);
    console.log('  Top Overall Bundles:');
    bundling.overallBundles.slice(0, 3).forEach(bundle => {
        console.log(`    ${bundle.pair}: ${bundle.frequency} times together`);
    });
    
    console.log('\n📦 Inventory Optimization Model:');
    const inventory = createInventoryOptimizationModel(expertData);
    inventory.slice(0, 4).forEach(item => {
        console.log(`  ${item.product} (${item.category}):`);
        console.log(`    Monthly Sales: ${item.avgMonthlySales} | Risk: ${item.recommendations.riskLevel}`);
        console.log(`    Reorder Point: ${item.recommendations.reorderPoint} | Optimal Stock: ${item.recommendations.optimalStock}`);
    });
    
    console.log('\n🔄 Customer Journey Analysis:');
    const journey = analyzeCustomerJourney(expertData);
    console.log(`  Single Purchase Customers: ${journey.singlePurchase}`);
    console.log(`  Repeat Customers: ${journey.repeatCustomers}`);
    console.log(`  Average Days to Repeat: ${journey.avgTimeToRepeat}`);
    console.log(`  Cross-Category Purchases: ${journey.crossCategoryPurchases}`);
    console.log('  Top Journey Patterns:');
    journey.topJourneyPatterns.slice(0, 3).forEach(pattern => {
        console.log(`    ${pattern.pattern}: ${pattern.count} customers`);
    });
    
    console.log('\n🚨 Performance Alerts:');
    const alerts = generatePerformanceAlerts(expertData);
    if (alerts.length > 0) {
        alerts.slice(0, 4).forEach(alert => {
            console.log(`  [${alert.type}] ${alert.product}: ${alert.issue}`);
            console.log(`    ${alert.details} | Action: ${alert.action}`);
        });
    } else {
        console.log('  No performance alerts at this time');
    }
    
    console.log('\n📈 Price Elasticity Analysis:');
    const elasticity = calculatePriceElasticity(expertData);
    elasticity.forEach(category => {
        if (typeof category.elasticity === 'number') {
            console.log(`  ${category.category}: ${category.elasticity} (${category.demandType})`);
            console.log(`    ${category.pricingRecommendation}`);
        } else {
            console.log(`  ${category.category}: ${category.elasticity}`);
        }
    });
    
    console.log('\n👤 Customer Segmentation (RFM Analysis):');
    const segmentation = createCustomerSegmentation(expertData);
    Object.entries(segmentation.segmentStatistics).forEach(([segment, stats]) => {
        console.log(`  ${segment}: ${stats.count} customers (${stats.percentOfCustomers}%)`);
        console.log(`    Avg Revenue: $${stats.avgMonetary} | Avg Frequency: ${stats.avgFrequency}`);
    });
    
    console.log('\n🎊 Expert analytics complete! All systems operational.');
    console.log('\n💡 Pro Tip: Use these insights to optimize your business strategy!');
}

// Add comprehensive test runner
function runAllAnalytics() {
    console.log('🚀 COMPREHENSIVE DATA ANALYTICS SUITE');
    console.log('=' * 70);
    
    // Run basic analysis
    console.log('\n📊 BASIC ANALYSIS:');
    runAnalysis();
    
    // Run advanced analytics
    runAdvancedAnalytics();
    
    // Run expert-level analytics
    runExpertAnalytics();
    
    console.log('\n🎯 SUMMARY:');
    console.log('✅ Basic business metrics calculated');
    console.log('✅ Advanced analytics completed');
    console.log('✅ Expert-level insights generated');
    console.log('✅ All 14 analytics functions operational');
    console.log('\n🚀 Your data analysis system is ready for production!');
}

// Test specific analytics
const data = generateSampleData(150);

// Test CLV
const clv = calculateCustomerLifetimeValue(data);
console.log('Top 5 Customers by CLV:', clv.slice(0, 5));

// Test seasonal trends
const trends = findSeasonalTrends(data);
console.log('Seasonal Trends:', trends);

// Test forecasting
const forecast = generateQuarterlyForecast(data);
console.log('Forecast:', forecast);

// Calculate customer lifetime value from repeat purchases
// Find seasonal trends in product categories  
// Identify products with declining sales
// Calculate profit margins by category
// Generate forecasts for next quarter
// Find correlation between price and sales volume
// Create cohort analysis for customer retention

// ========== EXPERT-LEVEL ANALYTICS FUNCTIONS ==========
// Advanced business intelligence with GitHub Copilot

// Calculate return on investment for marketing campaigns
function calculateMarketingROI(salesData, campaignData = null) {
    // Simulate marketing campaign data (would typically come from CRM/Marketing tools)
    const campaigns = campaignData || [
        { name: 'Summer Electronics Sale', startDate: '2024-06-01', endDate: '2024-08-31', cost: 5000, category: 'Electronics' },
        { name: 'Back to School Books', startDate: '2024-08-01', endDate: '2024-09-30', cost: 2000, category: 'Books' },
        { name: 'Holiday Home Decor', startDate: '2024-11-01', endDate: '2024-12-31', cost: 3500, category: 'Home' },
        { name: 'New Year Fitness', startDate: '2024-12-15', endDate: '2024-02-28', cost: 4000, category: 'Sports' }
    ];
    
    const campaignROI = campaigns.map(campaign => {
        // Filter sales data for campaign period and category
        const campaignSales = salesData.filter(sale => {
            const saleDate = new Date(sale.date);
            const startDate = new Date(campaign.startDate);
            const endDate = new Date(campaign.endDate);
            
            return saleDate >= startDate && 
                   saleDate <= endDate && 
                   sale.category === campaign.category;
        });
        
        const totalRevenue = campaignSales.reduce((sum, sale) => sum + sale.revenue, 0);
        const totalOrders = campaignSales.length;
        const roi = ((totalRevenue - campaign.cost) / campaign.cost) * 100;
        const costPerAcquisition = totalOrders > 0 ? campaign.cost / totalOrders : 0;
        
        return {
            campaignName: campaign.name,
            category: campaign.category,
            period: `${campaign.startDate} to ${campaign.endDate}`,
            cost: campaign.cost,
            revenue: Math.round(totalRevenue * 100) / 100,
            orders: totalOrders,
            roi: Math.round(roi * 100) / 100,
            costPerAcquisition: Math.round(costPerAcquisition * 100) / 100,
            profitability: roi > 0 ? 'Profitable' : 'Loss'
        };
    });
    
    // Sort by ROI descending
    return campaignROI.sort((a, b) => b.roi - a.roi);
}

// Identify seasonal product bundling opportunities
function identifyBundlingOpportunities(salesData) {
    // Analyze products frequently bought together within same time periods
    const coOccurrenceMatrix = {};
    const monthlyPurchases = {};
    
    // Group purchases by month and customer pattern
    salesData.forEach(sale => {
        const month = sale.date.substring(0, 7);
        const customerId = `CUST_${sale.product.slice(0, 3)}_${sale.date.slice(-2)}`;
        
        if (!monthlyPurchases[month]) {
            monthlyPurchases[month] = {};
        }
        
        if (!monthlyPurchases[month][customerId]) {
            monthlyPurchases[month][customerId] = [];
        }
        
        monthlyPurchases[month][customerId].push(sale.product);
    });
    
    // Calculate product co-occurrence
    Object.values(monthlyPurchases).forEach(monthData => {
        Object.values(monthData).forEach(customerProducts => {
            // Find product pairs for customers who bought multiple items
            for (let i = 0; i < customerProducts.length; i++) {
                for (let j = i + 1; j < customerProducts.length; j++) {
                    const product1 = customerProducts[i];
                    const product2 = customerProducts[j];
                    const pair = [product1, product2].sort().join(' + ');
                    
                    if (!coOccurrenceMatrix[pair]) {
                        coOccurrenceMatrix[pair] = 0;
                    }
                    coOccurrenceMatrix[pair]++;
                }
            }
        });
    });
    
    // Identify seasonal patterns
    const seasonalBundles = {};
    const quarters = {
        'Q1': ['01', '02', '03'],
        'Q2': ['04', '05', '06'], 
        'Q3': ['07', '08', '09'],
        'Q4': ['10', '11', '12']
    };
    
    Object.entries(quarters).forEach(([quarter, months]) => {
        const quarterlyCoOccurrence = {};
        
        Object.entries(monthlyPurchases).forEach(([month, monthData]) => {
            if (months.includes(month.substring(5, 7))) {
                Object.values(monthData).forEach(customerProducts => {
                    for (let i = 0; i < customerProducts.length; i++) {
                        for (let j = i + 1; j < customerProducts.length; j++) {
                            const product1 = customerProducts[i];
                            const product2 = customerProducts[j];
                            const pair = [product1, product2].sort().join(' + ');
                            
                            if (!quarterlyCoOccurrence[pair]) {
                                quarterlyCoOccurrence[pair] = 0;
                            }
                            quarterlyCoOccurrence[pair]++;
                        }
                    }
                });
            }
        });
        
        // Get top bundles for this quarter
        const topBundles = Object.entries(quarterlyCoOccurrence)
            .map(([pair, frequency]) => ({ pair, frequency }))
            .sort((a, b) => b.frequency - a.frequency)
            .slice(0, 5);
            
        seasonalBundles[quarter] = topBundles;
    });
    
    return {
        overallBundles: Object.entries(coOccurrenceMatrix)
            .map(([pair, frequency]) => ({ pair, frequency }))
            .sort((a, b) => b.frequency - a.frequency)
            .slice(0, 10),
        seasonalBundles
    };
}

// Create predictive model for inventory optimization
function createInventoryOptimizationModel(salesData) {
    // Analyze sales velocity and seasonal patterns for inventory planning
    const productMetrics = {};
    
    // Calculate key metrics for each product
    salesData.forEach(sale => {
        if (!productMetrics[sale.product]) {
            productMetrics[sale.product] = {
                category: sale.category,
                totalSales: 0,
                totalRevenue: 0,
                orders: 0,
                monthlySales: {},
                priceHistory: []
            };
        }
        
        const month = sale.date.substring(0, 7);
        if (!productMetrics[sale.product].monthlySales[month]) {
            productMetrics[sale.product].monthlySales[month] = 0;
        }
        
        productMetrics[sale.product].totalSales += sale.quantity;
        productMetrics[sale.product].totalRevenue += sale.revenue;
        productMetrics[sale.product].orders += 1;
        productMetrics[sale.product].monthlySales[month] += sale.quantity;
        productMetrics[sale.product].priceHistory.push(sale.price);
    });
    
    // Calculate inventory recommendations
    const inventoryRecommendations = Object.entries(productMetrics).map(([product, metrics]) => {
        const monthlyValues = Object.values(metrics.monthlySales);
        const avgMonthlySales = monthlyValues.reduce((sum, val) => sum + val, 0) / monthlyValues.length;
        const salesVelocity = avgMonthlySales; // units per month
        
        // Calculate seasonality factor
        const maxMonthlySales = Math.max(...monthlyValues);
        const minMonthlySales = Math.min(...monthlyValues);
        const seasonalityFactor = maxMonthlySales / Math.max(1, minMonthlySales);
        
        // Calculate price volatility
        const avgPrice = metrics.priceHistory.reduce((sum, price) => sum + price, 0) / metrics.priceHistory.length;
        const priceVariance = metrics.priceHistory.reduce((sum, price) => sum + Math.pow(price - avgPrice, 2), 0) / metrics.priceHistory.length;
        const priceVolatility = Math.sqrt(priceVariance) / avgPrice;
        
        // Inventory recommendations
        const safetyStock = Math.ceil(avgMonthlySales * 0.5); // 2 weeks buffer
        const reorderPoint = Math.ceil(avgMonthlySales * 0.75); // 3 weeks lead time
        const optimalStock = Math.ceil(avgMonthlySales * seasonalityFactor * 1.2);
        
        // Risk assessment
        let riskLevel = 'Low';
        if (seasonalityFactor > 3 || priceVolatility > 0.2) riskLevel = 'High';
        else if (seasonalityFactor > 2 || priceVolatility > 0.1) riskLevel = 'Medium';
        
        return {
            product,
            category: metrics.category,
            avgMonthlySales: Math.round(avgMonthlySales * 100) / 100,
            seasonalityFactor: Math.round(seasonalityFactor * 100) / 100,
            priceVolatility: Math.round(priceVolatility * 1000) / 1000,
            recommendations: {
                safetyStock,
                reorderPoint,
                optimalStock,
                riskLevel
            },
            totalRevenue: Math.round(metrics.totalRevenue * 100) / 100
        };
    });
    
    return inventoryRecommendations.sort((a, b) => b.totalRevenue - a.totalRevenue);
}

// Analyze customer journey from first to repeat purchase
function analyzeCustomerJourney(salesData) {
    const customerJourneys = {};
    
    // Group sales by customer and track their journey
    salesData.forEach(sale => {
        const customerId = `CUST_${sale.product.slice(0, 3)}_${sale.date.slice(-2)}`;
        
        if (!customerJourneys[customerId]) {
            customerJourneys[customerId] = [];
        }
        
        customerJourneys[customerId].push({
            date: sale.date,
            product: sale.product,
            category: sale.category,
            revenue: sale.revenue,
            quantity: sale.quantity
        });
    });
    
    // Analyze journey patterns
    const journeyAnalysis = {
        singlePurchase: 0,
        repeatCustomers: 0,
        avgTimeToRepeat: 0,
        categoryLoyalty: {},
        crossCategoryPurchases: 0,
        journeyPatterns: []
    };
    
    let totalRepeatDays = 0;
    let repeatCount = 0;
    
    Object.entries(customerJourneys).forEach(([customerId, purchases]) => {
        purchases.sort((a, b) => new Date(a.date) - new Date(b.date));
        
        if (purchases.length === 1) {
            journeyAnalysis.singlePurchase++;
        } else {
            journeyAnalysis.repeatCustomers++;
            
            // Calculate time between first and second purchase
            const firstPurchase = new Date(purchases[0].date);
            const secondPurchase = new Date(purchases[1].date);
            const daysBetween = (secondPurchase - firstPurchase) / (1000 * 60 * 60 * 24);
            
            totalRepeatDays += daysBetween;
            repeatCount++;
            
            // Analyze category loyalty
            const firstCategory = purchases[0].category;
            if (!journeyAnalysis.categoryLoyalty[firstCategory]) {
                journeyAnalysis.categoryLoyalty[firstCategory] = { total: 0, loyal: 0 };
            }
            journeyAnalysis.categoryLoyalty[firstCategory].total++;
            
            if (purchases[1].category === firstCategory) {
                journeyAnalysis.categoryLoyalty[firstCategory].loyal++;
            } else {
                journeyAnalysis.crossCategoryPurchases++;
            }
            
            // Create journey pattern
            const pattern = purchases.slice(0, 3).map(p => p.category).join(' → ');
            journeyAnalysis.journeyPatterns.push(pattern);
        }
    });
    
    // Calculate averages and patterns
    journeyAnalysis.avgTimeToRepeat = repeatCount > 0 ? Math.round(totalRepeatDays / repeatCount) : 0;
    
    // Calculate loyalty percentages
    Object.keys(journeyAnalysis.categoryLoyalty).forEach(category => {
        const data = journeyAnalysis.categoryLoyalty[category];
        data.loyaltyRate = Math.round((data.loyal / data.total) * 10000) / 100;
    });
    
    // Find most common journey patterns
    const patternCounts = {};
    journeyAnalysis.journeyPatterns.forEach(pattern => {
        patternCounts[pattern] = (patternCounts[pattern] || 0) + 1;
    });
    
    journeyAnalysis.topJourneyPatterns = Object.entries(patternCounts)
        .map(([pattern, count]) => ({ pattern, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);
    
    return journeyAnalysis;
}

// Generate automated alerts for declining product performance
function generatePerformanceAlerts(salesData) {
    const alerts = [];
    const currentDate = new Date();
    const threeMonthsAgo = new Date(currentDate.getTime() - (90 * 24 * 60 * 60 * 1000));
    
    // Get recent sales data (last 3 months)
    const recentSales = salesData.filter(sale => new Date(sale.date) >= threeMonthsAgo);
    
    // Analyze each product's performance
    const productPerformance = {};
    
    recentSales.forEach(sale => {
        const month = sale.date.substring(0, 7);
        
        if (!productPerformance[sale.product]) {
            productPerformance[sale.product] = {
                category: sale.category,
                monthlySales: {},
                monthlyRevenue: {}
            };
        }
        
        if (!productPerformance[sale.product].monthlySales[month]) {
            productPerformance[sale.product].monthlySales[month] = 0;
            productPerformance[sale.product].monthlyRevenue[month] = 0;
        }
        
        productPerformance[sale.product].monthlySales[month] += sale.quantity;
        productPerformance[sale.product].monthlyRevenue[month] += sale.revenue;
    });
    
    // Generate alerts based on performance criteria
    Object.entries(productPerformance).forEach(([product, data]) => {
        const months = Object.keys(data.monthlySales).sort();
        const salesValues = months.map(month => data.monthlySales[month]);
        const revenueValues = months.map(month => data.monthlyRevenue[month]);
        
        if (months.length >= 2) {
            // Check for declining sales trend
            const latestSales = salesValues[salesValues.length - 1];
            const previousSales = salesValues[salesValues.length - 2];
            const salesDecline = ((previousSales - latestSales) / previousSales) * 100;
            
            const latestRevenue = revenueValues[revenueValues.length - 1];
            const previousRevenue = revenueValues[revenueValues.length - 2];
            const revenueDecline = ((previousRevenue - latestRevenue) / previousRevenue) * 100;
            
            // Alert criteria
            if (salesDecline > 30) {
                alerts.push({
                    type: 'CRITICAL',
                    priority: 'High',
                    product,
                    category: data.category,
                    issue: 'Severe Sales Decline',
                    details: `Sales dropped ${salesDecline.toFixed(1)}% from previous month`,
                    action: 'Immediate investigation required',
                    impact: 'High revenue risk'
                });
            } else if (salesDecline > 15) {
                alerts.push({
                    type: 'WARNING',
                    priority: 'Medium',
                    product,
                    category: data.category,
                    issue: 'Sales Decline',
                    details: `Sales dropped ${salesDecline.toFixed(1)}% from previous month`,
                    action: 'Review pricing and marketing strategy',
                    impact: 'Medium revenue risk'
                });
            }
            
            // Zero sales alert
            if (latestSales === 0 && previousSales > 0) {
                alerts.push({
                    type: 'CRITICAL',
                    priority: 'High',
                    product,
                    category: data.category,
                    issue: 'No Sales This Month',
                    details: 'Product had sales last month but zero this month',
                    action: 'Check inventory and marketing',
                    impact: 'Potential stockout or demand issue'
                });
            }
            
            // Low performance alert
            const avgMonthlySales = salesValues.reduce((sum, val) => sum + val, 0) / salesValues.length;
            if (avgMonthlySales < 2 && avgMonthlySales > 0) {
                alerts.push({
                    type: 'INFO',
                    priority: 'Low',
                    product,
                    category: data.category,
                    issue: 'Low Sales Volume',
                    details: `Average monthly sales: ${avgMonthlySales.toFixed(1)} units`,
                    action: 'Consider discontinuation or promotion',
                    impact: 'Low revenue contribution'
                });
            }
        }
    });
    
    return alerts.sort((a, b) => {
        const priorityOrder = { 'High': 3, 'Medium': 2, 'Low': 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
}

// Calculate price elasticity for each product category
function calculatePriceElasticity(salesData) {
    const categoryElasticity = {};
    
    // Group data by category and calculate price-quantity relationships
    salesData.forEach(sale => {
        if (!categoryElasticity[sale.category]) {
            categoryElasticity[sale.category] = {
                dataPoints: [],
                products: new Set()
            };
        }
        
        categoryElasticity[sale.category].dataPoints.push({
            price: sale.price,
            quantity: sale.quantity,
            revenue: sale.revenue,
            product: sale.product
        });
        categoryElasticity[sale.category].products.add(sale.product);
    });
    
    // Calculate elasticity for each category
    const elasticityResults = Object.entries(categoryElasticity).map(([category, data]) => {
        const points = data.dataPoints;
        
        if (points.length < 5) {
            return {
                category,
                elasticity: 'Insufficient data',
                interpretation: 'Need more data points',
                productCount: data.products.size,
                dataPoints: points.length
            };
        }
        
        // Group by price ranges to calculate elasticity
        const priceRanges = {};
        points.forEach(point => {
            const priceRange = Math.floor(point.price / 50) * 50; // Group by $50 ranges
            if (!priceRanges[priceRange]) {
                priceRanges[priceRange] = { quantities: [], count: 0 };
            }
            priceRanges[priceRange].quantities.push(point.quantity);
            priceRanges[priceRange].count++;
        });
        
        // Calculate average quantity for each price range
        const priceQuantityPairs = Object.entries(priceRanges)
            .filter(([_, data]) => data.count >= 2) // Need multiple data points
            .map(([priceRange, data]) => ({
                price: parseInt(priceRange),
                avgQuantity: data.quantities.reduce((sum, q) => sum + q, 0) / data.count
            }))
            .sort((a, b) => a.price - b.price);
        
        if (priceQuantityPairs.length < 2) {
            return {
                category,
                elasticity: 'Insufficient price variation',
                interpretation: 'Need more price diversity',
                productCount: data.products.size,
                dataPoints: points.length
            };
        }
        
        // Calculate elasticity using percentage change method
        let totalElasticity = 0;
        let elasticityCount = 0;
        
        for (let i = 1; i < priceQuantityPairs.length; i++) {
            const p1 = priceQuantityPairs[i - 1];
            const p2 = priceQuantityPairs[i];
            
            const percentPriceChange = ((p2.price - p1.price) / p1.price) * 100;
            const percentQuantityChange = ((p2.avgQuantity - p1.avgQuantity) / p1.avgQuantity) * 100;
            
            if (percentPriceChange !== 0) {
                const elasticity = percentQuantityChange / percentPriceChange;
                totalElasticity += elasticity;
                elasticityCount++;
            }
        }
        
        const avgElasticity = elasticityCount > 0 ? totalElasticity / elasticityCount : 0;
        
        // Interpret elasticity
        let interpretation;
        let demandType;
        
        if (Math.abs(avgElasticity) > 1) {
            interpretation = 'Elastic demand - quantity sensitive to price changes';
            demandType = 'Elastic';
        } else if (Math.abs(avgElasticity) > 0.5) {
            interpretation = 'Moderately elastic - some price sensitivity';
            demandType = 'Moderately Elastic';
        } else {
            interpretation = 'Inelastic demand - quantity not very sensitive to price';
            demandType = 'Inelastic';
        }
        
        // Pricing recommendations
        let pricingRecommendation;
        if (avgElasticity < -1) {
            pricingRecommendation = 'Consider price reductions to increase revenue';
        } else if (avgElasticity > -0.5) {
            pricingRecommendation = 'Can increase prices with minimal quantity impact';
        } else {
            pricingRecommendation = 'Price changes should be moderate';
        }
        
        return {
            category,
            elasticity: Math.round(avgElasticity * 1000) / 1000,
            demandType,
            interpretation,
            pricingRecommendation,
            productCount: data.products.size,
            dataPoints: points.length,
            priceRanges: priceQuantityPairs.length
        };
    });
    
    return elasticityResults.sort((a, b) => b.dataPoints - a.dataPoints);
}

// Create customer segmentation based on purchase behavior
function createCustomerSegmentation(salesData) {
    const customerMetrics = {};
    
    // Calculate RFM metrics for each customer
    salesData.forEach(sale => {
        const customerId = `CUST_${sale.product.slice(0, 3)}_${sale.date.slice(-2)}`;
        
        if (!customerMetrics[customerId]) {
            customerMetrics[customerId] = {
                purchases: [],
                totalRevenue: 0,
                categories: new Set(),
                firstPurchase: sale.date,
                lastPurchase: sale.date
            };
        }
        
        customerMetrics[customerId].purchases.push({
            date: sale.date,
            revenue: sale.revenue,
            category: sale.category,
            product: sale.product
        });
        
        customerMetrics[customerId].totalRevenue += sale.revenue;
        customerMetrics[customerId].categories.add(sale.category);
        
        if (sale.date < customerMetrics[customerId].firstPurchase) {
            customerMetrics[customerId].firstPurchase = sale.date;
        }
        
        if (sale.date > customerMetrics[customerId].lastPurchase) {
            customerMetrics[customerId].lastPurchase = sale.date;
        }
    });
    
    // Calculate RFM scores
    const currentDate = new Date();
    const customerRFM = Object.entries(customerMetrics).map(([customerId, metrics]) => {
        const recency = Math.floor((currentDate - new Date(metrics.lastPurchase)) / (1000 * 60 * 60 * 24));
        const frequency = metrics.purchases.length;
        const monetary = metrics.totalRevenue;
        
        return {
            customerId,
            recency,
            frequency,
            monetary: Math.round(monetary * 100) / 100,
            categoryDiversity: metrics.categories.size,
            customerLifespan: Math.floor((new Date(metrics.lastPurchase) - new Date(metrics.firstPurchase)) / (1000 * 60 * 60 * 24)),
            avgOrderValue: Math.round((monetary / frequency) * 100) / 100
        };
    });
    
    // Calculate quintiles for RFM scoring
    const recencyValues = customerRFM.map(c => c.recency).sort((a, b) => a - b);
    const frequencyValues = customerRFM.map(c => c.frequency).sort((a, b) => b - a);
    const monetaryValues = customerRFM.map(c => c.monetary).sort((a, b) => b - a);
    
    const getQuintile = (value, values, reverse = false) => {
        const index = values.indexOf(value);
        const quintile = Math.ceil(((index + 1) / values.length) * 5);
        return reverse ? 6 - quintile : quintile;
    };
    
    // Assign RFM scores and segments
    const segmentedCustomers = customerRFM.map(customer => {
        const rScore = getQuintile(customer.recency, recencyValues, true); // Lower recency = higher score
        const fScore = getQuintile(customer.frequency, frequencyValues);
        const mScore = getQuintile(customer.monetary, monetaryValues);
        
        const rfmScore = `${rScore}${fScore}${mScore}`;
        
        // Determine segment based on RFM scores
        let segment;
        let description;
        let strategy;
        
        if (rScore >= 4 && fScore >= 4 && mScore >= 4) {
            segment = 'Champions';
            description = 'Best customers - high value, frequent, recent purchases';
            strategy = 'VIP treatment, exclusive offers, loyalty rewards';
        } else if (rScore >= 3 && fScore >= 3 && mScore >= 4) {
            segment = 'Loyal Customers';
            description = 'High value customers with good frequency';
            strategy = 'Personalized offers, cross-sell opportunities';
        } else if (rScore >= 4 && fScore <= 2 && mScore >= 3) {
            segment = 'Big Spenders';
            description = 'High value but infrequent purchases';
            strategy = 'Increase purchase frequency with targeted campaigns';
        } else if (rScore >= 4 && fScore >= 3 && mScore <= 2) {
            segment = 'Potential Loyalists';
            description = 'Recent and frequent but low spending';
            strategy = 'Increase spending with upsell campaigns';
        } else if (rScore <= 2 && fScore >= 3 && mScore >= 3) {
            segment = 'At Risk';
            description = 'Good customers who haven\'t purchased recently';
            strategy = 'Win-back campaigns, special discounts';
        } else if (rScore <= 2 && fScore <= 2 && mScore >= 4) {
            segment = 'Cannot Lose Them';
            description = 'High value customers who may be churning';
            strategy = 'Urgent retention efforts, personal outreach';
        } else if (rScore >= 3 && fScore <= 2 && mScore <= 2) {
            segment = 'New Customers';
            description = 'Recent but low frequency/value';
            strategy = 'Onboarding campaigns, education, engagement';
        } else {
            segment = 'Others';
            description = 'Various characteristics needing individual attention';
            strategy = 'Analyze individual patterns for custom approach';
        }
        
        return {
            ...customer,
            rfmScore,
            rScore,
            fScore,
            mScore,
            segment,
            description,
            strategy
        };
    });
    
    // Calculate segment statistics
    const segmentStats = {};
    segmentedCustomers.forEach(customer => {
        if (!segmentStats[customer.segment]) {
            segmentStats[customer.segment] = {
                count: 0,
                totalRevenue: 0,
                avgRecency: 0,
                avgFrequency: 0,
                avgMonetary: 0
            };
        }
        
        const stats = segmentStats[customer.segment];
        stats.count++;
        stats.totalRevenue += customer.monetary;
        stats.avgRecency += customer.recency;
        stats.avgFrequency += customer.frequency;
        stats.avgMonetary += customer.monetary;
    });
    
    // Calculate averages
    Object.values(segmentStats).forEach(stats => {
        stats.avgRecency = Math.round(stats.avgRecency / stats.count);
        stats.avgFrequency = Math.round((stats.avgFrequency / stats.count) * 100) / 100;
        stats.avgMonetary = Math.round((stats.avgMonetary / stats.count) * 100) / 100;
        stats.totalRevenue = Math.round(stats.totalRevenue * 100) / 100;
        stats.percentOfCustomers = Math.round((stats.count / segmentedCustomers.length) * 10000) / 100;
    });
    
    return {
        customerSegments: segmentedCustomers,
        segmentStatistics: segmentStats,
        totalCustomers: segmentedCustomers.length
    };
}

// Add this to the bottom of your file to test
runAllAnalytics();

// Calculate return on investment for marketing campaigns
// Identify seasonal product bundling opportunities  
// Create predictive model for inventory optimization
// Analyze customer journey from first to repeat purchase
// Generate automated alerts for declining product performance
// Calculate price elasticity for each product category
// Create customer segmentation based on purchase behavior
