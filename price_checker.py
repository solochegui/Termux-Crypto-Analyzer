#!/usr/bin/env python3
"""
Termux-Crypto-Analyzer - price_checker.py
Analizador avanzado de precios crypto (CLI) con Proyección, Análisis Técnico y notificaciones Telegram.
Creado por Non Fungible Metaverse.
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Optional dependencies
try:
    from tabulate import tabulate  # type: ignore
    HAS_TABULATE = True
except Exception:
    HAS_TABULATE = False

try:
    from colorama import Fore, Back, Style, init as colorama_init  # type: ignore
    # Se añade autoreset para simplificar el código
    colorama_init(autoreset=True) 
    HAS_COLORAMA = True
except Exception:
    HAS_COLORAMA = False
    # --- Clases de reserva ANSI para cuando colorama no está instalado ---
    class Ansi:
        RESET = ""
        RED = ""
        GREEN = ""
        CYAN = ""
        YELLOW = ""
        BOLD = ""
        BG_RED = ""
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

# NOTA IMPORTANTE DE SEGURIDAD: 
# Estos campos están vacíos por defecto. PARA USAR TELEGRAM, 
# DEBE CONFIGURAR LAS VARIABLES DE ENTORNO EN TERMUX: 
# export TELEGRAM_BOT_TOKEN="SU_TOKEN"
# export TELEGRAM_CHAT_ID="SU_CHAT_ID"
TELEGRAM_BOT_TOKEN = "" 
TELEGRAM_CHAT_ID = ""   

# Defaults
DEFAULT_CRYPTOS = "bitcoin,ethereum,solana,boricoin,pepe,bonk,ripple,xyo"
DEFAULT_CURRENCY = "usd"
DEFAULT_INTERVAL = 10
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
RATE_LIMIT_WAIT_TIME = 60 # Tiempo de espera recomendado para HTTP 429

# Logging config
logger = logging.getLogger("price_checker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)


# --- 2. FUNCIONES AUXILIARES DE CONEXIÓN Y UTILIDADES ---

def create_session(retries: int = 3, backoff_factor: float = 1.0, status_forcelist: Optional[List[int]] = None) -> requests.Session:
    """Configura una sesión HTTP con reintentos para manejar errores de red y Rate Limits."""
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


def clear_terminal():
    """Limpia la terminal (funciona en Windows, Linux y Termux)."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def fetch_data(session: requests.Session, cryptos: str, currency: str, per_page: int = 100, timeout: int = 10) -> Optional[List[dict]]:
    """Obtiene datos desde CoinGecko con manejo de reintentos."""
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
            logger.error(f"Rate Limit (429) alcanzado. ⚠️ Esperando {RATE_LIMIT_WAIT_TIME} segundos...")
            time.sleep(RATE_LIMIT_WAIT_TIME)
        else:
            logger.warning("Error HTTP (%s) al conectar con CoinGecko: %s", resp.status_code, e)
        return None
    except requests.exceptions.RequestException as e:
        logger.warning("Error de conexión con CoinGecko: %s", e)
        return None

# --- 3. FUNCIONES DE FORMATO Y LÓGICA DE ALERTA ---

def format_price(price: Optional[float], decimal_limit: int = 2) -> str:
    """Formatea el precio, usando más decimales para valores bajos."""
    if price is None:
        return "N/A"
    try:
        if price < 0.1:
            return f"${price:,.8f}"
        return f"${price:,.{decimal_limit}f}"
    except Exception:
        return str(price)

def format_limit_price(price: Optional[float]) -> str:
    """Calcula y formatea el precio sugerido para una orden limitada (2% de descuento)."""
    if price is None:
        return "N/A"
    
    limit_price = price * (1 - 0.02) # Precio 2% más bajo
    return format_price(limit_price, decimal_limit=4) 

def colorize_percent(value: Optional[float]) -> str:
    """Aplica color a los porcentajes de cambio (verde positivo, rojo negativo)."""
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
    """Calcula la alerta de compra/venta/riesgo basada en la lógica avanzada de Non Fungible Metaverse (7 Señales)."""
    if change_24h is None or change_7d is None:
        return ""
    
    # 1. Señal de VENTA: Posible sobrecompra / Toma de Ganancias (Take Profit)
    if change_24h > 10.0 and change_7d > 15.0:
        return (Back.GREEN + Fore.BLACK + " 💸 ¡VENTA! (FOMO) ") if HAS_COLORAMA else "💸 ¡VENTA! (FOMO)"

    # 2. Señal de COMPRA: Caída fuerte en 24h (> 4%) pero tendencia positiva en 7d (> 0%) - Comprar el DIP
    if change_24h < -4.0 and change_7d > 0:
        return (Back.BLUE + Fore.WHITE + " 📉 ¡COMPRA! (DIP) ") if HAS_COLORAMA else "📉 ¡COMPRA! (DIP)"

    # 3. Señal de RIESGO/CAPITULACIÓN: Fuerte caída de corto y mediano plazo
    if change_24h < -8.0 or change_7d < -10.0:
        return (Fore.RED + "🔥 RIESGO/CAPITULACIÓN") if HAS_COLORAMA else "🔥 RIESGO/CAPITULACIÓN"
        
    # --- NUEVAS SEÑALES ANALÍTICAS ---

    # 4. Tendencia de CRECIMIENTO SOSTENIBLE: Momentum Alcista Saludable (Buy)
    if change_24h > 2.0 and change_7d > 8.0:
        return (Fore.MAGENTA + "🟢 MOMENTUM SALUDABLE") if HAS_COLORAMA else "🟢 MOMENTUM SALUDABLE"

    # 5. Corrección de CORTO PLAZO (Warning/Hold)
    if -4.0 <= change_24h < -2.0 and change_7d > 10.0:
        return (Fore.YELLOW + "⚠️ CORRECCIÓN C/P") if HAS_COLORAMA else "⚠️ CORRECCIÓN C/P"

    # 6. Alerta de LATERALIZACIÓN (RANGO): Consolidación (Neutral)
    if -1.5 <= change_24h <= 1.5 and -3.0 <= change_7d <= 3.0:
        return (Fore.BLUE + "😴 RANGO/CONSOLIDACIÓN") if HAS_COLORAMA else "😴 RANGO/CONSOLIDACIÓN"

    # 7. Señal de Estabilidad (Umbral más estricto ahora)
    if -1.0 <= change_24h <= 1.0:
        return (Fore.CYAN + "⚖️ ESTABLE") if HAS_COLORAMA else "⚖️ ESTABLE"
        
    return "" # Por defecto

def compute_projection(current_price: Optional[float], change_24h: Optional[float]) -> str:
    """
    Calcula una proyección simple del precio a 48 horas (ASUMCIÓN LINEAL).
    NO es un modelo predictivo avanzado, sino una estimación de momentum.
    """
    if current_price is None or change_24h is None:
        return "N/A"
    
    try:
        # Factor de cambio: (1 + cambio_24h/100)
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

    except Exception:
        return "N/A"

def compute_technical_sentiment(change_24h: Optional[float], change_7d: Optional[float]) -> str:
    """Simula un resumen de análisis técnico (ej. Medias Móviles + RSI) basado en el impulso."""
    if change_24h is None or change_7d is None:
        return ""
    
    # 1. FUERTE COMPRA: Impulso alcista claro y sostenido
    if change_24h > 5.0 and change_7d > 10.0:
        return (Fore.GREEN + Style.BRIGHT + "FUERTE COMPRA (Golden Cross)") if HAS_COLORAMA else "FUERTE COMPRA"
    
    # 2. COMPRA: Impulso alcista reciente (Breakout) o buen rebote
    if change_24h > 2.0 and change_7d > 0:
        return (Fore.GREEN + "COMPRA") if HAS_COLORAMA else "COMPRA"
        
    # 3. FUERTE VENTA: Caída severa y tendencia negativa (Death Cross)
    if change_24h < -5.0 and change_7d < -10.0:
        return (Fore.RED + Style.BRIGHT + "FUERTE VENTA (Death Cross)") if HAS_COLORAMA else "FUERTE VENTA"

    # 4. VENTA: Tendencia bajista clara
    if change_24h < -2.0 and change_7d < 0:
        return (Fore.RED + "VENTA") if HAS_COLORAMA else "VENTA"
        
    # 5. NEUTRAL / CONSOLIDACIÓN: Sin dirección clara
    if -2.0 <= change_24h <= 2.0 and -5.0 <= change_7d <= 5.0:
        return (Fore.YELLOW + "NEUTRAL") if HAS_COLORAMA else "NEUTRAL"

    # 6. NEUTRAL / SOBRECOMPRA: Riesgo de corrección (RSI > 70)
    if change_24h > 7.0 and change_7d > 20.0:
        return (Fore.MAGENTA + "NEUTRAL (Sobrecompra)") if HAS_COLORAMA else "NEUTRAL (Sobrecompra)"

    return "NEUTRAL"


# --- 4. FUNCIÓN DE TABLA Y NOTIFICACIÓN DE TELEGRAM ---

def print_table(data: List[dict], prev_prices: Dict[str, float], currency: str):
    """
    Formatea e imprime los datos en la terminal, incluyendo la proyección de 48h y el análisis técnico.
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
        
        limit_suggered_str = ""
        # Solo guardar para Telegram si es una señal de COMPRA (DIP)
        if "¡COMPRA! (DIP)" in alert_raw:
            limit_suggered_str = format_limit_price(price)
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

        # Delta desde el precio previo
        delta_str = ""
        prev = prev_prices.get(name)
        if prev is not None and price is not None:
            try:
                pct = (price - prev) / prev * 100 if prev != 0 else 0.0
                delta_str = f"{pct:+.2f}%"
                if HAS_COLORAMA:
                    delta_str = (Fore.GREEN + delta_str) if pct >= 0 else (Fore.RED + delta_str)
            except Exception:
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
            "MarketCap": market_cap_str,
            "_id": name,
            "_price_raw": price,
        })

    # Uso de tabulate o fallback simple
    headers = ["Moneda", "Precio", "Δ(prev)", "24h", "7d", "Proyección 48h", "Análisis Técnico", "Alerta", "Límite Sugerido", "MarketCap"]
    if HAS_TABULATE:
        active_headers = [h for h in headers if h != "Límite Sugerido" or any(r["Límite Sugerido"] for r in rows)]
        table_data = [[r[h] for h in active_headers] for r in rows]
        print(tabulate(table_data, headers=active_headers, tablefmt="plain"))
    else:
        active_headers = headers
        col_widths = {h: len(h) for h in active_headers}
        for r in rows:
            for h in active_headers:
                col_widths[h] = max(col_widths[h], len(str(r[h])))
        sep = "  "
        header_line = sep.join(h.ljust(col_widths[h]) for h in active_headers)
        print(header_line)
        print("—"*4 + " ₿ " + "—"*4 + " 📈 " + "—"*4 + " 💸 " + "—"*4)
        for r in rows:
            line = sep.join(str(r[h]).ljust(col_widths[h]) for h in active_headers)
            print(line)

    return {
        "prev_prices": {r["_id"]: r["_price_raw"] for r in rows if r["_id"]},
        "buy_signals": buy_signals_data
    }


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Envía un mensaje a un chat de Telegram específico."""
    if not bot_token or not chat_id:
        logger.debug("Omisión de Telegram: Token o Chat ID no configurados.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        resp = requests.post(url, data={"chat_id": chat_id, "text": message, "parse_mode": "MarkdownV2"}, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.warning("Error enviando Telegram: %s", e)
        return False


# --- 5. FUNCIÓN PRINCIPAL DE EJECUCIÓN (MAIN) ---

def parse_args():
    """Define y parsea los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description="Analizador avanzado de precios crypto (CLI)")
    parser.add_argument("--cryptos", type=str, default=os.environ.get("CRYPTOS", DEFAULT_CRYPTOS),
                        help=f"IDs de CoinGecko separados por comas (default: {DEFAULT_CRYPTOS})")
    parser.add_argument("--currency", type=str, default=os.environ.get("CURRENCY", DEFAULT_CURRENCY),
                        help="Moneda fiat (default: usd)")
    parser.add_argument("--interval", type=int, default=int(os.environ.get("UPDATE_INTERVAL", DEFAULT_INTERVAL)),
                        help=f"Intervalo de actualización en segundos (default: {DEFAULT_INTERVAL})")
    parser.add_argument("--retries", type=int, default=3, help="Reintentos HTTP")
    parser.add_argument("--backoff", type=float, default=1.0, help="Factor de backoff entre reintentos")
    parser.add_argument("--per-page", type=int, default=100, help="Número de resultados por página")
    parser.add_argument("--verbose", action="store_true", help="Mostrar logs DEBUG")
    parser.add_argument("--no-clear", action="store_true", help="No limpiar terminal en cada actualización")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    telegram_chat = os.environ.get("TELEGRAM_CHAT_ID") or TELEGRAM_CHAT_ID
    
    if not telegram_token or not telegram_chat:
        logger.warning("Telegram deshabilitado: TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados.")

    session = create_session(retries=args.retries, backoff_factor=args.backoff)
    prev_prices: Dict[str, float] = {}

    try:
        while True:
            data = fetch_data(session, args.cryptos, args.currency, per_page=args.per_page)
            if not args.no_clear:
                clear_terminal()
            
            # --- TÍTULO DECORADO ---
            print(Fore.CYAN + "✨ " + Style.BRIGHT + "NON FUNGIBLE METAVERSE" + Style.RESET_ALL + Fore.CYAN + " ✨")
            print(f"--- 🧠 Analizador Avanzado de Precios Crypto (CLI) 🚀 ---")
            print(f"Última Actualización: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC | Cryptos: {args.cryptos} | Fiat: {args.currency}")
            print("=" * min(120, shutil.get_terminal_size((120, 20)).columns))

            if data:
                result = print_table(data, prev_prices, args.currency)
                new_prev = result["prev_prices"]
                buy_signals = result["buy_signals"]
                
                # Si Telegram configurado y hay señales de compra, enviar notificación
                if buy_signals and telegram_token and telegram_chat:
                    msg_parts = [
                        "🚨 *ALERTA DE COMPRA \\(DIP\\) EN EL METAVERSO* 🚨",
                        "El mercado presenta oportunidades de entrada:",
                        "" # Línea vacía
                    ]
                    
                    for signal in buy_signals:
                        symbol = signal['symbol'].replace('_', '\\_')
                        name = signal['name'].replace('_', '\\_')
                        
                        msg_parts.append(
                            f"💰 *{symbol}* \\({name}\\) \\- ¡A la Caza\\! 🎯"
                        )
                        msg_parts.append(
                            f"   \\- Precio Actual: *{format_price(signal['price']).replace('$', '\\$')}*"
                        )
                        msg_parts.append(
                            f"   \\- Var\\. 24h: {colorize_percent(signal['change_24h']).replace('+', '\\+').replace('-', '\\-')}"
                        )
                        msg_parts.append(
                            f"   \\- Var\\. 7d: {colorize_percent(signal['change_7d']).replace('+', '\\+').replace('-', '\\-')}"
                        )
                        msg_parts.append(
                            f"   \\- *Límite Sugerido \\(\\-2\\%\\):* *{signal['limit_price'].replace('$', '\\$')}* ✍️"
                        )
                        msg_parts.append("") # Línea vacía

                    msg_parts.append("---")
                    msg_parts.append(Style.BRIGHT + "Estrategia de inversión compartida por *Non Fungible Metaverse*\\. 🚀")
                    
                    msg = "\n".join(msg_parts)
                    
                    if send_telegram_message(telegram_token, telegram_chat, msg):
                        logger.info("Notificación Telegram de compra enviada. 🔔")

                prev_prices.update({k: v for k, v in new_prev.items() if v is not None})
            else:
                logger.warning("No se obtuvieron datos de CoinGecko. Reintentando... 🔄")

            # --- MENSAJE DE CIERRE DECORADO ---
            print("=" * min(120, shutil.get_terminal_size((120, 20)).columns))
            print(Fore.YELLOW + f"Actualizando en {args.interval} segundos... (Ctrl+C para detener 🛑)")
            time.sleep(max(1, args.interval))

    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\nAnalizador detenido. ¡Buen trading en el 🌐 Metaverse!")
        sys.exit(0)


if __name__ == "__main__":
    main()
