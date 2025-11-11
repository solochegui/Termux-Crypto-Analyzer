#!/usr/bin/env python3
"""
Termux-Crypto-Analyzer - price_checker.py
Analizador avanzado de precios crypto (CLI) con notificaciones Telegram opcionales.

Mejoras clave:
 - argparse para configuración por CLI/ENV.
 - Retries con backoff para manejo de la API (CoinGecko).
 - colorama/tabulate para mejor salida en terminal.
 - Notificaciones Telegram para señales de compra (DIP).
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
    colorama_init(autoreset=True) # Se añade autoreset para simplificar el código
    HAS_COLORAMA = True
except Exception:
    HAS_COLORAMA = False
    class Ansi:
        RESET = ""
        RED = ""
        GREEN = ""
        CYAN = ""
        YELLOW = ""
        BOLD = ""
        BG_RED = ""
    Fore = Back = Style = Ansi()

# --- 1. CONFIGURACIÓN MEJORADA & CREDENCIALES ---

# Credenciales de Telegram (Sincronizadas con tus valores)
# NOTA: Se recomienda borrar estos valores y usar variables de entorno para producción/seguridad.
TELEGRAM_BOT_TOKEN = "8055717881:AAFQO3wJDDGE7sFNjCDLdGnwN-ZLNsJTxsk"
TELEGRAM_CHAT_ID = "5201198514"

# Defaults
DEFAULT_CRYPTOS = "bitcoin,ethereum,solana,boricoin,pepe,bonk,ripple,xyo"
DEFAULT_CURRENCY = "usd"
DEFAULT_INTERVAL = 10
API_URL = "https://api.coingecko.com/api/v3/coins/markets"

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
    except requests.exceptions.RequestException as e:
        logger.warning("Error al conectar con CoinGecko: %s", e)
        return None

# --- 3. FUNCIONES DE FORMATO Y LÓGICA DE ALERTA ---

def format_price(price: Optional[float]) -> str:
    """Formatea el precio, usando más decimales para valores bajos."""
    if price is None:
        return "N/A"
    try:
        if price < 0.1:
            return f"${price:,.8f}"
        return f"${price:,.2f}"
    except Exception:
        return str(price)


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
    """Calcula la alerta de compra basada en la lógica de 'comprar el dip'."""
    if change_24h is None or change_7d is None:
        return ""
    
    # Señal de Compra: Caída fuerte en 24h (> 4%) pero tendencia positiva en 7d (> 0%)
    if change_24h < -4.0 and change_7d > 0:
        return (Back.RED + Fore.WHITE + " ¡COMPRA! (DIP) ") if HAS_COLORAMA else "¡COMPRA! (DIP)"
    # Señal de Riesgo: Tendencia bajista fuerte en 7d
    if change_7d < -8.0:
        return (Fore.RED + "RIESGO") if HAS_COLORAMA else "RIESGO"
    # Señal de Estabilidad: Precio relativamente estable
    if -2.0 <= change_24h <= 2.0:
        return (Fore.CYAN + "ESTABLE") if HAS_COLORAMA else "ESTABLE"
    return ""


# --- 4. FUNCIÓN DE TABLA Y NOTIFICACIÓN DE TELEGRAM ---

def print_table(data: List[dict], prev_prices: Dict[str, float], currency: str):
    """
    Formatea e imprime los datos en la terminal, usando tabulate si está disponible.
    Devuelve el nuevo mapa de precios.
    """
    rows = []
    for coin in data:
        symbol = coin.get("symbol", "").upper()
        name = coin.get("id", "")
        price = coin.get("current_price")
        change_24h = coin.get("price_change_percentage_24h_in_currency")
        change_7d = coin.get("price_change_percentage_7d_in_currency")
        market_cap = coin.get("market_cap")

        alert = compute_alert(change_24h, change_7d)
        price_str = format_price(price)
        change_24h_str = colorize_percent(change_24h)
        change_7d_str = colorize_percent(change_7d)
        market_cap_str = f"${market_cap:,.0f}" if market_cap else "N/A"

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
            "Alerta": alert,
            "MarketCap": market_cap_str,
            "_id": name,
            "_price_raw": price,
        })

    # Uso de tabulate o fallback simple
    headers = ["Moneda", "Precio", "Δ(prev)", "24h", "7d", "Alerta", "MarketCap"]
    if HAS_TABULATE:
        table = tabulate([[r[h] for h in headers] for r in rows], headers=headers, tablefmt="plain")
        print(table)
    else:
        # Lógica de impresión alineada simple (sin tabulate)
        col_widths = {h: len(h) for h in headers}
        for r in rows:
            for h in headers:
                col_widths[h] = max(col_widths[h], len(str(r[h])))
        sep = "  "
        header_line = sep.join(h.ljust(col_widths[h]) for h in headers)
        print(header_line)
        print("-" * min(shutil.get_terminal_size((80, 20)).columns, sum(col_widths.values()) + len(sep) * (len(headers) - 1)))
        for r in rows:
            line = sep.join(str(r[h]).ljust(col_widths[h]) for h in headers)
            print(line)

    return {r["_id"]: r["_price_raw"] for r in rows if r["_id"]}


def send_telegram_message(bot_token: str, chat_id: str, message: str) -> bool:
    """Envía un mensaje a un chat de Telegram específico."""
    # Validación de credenciales para evitar peticiones inútiles (aunque ya se hace en main)
    if not bot_token or not chat_id or bot_token == "8055717881:AAFQO3wJDDGE7sFNjCDLdGnwN-ZLNsJTxsk":
        logger.debug("Omisión de Telegram: Token o Chat ID no configurados o son de ejemplo.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        # Se envía la petición usando el texto sin parse_mode (por simplicidad)
        resp = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
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

    # Lógica de sincronización de Telegram:
    # 1. Intenta leer de variables de entorno (más seguro).
    # 2. Si no existen, usa las variables globales definidas al inicio (tus valores).
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN") or TELEGRAM_BOT_TOKEN
    telegram_chat = os.environ.get("TELEGRAM_CHAT_ID") or TELEGRAM_CHAT_ID
    
    # Comprobación de que las credenciales no son las de ejemplo (si se usan las globales)
    if telegram_token == "8055717881:AAFQO3wJDDGE7sFNjCDLdGnwN-ZLNsJTxsk":
        logger.warning("Usando credenciales de Telegram de ejemplo/prueba.")

    session = create_session(retries=args.retries, backoff_factor=args.backoff)
    prev_prices: Dict[str, float] = {}

    try:
        while True:
            data = fetch_data(session, args.cryptos, args.currency, per_page=args.per_page)
            if not args.no_clear:
                clear_terminal()

            print(f"--- 🧠 Analizador Avanzado de Precios Crypto (CLI) ---")
            print(f"Última Actualización: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC | Cryptos: {args.cryptos} | Fiat: {args.currency}")
            print("-" * min(120, shutil.get_terminal_size((120, 20)).columns))

            if data:
                new_prev = print_table(data, prev_prices, args.currency)

                # Detección de señales de compra
                buy_signals = []
                for coin in data:
                    change_24h = coin.get("price_change_percentage_24h_in_currency")
                    change_7d = coin.get("price_change_percentage_7d_in_currency")
                    name = coin.get("id")
                    symbol = coin.get("symbol", "").upper()
                    if change_24h is not None and change_7d is not None:
                        # Replicando la lógica de compute_alert para generar el mensaje
                        if change_24h < -4.0 and change_7d > 0:
                            price = coin.get("current_price")
                            price_str = format_price(price)
                            buy_signals.append(f"*{symbol}* ({name}): Precio actual {price_str}, 24h {change_24h:+.2f}%, 7d {change_7d:+.2f}%")

                # Si Telegram configurado y hay señales de compra, enviar notificación
                if buy_signals and telegram_token and telegram_chat:
                    msg = "📣 Señales de *COMPRA* encontradas:\n" + "\n".join(buy_signals)
                    # Usamos Markdown para el mensaje de Telegram
                    send_telegram_message(telegram_token, telegram_chat, msg)
                    logger.info("Notificación Telegram de compra enviada.")

                prev_prices.update({k: v for k, v in new_prev.items() if v is not None})
            else:
                logger.warning("No se obtuvieron datos de CoinGecko. Reintentando...")

            print("-" * min(120, shutil.get_terminal_size((120, 20)).columns))
            print(f"Actualizando en {args.interval} segundos... (Ctrl+C para detener)")
            time.sleep(max(1, args.interval))

    except KeyboardInterrupt:
        print("\nAnalizador detenido. ¡Buen trading!")
        sys.exit(0)


if __name__ == "__main__":
    main()
