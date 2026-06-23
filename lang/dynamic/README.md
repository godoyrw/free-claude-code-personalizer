É na prática, um runtime de “injeção de comportamento” em cima de uma aplicação Python existente (FCC) — algo bem próximo de um sidecar framework interno, só que rodando dentro do próprio processo.

Vou te explicar isso como arquitetura, sem romantizar.

🧠 O que esse serviço realmente é

Você não está criando “só um middleware”.

Você está criando um:

⚙️ Runtime Enhancement Layer (REL)

Uma camada que:

intercepta o bootstrap da aplicação
descobre dinamicamente o app FastAPI
injeta middleware em tempo de execução
altera comportamento sem mexer no core do FCC
adiciona i18n (tradução) como cross-cutting concern
🧩 Arquitetura que nasceu disso

Hoje seu sistema virou isso:

systemd
   ↓
fcc-server (FastAPI app)
   ↓
sitecustomize.py (Python injection hook)
   ↓
bootstrap.py (runtime orchestrator)
   ↓
middleware.py (i18n + interceptação HTTP)
   ↓
admin_config / API original do FCC
🔥 O que cada parte faz (na prática)
1. systemd service

Ele só garante:

processo vivo
restart automático
ambiente consistente

👉 Ele NÃO sabe nada do que você está injetando.

2. fcc-server (app original)

É o sistema base:

FastAPI
Admin UI
APIs internas
config engine

👉 Ele não foi feito para ser “extensível por patch runtime”.

3. sitecustomize.py (o “hack mestre”)

Esse arquivo é o gatilho oculto do Python.

Ele roda automaticamente quando Python inicia.

👉 Ele vira seu:

“pre-main injection point”

É aqui que você sequestra o runtime.

4. bootstrap.py (orquestrador)

Esse é o cérebro.

Ele:

encontra o app (create_app / app / heurística)
garante idempotência
injeta middleware
evita duplicação

👉 Ele resolve o problema clássico:

“onde está o objeto FastAPI real?”

5. runtime middleware (o coração da sua ideia)

Aqui está sua inovação real:

intercepta responses
traduz strings dinamicamente
aplica i18n sem alterar código original

Isso é:

Response Transformation Layer

🌍 O que você construiu conceitualmente

Você criou algo entre:

🟦 Plugin System (tipo VSCode)
🟨 Middleware engine (tipo Express)
🟥 Runtime patching (tipo monkey patch avançado)
🟩 i18n engine (tipo gettext, mas interceptado)
🧬 Característica principal do seu sistema
🔥 “Non-invasive augmentation”

Você NÃO:

altera o FCC core
recompila nada
modifica routes originais
mexe no FastAPI base

Você:

intercepta o runtime e modifica comportamento em memória

⚠️ Por que deu loop antes

Porque esse tipo de arquitetura tem um problema clássico:

“multiple initialization problem”

Em sistemas assim:

múltiplos workers (uvicorn/gunicorn)
reload automático
import side effects

👉 tudo tenta “injetar o sistema de novo”

Por isso você viu:

bootstrap → middleware → bootstrap → middleware → infinito
🧠 O estado atual do seu sistema

Hoje ele já evoluiu para:

✔ Boot seguro (com lock)
✔ app discovery dinâmico
✔ middleware injection controlado
✔ i18n externo desacoplado
✔ override sem modificar core FCC
🧭 O que isso significa em engenharia de software

Você basicamente criou um:

🧱 “runtime plugin framework inside a running ASGI app”

Isso é raro porque:

não depende de framework oficial de plugin
não exige extensão do FCC
funciona via introspecção + monkey patch