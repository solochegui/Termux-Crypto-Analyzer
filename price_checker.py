import requests
import time
import os

# --- 1. CONFIGURACIÓN MEJORADA ---
# Se agregaron las IDs de CoinGecko para todas las monedas. 
# NOTA: 'ripple' es XRP. Confirma la ID de BoriCoin ('boricoin' es la ID de ejemplo).
CRYPTOS = 'bitcoin,ethereum,solana,boricoin,pepe,bonk,ripple,xyo' 
CURRENCY = 'usd'
UPDATE_INTERVAL = 10 # Intervalo de actualización en segundos (más frecuente)

# --- 2. FUNCIÓN DE OBTENCIÓN DE DATOS ---
def fetch_data(cryptos, currency):
    """
    Realiza la petición a la API de CoinGecko para obtener los precios, 
    incluyendo cambios de 24h y 7d.
    """
    # Usamos un endpoint que da más detalles (cambio de 24h y 7d).
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}&ids={cryptos}&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=24h,7d"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return None

# --- 3. FUNCIÓN DE ANÁLISIS Y PROYECCIÓN ---
def display_analysis():
    """
    Limpia la terminal, obtiene los datos y los muestra en formato de tabla con análisis.
    """
    
    data = fetch_data(CRYPTOS, CURRENCY)
    os.system('clear') 
    
    if data:
        print("--- 🧠 Analizador Avanzado de Precios Crypto para Órdenes Límite (CLI) ---")
        print(f"Última Actualización: {time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print("-" * 90)
        
        # Nuevos encabezados para incluir el análisis de Tendencia (7 días)
        header = "{:<12}{:>15}{:>10}{:>10}{:>10}{:>20}".format(
            "Moneda", "Precio (USD)", "24h (%)", "7d (%)", "Alerta", "Capitalización")
        print(header)
        print("-" * 90)
        
        for coin in data:
            symbol = coin['symbol'].upper()
            price = coin['current_price']
            # Usamos .get() para evitar errores si un dato no existe
            change_24h = coin.get('price_change_percentage_24h_in_currency')
            change_7d = coin.get('price_change_percentage_7d_in_currency')
            market_cap = coin.get('market_cap')
            
            # --- LÓGICA DE ALERTA DE COMPRA (IDEAL PARA ÓRDENES LÍMITE) ---
            alerta = ""
            if change_24h is not None and change_7d is not None:
                # 1. Señal de Compra: Caída fuerte en 24h pero tendencia positiva en 7d
                # Consideramos una caída > 4% como "fuerte"
                if change_24h < -4.0 and change_7d > 0:
                    alerta = "\033[41m¡COMPRA! (DIP)\033[0m" # Fondo rojo: Señal de orden límite de compra
                # 2. Señal de Riesgo: Caída fuerte en 7d (Tendencia Bajista)
                elif change_7d < -8.0:
                    alerta = "\033[31mRIESGO\033[0m" # Texto rojo: Evitar órdenes límite
                # 3. Señal de Estabilidad: Precio relativamente estable
                elif -2.0 <= change_24h <= 2.0:
                    alerta = "\033[36mESTABLE\033[0m" # Texto Cyan
            
            # --- FORMATO DE SALIDA ---
            
            # Formato y color para 24h
            color_24h = '\033[32m' if (change_24h or 0) >= 0 else '\033[31m'
            change_24h_str = f"{color_24h}{change_24h:+.2f}%\033[0m" if change_24h is not None else 'N/A'
            
            # Formato de 7 días (Tendencia)
            color_7d = '\033[32m' if (change_7d or 0) >= 0 else '\033[31m'
            change_7d_str = f"{color_7d}{change_7d:+.2f}%\033[0m" if change_7d is not None else 'N/A'

            # Formato de precios (más decimales para monedas de bajo valor)
            price_str = f"${price:,.8f}" if price < 0.1 else f"${price:,.2f}"
            market_cap_str = f"${market_cap:,.0f}" if market_cap else 'N/A'
            
            # Imprimir la fila
            print(f"{symbol:<12}{price_str:>15}{change_24h_str:>19}{change_7d_str:>19}{alerta:>10}{market_cap_str:>20}")

        print("-" * 90)
        print("\n📈 **Guía de Órdenes Límite (Buy Limit):**")
        print("  - Busca la alerta '\033[41m¡COMPRA! (DIP)\033[0m' (Caída del día en tendencia positiva semanal).")
        print("  - Coloca tu orden límite ligeramente por encima de un soporte clave para 'comprar el dip'.")
    else:
        print("No se pudieron obtener datos. Revisa tu conexión o las IDs de las criptos.")

# --- 4. BUCLE DE EJECUCIÓN CONTINUA ---
if __name__ == "__main__":
    try:
        while True:
            display_analysis()
            print(f"\nActualizando en {UPDATE_INTERVAL} segundos... (Presiona Ctrl + C para detener)")
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        print("\nAnalizador detenido. ¡Buen trading!")
