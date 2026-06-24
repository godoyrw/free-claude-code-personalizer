#!/bin/bash

# fcc-personalizer.sh
# Instala tema, idioma, systemd template e aliases para Free Claude Code

set -euo pipefail

# ------------------- CONFIGURAÇÕES -------------------

DEST_DIR="/home/godoy/.local/share/uv/tools/free-claude-code/lib/python3.14/site-packages/api/admin_static"
SERVICE_DIR="/etc/systemd/system"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="fcc@.service"
SERVICE_PATH="$SERVICE_DIR/$SERVICE_NAME"
SOURCE_SERVICE="$PROJECT_DIR/service/$SERVICE_NAME"
ALIASES_FILE="$PROJECT_DIR/service/fcc.aliases.sh"
BASHRC="$HOME/.bashrc"

# ------------------- FUNÇÕES -------------------

error() {
    echo "❌ Erro: $*" >&2
    exit 1
}

warning() {
    echo "⚠️ $*"
}

success() {
    echo "✅ $*"
}

# ------------------- UNINSTALL -------------------

if [[ "${1:-}" == "--uninstall" ]]; then
    echo "🗑️ Removendo FCC Personalizer..."

    TARGET_USER="${SUDO_USER:-$USER}"

    echo "🧹 Limpando instância systemd..."

    sudo systemctl stop "fcc@$TARGET_USER" 2>/dev/null || true
    sudo systemctl disable "fcc@$TARGET_USER" 2>/dev/null || true

    if [[ -f "/etc/systemd/system/fcc@.service" ]]; then
        sudo rm -f /etc/systemd/system/fcc@.service
        success "Template systemd removido"
    fi

    if [[ -d "/etc/systemd/system/fcc@.service.d" ]]; then
        sudo rm -rf /etc/systemd/system/fcc@.service.d
        success "Overrides systemd removidos"
    fi

    sudo systemctl daemon-reload
    sudo systemctl reset-failed || true

    # aliases
    if grep -q "Free Claude Code aliases" "$BASHRC"; then
        sed -i '/# Free Claude Code aliases - Installed/,/# Fim dos aliases do Free Claude Code/d' "$BASHRC"
        success "Aliases removidos do bashrc"
    fi

    if [[ -f /etc/bash.bashrc.d/fcc-aliases ]]; then
        sudo rm -f /etc/bash.bashrc.d/fcc-aliases
        success "Aliases system-wide removidos"
    fi

    # THEME + LANG RESTORE (sem pergunta)
    DEFAULT_THEME_SRC="$PROJECT_DIR/themes/default/admin.css"
    if [[ -f "$DEFAULT_THEME_SRC" ]]; then
        echo "♻️ Restaurando tema padrão..."
        sudo cp -f "$DEFAULT_THEME_SRC" "$DEST_DIR/admin.css"
        success "Tema padrão restaurado"
    else
        warning "Tema default não encontrado em $DEFAULT_THEME_SRC"
    fi

    DEFAULT_LANG_SRC="$PROJECT_DIR/lang/static/default"
    if [[ -d "$DEFAULT_LANG_SRC" ]]; then
        echo "♻️ Restaurando idioma padrão..."
        for f in "$DEFAULT_LANG_SRC"/*; do
            [[ -f "$f" ]] && sudo cp -f "$f" "$DEST_DIR/$(basename "$f")"
        done
        success "Idioma padrão restaurado"
    else
        warning "Idioma default não encontrado em $DEFAULT_LANG_SRC"
    fi

    # Remove proxy files
    echo "🧹 Removendo arquivos do proxy..."
    sudo rm -f "/home/${TARGET_USER}/.fcc/fcc_proxy.py"
    sudo rm -rf "/home/${TARGET_USER}/.fcc/locales"
    # Remove proxy service
    echo "🧹 Removendo serviço do proxy..."
    sudo systemctl stop "fcc-proxy@${TARGET_USER}" 2>/dev/null || true
    sudo systemctl disable "fcc-proxy@${TARGET_USER}" 2>/dev/null || true
    sudo rm -f "/etc/systemd/system/fcc-proxy@.service"
    sudo systemctl daemon-reload
    sudo systemctl reset-failed || true
    success "Uninstall concluído"
    exit 0
fi

# ------------------- INÍCIO -------------------

echo "🎨 Free Claude Code Personalizer"
echo "=================================="

[[ -d "$DEST_DIR" ]] || error "DEST_DIR não existe: $DEST_DIR"

# ------------------- TEMA -------------------

echo ""
echo "🎨 Seleção de tema:"

theme_options=()
for theme_dir in "$PROJECT_DIR"/themes/*/; do
    [[ -d "$theme_dir" ]] && theme_options+=("$(basename "$theme_dir")")
done

[[ ${#theme_options[@]} -gt 0 ]] || error "Nenhum tema encontrado"

select theme in "${theme_options[@]}"; do
    [[ -n "${theme:-}" ]] && break
done

THEME_SRC="$PROJECT_DIR/themes/$theme/admin.css"
[[ -f "$THEME_SRC" ]] || error "admin.css não encontrado no tema"

echo "📦 Instalando tema..."
sudo cp -f "$THEME_SRC" "$DEST_DIR/admin.css"
success "Tema '$theme' instalado"

# ------------------- IDIOMA -------------------

echo ""
echo "🌐 Seleção de idioma:"

lang_options=()
for lang_dir in "$PROJECT_DIR"/lang/static/*/; do
    [[ -d "$lang_dir" ]] && lang_options+=("$(basename "$lang_dir")")
done

if [[ ${#lang_options[@]} -eq 0 ]]; then
    warning "Nenhum idioma encontrado em lang/static/ — ignorando seleção de idioma"
else
    select lang in "${lang_options[@]}"; do
        [[ -n "${lang:-}" ]] && break
    done

    LANG_SRC="$PROJECT_DIR/lang/static/$lang"
    [[ -d "$LANG_SRC" ]] || error "Pasta de idioma não encontrada: $LANG_SRC"

    echo "📦 Instalando idioma '$lang'..."
    for f in "$LANG_SRC"/*; do
        if [[ -f "$f" ]]; then
            sudo cp -f "$f" "$DEST_DIR/$(basename "$f")"
            success "  $(basename "$f") copiado"
        fi
    done
    success "Idioma '$lang' instalado"
fi

echo ""
echo "🔧 Instalando proxy..."
# Ensure TARGET_USER is set (for when this block runs before the systemd section)
: "${TARGET_USER:=${SUDO_USER:-$USER}}"

# Copy fcc_proxy.py
PROXY_SRC="$PROJECT_DIR/lang/fcc_proxy.py"
PROXY_DEST="/home/${TARGET_USER}/.fcc/fcc_proxy.py"
mkdir -p "/home/${TARGET_USER}/.fcc"
sudo cp -f "$PROXY_SRC" "$PROXY_DEST"

# Copy locales
LOCALES_SRC="$PROJECT_DIR/lang/dynamic/locales"
LOCALES_DEST="/home/${TARGET_USER}/.fcc/locales"
sudo rm -rf "$LOCALES_DEST"
sudo cp -r "$LOCALES_SRC" "$LOCALES_DEST"

# Install service
PROXY_SERVICE_NAME="fcc-proxy@.service"
PROXY_SERVICE_DIR="/etc/systemd/system"
PROXY_SERVICE_PATH="$PROXY_SERVICE_DIR/$PROXY_SERVICE_NAME"
PROXY_SOURCE_SERVICE="$PROJECT_DIR/service/$PROXY_SERVICE_NAME"

echo "📦 Instalando template do proxy..."
sudo cp -f "$PROXY_SOURCE_SERVICE" "$PROXY_SERVICE_PATH"

echo "🔄 systemd daemon-reload..."
sudo systemctl daemon-reload
TARGET_USER="${SUDO_USER:-$USER}"

echo "🚀 Ativando instância do proxy: $TARGET_USER"
sudo systemctl stop "fcc-proxy@$TARGET_USER" 2>/dev/null || true
sudo systemctl disable "fcc-proxy@$TARGET_USER" 2>/dev/null || true
sudo systemctl enable "fcc-proxy@$TARGET_USER"
sudo systemctl start "fcc-proxy@$TARGET_USER"
sleep 1
echo "🔎 Validando serviço do proxy..."
if systemctl is-active --quiet "fcc-proxy@$TARGET_USER"; then
    success "fcc-proxy@$TARGET_USER ativo e saudável"
else
    echo "❌ Falha ao iniciar serviço do proxy"
    sudo systemctl status "fcc-proxy@$TARGET_USER" --no-pager || true
    sudo journalctl -u "fcc-proxy@$TARGET_USER" --no-pager -n 50 || true
    exit 1
fi

# ------------------- SYSTEMD TEMPLATE -------------------

echo ""
echo "⚙️ Instalando systemd template (fcc@.service)..."

[[ -f "$SOURCE_SERVICE" ]] || error "fcc@.service não encontrado em $SOURCE_SERVICE"

echo "📦 Instalando template..."
sudo cp -f "$SOURCE_SERVICE" "$SERVICE_PATH"

echo "🔄 systemd daemon-reload..."
sudo systemctl daemon-reload

TARGET_USER="${SUDO_USER:-$USER}"
echo "🚀 Ativando instância: $TARGET_USER"

sudo systemctl stop "fcc@$TARGET_USER" 2>/dev/null || true
sudo systemctl disable "fcc@$TARGET_USER" 2>/dev/null || true
sudo systemctl enable "fcc@$TARGET_USER"
sudo systemctl start "fcc@$TARGET_USER"

sleep 1

echo "🔎 Validando serviço..."
if systemctl is-active --quiet "fcc@$TARGET_USER"; then
    success "fcc@$TARGET_USER ativo e saudável"
else
    echo "❌ Falha ao iniciar serviço"
    sudo systemctl status "fcc@$TARGET_USER" --no-pager || true
    sudo journalctl -u "fcc@$TARGET_USER" --no-pager -n 50 || true
    exit 1
fi

# ------------------- ALIASES -------------------

echo ""
echo "🔧 Instalando aliases..."

if [[ -f "$ALIASES_FILE" ]]; then
    if grep -q "Free Claude Code aliases" "$BASHRC"; then
        sed -i '/# Free Claude Code aliases - Installed/,/# Fim dos aliases do Free Claude Code/d' "$BASHRC"
    fi

    {
        echo ""
        echo "# Free Claude Code aliases - Installed $(date)"
        cat "$ALIASES_FILE"
        echo "# Fim dos aliases do Free Claude Code"
    } >> "$BASHRC"

    success "Aliases instalados no bashrc"

    if sudo mkdir -p /etc/bash.bashrc.d 2>/dev/null; then
        sudo cp -f "$ALIASES_FILE" /etc/bash.bashrc.d/fcc-aliases
        success "Aliases system-wide instalados"
    fi

    source "$BASHRC" 2>/dev/null || true
else
    warning "Arquivo de aliases não encontrado"
fi

# ------------------- FINAL -------------------

echo ""
echo "🎉 Instalação concluída com sucesso"
echo ""
echo "📌 Status da instância e Proxy:"
sudo systemctl status "fcc@$TARGET_USER" --no-pager || true
echo ""
sudo systemctl status "fcc-proxy@$TARGET_USER" --no-pager || true
echo ""
echo ""
echo "⚙️ Acessso Admin Proxy:"
echo "   http://127.0.0.1:8083/admin"
echo ""
echo ""
