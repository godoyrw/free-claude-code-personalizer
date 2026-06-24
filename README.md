<p align="center">
   <img src="./assets/free-claude-code-personalizer.jpg" alt="Free Claude Code - Personalizer">
</p>

<p align="center">
 
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Shell Script](https://img.shields.io/badge/Shell-Bash-4EAA25?logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?logo=linux&logoColor=black)](https://www.kernel.org/)
[![systemd](https://img.shields.io/badge/Init-systemd-informational)](https://systemd.io/)
[![Themes](https://img.shields.io/badge/Themes-14-blueviolet)](#-temas-disponíveis)
[![GitHub stars](https://img.shields.io/github/stars/godoyrw/free-claude-code-personalizer?style=social)](https://github.com/godoyrw/free-claude-code-personalizer/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/godoyrw/free-claude-code-personalizer)](https://github.com/godoyrw/free-claude-code-personalizer/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/godoyrw/free-claude-code-personalizer)](https://github.com/godoyrw/free-claude-code-personalizer/commits/main)

</p>

# Free Claude Code - Personalizer

Este projeto permite personalizar a interface de administração do Free Claude Code com diferentes temas visuais, instalar o serviço systemd, adicionar aliases de comando e configurar um proxy para tradução dinâmica.

#### Versão: v1.0.0

---

## 📋 Visão Geral

O script `fcc-personalizer.sh` permite que você:

- Selecione entre diversos temas visuais para a interface admin
- Instale o serviço systemd **template** (`fcc@.service`) para gerenciamento automático do Free Claude Code (uma instância por usuário)
- Instale o serviço proxy (`fcc-proxy@.service`) para tradução dinâmica da interface
- Instale aliases de comando para facilitar o controle do serviço (`fcc-start`, `fcc-stop`, etc.)
- Verifique e reinicie instâncias existentes do serviço com segurança
- Desinstale tudo e restaure o tema padrão com a flag `--uninstall`

---

## 🧩 Componentes Principais

🟨 **fcc-personalizer.sh**
- Instala temas visuais
- Configura idiomas estáticos
- Configura systemd (serviços principal e proxy)
- Inicializa o serviço de proxy
- Gerencia aliases de comando

🐍 **fcc_proxy.py**
- Intercepta requisições HTTP entre o navegador e o runtime
- Aplica tradução dinâmica usando arquivos JSON em `lang/dynamic/locales/`
- Permite override de elementos da interface via middleware
- Carrega locales em tempo real sem necessidade de reinicialização

⚙️ **fcc@.service**
- Template do serviço systemd para o runtime principal do Free Claude Code
- Cria uma instância isolada por usuário (`fcc@$USER.service`)
- Configura auto-restart via systemd em caso de falha
- Gerencia o ciclo de vida do processo `fcc-server`

⚙️ **fcc-proxy@.service**
- Template do serviço systemd para o proxy de tradução
- Executa como middleware entre o navegador e o runtime principal
- Responsável por interceptar e modificar resposta HTTP para aplicar traduções
- Gerencia o ciclo de vida do processo de proxy

---

## 📁 Estrutura do Projeto

```
.
├── .gitignore                # Arquivos e pastas ignorados pelo Git (inclui lang/)
├── lang/                     # Arquivos de idioma (JavaScript) – versionados no repositório
│   ├── static/               # Idiomas estáticos
│   │   ├── default/          # Idioma padrão (inglês)
│   │   │   ├── admin.js
│   │   │   └── index.html
│   │   └── pt-br/            # Português do Brasil
│   │       ├── admin.js
│   │       └── index.html
│   ├── dynamic/              # Idiomas dinâmicos (locales)
│   │   ├── locales/
│   │   │   ├── config.json
│   │   │   ├── en.json
│   │   │   └── pt_BR.json
│   │   └── README.md
│   ├── fcc_proxy.py          # Script proxy para tradução dinâmica
│   └── fcc-proxy@.service    # Template de serviço systemd para o proxy
├── service/                  # Arquivos de serviço e aliases
│   ├── fcc@.service          # Template de serviço systemd
│   └── fcc.aliases.sh        # Aliases de comando para gerenciamento
├── themes/                   # Temas visuais (CSS)
│   ├── campbell/
│   ├── default/
│   ├── dracula/
│   ├── gnome/
│   ├── god-purple/
│   ├── high-contrast/
│   ├── horizon/
│   ├── linux/
│   ├── nord/
│   ├── solarized/
│   ├── tango/
│   ├── ubuntu/
│   ├── vs-code/
│   └── xterm/
├── fcc-personalizer.sh       # Script principal (instalação e desinstalação)
└── README.md                 # Este arquivo
```

Diagrama Mermaid da estrutura completa:

```mermaid
graph TD
    root[Root]
    root --> fcc[fcc-personalizer.sh]
    root --> lang[lang]
    lang --> static[static]
    static --> default[default]
    default --> admin_js[admin.js]
    default --> index_html[index.html]
    static --> pt_br[pt-br]
    pt_br --> admin_js_pt[admin.js]
    pt_br --> index_html_pt[index.html]
    lang --> dynamic[dynamic]
    dynamic --> locales[locales]
    locales --> config[config.json]
    locales --> en[en.json]
    locales --> pt_BR[pt_BR.json]
    dynamic --> readme_d[README.md]
    dynamic --> proxy_py[fcc_proxy.py]
    dynamic --> proxy_service[fcc-proxy@.service]
    root --> readme[README.md]
    root --> service[service]
    service --> aliases[fcc.aliases.sh]
    service --> service_file["fcc@.service"]
    root --> themes[themes]
    themes --> campbell[campbell]
    campbell --> css_c[admin.css]
    themes --> default_t[default]
    default_t --> css_d[admin.css]
    themes --> dracula[dracula]
    dracula --> css_dr[admin.css]
    themes --> gnome[gnome]
    gnome --> css_g[admin.css]
    themes --> god_purple[god-purple]
    god_purple --> css_gp[admin.css]
    themes --> high_contrast[high-contrast]
    high_contrast --> css_hc[admin.css]
    themes --> horizon[horizon]
    horizon --> css_hz[admin.css]
    themes --> linux[linux]
    linux --> css_l[admin.css]
    themes --> nord[nord]
    nord --> css_n[admin.css]
    themes --> solarized[solarized]
    solarized --> css_s[admin.css]
    themes --> tango[tango]
    tango --> css_t[admin.css]
    themes --> ubuntu[ubuntu]
    ubuntu --> css_u[admin.css]
    themes --> vs_code[vs-code]
    vs_code --> css_vs[admin.css]
    themes --> xterm[xterm]
    xterm --> css_x[admin.css]
```

---

## 🚀 Como Usar

1. **Certifique-se de que o Free Claude Code está instalado** no seu sistema
2. **Clone o repositório:**

```bash
git clone https://github.com/godoyrw/free-claude-code-personalizer.git
cd free-claude-code-personalizer
```

3. **Torne o script executável (se necessário):**

```bash
chmod +x fcc-personalizer.sh
```

4. **Execute o script:**

```bash
./fcc-personalizer.sh
```

5. **Siga as instruções na tela:**
   - Selecione o tema desejado
   - Selecione o idioma desejado
   - O script instalará automaticamente o serviço systemd template, o serviço proxy e iniciará uma instância para o seu usuário
   - Os aliases serão adicionados ao `~/.bashrc` e carregados imediatamente na sessão atual
   - O status dos serviços será exibido ao final


### Acesso ao proxy administrativo e traduzido:

```bash
acesse : http://127.0.0.1:8083/admin
```

A flag `--uninstall` para e desabilita os serviços, remove os templates systemd, remove os aliases do `~/.bashrc` e restaura o tema padrão de `themes/default/admin.css`.

> ⚠️ **Atenção:** O `DEST_DIR` no script está configurado para um caminho fixo. Antes de usar, verifique e ajuste a variável `DEST_DIR` no início do `fcc-personalizer.sh` para corresponder ao seu ambiente.

---

## 🎨 Temas Disponíveis

| Tema          | Descrição                                  |
| ------------- | ------------------------------------------ |
| campbell      | Tema inspirado no terminal do Windows      |
| default       | Tema padrão do Free Claude Code            |
| dracula       | Tema escuro com cores vibrantes            |
| gnome         | Tema inspirado no desktop GNOME            |
| god-purple    | Tema roxo escuro                           |
| high-contrast | Tema de alto contraste para acessibilidade |
| horizon       | Tema com cores suaves e agradáveis         |
| linux         | Tema inspirado no terminal Linux           |
| nord          | Tema com paleta de cores frias             |
| solarized     | Tema com cores suaves para longas sessões  |
| tango         | Tema inspirado na paleta Tango             |
| ubuntu        | Tema inspirado no Ubuntu                   |
| vs-code       | Tema inspirado no Visual Studio Code       |
| xterm         | Tema clássico do terminal XTerm            |

| Idioma | Pasta | Status |
|----------|----------|----------|
| Inglês (padrão) | `lang/static/default/` | ✅ Completo |
| Português do Brasil | `lang/static/pt-br/` | ✅ Completo |

O sistema de seleção de idioma está integrado ao script, permitindo escolher entre os idiomas disponíveis em `lang/static/`.

---

## ⚙️ Serviços Systemd

O script instala automaticamente dois templates systemd:

### 1. Serviço Principal (`fcc@.service`)

- Copia `fcc@.service` para `/etc/systemd/system/`
- Recarrega o daemon do systemd
- Para e desabilita qualquer instância anterior com segurança
- Habilita e inicia uma nova instância para o usuário atual (`fcc@$USER`)
- Valida se o serviço está ativo após a instalação e exibe logs em caso de falha

Após instalado, gerencie o serviço com (substitua `<user>` pelo seu nome de usuário):

```bash
sudo systemctl start   fcc@<user>.service   # Iniciar
sudo systemctl stop    fcc@<user>.service   # Parar
sudo systemctl restart fcc@<user>.service   # Reiniciar
sudo systemctl status  fcc@<user>.service   # Ver status
journalctl -u fcc@<user> -f                 # Acompanhar logs em tempo real
```

### 2. Serviço Proxy (`fcc-proxy@.service`)

- Copia `fcc-proxy@.service` para `/etc/systemd/system/`
- Recarrega o daemon do systemd
- Para e desabilita qualquer instância anterior com segurança
- Habilita e inicia uma nova instância para o usuário atual (`fcc-proxy@$USER`)
- Valida se o serviço está ativo após a instalação e exibe logs em caso de falha


```bash
sudo systemctl start   fcc-proxy@<user>.service   # Iniciar
sudo systemctl stop    fcc-proxy@<user>.service   # Parar
sudo systemctl restart fcc-proxy@<user>.service   # Reiniciar
sudo systemctl status  fcc-proxy@<user>.service   # Ver status
journalctl -u fcc-proxy@<user> -f                 # Acompanhar logs em tempo real
```

> **Acesso à interface administrativa traduzida:** Após a instalação do proxy, a interface administrativa do Free Claude Code com tradução dinâmica estará disponível em: **http://127.0.0.1:8083/admin**

---

## 🔧 Aliases de Comando

O script adiciona os seguintes aliases ao `~/.bashrc` (e opcionalmente em `/etc/bash.bashrc.d/fcc-aliases` para disponibilidade system-wide):

| Alias | Ação |
|---|---|
| `fcc-start` | Inicia o serviço Free Claude Code |
| `fcc-stop` | Para o serviço Free Claude Code |
| `fcc-restart` | Reinicia o serviço Free Claude Code |
| `fcc-status` | Mostra o status do serviço |
| `fcc-logs` | Visualiza os logs em tempo real |

Os aliases ficam disponíveis imediatamente na sessão atual após a instalação. Em novas sessões de terminal, são carregados automaticamente via `~/.bashrc`. Se necessário, carregue manualmente:

```bash
source ~/.bashrc
```

Se já existirem aliases do FCC no `~/.bashrc`, o script os remove antes de reinstalar.

---

## ⚙️ Como Funciona o Script

O `fcc-personalizer.sh`:

1. Verifica se o `DEST_DIR` existe
2. Lista os temas disponíveis em `themes/` e solicita seleção
3. Copia o `admin.css` do tema selecionado para o diretório de instalação do Free Claude Code
4. Lista os idiomas disponíveis em `lang/static/` e solicita seleção
5. Copia os arquivos de idioma selecionados para o diretório de instalação do Free Claude Code
6. Instala o template `fcc@.service` em `/etc/systemd/system/`
7. Instala o template `fcc-proxy@.service` em `/etc/systemd/system/`
8. Executa `systemctl daemon-reload`
9. Para e desabilita qualquer instância anterior dos serviços com segurança
10. Habilita e inicia as instâncias `fcc@$USER` e `fcc-proxy@$USER`
11. Valida se os serviços estão ativos (exibe logs em caso de falha)
12. Remove aliases anteriores do `~/.bashrc` (se existirem)
13. Instala os novos aliases em `~/.bashrc` e em `/etc/bash.bashrc.d/fcc-aliases`
14. Carrega os aliases imediatamente com `source ~/.bashrc`
15. Copia o script proxy `fcc_proxy.py` para `~/.fcc/`
16. Copia os arquivos de locale dinâmicos para `~/.fcc/locales/`

> O script **não cria backup** dos arquivos substituídos. Para restaurar o padrão, use `--uninstall`.

---

## 🛠️ Personalização Avançada

### Criar um novo tema

1. Duplique uma pasta existente em `themes/`
2. Modifique o `admin.css` com suas variáveis CSS personalizadas
3. O tema será detectado automaticamente pelo script

### Adicionar um novo idioma estático

1. Duplique uma pasta existente em `lang/static/`
2. Modifique `admin.js` e `index.html` traduzindo as strings
3. O idioma será detectado automaticamente pelo script na próxima execução

### Personalizar traduções dinâmicas

1. Modifique os arquivos JSON em `lang/dynamic/locales/`
2. O proxy carregará essas traduções em tempo de execução

---

## 📝 Requisitos

- Free Claude Code instalado e com `fcc-server` disponível no `PATH`
- `sudo` para instalação dos serviços systemd e cópia de arquivos para o `DEST_DIR`
- Shell Bash

---

## 💡 Dicas

- Experimente diferentes temas para encontrar o que mais agrada
- O tema `god-purple` foi projetado especialmente para uma experiência moderna com tons de roxo e preto
- Execute `journalctl -u fcc@$USER -f` para acompanhar os logs do serviço principal em tempo real após a instalação
- Execute `journalctl -u fcc-proxy@$USER -f` para acompanhar os logs do serviço proxy em tempo real após a instalação
- Execute o script novamente a qualquer momento para trocar de tema ou idioma — as existentes serão detectadas e reinstaladas automaticamente
- Use `--uninstall` para remover tudo e voltar ao estado original

---

## 🔍 Observações Técnicas

- **Instância por usuário via systemd template**: Cada usuário do sistema tem sua própria isolada instância do serviço, garantindo segurança e independência
- **Proxy roda antes do runtime principal**: O serviço de proxy atua como middleware, processando requisições antes que cheguem ao runtime do Free Claude Code
- **Tradução dinâmica via JSON locales**: Arquivos JSON em `lang/dynamic/locales/` permitem atualização de traduções sem reiniciar serviços
- **Arquitetura totalmente desacoplada**: Nenhum componente modifica diretamente o core do Free Claude Code, facilitando atualizações futuras
- **Sem modificação do core do Claude Code**: Todas as personalizações ocorrem em camadas externas (temas, proxy, preservando a integridade do sistema base)

---

## 🧠 Design

- **Zero patch no core**: Nenhuma alteração é feita no código-fonte original do Free Claude Code
- **Proxy-first architecture**: O proxy é a primeira camada a receber requisições, permitindo intervenção antes do processamento principal
- **Multi-user safe runtime**: Utiliza templates do systemd com instância por usuário (`fcc@$USER`) para isolamento completo entre usuários
- **Hot-swappable themes**: Temas podem ser trocados em tempo real simplesmente executando o script novamente
- **Locale injection via middleware**: O proxy injeta dinamicamente os locales nas respostas HTTP, permitindo atualização instantânea de traduções

---

## 🗑️ Desinstalação

```bash
./fcc-personalizer.sh --uninstall
```
Remove:

```
fcc@.service
fcc-proxy@.service
~/.fcc/*
aliases bash
restore tema default
restore idioma default
```

## 📄 Licença

Este projeto está licenciado sob a **MIT License**.

---

## 👤 Autor

Desenvolvido por [Roberto Godoy](https://github.com/godoyrw)  
[![ORCID](https://img.shields.io/badge/ORCID-0009--0003--2100--4772-green.svg)](https://orcid.org/0009-0003-2100-4772)

##### Versão: v1.0.0
---