# 🧠 Termux-Crypto-Analyzer: Analizador Avanzado de Precios Crypto (CLI) 🚀

Este proyecto es una herramienta de línea de comandos (CLI) escrita en Python, diseñada para monitorear precios de criptomonedas en tiempo real, aplicar una lógica de inversión avanzada (basada en el análisis de Non Fungible Metaverse) y generar señales de **COMPRA (DIP/Reversión)** y **VENTA (FOMO/Bull Trap)**.

Está optimizado para ser ejecutado en entornos móviles como **Termux** (Android/iOS) y puede integrarse con Telegram para notificaciones y con la API de Coinbase para automatización.

## ✨ Filosofía de Inversión (Non Fungible Metaverse)

El analizador se centra en la estrategia de **"Comprar el DIP"** (Buy the Dip) y la detección temprana de reversiones y trampas. Utiliza el cambio de precio en **24 horas** y **7 días** para evaluar el *momentum* y la salud de la tendencia.

Se han implementado **11 señales** de *trading* específicas para clasificar el estado de cada activo:

| Señal | Condición Clave | Acción |
| :--- | :--- | :--- |
| **📉 COMPRA! (DIP)** | Caída en 24h, tendencia de 7d positiva. | **COMPRA LÍMITE (PLR).** |
| **📈 REVERSIÓN V/B** | Rebote fuerte (>4%) tras caída de 7d. | **COMPRA FUERTE.** |
| **💎 ACUMULACIÓN FUERTE** | Precio tocando fondo tras caída prolongada. | Compra de **Largo Plazo (LT)**. |
| **🚀 RUPTURA ALCISTA** | Fuerte momentum en 24h/7d. | Continuación, COMPRA. |
| **💸 VENTA! (FOMO)** | Subidas explosivas y sostenidas. | **Take Profit / VENTA.** |
| **⚠️ BULL TRAP** | Subida rápida sin soporte en 7d. | **VENTA / Alto Riesgo.** |
| **💀 CAPITULACIÓN** | Caída extrema y sostenida. | Observar / Máximo Riesgo. |
| **🟢 MOMENTUM SALUDABLE** | Crecimiento sostenible. | HOLD. |
| **😴 RANGO/CONSOLIDACIÓN** | Baja volatilidad. | HOLD / Neutral. |

## ⚙️ Requisitos

1.  **Python 3** (Idealmente 3.8 o superior).
2.  **Librerías Python:**
    ```bash
    pip install requests coinbase
    ```
3.  **Termux (Opcional):** Si lo usas en Termux, asegúrate de tener `python` instalado: `pkg install python`.

## 🛠️ Configuración y Variables de Entorno

El script utiliza variables de entorno para gestionar las credenciales de forma segura.

### 1. CoinGecko (API de Precios)

No requiere configuración de claves, pero está sujeto a los límites de la API pública.

### 2. Telegram (Notificaciones)

Para recibir alertas de **COMPRA (DIP/Reversión)**, debes configurar:

| Variable | Descripción |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token de tu Bot de Telegram (Obtenido de BotFather). |
| `TELEGRAM_CHAT_ID` | ID del chat o grupo donde el bot enviará las alertas. |

### 3. Coinbase (Automatización de Órdenes)

Para que el script envíe automáticamente una **Orden de Mercado** (simulando una Orden Límite) al detectar una señal de compra, configura:

| Variable | Descripción |
| :--- | :--- |
| `COINBASE_API_KEY` | Clave API de Coinbase. |
| `COINBASE_API_SECRET` | Secreto API de Coinbase. |

**⚠️ NOTA IMPORTANTE:** La automatización de Coinbase en este script utiliza la **API de Wallet** para ejecutar una orden de **MERCADO** de `$10.00 USD` al detectar una señal. Esto **no es una orden limitada**. Utiliza esta función bajo tu propia responsabilidad.

### 💡 Cómo establecer las variables en Termux

Abre tu archivo `.bashrc` o `.zshrc` y añade tus claves:

```bash
# Variables de Coinbase (Automatización de Trading)
export COINBASE_API_KEY="tu_clave_aqui"
export COINBASE_API_SECRET="tu_secreto_aqui"

# Variables de Telegram (Alertas)
export TELEGRAM_BOT_TOKEN="tu_token_bot_aqui"
export TELEGRAM_CHAT_ID="tu_chat_id_aqui"

