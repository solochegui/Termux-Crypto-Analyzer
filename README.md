🧠 ₮ɆⱤⲘɄӾ-₵ⱤɎ₱₮Ø-₳₦₳ⱠɎⱫɆⱤ: Analizador Avanzado de Precios 🌐 Crypto (CLI) 🚀
⚔️ Introducción: Trading con Estrategia NFM ⚔️
El ₮ɆⱤⲘɄӾ-₵ⱤɎ₱₮Ø-₳₦₳ⱠɎⱫɆⱤ no es solo un monitor de precios; es un ֆɨֆȶɛʍǟ ǟʊȶօʍǟȶɨʐǟɖօ de detección de oportunidades diseñado bajo la rigurosa Filosofía de Inversión 🅝🅞🅝 🅕🅤🅝🅖🅘🅑🅛🅔 🅜🅔🅣🅐🅥🅔🅡🅢🅔 (NFM). Escrito en Python 🐍, esta herramienta CLI (Command Line Interface) es perfecta para ser ejecutada 24/7 en plataformas móviles como Termux (Android/iOS), proporcionando 🅸🅽🆃🅴🅻🅸🅶🅴🅽🅲🅸🅰 🅳🅴 🅼🅴🆁🅲🅰🅳🅾 en tiempo real directamente a tu dispositivo.
Este analizador te permite:
 * 👁️ Monitorear un portafolio de criptomonedas predefinido (incluyendo BoriCoin).
 * ✨ Aplicar una avanzada lógica de 12 puntos para clasificar el estado de tendencia y riesgo.
 * 🔔 Generar alertas de trading altamente específicas y descriptivas a través de Telegram.
 * 🤖 Automatizar órdenes de compra (de mercado) en Coinbase al detectar una señal de DIP.
✨ Filosofía de Inversión NFM: Caza del DIP y Ciclo de Mercado 🌑
Nuestra estrategia se basa en evitar el F.O.M.O (Fear Of Missing Out) y capitalizar el miedo y la corrección (DIP). El éxito en criptomonedas no reside en comprar en la euforia, sino en la Acumulación Estratégica en fases de corrección y pánico. El analizador evalúa dos métricas clave de momentum para determinar la fase del ciclo de mercado de cada activo:
 * Change (24h) 🕐: Indicador de volatilidad y momentum a ₵ØⱤ₮Ø ₱Ⱡ₳ⱫØ.
 * Change (7d) 🗓️: Indicador de la Salud de la Tendencia subyacente.
La combinación permite diferenciar entre un Pullback Saludable (señal de ✅ COMPRA! DIP) y una simple subida sin soporte (⚠️ BULL TRAP).
🎯 ᏝóᎶᎥፈᏗ Ꮛ⚔️TᏋᏁᎴᎥᎴᏗ: Las ①② Señales de Trading ⚡
La Lógica de 12 Puntos es el núcleo del sistema, proporcionando un mapa detallado del estado emocional y técnico de cada criptomoneda.
| Señal | Condición Clave | Descripción y Acción Estratégica |
|---|---|---|
|
|---|---|---|---|
| ✅ COMPRA! DIP | \Delta 24h < -4\% y \Delta 7d > 0\% | Corrección de la Tendencia | ORDEN LÍMITE (PLR) - Entrada óptima. |
| 📈 REVERSIÓN V/B | \Delta 24h > 4\% y \Delta 7d < -5\% | Fuerza de Rebote | COMPRA FUERTE - Capitalizar cambio de dirección. |
| 💎 ACUMULACIÓN L/P | \Delta 7d < -15\% y \Delta 24h Estrecho | Fin de Pánico | COMPRA LT - Acumulación en la base. |
| 🚀 RUPTURA ALCISTA | \Delta 24h > 5\% y \Delta 7d > 3\% | Momentum de Continuación | COMPRA - Seguir el impulso de la ruptura. |
| 🚨 ALERTA ROJA | \Delta 24h > 15\% o Euforia Extrema | Sobrecompra/Euforia | VENTA / TOMA DE GANANCIAS |
| ⚠️ BULL TRAP | \Delta 24h > 6\% y \Delta 7d < 0\% | Subida sin Soporte | VENTA / Alto Riesgo C/P - Posible Distribución. |
| 💀 CAPITULACIÓN | \Delta 24h < -10\% y \Delta 7d < -20\% | Pánico Máximo | COMPRA DE RIESGO - Entrada contraria a la masa. |
| 📉 AGOTAMIENTO | \Delta 24h < -2.5\% tras \Delta 7d > 20\% | Advertencia de Giro | TOMA DE GANANCIAS - Asegurar beneficios. |
| 🟢 MOMENTUM SALUDABLE | \Delta 24h > 1.5\% y \Delta 7d > 5\% | Crecimiento Sostenible | HOLD - Mantener la posición. |
| 😴 RANGO ESTRECHO | Volatilidad muy baja y \Delta 7d lateral | Consolidación | HOLD / NEUTRAL - Paciencia. |
| ⚖️ ESTABLE | \Delta 24h cerca de 0\% | Baja Volatilidad | NEUTRAL - Sin señal fuerte. |
| ❓ TENDENCIA INDEFINIDA | Ninguna de las anteriores | Incertidumbre | OBSERVAR - Esperar confirmación. |
🛠️ Tabla de Configuración de Variables de Entorno (Termux/NFM)
Esta tabla resume las variables necesarias para la correcta funcionalidad de las notificaciones de Telegram y la automatización de órdenes de Coinbase.
| Componente | Variable de Entorno | Función y Descripción |
|---|---|---|🛠️
Para ejecutar el analizador en tu entorno, necesitas las siguientes dependencias:
 * Python 3.8+ 🐍
 * Librerías Python: requests (para CoinGecko API) y coinbase (para automatización).
   pip install requests coinbase

 * Entorno Termux: Si usas Termux, asegura Python instalado con:
   pkg install python

🛠️ 🅲🅾🅽🅵🅸🅶🆄🆁🅰🅲🅸ó🅽 🅰🆅🅰🅽🆉🅰🅳🅰 y $ecuridad 🔒
El script utiliza 🆅🅰🆁🅸🅰🅱🅻🅴🆂 🅳🅴 🅴🅽🆃🅾🆁🅽🅾 para manejar las credenciales de forma segura.
1. 📧 ₮ɆⱠɆ₲Ɽ₳Ⲙ (Notificaciones Enriquecidas)
Las alertas de COMPRA (DIP) están optimizadas con formatos HTML, incluyendo: Análisis Descriptivo, Sugerencia Precisa y tu Enlace de Referido de Coinbase.
| Variable | Descripción |
|---|---|
| TELEGRAM_BOT_TOKEN | Token de acceso único de tu Bot, obtenido de BotFather. |
| TELEGRAM_CHAT_ID | ID numérico del chat o grupo al que el bot enviará las alertas. |
2. 🪙 ₵Øł₦฿₳₴Ɇ (Automatización de Órdenes y Referido)
El script puede ejecutar órdenes reales en tu cuenta de Coinbase. Se requiere 🅿🆁🅴🅲🅰🆄🅲🅸ó🅽 🅴🆇🆃🆁🅴🅼🅰.
| Variable | Descripción |
|---|---|
| COINBASE_API_KEY | Clave API de Coinbase (permisos: wallet:buys y wallet:accounts:read). |
| COINBASE_API_SECRET | Secreto API asociado a tu clave. |
> ⚠️ NOTA CRÍTICA SOBRE LA AUTOMATIZACIÓN:
> La automatización actual utiliza la API de Wallet para forzar una ØⱤĐɆ₦ ĐɆ ⲘɆⱤ₵₳ĐØ por un monto fijo de $10.00 USD al detectar el DIP. Esto no es una orden limitada real y el precio de ejecución será el precio actual. Utiliza esta función bajo tu propia responsabilidad, entendiendo el riesgo de deslizamiento.
> 
💰 Link de Referido Coinbase (Afiliado NFM)
El mensaje de Telegram incluye un llamado a la acción para que tus seguidores se registren:
> Regístrate en Coinbase con mi enlace y ambos ganaremos 💰 10 USD en BTC:
> https://coinbase.com/join/QHMF3XN?src=android-share
> 
💡 Cómo establecer las variables en Termux 📲
Para hacer que estas variables persistan y sean accesibles al script, edita tu archivo de perfil de shell (.bashrc o .zshrc):
nano ~/.bashrc

Añade las siguientes líneas, reemplazando los valores genéricos:
# Variables de Coinbase (Automatización de Trading)
export COINBASE_API_KEY="tu_clave_aqui"
export COINBASE_API_SECRET="tu_secreto_aqui"

# Variables de Telegram (Alertas)
export TELEGRAM_BOT_TOKEN="tu_token_bot_aqui"
export TELEGRAM_CHAT_ID="tu_chat_id_aqui"

Guarda el archivo y aplica los cambios:
source ~/.bashrc
