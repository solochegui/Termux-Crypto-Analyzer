#!/usr/bin/env python3
"""
Termux-Crypto-Analyzer - price_checker.py
Analizador avanzado de precios crypto (CLI) con Proyección, Análisis Técnico,
Estimación de Tiempo al PLR y notificaciones Telegram/Coinbase.
Versión simplificada: Sin rich, colorama o tabulate. Solo texto plano.
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
import time
from datetime import datetime, UTC
from typing import Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- DESHABILITACIÓN COMPLETA DE LIBRERÍAS DE FORMATO ---
# Se usan variables de entorno para las credenciales, como antes.

# >>> INTEGRACIÓN COINBASE - AJUSTADA PARA SDK 'coinbase' <<<
try:
    from coinbase.wallet.client import Client as CoinbaseClient
    HAS_COINBASE = True
except ImportError:
    HAS_COINBASE = False
# >>> FIN INTEGRACIÓN COINBASE <<<
    
# --- 1. CONFIGURACIÓN & CREDENCIALES ---

# Credenciales de Plataformas (Obtenidas de variables de entorno)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")   
COINBASE_API_KEY = os.environ.get("COINBASE_API_KEY", "")
COINBASE_API_SECRET = os.environ.get("COINBASE_API_SECRET", "")
DEFAULT_TRADE_AMOUNT_USD = 10.0 # Monto de la orden de compra en USD

# Defaults
DEFAULT_CRYPTOS = "bitcoin,ethereum,solana,boricoin,ripple,binancecoin,cardano,avalanche-2,chainlink,polygon,dogecoin,arbitrum,render-token,fetch-ai,pepe,bonk,shiba-inu,xyo"
DEFAULT_CURRENCY = "usd"
DEFAULT_INTERVAL = 10 # seconds

# CoinGecko API
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
RATE_LIMIT_WAIT_TIME = 60 

# Logging configuration
logger = logging.getLogger("price_checker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


# --- 2. AUXILIARY CONNECTION AND UTILITY FUNCTIONS ---

def create_session(retries: int = 3, backoff_factor: float = 1.0, status_forcelist: Optional[List[int]] = None) -> requests.Session:
    """Configures an HTTP session with retries for network errors and rate limits."""
    status_forcelist = status_forcelist or [429, 500, 502, 503, 504] 
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        raise_on_redirect=True,
        raise_on_status=False,
        respect_retry_after_header=True, 
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def clear_terminal() -> None:
    """Clears the terminal (works on Windows, Linux, and Termux)."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def fetch_data(session: requests.Session, cryptos: str, currency: str, per_page: int = 100, timeout: int = 10) -> Optional[List[dict]]:
    """Fetches data from CoinGecko with retry handling."""
    params = {
        "vs_currency": currency,
        "ids": cryptos,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d",
    }
    try:
        resp = session.get(API_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 429:
            logger.error(f"Rate Limit (429) hit. ⚠️ Waiting {RATE_LIMIT_WAIT_TIME} seconds...")
            time.sleep(RATE_LIMIT_WAIT_TIME)
        else:
            logger.warning("HTTP Error (%s) connecting to CoinGecko: %s", resp.status_code, e)
        return None
    except requests.exceptions.RequestException as e:
        logger.warning("Connection Error with CoinGecko: %s", e)
        return None

# --- 3. FORMATTING AND ALERT LOGIC FUNCTIONS ---

def format_price(price: Optional[float], decimal_limit: int = 2) -> str:
    """Formats the price, using more decimals for very low values."""
    if price is None:
        return "N/A"
    try:
        if price < 0.1:
            return f"${price:,.8f}"
        return f"${price:,.{decimal_limit}f}"
    except (ValueError, TypeError):
        return str(price)

def format_percent(value: Optional[float]) -> str:
    """Formats the percentage change with a sign."""
    if value is None:
        return "N/A"
    return f"{value:+.2f}%"

def compute_alert(change_24h: Optional[float], change_7d: Optional[float]) -> str:
    """Calculates the buy/sell/risk alert (texto plano) con más variedades."""
    if change_24h is None or change_7d is None:
        return ""
    
    # 1. Señal de VENTA / EUFORIA (FOMO)
    if change_24h > 10.0 and change_7d > 15.0:
        return "💸 VENTA! (FOMO)"
        
    # 2. Señal de RIESGO / VENTA (BULL TRAP)
    elif change_24h > 6.0 and change_7d < 0.0:
        return "⚠️ BULL TRAP / VENTA C/P"

    # 3. Señal de RIESGO MÁXIMO (CAPITULACIÓN)
    elif change_24h < -8.0 and change_7d < -15.0:
        return "💀 CAPITULACIÓN/PÁNICO"
    
    # 4. Señal de COMPRA FUERTE (REVERSIÓN V o B) - Rebote en 24h tras caída de 7d
    # Ocurre cuando ya viste Capitulación y el precio rebota fuerte
    elif change_24h > 4.0 and change_7d < -5.0:
        return "📈 REVERSIÓN V/B (COMPRA)"
        
    # 5. Señal de RUPTURA ALCISTA (CONTINUACIÓN)
    elif change_24h > 5.0 and change_7d > 3.0 and change_7d < 10.0:
        return "🚀 RUPTURA ALCISTA (COMPRA)"

    # 6. Señal de COMPRA (DIP) - Corrección dentro de una tendencia alcista sana
    elif change_24h < -4.0 and change_7d > 0.0:
        return "📉 COMPRA! (DIP)"

    # 7. Señal de ACUMULACIÓN (Largo Plazo)
    elif change_24h < -1.0 and change_24h > -4.0 and change_7d < -10.0:
        return "💎 ACUMULACIÓN FUERTE (LT)"
        
    # 8. Señal de CRECIMIENTO SALUDABLE (MOMENTUM)
    elif change_24h > 2.0 and change_7d > 8.0:
        return "🟢 MOMENTUM SALUDABLE"

    # 9. Señal de ADVERTENCIA (CORRECCIÓN C/P)
    elif -4.0 <= change_24h < -2.0 and change_7d > 10.0:
        return "⚠️ CORRECCIÓN C/P"

    # 10. Señal de CONSOLIDACIÓN (RANGO)
    elif -1.5 <= change_24h <= 1.5 and -3.0 <= change_7d <= 3.0:
        return "😴 RANGO/CONSOLIDACIÓN"

    # 11. Señal de ESTABILIDAD (Cierre, debe ser la última)
    elif -1.0 <= change_24h <= 1.0:
        return "⚖️ ESTABLE"
    
    else:
        return ""

def compute_projection(current_price: Optional[float], change_24h: Optional[float]) -> str:
    """Calculates a simple 48-hour price projection (LINEAR ASSUMPTION)."""
    if current_price is None or change_24h is None:
        return "N/A"
    
    try:
        projection_factor = 1 + (change_24h / 100.0)
        projected_price = current_price * projection_factor
        
        return format_price(projected_price)

    except (ValueError, TypeError):
        return "N/A"

def compute_technical_sentiment(change_24h: Optional[float], change_7d: Optional[float]) -> str:
    """Simulates a technical analysis summary (e.g., Moving Averages + RSI) based on momentum (texto plano)."""
    if change_24h is None or change_7d is None:
        return ""
    
    if change_24h > 5.0 and change_7d > 10.0:
        return "FUERTE COMPRA (Golden Cross)"
    elif change_24h > 2.0 and change_7d > 0:
        return "COMPRA"
    elif change_24h < -5.0 and change_7d < -10.0:
        return "FUERTE VENTA (Death Cross)"
    elif change_24h < -2.0 and change_7d < 0:
        return "VENTA"
    elif -2.0 <= change_24h <= 2.0 and -5.0 <= change_7d <= 5.0:
        return "NEUTRAL"
    elif change_24h > 7.0 and change_7d > 20.0:
        return "NEUTRAL (Sobrecompra)"
    else:
        return "NEUTRAL"

def compute_time_to_plr(current_price: Optional[float], change_24h: Optional[float], suggested_limit_price: Optional[float]) -> str:
    """Estimates the time it would take for the price to reach the Suggested Limit Price (PLR)."""
    if current_price is None or change_24h is None or suggested_limit_price is None or suggested_limit_price == 0:
        return "N/A"
    
    target_change_pct = ((suggested_limit_price - current_price) / current_price) * 100
    velocity_per_hour = change_24h / 24.0
    
    if abs(velocity_per_hour) < 0.001:
        return "N/A (Velocidad 0)"
    
    if (target_change_pct > 0 and velocity_per_hour < 0) or \
       (target_change_pct < 0 and velocity_per_hour > 0):
        return "N/A (Dir. Incompatible)"

    try:
        hours_needed = target_change_pct / velocity_per_hour
        
        if hours_needed < 0: 
            return "N/A (Reversión Necesaria)"

        if hours_needed >= 24 * 30: 
            months = round(hours_needed / (24 * 30))
            return f"~{months} meses"
        elif hours_needed >= 24: 
            days = round(hours_needed / 24)
            return f"~{days} días"
        elif hours_needed > 1: 
            return f"~{round(hours_needed, 1)} horas"
        else: 
            minutes = max(1, round(hours_needed * 60))
            return f"~{minutes} minutos"

    except (ZeroDivisionError, ValueError, TypeError):
        return "N/A"

# --- 4. TABLE PRINTING, TELEGRAM NOTIFICATION Y COINBASE ORDER FUNCTION ---

def get_crypto_account_id(client: CoinbaseClient, symbol: str) -> Optional[str]:
    """Busca el ID de la cuenta de la criptomoneda (Ej. BTC) en la Wallet de Coinbase."""
    try:
        accounts = client.get_accounts().data
        for account in accounts:
            if account['currency'] == symbol:
                return account['id']
        logger.warning(f"No se encontró una cuenta de Coinbase para la moneda: {symbol}.")
        return None
    except Exception as e:
        logger.error(f"Error al obtener cuentas de Coinbase: {e}")
        return None

def place_limit_order_coinbase(
    client: CoinbaseClient, 
    symbol: str, 
    limit_price: float, 
    usd_amount: float
) -> Optional[dict]:
    """
    Coloca una orden BUY (de Mercado) usando la Wallet API, ya que no soporta órdenes Límite.
    Compra la cantidad de USD especificada al precio actual de mercado.
    """
    if not HAS_COINBASE or client is None:
        logger.warning("Coinbase client no está disponible.")
        return None
    
    account_id = get_crypto_account_id(client, symbol)
    if not account_id:
        return None

    try:
        # Ejecuta una 'buy' gastando la cantidad de dinero (USD)
        response = client.buy(
            account_id=account_id,
            amount=usd_amount, # Cantidad de FIAT a gastar
            currency="USD",   # Moneda a gastar
            commit=True      # Realizar la compra
        )

        logger.info(f"🚀 Orden de COMPRA (Mercado) enviada a Coinbase para {symbol}. Monto: ${usd_amount:.2f} USD.")
        logger.warning(f"⚠️ Atención: Esta es una orden de MERCADO, no LÍMITE.")
        return response.get('data')
    except Exception as e:
        logger.error(f"❌ Error al enviar la orden de Coinbase para {symbol}: {e}")
        return None

def print_table(data: List[dict], prev_prices: Dict[str, float], currency: str, coinbase_client: Optional[CoinbaseClient]) -> Dict[str, Union[Dict[str, float], List[Dict[str, str | float]]]]:
    """Formats and prints the data to the terminal using simple text formatting."""
    rows = []
    buy_signals_data: List[Dict[str, str | float]] = [] 
    
    # Pre-cálculo para determinar si se necesitan las columnas de PLR/Tiempo
    has_buy_signal_flag = any("📉 COMPRA! (DIP)" in compute_alert(coin.get("price_change_percentage_24h_in_currency"), coin.get("price_change_percentage_7d_in_currency")) for coin in data)

    # Headers para el output de texto plano
    active_headers = ["Moneda", "Precio", "Δ(prev)", "24h", "7d", "Proyección 48h", "Alerta", "Técnico"]
    if has_buy_signal_flag:
        active_headers.extend(["Límite Sugerido", "Tiempo al PLR"])


    for coin in data:
        symbol = coin.get("symbol", "").upper()
        name = coin.get("id", "")
        price = coin.get("current_price")
        change_24h = coin.get("price_change_percentage_24h_in_currency")
        change_7d = coin.get("price_change_percentage_7d_in_currency")

        alert_str = compute_alert(change_24h, change_7d)
        limit_suggered_float: Optional[float] = None
        limit_suggered_str = ""

        # LÓGICA DE COMPRA Y ORDEN AUTOMÁTICA
        if "COMPRA! (DIP)" in alert_str and price is not None:
            limit_suggered_float = price * (1 - 0.02)
            limit_suggered_str = format_price(limit_suggered_float, decimal_limit=4)
            
            # --- ENVÍO DE ORDEN AUTOMÁTICA A COINBASE ---
            if HAS_COINBASE and coinbase_client and DEFAULT_TRADE_AMOUNT_USD > 0 and limit_suggered_float > 0:
                try:
                    place_limit_order_coinbase(
                        client=coinbase_client,
                        symbol=symbol,
                        limit_price=limit_suggered_float, 
                        usd_amount=DEFAULT_TRADE_AMOUNT_USD
                    )
                except Exception as e:
                    logger.error(f"Error en cálculo/envío para {symbol}: {e}")

            # Datos para notificación de Telegram
            buy_signals_data.append({
                "symbol": symbol,
                "name": name,
                "price": price,
                "change_24h": change_24h,
                "change_7d": change_7d,
                "limit_price": limit_suggered_str,
            })

        price_str = format_price(price)
        change_24h_str = format_percent(change_24h)
        change_7d_str = format_percent(change_7d)
        
        projection_48h_str = compute_projection(price, change_24h)
        technical_sentiment_str = compute_technical_sentiment(change_24h, change_7d)
        time_to_plr_str = compute_time_to_plr(price, change_24h, limit_suggered_float)

        delta_str = ""
        prev = prev_prices.get(name)
        if prev is not None and price is not None:
            try:
                pct = (price - prev) / prev * 100 if prev != 0 else 0.0
                delta_str = f"{pct:+.2f}%"
            except (ValueError, TypeError):
                delta_str = ""
        
        # Construir la fila de datos para impresión
        row_data = {
            "Moneda": symbol,
            "Precio": price_str,
            "Δ(prev)": delta_str,
            "24h": change_24h_str,
            "7d": change_7d_str,
            "Proyección 48h": projection_48h_str,
            "Alerta": alert_str,
            "Técnico": technical_sentiment_str
        }
        
        if has_buy_signal_flag:
            row_data["Límite Sugerido"] = limit_suggered_str
            row_data["Tiempo al PLR"] = time_to_plr_str
        
        rows.append(row_data)

    # --- Impresión final (Texto Plano) ---
    if rows:
        # Calcular el ancho máximo para cada columna
        col_widths = {h: len(h) for h in active_headers}
        for row in rows:
            for header in active_headers:
                col_widths[header] = max(col_widths[header], len(str(row.get(header, ''))))
        
        # Función auxiliar para formatear la línea
        def format_line(data_dict: Dict[str, str], is_header: bool = False) -> str:
            line = ""
            for header in active_headers:
                value = data_dict.get(header, '')
                padding = col_widths[header]
                # Alinear a la izquierda (Moneda, Alerta, Técnico)
                if header in ["Moneda", "Alerta", "Técnico"]:
                    line += f"| {str(value).ljust(padding)} "
                # Alinear a la derecha (Precios, Porcentajes, Tiempos)
                else:
                    line += f"| {str(value).rjust(padding)} "
            return line + "|"
            
        # Imprimir Encabezado
        header_dict = {h: h for h in active_headers}
        header_line = format_line(header_dict, is_header=True)
        print(header_line)
        print("-" * len(header_line))

        # Imprimir Datos
        for row in rows:
            print(format_line(row))
        
        print("-" * len(header_line))


    return {
        "prev_prices": {name: price for name, price in zip([coin.get("id") for coin in data], [coin.get("current_price") for coin in data]) if name and price is not None},
        "buy_signals": buy_signals_data
    }


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Sends a message to a specific Telegram chat."""
    if not bot_token or not chat_id:
        logger.debug("Telegram skipped: Token or Chat ID not configured.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "MarkdownV2"}, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.warning("Error sending Telegram message: %s", e)
        return False

def create_coinbase_client_instance(api_key: str, api_secret: str) -> Optional[CoinbaseClient]:
    """Inicializa el cliente de Coinbase SDK (Wallet API)."""
    global HAS_COINBASE
    
    if not HAS_COINBASE:
        logger.warning("Coinbase SDK no está instalado. Automatización deshabilitada.")
        return None
        
    if not api_key or not api_secret:
        logger.warning("Coinbase API Key/Secret no configurados. La automatización de trading está deshabilitada.")
        return None
    
    try:
        client = CoinbaseClient(api_key, api_secret) 
        client.get_current_user() 
        logger.info("✅ Cliente de Coinbase Wallet API inicializado y conectado.")
        return client
    except Exception as e:
        logger.error(f"❌ Error al conectar a Coinbase (Verifica tus claves/permisos): {e}")
        HAS_COINBASE = False 
        return None


# --- 5. MAIN EXECUTION FUNCTION ---

def parse_args() -> argparse.Namespace:
    """Defines and parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Advanced Crypto Price Analyzer (CLI)")
    parser.add_argument("--cryptos", type=str, default=DEFAULT_CRYPTOS,
                        help=f"Comma-separated CoinGecko IDs (default: {DEFAULT_CRYPTOS})")
    parser.add_argument("--currency", type=str, default=DEFAULT_CURRENCY,
                        help=f"Fiat currency (default: {DEFAULT_CURRENCY})")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Update interval in seconds (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--retries", type=int, default=3, help="HTTP retries")
    parser.add_argument("--per-page", type=int, default=100, help="Number of results per page")
    parser.add_argument("--verbose", action="store_true", help="Show DEBUG logs")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear terminal on each update")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    telegram_token = TELEGRAM_BOT_TOKEN 
    telegram_chat = TELEGRAM_CHAT_ID
    
    coinbase_client = create_coinbase_client_instance(COINBASE_API_KEY, COINBASE_API_SECRET)

    session = create_session(retries=args.retries)
    prev_prices: Dict[str, float] = {}

    try:
        while True:
            data = fetch_data(session, args.cryptos, args.currency, per_page=args.per_page)
            if not args.no_clear:
                clear_terminal()
            
            # Reemplazamos .utcnow() por .now(datetime.UTC) para evitar el DeprecationWarning
            current_time_utc = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

            # --- TÍTULO DECORADO (Texto Plano) ---
            print("=========================================================================================")
            print("✨ NON FUNGIBLE METAVERSE ✨")
            print("--- 🧠 Analizador Avanzado de Precios Crypto (CLI) 🚀 ---")
            print(f"Última Actualización: {current_time_utc} UTC | Cryptos: {args.cryptos} | Fiat: {args.currency}")
            print("=========================================================================================")

            if data:
                result = print_table(data, prev_prices, args.currency, coinbase_client) 
                new_prev = result["prev_prices"]
                buy_signals = result["buy_signals"]
                
                # Enviar notificación de Telegram (lógica se mantiene igual)
                if buy_signals and telegram_token and telegram_chat:
                    msg_parts = [
                        "🚨 *ALERTA DE COMPRA \\(DIP\\) EN EL METAVERSO* 🚨",
                        "El mercado presenta oportunidades de entrada:",
                        ""
                    ]
                    
                    for signal in buy_signals:
                        symbol = str(signal['symbol']).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
                        name = str(signal['name']).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
                        
                        msg_parts.append(f"💰 *{symbol}* \\({name}\\) \\- ¡A la Caza\\! 🎯")
                        msg_parts.append(f"   \\- Precio Actual: *{format_price(signal['price']).replace('$', '\\$').replace('.', '\\.')}*")
                        # Usamos la versión de texto plano de format_percent
                        pct_24h_plain = format_percent(signal['change_24h'])
                        pct_7d_plain = format_percent(signal['change_7d'])
                        
                        msg_parts.append(f"   \\- Var\\. 24h: {pct_24h_plain.replace('+', '\\+').replace('-', '\\-')}")
                        msg_parts.append(f"   \\- Var\\. 7d: {pct_7d_plain.replace('+', '\\+').replace('-', '\\-')}")
                        msg_parts.append(f"   \\- *Límite Sugerido \\(\\-2\\%\\):* *{str(signal['limit_price']).replace('$', '\\$').replace('.', '\\.')}* ✍️")
                        msg_parts.append("") 

                    msg_parts.append("---")
                    msg_parts.append("Estrategia de inversión compartida por *Non Fungible Metaverse*\\. 🚀")
                    
                    msg = "\n".join(msg_parts)
                    
                    if send_telegram_message(telegram_token, telegram_chat, msg):
                        logger.info("Telegram buy notification sent. 🔔")

                prev_prices.update({k: v for k, v in new_prev.items() if v is not None})
            else:
                logger.warning("No data retrieved from CoinGecko. Retrying... 🔄")

            # --- MENSAJE DE CIERRE ---
            print("=========================================================================================")
            print(f"Updating in {args.interval} seconds... (Ctrl+C to stop 🛑)")
            
            time.sleep(max(1, args.interval))

    except KeyboardInterrupt:
        print("\nAnalyzer stopped. Happy trading in the 🌐 Metaverse!")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
