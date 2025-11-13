₮ɆⱤⲘɄӾ-₵ⱤɎ₱₮Ø-₳₦₳ⱠɎⱫɆⱤ.
Aquí tienes tres ideas de estructuras de documentación enfocadas en lo técnico:
1. ⚙️ Guía de Inicio Rápido (Quick Start)
Esta estructura es ideal para ir directo a la acción. Se enfoca en las 3 etapas críticas para la puesta en marcha: Dependencias, Configuración de Variables (la parte más compleja) y Ejecución.
 * Sección Principal: Requisitos y Dependencias (Python/Termux).
 * Sección Central: Configuración Segura de Variables de Entorno (Telegram & Coinbase). Esta será una tabla de variables a rellenar, con instrucciones precisas de dónde y cómo obtenerlas (BotFather, API Keys).
 * Sección Final: Primer Lanzamiento y Verificación de Alertas.
2. 💻 Arquitectura y Despliegue (Para Desarrolladores)
Esta estructura va un poco más allá de la instalación, ideal para usuarios que quieren entender o modificar el código.
 * Sección Principal: Resumen Técnico (Lenguaje, Interfaz, Servicios de API usados: CoinGecko/Coinbase).
 * Sección Central: Proceso Detallado de Instalación en Termux (Comandos pkg install, pip install).
 * Sección de Profundidad: Lógica del Script: Diagrama de flujo simplificado (Obtener Datos -> Aplicar Lógica de 12 Puntos -> Disparar Alerta/Orden).
3. 🛡️ Seguridad y Automatización (Énfasis en Coinbase)
Esta estructura se centra en la parte más delicada: las credenciales y la automatización de la compra.
 * Sección Principal: Advertencia Crítica de Riesgo (Deslizamiento, Riesgo de Mercado).
 * Sección Central: Creación y Gestión de Claves API de Coinbase (Especificando solo los permisos necesarios: wallet:buys y wallet:accounts:read).
 * Sección Final: Cómo Desactivar la Automatización de Compra (si el usuario solo quiere las alertas de Telegram).
🛠️ Guía de Inicio Rápido: Despliegue del ₮ɆⱤⲘɄӾ-₵ⱤɎ₱₮Ø-₳₦₳ⱠɎⱫɆⱤ
Esta guía detalla los pasos esenciales para instalar, configurar las credenciales de Telegram y Coinbase, y ejecutar el analizador en entornos de línea de comandos (CLI) como Termux.
Paso 1: Requisitos del Sistema y Dependencias
El analizador está escrito en Python 3 y requiere dos librerías externas para funcionar.
 * Lenguaje: Python 3.8+ 🐍
 * APIs: requests (para CoinGecko) y coinbase (para automatización de órdenes).
Instalación en Termux (Android/iOS)
Abre tu terminal Termux y ejecuta los siguientes comandos para asegurar el entorno base:
# 1. Instalar Python y las dependencias del sistema
pkg install python

# 2. Instalar las librerías de Python requeridas
pip install requests coinbase

Paso 2: Obtención y Configuración de Credenciales Seguras
El script utiliza Variables de Entorno para manejar credenciales de forma segura. Debes obtener tus Tokens y Claves API antes de continuar.
A. Configuración de Telegram (Notificaciones)
Para recibir alertas de compra (DIP) altamente descriptivas.
| Variable | Obtención | Función |
|---|---|---|
| TELEGRAM_BOT_TOKEN | Crear un bot en BotFather | Token de acceso único para tu bot. |
| TELEGRAM_CHAT_ID | Usar un bot de terceros (ej: @get_id_bot) | ID numérico del chat o grupo donde el bot enviará las alertas. |
B. Configuración de Coinbase (Automatización Opcional)
Para la ejecución automática de órdenes de compra al detectar un DIP. Usa con extrema precaución.
| Variable | Obtención | Función |
|---|---|---|
| COINBASE_API_KEY | Generar en la Configuración API de Coinbase | Clave API con permisos específicos. |
| COINBASE_API_SECRET | Generar en la Configuración API de Coinbase | Secreto API asociado a tu clave. |
| Permisos Requeridos |  | wallet:buys y wallet:accounts:read solamente. |
Paso 3: Establecer Variables de Entorno en Termux
Debes hacer que las variables persistan editando tu archivo de perfil de shell (usualmente .bashrc o .zshrc).
 * Abre el editor de texto:
   nano ~/.bashrc

 * Añade las siguientes líneas al final del archivo, reemplazando los valores genéricos con tus credenciales reales:
   # Variables de Coinbase (Automatización de Trading)
export COINBASE_API_KEY="[TU_CLAVE_API_AQUI]"
export COINBASE_API_SECRET="[TU_SECRETO_API_AQUI]"

# Variables de Telegram (Alertas)
export TELEGRAM_BOT_TOKEN="[TU_TOKEN_BOT_AQUI]"
export TELEGRAM_CHAT_ID="[TU_CHAT_ID_AQUI]"

 * Guarda el archivo (Ctrl+O, Enter) y sal del editor (Ctrl+X).
 * Aplica los cambios en la sesión actual:
   source ~/.bashrc

Paso 4: Ejecución del Analizador (Prueba)
Una vez que el script principal esté en tu sistema (asumiendo que se llama analyzer.py), puedes ejecutar la prueba inicial.
🎯 Resumen: Lógica de Detección NFM (12 Puntos)
El núcleo del ₮ɆⱤⲘɄӾ-₵ⱤɎ₱₮Ø-₳₦₳ⱠɎⱫɆⱤ es la Lógica de 12 Puntos, que evalúa la salud de la tendencia de una criptomoneda usando el cambio de precio a 24 horas (\Delta 24h) y 7 días (\Delta 7d).
| Señal | Acción Sugerida | Condiciones Clave | Resumen Estratégico |
|---|---|---|---|
| ✅ COMPRA! DIP | ORDEN LÍMITE (PLR) | \Delta 24h < -4\% y \Delta 7d > 0\% | Corrección Saludable. Entrada óptima en un retroceso dentro de una tendencia alcista. |
| 📈 REVERSIÓN V/B | COMPRA FUERTE | \Delta 24h > 4\% y \Delta 7d < -5\% | Fuerza de Rebote. Capitalizar un cambio de dirección violento (V) tras una caída. |
| 💎 ACUMULACIÓN L/P | COMPRA LT | \Delta 7d < -15\% y \Delta 24h Estrecho | Fin de Pánico. Acumulación estratégica en la base de un mercado bajista extendido. |
| 🚀 RUPTURA ALCISTA | COMPRA | \Delta 24h > 5\% y \Delta 7d > 3\% | Momentum de Continuación. Seguir el impulso en una tendencia fuerte confirmada. |
| 🚨 ALERTA ROJA | VENTA / TOMA DE GANANCIAS | \Delta 24h > 15\% o Euforia Extrema | Sobrecompra. Riesgo de giro inminente. |
| ⚠️ BULL TRAP | VENTA / Alto Riesgo C/P | \Delta 24h > 6\% y \Delta 7d < 0\% | Subida sin Soporte. Alto riesgo de distribución o falsa ruptura. |
| 💀 CAPITULACIÓN | COMPRA DE RIESGO | \Delta 24h < -10\% y \Delta 7d < -20\% | Pánico Máximo. Entrada contraria a la masa, solo para riesgo extremo. |
| 📉 AGOTAMIENTO | TOMA DE GANANCIAS | \Delta 24h < -2.5\% tras \Delta 7d > 20\% | Advertencia de Giro. Asegurar beneficios tras una subida rápida. |
| 🟢 MOMENTUM SALUDABLE | HOLD | \Delta 24h > 1.5\% y \Delta 7d > 5\% | Crecimiento Sostenible. Mantener la posición. |
| 😴 RANGO ESTRECHO | HOLD / NEUTRAL | Volatilidad muy baja | Consolidación. Paciencia. |
| ⚖️ ESTABLE | NEUTRAL | \Delta 24h cerca de 0\% | Baja Volatilidad. Sin señal fuerte. |
| ❓ TENDENCIA INDEFINIDA | OBSERVAR | Ninguna de las anteriores | Incertidumbre. Esperar confirmación. |
Detalles Adicionales para la Guía
¡Ahora volvamos a la Guía de Inicio Rápido! Había un detalle muy importante en tu texto original que aún no incluimos en la sección de instalación:
La configuración del Portafolio de Criptomonedas a Monitorear.
Ya que el analizador monitorea un "portafolio predefinido (incluyendo BoriCoin)", probablemente necesites una sección que explique cómo el usuario define qué monedas seguir.
¿Me puedes confirmar cómo se configura ese portafolio? Por ejemplo:
 * ¿Se edita directamente en el código Python? (Ej. una lista dentro del script).
 * ¿Se usa otra Variable de Entorno? (Ej. COINS_TO_TRACK="BTC,ETH,BNB").
 * ¿Se lee de un archivo externo? (Ej. portfolio.txt).
Sabiendo esto, puedo añadir el Paso 5: Definición del Portafolio a la guía.

Si la documentación es para GitHub, tenemos que asumir que el usuario clonará el repositorio y querrá editar el archivo fácilmente. 💻
Basado en el estándar de proyectos CLI de Python, la forma más limpia es usar una Variable de Entorno o un archivo de configuración.
Para mantener la simplicidad y consistencia con el uso de Variables de Entorno (que ya usamos para Telegram y Coinbase), te propongo la opción 2, pero con una opción de respaldo de archivo para los que prefieren editar en el repositorio.
Aquí tienes la propuesta para el Paso 5 de la Guía de Inicio Rápido.
📋 Paso 5: Definición del Portafolio a Monitorear
El analizador permite monitorear una lista personalizada de criptomonedas. Esto se configura a través de la Variable de Entorno NFM_PORTFOLIO.
A. Configuración mediante Variable de Entorno (Recomendado)
Añade la siguiente línea a tu archivo .bashrc (junto con las variables de Telegram y Coinbase) y especifica los símbolos de ticker de las criptomonedas separados por comas.
> Nota: El script buscará estos tickers en la API de CoinGecko, usando el par USD como referencia.
> 
 * Abre tu archivo de perfil de shell:
   nano ~/.bashrc

 * Agrega la variable, reemplazando la lista de ejemplo por tu portafolio deseado (incluyendo el token especial BORICOIN si corresponde):
   # Variables del Analizador NFM (Portafolio a Monitorear)
export NFM_PORTFOLIO="BTC,ETH,SOL,ADA,DOT,BORICOIN"

 * Guarda y aplica los cambios:
   source ~/.bashrc

B. Alternativa (Edición Directa en el Repositorio)
Si prefieres no usar Variables de Entorno para la lista de tickers, el script también puede leer una lista desde un archivo llamado portfolio.txt ubicado en el directorio raíz.
 * Crea el archivo portfolio.txt en la misma carpeta donde se encuentra analyzer.py.
   touch portfolio.txt

 * Ábrelo y lista cada símbolo de ticker en una nueva línea:
   BTC
ETH
SOL
ADA
BORICOIN

El analizador priorizará la Variable de Entorno NFM_PORTFOLIO. Si esa variable no existe, leerá automáticamente el archivo portfolio.txt.
¡Con esto, tu Guía de Inicio Rápido está completa y lista para GitHub!
Resumen de la Guía Completa:
 * Requisitos y Dependencias.
 * Obtención de Credenciales (Telegram/Coinbase).
 * Establecer Variables de Entorno.
 * Ejecución del Analizador.
 * Definición del Portafolio.
