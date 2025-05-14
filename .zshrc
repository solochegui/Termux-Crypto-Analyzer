# Set PATH to include custom directories
export PATH=$PATH:/data/data/com.termux/files/usr/bin:/data/data/com.termux/files/usr/local/bin

# Set system-wide username and hostname
export USER="Hacking"
export LOGNAME="Hacking"
export HOSTNAME="system"

# Cyberpunk Prompt with Colors
autoload -U colors && colors
PROMPT='%F{cyan}Hacking🌐system%f:%F{green}%~%f '



# Enable auto-suggestions
if [[ -f ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh ]]; then
    source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
fi

# Configure history settings
export HISTFILE=~/.zsh_history
export HISTSIZE=10000
export SAVEHIST=10000

# Load `.bash_profile` if exists
if [[ -f ~/.bash_profile ]]; then
    source ~/.bash_profile
fi

# Personalized welcome banner with ASCII art (Single Instance)
figlet "Non Fungible Metaverse" | lolcat

# Enable color support
export LS_COLORS="di=34:ln=36:so=32:pi=33:ex=31"
export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced

# Fix terminal display issues
export TERM=xterm-256color

# Enable auto-completion
autoload -Uz compinit && compinit

# Optimized Command Execution
setopt HIST_IGNORE_DUPS       # Avoid duplicate history entries
setopt SHARE_HISTORY          # Share history between multiple sessions
setopt AUTO_CD                # Change directory without 'cd'
setopt CORRECT                # Auto-correct mistyped commands
setopt NO_CASE_GLOB           # Case-insensitive globbing
setopt EXTENDED_GLOB          # Enable extended globbing

### 🔥 **Aliases for Speed & Efficiency**
# File management
alias ll='ls -alF --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'
alias rm='rm -i'  # Protect from accidental deletions
alias cp='cp -i'
alias mv='mv -i'
alias grep='grep --color=auto'
alias df='df -h'  # Human-readable disk space
alias du='du -h'  # Human-readable disk usage

# Termux-specific
alias cls='clear'
alias reboot='termux-reboot'
alias battery='termux-battery-status'
alias storage='termux-setup-storage'

# Fun & Visual
alias matrix='cmatrix -s'  # Hacker matrix effect
alias hello="ollama run llama2-uncensored"
alias banner='figlet "Welcome Hacking System!" | lolcat'

# Networking
alias myip='curl ifconfig.me'  # Get public IP address
alias pingtest='ping -c 4 8.8.8.8'  # Test internet connectivity
alias ports='netstat -tulanp'  # List open ports

# System monitoring
alias top='htop'  # Enhanced task manager
alias usage='du -sh * | sort -h'  # Disk usage sorted by size
alias meminfo='free -h'  # Memory usage
alias cpuinfo='lscpu'  # CPU info

# Git shortcuts
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'

### 🔥 **Functions for Power Users**
# Make directory and navigate to it
mkcd() { mkdir -p "$1" && cd "$1"; }

# Extract tar files quickly
extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2) tar xjf "$1" ;;
            *.tar.gz) tar xzf "$1" ;;
            *.bz2) bunzip2 "$1" ;;
            *.rar) unrar x "$1" ;;
            *.gz) gunzip "$1" ;;
            *.tar) tar xf "$1" ;;
            *.tbz2) tar xjf "$1" ;;
            *.tgz) tar xzf "$1" ;;
            *.zip) unzip "$1" ;;
            *.Z) uncompress "$1" ;;
            *.7z) 7z x "$1" ;;
            *) echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# Check internet connectivity
checknet() { ping -c 4 8.8.8.8; }

# Create a quick backup
backup_file() { cp "$1" "$1.bak"; echo "Backup created: $1.bak"; }

# Animated hacker intro sequence
hacker_mode() {
  echo -e "\033[32mBooting up...\033[0m"
  sleep 1
  echo -e "\033[31mConnecting to the mainframe...\033[0m"
  sleep 1
  echo -e "\033[34mLoading firewall bypass scripts...\033[0m"
  sleep 1
  for i in $(seq 1 100); do echo -n "."; sleep 0.05; done
  echo -e "\n\033[35mAccess Granted! Welcome, Hacking@System.\033[0m"
}

# Search for files
findfile() { find . -name "$1"; }

# Show disk usage in a friendly format
diskusage() { df -h | grep -E 'Filesystem|/data'; }

# Start HTTP server
start_server() {
  local port=${1:-8080}
  echo "Starting HTTP server on port $port..."
  python3 -m http.server "$port"
}

# Update and upgrade Termux packages
update_termux() {
  echo "Updating Termux packages..."
  pkg update && pkg upgrade -y
}

# Kill a process by name
killproc() {
  pkill -f "$1" && echo "Process '$1' terminated."
}

# Auto-start Matrix Mode after inactivity
TMOUT=100
function TRAPALRM() { cmatrix -s; }

# Source important Zsh modules
source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh
