// Carregar dados dos dashboards
async function carregarDashboards() {
    try {
        console.log('🚀 Iniciando carregamento dos dashboards...');

        // 1. Top Products (Valor)
        console.log('📊 Carregando top products...');
        const topProductsResponse = await fetch('/api/top_products');
        if (!topProductsResponse.ok) throw new Error('Erro ao carregar top products');
        const topProducts = await topProductsResponse.json();
        console.log('Top products carregados:', topProducts);

        if (topProducts && topProducts.length > 0) {
            new Chart(document.getElementById('topProductsChart'), {
                type: 'bar',
                data: {
                    labels: topProducts.map(p => p.produto ? p.produto.substring(0, 20) + (p.produto.length > 20 ? '...' : '') : 'N/A'),
                    datasets: [{
                        label: 'Valor Vendido (R$)',
                        data: topProducts.map(p => p.total_vendido || 0),
                        backgroundColor: 'rgba(54, 162, 235, 0.8)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        } else {
            document.getElementById('topProductsChart').innerHTML = '<p>Nenhum dado disponível</p>';
        }

        // 2. Daily Revenue
        console.log('📈 Carregando daily revenue...');
        const revenueResponse = await fetch('/api/daily_revenue');
        if (!revenueResponse.ok) throw new Error('Erro ao carregar daily revenue');
        const revenue = await revenueResponse.json();
        console.log('Daily revenue carregado:', revenue);

        if (revenue && revenue.length > 0) {
            new Chart(document.getElementById('revenueChart'), {
                type: 'line',
                data: {
                    labels: revenue.map(r => r.data || 'N/A'),
                    datasets: [{
                        label: 'Faturamento (R$)',
                        data: revenue.map(r => r.faturamento || 0),
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true
                }
            });
        } else {
            document.getElementById('revenueChart').innerHTML = '<p>Nenhum dado disponível</p>';
        }

        // 3. Discount Analysis
        console.log('💰 Carregando discount analysis...');
        const discountsResponse = await fetch('/api/discount_analysis');
        if (!discountsResponse.ok) throw new Error('Erro ao carregar discount analysis');
        const discounts = await discountsResponse.json();
        console.log('Discount analysis carregado:', discounts);

        if (discounts && discounts.length > 0) {
            new Chart(document.getElementById('discountChart'), {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Valor Bruto vs Desconto',
                        data: discounts.map(d => ({ 
                            x: d.valor_bruto || 0, 
                            y: d.desconto || 0 
                        })),
                        backgroundColor: 'rgba(75, 192, 192, 0.6)'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: { 
                            title: { display: true, text: 'Valor Bruto (R$)' },
                            beginAtZero: true
                        },
                        y: { 
                            title: { display: true, text: 'Desconto (R$)' },
                            beginAtZero: true
                        }
                    }
                }
            });
        } else {
            document.getElementById('discountChart').innerHTML = '<p>Nenhum dado disponível</p>';
        }

        // 4. Top Products por Quantidade
        console.log('📦 Carregando top products quantity...');
        const topQuantityResponse = await fetch('/api/top_products_quantity');
        if (!topQuantityResponse.ok) throw new Error('Erro ao carregar top products quantity');
        const topQuantity = await topQuantityResponse.json();
        console.log('Top products quantity carregado:', topQuantity);

        if (topQuantity && topQuantity.length > 0) {
            new Chart(document.getElementById('quantityChart'), {
                type: 'bar',
                data: {
                    labels: topQuantity.map(p => p.produto ? p.produto.substring(0, 20) + (p.produto.length > 20 ? '...' : '') : 'N/A'),
                    datasets: [{
                        label: 'Quantidade Vendida',
                        data: topQuantity.map(p => p.total_quantidade || 0),
                        backgroundColor: 'rgba(153, 102, 255, 0.8)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        } else {
            document.getElementById('quantityChart').innerHTML = '<p>Nenhum dado disponível</p>';
        }

        // 5. Vendas por CFOP
        console.log('🏷️ Carregando CFOP sales...');
        const cfopResponse = await fetch('/api/cfop_sales');
        if (!cfopResponse.ok) throw new Error('Erro ao carregar CFOP sales');
        const cfopData = await cfopResponse.json();
        console.log('CFOP sales carregado:', cfopData);

        if (cfopData && cfopData.length > 0) {
            new Chart(document.getElementById('cfopChart'), {
                type: 'doughnut',
                data: {
                    labels: cfopData.map(c => 'CFOP ' + (c.cfop || 'N/A')),
                    datasets: [{
                        data: cfopData.map(c => c.total_vendido || 0),
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)'
                        ]
                    }]
                },
                options: {
                    responsive: true
                }
            });
        } else {
            document.getElementById('cfopChart').innerHTML = '<p>Nenhum dado disponível</p>';
        }

        // 6. Média de Valor por Produto
        console.log('⚖️ Carregando avg product value...');
        const avgValueResponse = await fetch('/api/avg_product_value');
        if (!avgValueResponse.ok) throw new Error('Erro ao carregar avg product value');
        const avgValue = await avgValueResponse.json();
        console.log('Avg product value carregado:', avgValue);

        if (avgValue && avgValue.length > 0) {
            new Chart(document.getElementById('avgValueChart'), {
                type: 'bar',
                data: {
                    labels: avgValue.map(p => p.produto ? p.produto.substring(0, 15) + (p.produto.length > 15 ? '...' : '') : 'N/A'),
                    datasets: [{
                        label: 'Valor Médio (R$)',
                        data: avgValue.map(p => p.valor_medio || 0),
                        backgroundColor: 'rgba(255, 159, 64, 0.8)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        } else {
            document.getElementById('avgValueChart').innerHTML = '<p>Nenhum dado disponível</p>';
        }

        console.log('✅ Todos os dashboards carregados com sucesso!');

    } catch (error) {
        console.error('❌ Erro ao carregar dashboards:', error);
        
        // Mostrar mensagens de erro em todos os canvases
        const chartIds = [
            'topProductsChart', 'revenueChart', 'discountChart', 
            'quantityChart', 'cfopChart', 'avgValueChart'
        ];
        
        chartIds.forEach(chartId => {
            const element = document.getElementById(chartId);
            if (element) {
                element.innerHTML = '<p style="color: red; padding: 20px;">Erro ao carregar dados</p>';
            }
        });
    }
}

// Função para consulta em linguagem natural
async function fazerPergunta() {
    const pergunta = document.getElementById('perguntaInput').value;
    const respostaDiv = document.getElementById('resposta');
    
    if (!pergunta) {
        respostaDiv.innerHTML = '<p style="color: red;">⚠️ Digite uma pergunta</p>';
        return;
    }

    respostaDiv.innerHTML = '<p>🔍 Pesquisando...</p>';

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pergunta })
        });
        
        const data = await response.json();
        
        if (data.erro) {
            respostaDiv.innerHTML = `<p style="color: red;">❌ ${data.erro}</p>`;
        } else if (data.empresas) {
            respostaDiv.innerHTML = `<p><strong>🏢 Empresas encontradas:</strong><br>${data.empresas.join('<br>')}</p>`;
        } else {
            respostaDiv.innerHTML = `<p><strong>💰 Resposta:</strong> ${data.resultado}</p>`;
        }
    } catch (error) {
        respostaDiv.innerHTML = '<p style="color: red;">❌ Erro na consulta. Tente novamente.</p>';
    }
}

// Permitir Enter no input
document.getElementById('perguntaInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        fazerPergunta();
    }
});

// Carregar dashboards quando a página carregar
document.addEventListener('DOMContentLoaded', carregarDashboards);