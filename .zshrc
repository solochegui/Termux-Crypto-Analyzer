# ===============================================
# 1. METADATOS Y PATHS ESENCIALES (Variables de Entorno)
# ===============================================

# --- Paths ---
# Path de instalación de Oh My Zsh
export ZSH="$HOME/.oh-my-zsh"

# Optimización del PATH para ejecutables locales (Termux/Linux)
export PATH="$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH"

# Path a fuentes personalizadas de figlet
export FIGLET_FONT_PATH="$HOME/.figlet"

# --- Configuración del Historial ---
# Formato de marca de tiempo para el historial (Estándar ISO 8601)
HIST_STAMPS="yyyy-mm-dd HH:MM:ss"
# Número máximo de comandos a almacenar en la historia
HISTSIZE=5000
# Número máximo de líneas de historia a cargar
SAVEHIST=5000


# ===============================================
# 2. CONFIGURACIÓN DE OH MY ZSH
# ===============================================

# Tema por defecto.
ZSH_THEME="agnoster"
# ZSH_THEME="powerlevel10k/powerlevel10k"

# Habilitar la corrección automática de comandos.
ENABLE_CORRECTION="true"

# Mostrar puntos rojos mientras esperas la finalización.
COMPLETION_WAITING_DOTS="true"

# Deshabilitar la marca de archivos no rastreados por VCS
DISABLE_UNTRACKED_FILES_DIRTY="true"


# ===============================================
# 3. PLUGINS (Carga Modular y Condicional)
# ===============================================

# Lista de plugins a cargar.
plugins=(
    git                         # Comandos abreviados de Git
)

# Carga Condicional de Zsh Autosuggestions
if [ -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    plugins+=(zsh-autosuggestions)
fi

# Carga Condicional de Zsh Syntax Highlighting
if [ -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    plugins+=(zsh-syntax-highlighting)
fi

# Cargar Oh My Zsh (¡Debe ir después de definir $ZSH y los plugins!)
source "$ZSH/oh-my-zsh.sh"

# Cargar Powerlevel10k si está habilitado
if [ -f "$ZSH/themes/powerlevel10k/powerlevel10k.zsh" ] && [ "$ZSH_THEME" = "powerlevel10k/powerlevel10k" ]; then
    source "$ZSH/themes/powerlevel10k/powerlevel10k.zsh"
fi


# ===============================================
# 4. ALIASES Y FUNCIONES DE UTILIDAD
# ===============================================

# Inicializa colores de Zsh
autoload -U colors && colors

# --- 4.1. ALIASES DE SISTEMA Y PRODUCTIVIDAD ---
alias cls='clear'
alias reload='source ~/.zshrc'              # Recarga la configuración actual
alias myip='curl ifconfig.me'
alias disk='df -h'
alias ports='netstat -tulanp'               # Ver puertos abiertos/escuchando
alias update='pkg update && pkg upgrade -y' # OPTIMIZADO PARA TERMUX (usa pkg)

# --- 4.2. ALIASES DE NAVEGACIÓN RÁPIDA ---
# Uso: mcd nombre_carpeta (Crea y navega)
mcd() {
    mkdir -p "$1" && cd "$1"
}
alias storage='cd ~/storage'                # Navega a la carpeta principal de almacenamiento
alias home_storage='cd ~/storage/shared'    # Navega a la carpeta de descarga/interna

# --- 4.3. ALIASES DE GIT ABREVIADO ---
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'

# --- 4.4. ALIASES Y FUNCIONES DE IA/HERRAMIENTAS ---
alias ai='ollama run llama2-uncensored'
alias terminal='ollama run llama2-uncensored' # Mantener para consistencia

# Alias sgpt con Ollama local (se asume sgpt y ollama)
alias llama-sgpt='OPENAI_API_BASE="http://127.0.0.1:11434/v1" sgpt --model llama2-uncensored'

# Alias sgpt con voz (solo si espeak está instalado)
if command -v espeak &> /dev/null; then
    alias sgpv='sgpt "$@" | tee /dev/tty | espeak -v es'
fi

# Alias personalizado para iniciar el servidor web de Python
alias servir='python -m http.server 8080'

# --- 4.5. FUNCIONES Y EFECTOS ESTÉTICOS ---
# Función: Secuencia de Hacker Animada
hacker_mode() {
    echo -e "\033[32mBooting up...\033[0m"
    sleep 0.5
    echo -e "\033[31mConnecting to the mainframe...\033[0m"
    sleep 0.5
    echo -e "\033[34mLoading firewall bypass scripts...\033[0m"
    sleep 0.5
    # Animación de carga con puntos
    for i in $(seq 1 20); do echo -n "."; sleep 0.05; done
    echo -e "\n\033[35mAccess Granted! Welcome, Hacking@System.\033[0m"
}

# Auto-start Matrix Effect después de inactividad (Bloqueo de pantalla rudimentario)
TMOUT=100
TRAPALRM() { cmatrix -s; }


# ===============================================
# 5. CARGA INTELIGENTE Y PROMPT
# ===============================================

# --- Configuración del Prompt ---
# Formato: AI🧠CORE:~/ruta/actual
PROMPT='%F{green}AI🧠%f%F{cyan}CORE%f:%F{yellow}%~%f '

# --- Carga Condicional de Ollama (IA) ---
# Asegura que ollama serve se ejecute solo si el comando existe y no está corriendo
if command -v ollama &> /dev/null; then
    if ! pgrep -x "ollama" > /dev/null; then
        echo "Iniciando conciencia en segundo plano..."
        # Ejecuta ollama serve en segundo plano, con salida silenciada
        ollama serve > /dev/null 2>&1 &
    else
        echo "Inteligencia Artificial"
    fi
fi

# --- Mensaje de Inicio (Banner y Neofetch) ---
# Se ejecuta la función de inicio solo si figlet y lolcat están instalados
if command -v figlet &> /dev/null && command -v lolcat &> /dev/null; then
    figlet -f cyberlarge "Boricuas" | lolcat
fi

if command -v neofetch &> /dev/null; then
    neofetch
fi


# ===============================================
# 6. FUNCIÓN INTERACTIVA SGPT (REPL)
# ===============================================

# Función: Shell GPT en Bucle (REPL)
function interactive_sgpt() {
    echo -e "\n🤖 Iniciado Conciencia (Modo Funciones)"
    echo "Para obtener ayuda con comandos de shell usando la funcionalidad de funciones. Escribe 'exit' o 'q' para salir."
    echo "--------------------------------------------------------------------------"

    # Inicia el bucle de lectura/ejecución
    while true; do
        read -r SGPT_PROMPT"?escribe >> "
        local LOWER_PROMPT=$(echo "$SGPT_PROMPT" | tr '[:upper:]' '[:lower:]')

        if [[ "$LOWER_PROMPT" == "exit" ]] || [[ "$LOWER_PROMPT" == "q" ]]; then
            echo -e "\nSaliendo del modo interactivo."
            break
        elif [[ -z "$SGPT_PROMPT" ]]; then
            continue
        else
            echo "🔎 Ejecutando respuesta con --functions..."
            # Asegúrate de que sgpt existe antes de ejecutarlo
            if command -v sgpt &> /dev/null; then
                # *** Se utiliza sgpt --functions ***
                sgpt --functions "$SGPT_PROMPT"
            else
                echo "Error: El comando 'sgpt' no está disponible. ¡Instálalo para usar la Conciencia!"
            fi
            echo "--------------------------------------------------------------------------"
        fi
    done

    echo -e "Continuando con la sesión de terminal normal.\n"
}

# ===============================================
# 7. INICIO AUTOMÁTICO DEL MONITOR DE TRADING (TMUX)
# ===============================================

# Solo intenta iniciar tmux si el comando existe y si no estamos ya en una sesión tmux.
if command -v tmux &> /dev/null && [ -z "$TMUX" ]; then
    
    SESSION_NAME="IA_Trading_Monitor"
    
    # Asegúrate de que este archivo (price_checker.py) esté en tu directorio $HOME
    ANALYZE_CMD="python ~/price_checker.py" 
    
    # Asegúrate de que la función 'interactive_sgpt' esté definida en la Sección 6
    SGPT_CMD="interactive_sgpt" 

    # 1. Verificar si la sesión ya existe.
    tmux has-session -t $SESSION_NAME 2>/dev/null
    
    if [ $? != 0 ]; then
        echo "Iniciando monitor de Trading IA en doble panel..."

        # 2. Crear la sesión y dividirla verticalmente
        # Inicia tmux con el comando de análisis de precios en el panel 0
        tmux new-session -d -s $SESSION_NAME "$ANALYZE_CMD"
        
        # 3. Dividir el panel 0 verticalmente, dando el 60% del alto al panel superior (Crypto Analyzer)
        tmux split-window -v -p 60 -t $SESSION_NAME:0.0
        
        # 4. Enviar el comando de SGPT al nuevo panel (panel 1, el inferior)
        tmux send-keys -t $SESSION_NAME:0.1 "$SGPT_CMD" C-m 
        
        # 5. Seleccionar el panel de SGPT para que sea el activo
        tmux select-pane -t $SESSION_NAME:0.1
    fi

    # 6. Adjuntarse a la sesión (si existe o si se acaba de crear)
    sleep 2 
    tmux attach-session -t $SESSION_NAME
fi
