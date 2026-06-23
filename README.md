# Free Cloud Code - Personalizer

Este projeto permite personalizar a interface de administração do Free Claude Code com diferentes temas, idiomas, instalar o serviço systemd (como template) e adicionar aliases de comando para facilitar o gerenciamento.

## 📋 Visão Geral

O instalador permite que você:
- Escolha entre vários idiomas disponíveis (incluindo português do Brasil)
- Selecione entre diversos temas visuais para a interface admin
- Instale facilmente o idioma e tema escolhidos na sua instalação do Free Claude Code
- Instale o serviço systemd **template** (`fcc@.service`) para gerenciamento automático do Free Claude Code (uma instância por usuário)
- Instale aliases de comando para facilitar o controle do serviço (fcc-start, fcc-stop, etc.)
- Verifique se já existem aliases e escolha se deseja remover/reinstalar
- Veja o status do serviço após a instalação
- Reinicie o servidor após a instalação para aplicar as mudanças

## 📁 Estrutura do Projeto

```text
.
├── .claude/                 # Diretório de configuração do Claude Code (gerado pelo agente)
├── .git/                    # Repositório Git
├── .gitignore               # Arquivos e pastas ignorados pelo Git
├── lang/                    # Arquivos de idioma (JavaScript) – **ignorados pelo .gitignore**
│   ├── static/              # Contém os idiomas reais
│   │   ├── default/         # Idioma padrão (inglês)
│   │   └── pt-br/           # Português do Brasil
│   └── dynamic/             # (outro propósito)
├── service/                 # Arquivos de serviço e aliases
│   ├── fcc.service          # Arquivo de serviço systemd
│   └── fcc.aliases.sh       # Aliases de comando para gerenciamento
├── themes/                  # Arquivos de tema (CSS)
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
├── install_fcc-personalizer.sh   # Script de instalação interativo
├── uninstall_fcc-personalizer.sh # Script de desinstalação
└── README.md                # Este arquivo
```

A seguir está a estrutura completa de pastas e arquivos, representada em diagrama Mermaid:

```mermaid
graph TD
    root[Root]
    %% Scripts
    root --> fcc[ fcc-personalizer.sh]
    %% Lang
    root --> lang[lang]
    lang --> dynamic[dynamic]
    dynamic --> locales[locales]
    locales --> config[config.json]
    locales --> en[en.json]
    locales --> pt_BR[pt_BR.json]
    dynamic --> readme_d[README.md]
    lang --> static[static]
    static --> default[default]
    default --> admin_js[admin.js]
    default --> index_html[index.html]
    static --> pt_br[pt-br]
    pt_br --> admin_js_pt[admin.js]
    pt_br --> index_html_pt[index.html]
    %% README
    root --> readme[README.md]
    %% Service
    root --> service[service]
    service --> aliases[fcc.aliases.sh]
    service --> service_file[fcc@.service]
    %% Themes
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

> **Observação:** A pasta `lang/` está listada no `.gitignore` para evitar que os arquivos de idioma sejam versionados acidentalmente. Eles permanecem disponíveis localmente para uso.

## 🚀 Como Usar

1. **Certifique‑se de que o Free Claude Code está instalado** no seu sistema  
2. **Execute o script de instalação:**
   ```bash
   ./fcc-personalizer.sh
   ```
3. **Siga as instruções na tela:**
   - Selecione o idioma desejado  
   - Selecione o tema desejado  
   - O script verificará se já existem aliases e perguntará se deseja remover/reinstalar  
   - O script instalará automaticamente o serviço systemd template e mostrará seu status  
   - O script instalará os aliases e os carregará imediatamente na sessão atual  
   - Confirme se deseja reiniciar o servidor Free Claude Code após a instalação  

Para desinstalar e restaurar as configurações padrão:
```bash
./fcc-personalizer.sh --uninstall
```
(o mesmo script suporta a flag `--uninstall` para remover tudo)

## 🌐 Idiomas Disponíveis

- **default** – Inglês (padrão)  
- **pt-br** – Português do Brasil  

> ⚠️ A pasta `lang/` está listada no `.gitignore` para evitar que os arquivos de idioma sejam versionados acidentalmente. Eles ainda estão disponíveis no projeto para uso local.

## 🎨 Temas Disponíveis

O projeto inclui diversos temas visuais para personalizar a interface:

- `default` – Tema padrão do Free Claude Code  
- `god-purple` – Tema roxo e preto (destacado)  
- `campbell` – Tema baseado no esquema Campbell  
- `dracula` – Tema escuro popular Dracula  
- `gnome` – Tema inspirado no GNOME  
- `high-contrast` – Tema de alto contraste para acessibilidade  
- `horizon` – Tema com gradientes suaves  
- `linux` – Tema com cores do terminal Linux clássico  
- `nord` – Tema nórdico escuro  
- `solarized` – Tema Solarized (versão escura)  
- `tango` – Tema baseado no padrão Tango  
- `ubuntu` – Tema com cores da distribuição Ubuntu  
- `vs-code` – Tema inspirado no Visual Studio Code  
- `xterm` – Tema tradicional do terminal XTerm  
- … e muitos outros disponíveis em `themes/`

## ⚙️ Serviço Systemd

O instalador agora inclui a instalação automática do **template** systemd:

- Instala `fcc@.service` em `/etc/systemd/system/` (template de serviço)  
- Recarrega o daemon do systemd  
- Habilita e inicia uma instância do serviço para o usuário que executou o instalador (`fcc@$USER`)  
- Mostra o status da instância após a instalação  
- Permite gerenciamento via `systemctl` (substitua `<user>` pelo seu nome de usuário, geralmente o mesmo que lançou o instalador):

```bash
sudo systemctl start fcc@<user>.service    # Iniciar a instância do serviço
sudo systemctl stop fcc@<user>.service     # Parar a instância do serviço
sudo systemctl restart fcc@<user>.service  # Reiniciar a instância do serviço
sudo systemctl status fcc@<user>.service   # Ver status da instância do serviço
```

## 🔧 Aliases de Comando

Além do serviço, o instalador adiciona aliases convenientes ao seu `~/.bashrc`:

- `fcc-start` – Inicia o serviço Free Claude Code  
- `fcc-stop` – Para o serviço Free Claude Code  
- `fcc-restart` – Reinicia o serviço Free Claude Code  
- `fcc-status` – Mostra o status do serviço Free Claude Code  
- `fcc-logs` – Visualiza os logs do serviço em tempo real  

O script agora:
- Verifica se já existem aliases do Free Claude Code em `~/.bashrc`  
- Pergunta se você deseja remover os existentes e reinstalá-los  
- Carrega os imediatamente na sessão atual com `source ~/.bashrc`  
- Permite que você use os aliases imediatamente após a instalação  

Esses alias ficam disponíveis automaticamente em novas sessões de terminal ou podem ser carregados imediatamente com:
```bash
source ~/.bashrc
```

## 🛠️ Personalização Avançada

Se desejar criar seu próprio tema ou idioma:

### Para criar um novo tema:
1. Duplicar uma das pastas existentes em `themes/`  
2. Modificar o arquivo `admin.css` com suas variáveis CSS personalizadas  
3. O tema será automaticamente detectado pelo instalador  

### Para criar um novo idioma:
1. Duplicar uma das pastas existentes em `lang/static/`  
2. Modificar o arquivo `admin.js` traduzindo as strings para o seu idioma  
3. O idioma será automaticamente detectado pelo instalador  

## ⚙️ Como Funciona o Instalador

O script `fcc-personalizer.sh`:
1. Verifica se o Free Claude Code está instalado  
2. Apresenta uma lista de idiomas disponíveis para seleção  
3. Apresenta uma lista de temas disponíveis para seleção  
4. Copia os arquivos selecionados para o diretório de instalação do Free Claude Code  
5. Instala o serviço systemd template (`fcc@.service`) e o habilita  
6. Mostra o status da instância do serviço após a instalação  
7. Verifica se já existem aliases do Free Claude Code em `~/.bashrc`  
8. Pergunta se deseja remover e reinstalá-los (se existirem)  
9. Instala os aliases de comando em `~/.bashrc`  
10. Carrega os imediatamente na sessão atual  
11. **Não cria backup automático** – simplesmente substitui os arquivos existentes  
12. Opcionalmente reinicia o servidor Free Claude Code para aplicar as mudanças imediatamente  

## 📝 Notas

- Para restaurar o tema ou idioma padrão, você pode usar a opção de desinstalação (`--uninstall`) que copia o tema padrão de `themes/default/admin.css` e remove as personalizações, ou copiar manualmente os arquivos padrão presentes em `themes/default/` e `lang/static/` para os destinos apropriados.  
- Se encontrar qualquer problema, você pode restaurar manualmente a partir dos arquivos padrão presentes no repositório.  
- O script requer que o comando `fcc-server` esteja disponível no PATH  
- A instalação do serviço systemd requer privilegios `sudo`  
- Os aliases são adicionados ao `~/.bashrc` e ficam disponíveis em novas sessões  

## 💡 Dicas

- Experimente diferentes combinações de idioma e tema para encontrar sua preferida  
- O tema `god-purple` foi especialmente projetado para proporcionar uma experiência moderna com tons de roxo e preto  
- Após instalar o serviço, você pode gerenciá‑lo facilmente com os aliases (`fcc-start`, `fcc-stop`, etc.) ou comandos `systemctl` (usando a instância `fcc@<user>.service`)  
- Alterações só entram em efeito após reiniciar o servidor Free Claude Code  
- Se executar o script de instalação várias vezes, ele detectará aliases existentes e perguntará o que fazer  
- O mesmo script, com a flag `--uninstall`, restaura o tema e idioma padrão, remove o serviço e os alias  

--- 

*Documentação mantida em português brasileiro conforme as diretrizes do projeto.*