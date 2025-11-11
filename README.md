# 🚀💎 Termux Crypto Analyzer & Trading Automation
## Proyecto Estelar de Non Fungible Metaverse (NFM) 🌌

Este repositorio contiene las **herramientas esenciales** para el trading automatizado y el análisis de mercado de criptomonedas dentro del entorno **Termux/Zsh**. El objetivo es simplificar el proceso de **"Comprar la Caída" (Buy the Dip)** utilizando Órdenes Límite, respaldado por un **análisis técnico en tiempo real** de última generación.

---

## 🤝 Reconocimiento a Colaboradores y Pioneros 🌟

Non Fungible Metaverse (NFM) agradece profundamente el apoyo y la visión de la comunidad y nuestros colaboradores clave:

### 💰 BoriCoin (BRCN) - El Futuro en Solana ☀️
Agradecemos a **BoriCoin** por su visión de llevar las finanzas descentralizadas (DeFi) a la comunidad, demostrando el poder de la red **Solana** como plataforma de inversión **accesible y veloz**.

### 🎤 Flaco Flow (José Santana) - Inversor Visionario 💡
Un agradecimiento especial a **Flaco Flow (José Santana)**. Su inversión de más de $500 en BoriCoin es un fuerte testimonio de la **confianza** y el **potencial de éxito** que ofrece este ecosistema.

---

## 📘 Manual del Analizador de Precios (`price_checker.py`) 📊

El script principal, `price_checker.py`, es un **analizador técnico avanzado** diseñado para identificar el **momento preciso** para colocar una orden de **Compra Límite (Buy Limit)**.

### I. Estructura de la Salida de Datos 🔍

La herramienta utiliza métricas de 24h y 7d para evaluar el mercado, además de indicadores técnicos simulados:

| Columna | Símbolo | Descripción | Importancia Estratégica |
| :--- | :--- | :--- | :--- |
| **Moneda** | ₿ | Símbolo de la criptomoneda (Ej. BTC, ETH). | Identificación Rápida. |
| **Precio** | 💲 | Precio actual en USD (o la divisa seleccionada). | Valor de Mercado en Tiempo Real. |
| **24h (%) / 7d (%)** | ⏳ / 🗓️ | Variación porcentual de corto y mediano plazo. | Mide el **impulso** y la **tendencia general**. |
| **Proyección 48h** | 🔮 | **ESTIMACIÓN** del precio en 48 horas. | Ayuda a visualizar el potencial de **ganancia a corto plazo**. |
| **Análisis Técnico** | 🧠 | Resumen del sentimiento (*Golden Cross*, *Sobrecompra*). | Simula la interpretación de **MA y RSI**. |
| **Alerta** | 🚨 | Señal clara de compra, venta o riesgo. | **Punto de Decisión Clave.** |
| **PLR Sugerido** | 🎯 | **Precio Límite Recomendado** (2% de descuento en DIP). | Valor exacto para ingresar como **orden de compra**. |

---

### II. Interpretación de las 7 Señales Analíticas 🧭

El script genera alertas avanzadas basadas en la lógica de inversión de NFM:

| Alerta | Símbolo | Condición | Estrategia Recomendada |
| :--- | :--- | :--- | :--- |
| **💸 ¡VENTA! (FOMO)** | 📉 | Subida fuerte (> 10%) en 24h **Y** subida fuerte en 7d (> 15%). | **Toma de Ganancias (Take Profit).** Alto riesgo de corrección. |
| **📉 ¡COMPRA! (DIP)** | 🛒 | Caída > 4.0% en 24h **Y** tendencia positiva (> 0%) en 7d. | **OPORTUNIDAD IDEAL.** La alerta activa el PLR. |
| **🔥 RIESGO/CAPITULACIÓN** | 🛑 | Caída muy fuerte (> 8.0%) en 24h **O** gran caída en 7d (<-10%). | **CAUTELA MÁXIMA.** Posible ruptura de soportes. |
| **🟢 MOMENTUM SALUDABLE** | ✅ | Crecimiento moderado (> 2%) en 24h **Y** buena subida (> 8%) en 7d. | **HOLD/ACUMULACIÓN.** Crecimiento sostenible. |
| **⚠️ CORRECCIÓN C/P** | 🟡 | Caída ligera/moderada en 24h después de fuerte subida en 7d. | **NEUTRAL.** El activo se está "enfriando". |
| **😴 RANGO/CONSOLIDACIÓN** | ⏸️ | Poca volatilidad (< 1.5%) en 24h **Y** 7d. | **LATERALIZACIÓN.** Esperar el rompimiento del rango. |
| **⚖️ ESTABLE** | 🟦 | Variación entre -1.0% y +1.0% en 24h. | Consolidación muy ajustada. |

---

### III. Estrategia de Órdenes Límite (Buy Limit) ✍️

La estrategia se basa en el **PLR Sugerido** solo cuando se activa la alerta **🛒 ¡COMPRA! (DIP)**:

1.  **Espera la Señal:** Monitorea la alerta **🛒 ¡COMPRA! (DIP)**.
2.  **Cálculo del PLR:** El precio sugerido se calcula automáticamente al **2% por debajo del precio actual de mercado** (Estrategia de Órdenes Límite).
3.  **Acción:** Coloca tu orden de Compra Límite en tu plataforma de trading (ej. Coinbase Advanced, Binance) utilizando el precio exacto de la columna **🎯 PLR Sugerido**.

### IV. Instalación y Uso Básico (Termux) 📱

* **Requisitos:** Python 3 (`pkg install python`), `tmux` (`pkg install tmux`), librerías (`pip install requests tabulate colorama`).
* **Ejecución:** Simplemente ejecuta `python price_checker.py`.
* **Automatización:** La lógica en el archivo `.zshrc` inicia automáticamente el analizador en una pantalla dividida con tu IA al iniciar la sesión.

---

## 🤝 ¿Cómo Puedes Colaborar en el Metaverso? 🧑‍💻

Buscamos desarrolladores y colaboradores para llevar este proyecto al siguiente nivel:

1.  **🔗 Integración de APIs:** Conexión directa con APIs de trading para colocar órdenes límites automáticamente.
2.  **🧠 Análisis Avanzado:** Implementación de otros indicadores técnicos avanzados (ej. Bandas de Bollinger, Ichimoku) con datos históricos.
3.  **📖 Documentación y Tutoriales:** Creación de guías más detalladas y videos tutoriales para la comunidad de **Non Fungible Metaverse**.
