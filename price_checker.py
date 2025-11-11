#!/usr/bin/env python3
"""
Termux-Crypto-Analyzer - price_checker.py
Analizador avanzado de precios crypto (CLI) con Proyección, Análisis Técnico,
Estimación de Tiempo al PLR y notificaciones Telegram.
Creado por Non Fungible Metaverse.
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timedelta # Importar timedelta
from typing import Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Optional dependencies for rich output
try:
    from tabulate import tabulate  # type: ignore
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

try:
    from colorama import Fore, Back, Style, init as colorama_init  # type: ignore
    colorama_init(autoreset=True) 
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    # Fallback classes for ANSI colors if colorama is not installed
    class Ansi:
        RESET = ""
        RED = ""
        GREEN = ""
        CYAN = ""
        YELLOW = ""
        MAGENTA = ""
        BLUE = ""
        BLACK = "" # For Back.GREEN + Fore.BLACK
        BOLD = ""
        BG_GREEN = ""
        BRIGHT = ""
        DIM = ""
        NORMAL = ""

    class AnsiStyle:
        RESET_ALL = ""
        BRIGHT = ""
        DIM = ""
        NORMAL = ""
    
    Fore = Back = Ansi()
    Style = AnsiStyle()
    
# --- 1. CONFIGURACIÓN MEJORADA & CREDENCIALES ---

# IMPORTANT SECURITY NOTE: 
# These fields are empty by default. FOR TELEGRAM, 
# YOU MUST CONFIGURE ENVIRONMENT VARIABLES IN TERMUX: 
# export TELEGRAM_BOT_TOKEN="YOUR_TOKEN"
# export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "") 
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")   

# Defaults for cryptocurrencies, fiat currency, and update interval
DEFAULT_CRYPTOS = "bitcoin,ethereum,solana,boricoin,pepe,bonk,ripple,xyo"
DEFAULT_CURRENCY = "usd"
DEFAULT_INTERVAL = 10 # seconds

# CoinGecko API endpoint and rate limit handling
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
RATE_LIMIT_WAIT_TIME = 60 # Recommended wait time for HTTP 429

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

def format_limit_price(price: Optional[float]) -> str:
    """Calculates and formats the suggested limit price (2% discount)."""
    if price is None:
        return "N/A"
    
    limit_price = price * (1 - 0.02) # 2% lower price
    return format_price(limit_price, decimal_limit=4) 

def colorize_percent(value: Optional[float]) -> str:
    """Applies color to percentage changes (green for positive, red for negative)."""
    if value is None:
        return "N/A"
    sign = f"{value:+.2f}%"
    if not HAS_COLORAMA:
        return sign
    if value > 0:
        return Fore.GREEN + sign
    elif value < 0:
        return Fore.RED + sign
    else:
        return Fore.CYAN + sign

def compute_alert(change_24h: Optional[float], change_7d: Optional[float]) -> str:
    """Calculates the buy/sell/risk alert based on advanced Non Fungible Metaverse logic (7 Signals)."""
    if change_24h is None or change_7d is None:
        return ""
    
    # 1. SELL Signal: Potential Overbought / Take Profit (FOMO)
    if change_24h > 10.0 and change_7d > 15.0:
        return (Back.GREEN + Fore.BLACK + " 💸 ¡VENTA! (FOMO) ") if HAS_COLORAMA else "💸 ¡VENTA! (FOMO)"

    # 2. BUY Signal: Strong 24h drop (> 4%) but positive 7d trend (> 0%) - Buy the Dip
    if change_24h < -4.0 and change_7d > 0:
        return (Back.BLUE + Fore.WHITE + " 📉 ¡COMPRA! (DIP) ") if HAS_COLORAMA else "📉 ¡COMPRA! (DIP)"

    # 3. RISK/CAPITULATION Signal: Strong short- and medium-term drop
    if change_24h < -8.0 or change_7d < -10.0:
        return (Fore.RED + "🔥 RIESGO/CAPITULACIÓN") if HAS_COLORAMA else "🔥 RIESGO/CAPITULACIÓN"
        
    # --- NEW ANALYTICAL SIGNALS ---

    # 4. SUSTAINABLE GROWTH Trend: Healthy Bullish Momentum (Buy)
    if change_24h > 2.0 and change_7d > 8.0:
        return (Fore.MAGENTA + "🟢 MOMENTUM SALUDABLE") if HAS_COLORAMA else "🟢 MOMENTUM SALUDABLE"

    # 5. SHORT-TERM CORRECTION (Warning/Hold)
    if -4.0 <= change_24h < -2.0 and change_7d > 10.0:
        return (Fore.YELLOW + "⚠️ CORRECCIÓN C/P") if HAS_COLORAMA else "⚠️ CORRECCIÓN C/P"

    # 6. LATERALIZATION Alert (RANGE): Consolidation (Neutral)
    if -1.5 <= change_24h <= 1.5 and -3.0 <= change_7d <= 3.0:
        return (Fore.BLUE + "😴 RANGO/CONSOLIDACIÓN") if HAS_COLORAMA else "😴 RANGO/CONSOLIDACIÓN"

    # 7. STABILITY Signal (Stricter threshold now)
    if -1.0 <= change_24h <= 1.0:
        return (Fore.CYAN + "⚖️ ESTABLE") if HAS_COLORAMA else "⚖️ ESTABLE"
        
    return "" # Default if no category matches

def compute_projection(current_price: Optional[float], change_24h: Optional[float]) -> str:
    """
    Calculates a simple 48-hour price projection (LINEAR ASSUMPTION).
    This is NOT an advanced predictive model, but a momentum estimate.
    """
    if current_price is None or change_24h is None:
        return "N/A"
    
    try:
        projection_factor = 1 + (change_24h / 100.0)
        projected_price = current_price * projection_factor
        
        projection_str = format_price(projected_price)
        if not HAS_COLORAMA:
            return projection_str
        
        if projected_price > current_price:
            return Fore.GREEN + projection_str
        elif projected_price < current_price:
            return Fore.RED + projection_str
        else:
            return Fore.CYAN + projection_str

    except (ValueError, TypeError):
        return "N/A"

def compute_technical_sentiment(change_24h: Optional[float], change_7d: Optional[float]) -> str:
    """Simulates a technical analysis summary (e.g., Moving Averages + RSI) based on momentum."""
    if change_24h is None or change_7d is None:
        return ""
    
    # 1. STRONG BUY: Clear and sustained bullish momentum
    if change_24h > 5.0 and change_7d > 10.0:
        return (Fore.GREEN + Style.BRIGHT + "FUERTE COMPRA (Golden Cross)") if HAS_COLORAMA else "FUERTE COMPRA"
    
    # 2. BUY: Recent bullish momentum (Breakout) or good rebound
    if change_24h > 2.0 and change_7d > 0:
        return (Fore.GREEN + "COMPRA") if HAS_COLORAMA else "COMPRA"
        
    # 3. STRONG SELL: Severe drop and negative trend (Death Cross)
    if change_24h < -5.0 and change_7d < -10.0:
        return (Fore.RED + Style.BRIGHT + "FUERTE VENTA (Death Cross)") if HAS_COLORAMA else "FUERTE VENTA"

    # 4. SELL: Clear bearish trend
    if change_24h < -2.0 and change_7d < 0:
        return (Fore.RED + "VENTA") if HAS_COLORAMA else "VENTA"
        
    # 5. NEUTRAL / CONSOLIDATION: No clear direction
    if -2.0 <= change_24h <= 2.0 and -5.0 <= change_7d <= 5.0:
        return (Fore.YELLOW + "NEUTRAL") if HAS_COLORAMA else "NEUTRAL"

    # 6. NEUTRAL / OVERBOUGHT: Risk of correction (RSI > 70)
    if change_24h > 7.0 and change_7d > 20.0:
        return (Fore.MAGENTA + "NEUTRAL (Sobrecompra)") if HAS_COLORAMA else "NEUTRAL (Sobrecompra)"

    return "NEUTRAL"

def compute_time_to_plr(current_price: Optional[float], change_24h: Optional[float], suggested_limit_price: Optional[float]) -> str:
    """
    Estimates the time it would take for the price to reach the Suggested Limit Price (PLR),
    assuming the 24h change (velocity) remains constant.
    """
    if current_price is None or change_24h is None or suggested_limit_price is None or suggested_limit_price == 0:
        return "N/A"
    
    # 1. Calculate the percentage difference between the current price and the PLR.
    target_change_pct = ((suggested_limit_price - current_price) / current_price) * 100
    
    # 2. Velocity of change per hour (assuming change_24h is % in 24h)
    velocity_per_hour = change_24h / 24.0
    
    # Handle cases with zero velocity or incompatible direction
    if abs(velocity_per_hour) < 0.001:
        return "N/A (Velocidad 0)"
    
    if (target_change_pct > 0 and velocity_per_hour < 0) or \
       (target_change_pct < 0 and velocity_per_hour > 0):
        return "N/A (Dir. Incompatible)"

    try:
        # 3. Calculate the hours needed (Hours = Distance / Velocity)
        hours_needed = target_change_pct / velocity_per_hour
        
        if hours_needed < 0: # Should be caught by direction check, but good for robustness
            return "N/A (Reversión Necesaria)"

        # 4. Format the result to days/hours/minutes
        if hours_needed >= 24 * 30: # >= 30 days
            months = round(hours_needed / (24 * 30))
            return f"~{months} meses"
        elif hours_needed >= 24: # >= 1 day
            days = round(hours_needed / 24)
            return f"~{days} días"
        elif hours_needed > 1: # > 1 hour
            return f"~{round(hours_needed, 1)} horas"
        else: # <= 1 hour
            minutes = max(1, round(hours_needed * 60)) # At least 1 minute
            return f"~{minutes} minutos"

    except (ZeroDivisionError, ValueError, TypeError):
        return "N/A"

# --- 4. TABLE PRINTING AND TELEGRAM NOTIFICATION FUNCTION ---

def print_table(data: List[dict], prev_prices: Dict[str, float], currency: str) -> Dict[str, Union[Dict[str, float], List[Dict[str, str | float]]]]:
    """
    Formats and prints the data to the terminal, including 48h projection, technical analysis,
    and estimated time to PLR.
    """
    rows = []
    buy_signals_data: List[Dict[str, str | float]] = [] 

    for coin in data:
        symbol = coin.get("symbol", "").upper()
        name = coin.get("id", "")
        price = coin.get("current_price")
        change_24h = coin.get("price_change_percentage_24h_in_currency")
        change_7d = coin.get("price_change_percentage_7d_in_currency")
        market_cap = coin.get("market_cap")

        alert_raw = compute_alert(change_24h, change_7d)
        
        # Calculate Suggested Limit Price (PLR) - float value
        limit_suggered_float: Optional[float] = None
        limit_suggered_str = ""

        # Only calculate PLR and add to Telegram signals if it's a BUY (DIP) alert
        if "¡COMPRA! (DIP)" in alert_raw and price is not None:
            limit_suggered_float = price * (1 - 0.02) # 2% discount from current price
            limit_suggered_str = format_price(limit_suggered_float, decimal_limit=4)
            buy_signals_data.append({
                "symbol": symbol,
                "name": name,
                "price": price,
                "change_24h": change_24h,
                "change_7d": change_7d,
                "limit_price": limit_suggered_str,
            })

        alert_str = alert_raw
        price_str = format_price(price)
        change_24h_str = colorize_percent(change_24h)
        change_7d_str = colorize_percent(change_7d)
        market_cap_str = f"${market_cap:,.0f}" if market_cap else "N/A"
        
        projection_48h_str = compute_projection(price, change_24h)
        technical_sentiment_str = compute_technical_sentiment(change_24h, change_7d)
        
        # --- New: Estimated Time to PLR ---
        time_to_plr_str = compute_time_to_plr(price, change_24h, limit_suggered_float)

        # Delta from previous price
        delta_str = ""
        prev = prev_prices.get(name)
        if prev is not None and price is not None:
            try:
                pct = (price - prev) / prev * 100 if prev != 0 else 0.0
                delta_str = f"{pct:+.2f}%"
                if HAS_COLORAMA:
                    delta_str = (Fore.GREEN + delta_str) if pct >= 0 else (Fore.RED + delta_str)
            except (ValueError, TypeError):
                delta_str = ""

        rows.append({
            "Moneda": symbol,
            "Precio": price_str,
            "Δ(prev)": delta_str,
            "24h": change_24h_str,
            "7d": change_7d_str,
            "Proyección 48h": projection_48h_str,
            "Análisis Técnico": technical_sentiment_str,
            "Alerta": alert_str,
            "Límite Sugerido": limit_suggered_str, 
            "Tiempo al PLR": time_to_plr_str, # <--- ADDED HERE!
            "MarketCap": market_cap_str,
            "_id": name,
            "_price_raw": price,
        })

    # Headers for the table, now including "Tiempo al PLR"
    headers = ["Moneda", "Precio", "Δ(prev)", "24h", "7d", "Proyección 48h", "Análisis Técnico", "Alerta", "Límite Sugerido", "Tiempo al PLR", "MarketCap"]
    
    if HAS_TABULATE:
        # Filter out "Límite Sugerido" and "Tiempo al PLR" if no buy signals are present for cleaner output
        active_headers = [h for h in headers if h not in ["Límite Sugerido", "Tiempo al PLR"] or any(r["Límite Sugerido"] for r in rows)]
        table_data = [[r[h] for h in active_headers] for r in rows]
        print(tabulate(table_data, headers=active_headers, tablefmt="plain"))
    else:
        # Fallback for when tabulate is not installed
        active_headers = [h for h in headers if h not in ["Límite Sugerido", "Tiempo al PLR"] or any(r["Límite Sugerido"] for r in rows)]
        col_widths = {h: len(h) for h in active_headers}
        for r in rows:
            for h in active_headers:
                col_widths[h] = max(col_widths[h], len(str(r[h])))
        sep = "  "
        header_line = sep.join(h.ljust(col_widths[h]) for h in active_headers)
        print(header_line)
        print("—" * (len(header_line))) # Dynamic separator line
        for r in rows:
            line = sep.join(str(r[h]).ljust(col_widths[h]) for h in active_headers)
            print(line)

    return {
        "prev_prices": {r["_id"]: r["_price_raw"] for r in rows if r["_id"]},
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
    parser.add_argument("--backoff", type=float, default=1.0, help="Backoff factor between retries")
    parser.add_argument("--per-page", type=int, default=100, help="Number of results per page")
    parser.add_argument("--verbose", action="store_true", help="Show DEBUG logs")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear terminal on each update")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Telegram credentials from environment variables or hardcoded (empty by default)
    # Using os.environ.get is safer and more flexible
    telegram_token = TELEGRAM_BOT_TOKEN 
    telegram_chat = TELEGRAM_CHAT_ID
    
    if not telegram_token or not telegram_chat:
        logger.warning("Telegram notifications disabled: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not configured in environment.")

    session = create_session(retries=args.retries, backoff_factor=args.backoff)
    prev_prices: Dict[str, float] = {}

    try:
        while True:
            data = fetch_data(session, args.cryptos, args.currency, per_page=args.per_page)
            if not args.no_clear:
                clear_terminal()
            
            # --- DECORATED TITLE ---
            print(Fore.CYAN + "✨ " + Style.BRIGHT + "NON FUNGIBLE METAVERSE" + Style.RESET_ALL + Fore.CYAN + " ✨")
            print(f"--- 🧠 Analizador Avanzado de Precios Crypto (CLI) 🚀 ---")
            print(f"Última Actualización: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC | Cryptos: {args.cryptos} | Fiat: {args.currency}")
            print("=" * min(120, shutil.get_terminal_size((120, 20)).columns))

            if data:
                result = print_table(data, prev_prices, args.currency)
                new_prev = result["prev_prices"]
                buy_signals = result["buy_signals"]
                
                # If Telegram is configured and there are buy signals, send a notification
                if buy_signals and telegram_token and telegram_chat:
                    msg_parts = [
                        "🚨 *ALERTA DE COMPRA \\(DIP\\) EN EL METAVERSO* 🚨",
                        "El mercado presenta oportunidades de entrada:",
                        "" # Empty line
                    ]
                    
                    for signal in buy_signals:
                        # Escape Telegram MarkdownV2 special characters
                        symbol = str(signal['symbol']).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
                        name = str(signal['name']).replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace('`', '\\`')
                        
                        msg_parts.append(
                            f"💰 *{symbol}* \\({name}\\) \\- ¡A la Caza\\! 🎯"
                        )
                        msg_parts.append(
                            f"   \\- Precio Actual: *{format_price(signal['price']).replace('$', '\\$').replace('.', '\\.')}*" # Escape '.' in price
                        )
                        # Escape '+' and '-' in percentages
                        msg_parts.append(
                            f"   \\- Var\\. 24h: {colorize_percent(signal['change_24h']).replace('+', '\\+').replace('-', '\\-')}"
                        )
                        msg_parts.append(
                            f"   \\- Var\\. 7d: {colorize_percent(signal['change_7d']).replace('+', '\\+').replace('-', '\\-')}"
                        )
                        msg_parts.append(
                            f"   \\- *Límite Sugerido \\(\\-2\\%\\):* *{str(signal['limit_price']).replace('$', '\\$').replace('.', '\\.')}* ✍️" # Escape '.' in price
                        )
                        msg_parts.append("") # Empty line

                    msg_parts.append("---")
                    msg_parts.append(Style.BRIGHT + "Estrategia de inversión compartida por *Non Fungible Metaverse*\\. 🚀")
                    
                    msg = "\n".join(msg_parts)
                    
                    if send_telegram_message(telegram_token, telegram_chat, msg):
                        logger.info("Telegram buy notification sent. 🔔")

                prev_prices.update({k: v for k, v in new_prev.items() if v is not None})
            else:
                logger.warning("No data retrieved from CoinGecko. Retrying... 🔄")

            # --- DECORATED CLOSING MESSAGE ---
            print("=" * min(120, shutil.get_terminal_size((120, 20)).columns))
            print(Fore.YELLOW + f"Updating in {args.interval} seconds... (Ctrl+C to stop 🛑)")
            time.sleep(max(1, args.interval))

    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\nAnalyzer stopped. Happy trading in the 🌐 Metaverse!")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
