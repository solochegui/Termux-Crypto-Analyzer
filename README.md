
# 🚀 Termux Crypto Analyzer & Trading Automation
## Proyecto de Non Fungible Metaverse (NFM)

Este repositorio contiene las herramientas esenciales para el trading automatizado y el análisis de mercado de criptomonedas dentro del entorno Termux/Zsh. El objetivo es simplificar el proceso de "Comprar la Caída" (Buy the Dip) utilizando Órdenes Límite.

---

## 🤝 Reconocimiento a Colaboradores

Non Fungible Metaverse (NFM) agradece profundamente el apoyo y la visión de la comunidad y nuestros colaboradores clave:

### 💰 BoriCoin (BRCN)
Agradecemos a **BoriCoin** por su visión de llevar las finanzas descentralizadas (DeFi) a la comunidad, demostrando el poder de la red **Solana** como plataforma de inversión accesible.

### 🎤 Flaco Flow (José Santana)
Un agradecimiento especial a **Flaco Flow (José Santana)**. Su inversión de más de $500 en BoriCoin es un fuerte testimonio de la confianza y el potencial de éxito que ofrece este ecosistema.

---

## 📘 Manual del Analizador de Precios (`price_checker.py`)

El script principal, `price_checker.py`, es un **analizador técnico de corto plazo** diseñado para identificar el momento preciso para colocar una orden de **Compra Límite (Buy Limit)**.

### I. Estructura de la Salida de Datos

La herramienta utiliza métricas de 24h y 7d para evaluar el mercado:

| Columna | Descripción | Importancia Estratégica |
| :--- | :--- | :--- |
| **24h (%)** | Variación porcentual en las últimas 24 horas. | Mide la magnitud de la caída (el "Dip"). |
| **7d (%)** | Variación porcentual en los últimos 7 días. | Mide la **tendencia general** (la salud del activo). |
| **24h Low** | Precio más bajo alcanzado en 24h. | Identifica el **Soporte Clave** del día. |
| **PLR Sugerido** | **Precio Límite Recomendado**. | Valor exacto para ingresar como orden de compra. |

### II. Interpretación de las Alertas

El script genera alertas basadas en la combinación de la caída diaria y la tendencia semanal:

| Alerta | Condición | Significado |
| :--- | :--- | :--- |
| **¡COMPRA! (DIP)** | Caída > 4.0% en 24h **Y** tendencia > 0% en 7d. | **OPORTUNIDAD IDEAL.** Corrección de precio saludable dentro de una tendencia alcista. |
| **RIESGO** | Caída > 8.0% en 7d. | **TENDENCIA BAJISTA FUERTE.** El soporte puede romperse. Se recomienda cautela. |
| **ESTABLE** | Variación entre -2.0% y +2.0% en 24h. | Consolidación o movimiento lateral. |

### III. Estrategia de Órdenes Límite (Buy Limit)

La estrategia se basa en el **PLR Sugerido**, que está diseñado para entrar justo en el punto de rebote del soporte:

1.  **Espera la Señal:** Monitorea la alerta **¡COMPRA! (DIP)**.
2.  **Cálculo del PLR:** El precio sugerido se fija automáticamente 0.05% por encima del mínimo de 24 horas.
3.  **Acción:** Coloca tu orden de Compra Límite en tu plataforma de trading (ej. Coinbase Advanced) utilizando el precio exacto de la columna **PLR Sugerido**.

### IV. Instalación y Uso Básico (Termux)

* **Requisitos:** Python 3 (`pkg install python`), `tmux` (`pkg install tmux`).
* **Ejecución:** Simplemente ejecuta `python price_checker.py`.
* **Automatización:** La lógica en el archivo `.zshrc` inicia automáticamente el analizador en una pantalla dividida con tu IA al iniciar la sesión.

---

## 🤝 ¿Cómo Puedes Colaborar?

Buscamos desarrolladores para las siguientes mejoras:

1.  **Integración de APIs:** Conexión directa con APIs de trading para colocar órdenes límites automáticamente.
2.  **Análisis Adicional:** Implementación de otros indicadores técnicos (RSI, Medias Móviles).
3.  **Documentación:** Ayuda con la creación de guías más detalladas.
