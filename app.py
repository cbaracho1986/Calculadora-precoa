import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# Configuração de Temas e Estilos
def set_custom_style():
    st.markdown("""
        <style>
        /* Estilos Gerais */
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
            font-family: 'Inter', sans-serif;
        }
        
        /* Cabeçalho */
        .header-container {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* Cards de Entrada */
        .input-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        
        /* Campos de Entrada */
        .stTextInput > div > div > input {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 0.5rem;
        }
        
        /* Botões */
        .stButton > button {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 5px;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Resultados */
        .results-card {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
        }
        
        /* Métricas */
        .metric-container {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        /* Alertas */
        .stAlert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        /* Responsividade */
        @media (max-width: 768px) {
            .header-container {
                padding: 1rem;
            }
            
            .input-card, .results-card {
                padding: 1rem;
            }
        }
        
        /* Combo personalizado */
        .currency-input {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }
        
        .currency-pair {
            background-color: #f8f9fa;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            margin: 0.25rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .currency-pair:hover {
            background-color: #e9ecef;
        }
        </style>
    """, unsafe_allow_html=True)

def obter_cotacao(par_moedas):
    """
    Obtém a cotação para o par de moedas especificado.
    :param par_moedas: Par de moedas no formato 'USD/BRL', 'EUR/USD', etc.
    :return: Taxa de câmbio atual para o par de moedas.
    """
    try:
        base, quote = par_moedas.split('/')
        url = 'https://openexchangerates.org/api/latest.json'
        params = {
            'app_id': 'edd30e082f404192ae8c03219d82e3f6',
            'symbols': f"{base},{quote}"
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ValueError("Erro ao obter a cotação. Verifique a conexão com a internet.")
            
        data = response.json()
        if 'rates' not in data or base not in data['rates'] or quote not in data['rates']:
            raise ValueError(f"Cotações para {par_moedas} não encontradas.")
            
        return data['rates'][quote] / data['rates'][base]
    except Exception as e:
        st.error(f"Erro ao obter cotação: {str(e)}")
        return None

def calcular_lote_e_risco(risco_brl, par_moedas, pips):
    """
    Calcula o tamanho do lote e o risco.
    """
    try:
        taxa_brl_usd = obter_cotacao('USD/BRL')
        if not taxa_brl_usd:
            return None, None
            
        risco_usd = risco_brl / taxa_brl_usd
        taxa_cambio = obter_cotacao(par_moedas)
        
        if not taxa_cambio:
            return None, None
            
        tamanho_lote = risco_usd / (pips / taxa_cambio)
        return tamanho_lote, risco_usd
    except Exception as e:
        st.error(f"Erro no cálculo: {str(e)}")
        return None, None

def main():
    st.set_page_config(
        page_title="Calculadora Forex Pro",
        page_icon="💱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    set_custom_style()
    
    # Cabeçalho personalizado
    st.markdown("""
        <div class="header-container">
            <h1>💱 Calculadora Forex Profissional</h1>
            <p>Calcule tamanhos de lote e gerencie riscos com precisão</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Layout principal em duas colunas
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Parâmetros da Operação")
        
        # Input de risco com formatação monetária
        risco_brl = st.number_input(
            "💰 Risco em BRL",
            min_value=0.0,
            step=10.0,
            value=100.0,
            format="%.2f",
            help="Digite o valor em reais que está disposto a arriscar"
        )
        
        # Lista de pares comuns
        pares_comuns = [
            "EUR/USD", "GBP/USD", "USD/JPY", "USD/BRL", "EUR/BRL",
            "GBP/BRL", "AUD/USD", "USD/CAD", "USD/CHF"
        ]
        
        # Combo personalizado com opção de digitação
        st.markdown("### 🔄 Par de Moedas")
        par_moedas = st.text_input(
            "Digite ou selecione o par de moedas",
            value="USD/BRL",
            help="Use o formato BASE/QUOTE (ex: EUR/USD)"
        ).upper()
        
        # Botões rápidos para pares comuns
        st.markdown("#### Pares Populares")
        cols = st.columns(3)
        for idx, par in enumerate(pares_comuns[:9]):
            with cols[idx % 3]:
                if st.button(par, key=f"btn_{par}", use_container_width=True):
                    par_moedas = par
        
        # Input de pips com slider e campo numérico
        st.markdown("### 📏 Stop Loss")
        pips = st.number_input(
            "Quantidade de pips",
            min_value=0.0,
            max_value=200.0,
            value=50.0,
            step=0.1,
            help="Arraste para ajustar ou digite o valor"
        )
        
        # Botão de cálculo estilizado
        calcular = st.button("🎯 Calcular Posição", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="results-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Resultados da Análise")
        
        if calcular:
            with st.spinner('Processando cálculos...'):
                pips_adjusted = pips * 1.20
                resultado = calcular_lote_e_risco(risco_brl, par_moedas, pips_adjusted)
                
                if resultado and None not in resultado:
                    tamanho_lote, risco_usd = resultado
                    
                    # Display dos resultados em cards
                    cols = st.columns(3)
                    
                    with cols[0]:
                        st.markdown("""
                            <div class="metric-container">
                                <h4>Tamanho do Lote</h4>
                                <h2>{:.2f}</h2>
                                <p>Lotes</p>
                            </div>
                        """.format(tamanho_lote), unsafe_allow_html=True)
                    
                    with cols[1]:
                        st.markdown("""
                            <div class="metric-container">
                                <h4>Risco em USD</h4>
                                <h2>${:.2f}</h2>
                                <p>Dólares</p>
                            </div>
                        """.format(risco_usd), unsafe_allow_html=True)
                    
                    with cols[2]:
                        st.markdown("""
                            <div class="metric-container">
                                <h4>Risco em BRL</h4>
                                <h2>R${:.2f}</h2>
                                <p>Reais</p>
                            </div>
                        """.format(risco_brl), unsafe_allow_html=True)
                    
                    st.success("✅ Cálculos realizados com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Não foi possível realizar os cálculos. Verifique os dados inseridos.")
        else:
            st.info("👈 Configure os parâmetros e clique em 'Calcular Posição'")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 10px;">
            <small>Desenvolvido para Traders Profissionais • Dados em Tempo Real • v2.0</small>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
