"""Admin UI configuration manifest and managed env persistence."""

from __future__ import annotations

import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Literal

from dotenv import dotenv_values
from pydantic import ValidationError

from config.paths import managed_env_path
from config.provider_catalog import PROVIDER_CATALOG
from config.settings import Settings

FieldType = Literal[
    "text",
    "secret",
    "number",
    "boolean",
    "tri_boolean",
    "select",
    "textarea",
]
SourceType = Literal[
    "default",
    "template",
    "repo_env",
    "managed_env",
    "explicit_env_file",
    "process",
]

MASKED_SECRET = "********"


@dataclass(frozen=True, slots=True)
class ConfigSectionSpec:
    """A group of config fields rendered together in the admin UI."""

    section_id: str
    label: str
    description: str
    advanced: bool = False


@dataclass(frozen=True, slots=True)
class ConfigFieldSpec:
    """Typed metadata for one env-backed admin setting."""

    key: str
    label: str
    section_id: str
    field_type: FieldType = "text"
    settings_attr: str | None = None
    default: str = ""
    options: tuple[str, ...] = ()
    secret: bool = False
    advanced: bool = False
    restart_required: bool = False
    session_sensitive: bool = False
    description: str = ""


SECTIONS: tuple[ConfigSectionSpec, ...] = (
    ConfigSectionSpec(
        "providers",
        "Provedores",
        "Chaves dos provedores, endpoints locais e configurações de proxy.",
    ),
    ConfigSectionSpec(
        "models",
        "Roteamento de Modelos",
        "Modelos com prefixo do provedor usados para os níveis do Claude.",
    ),
    ConfigSectionSpec(
        "thinking",
        "Raciocínio",
        "Comportamento de raciocínio global e específico por nível.",
    ),
    ConfigSectionSpec(
        "runtime",
        "Ambiente de Execução",
        "Token da API do servidor, limites de taxa, timeouts e configurações de processo.",
    ),
    ConfigSectionSpec(
        "messaging",
        "Mensagens",
        "Discord, Telegram, workspace da CLI e configurações de sessão.",
    ),
    ConfigSectionSpec(
        "voice",
        "Voz",
        "Configurações de transcrição de notas de voz.",
    ),
    ConfigSectionSpec(
        "web_tools",
        "Ferramentas Web",
        "Comportamento local do web_search e web_fetch da Anthropic.",
    ),
    ConfigSectionSpec(
        "diagnostics",
        "Diagnóstico",
        "Flags de logging e depuração.",
        advanced=True,
    ),
    ConfigSectionSpec(
        "smoke",
        "Testes Smoke",
        "Substituições opcionais de modelos para testes smoke ao vivo.",
        advanced=True,
    ),
)


FIELDS: tuple[ConfigFieldSpec, ...] = (
    ConfigFieldSpec(
        "NVIDIA_NIM_API_KEY",
        "Chave da API NVIDIA NIM",
        "providers",
        "secret",
        settings_attr="nvidia_nim_api_key",
        secret=True,
        description="Usado pelo chat NVIDIA NIM e pela transcrição de voz opcional do NIM.",
    ),
    ConfigFieldSpec(
        "OPENROUTER_API_KEY",
        "Chave da API OpenRouter",
        "providers",
        "secret",
        settings_attr="open_router_api_key",
        secret=True,
    ),
    ConfigFieldSpec(
        "MISTRAL_API_KEY",
        "Chave da API Mistral",
        "providers",
        "secret",
        settings_attr="mistral_api_key",
        secret=True,
        description=(
            "Mistral La Plateforme (api.mistral.ai); o plano Experiment é gratuito com limites de taxa."
        ),
    ),
    ConfigFieldSpec(
        "CODESTRAL_API_KEY",
        "Chave da API Codestral",
        "providers",
        "secret",
        settings_attr="codestral_api_key",
        secret=True,
        description=(
            "Endpoint Mistral Codestral (codestral.mistral.ai); distinto do ``MISTRAL_API_KEY`` da Mistral "
            "La Plateforme. Consulte a documentação da Mistral para domínios de codificação/FIM."
        ),
    ),
    ConfigFieldSpec(
        "DEEPSEEK_API_KEY",
        "Chave da API DeepSeek",
        "providers",
        "secret",
        settings_attr="deepseek_api_key",
        secret=True,
    ),
    ConfigFieldSpec(
        "KIMI_API_KEY",
        "Chave da API Kimi",
        "providers",
        "secret",
        settings_attr="kimi_api_key",
        secret=True,
    ),
    ConfigFieldSpec(
        "WAFER_API_KEY",
        "Chave da API Wafer",
        "providers",
        "secret",
        settings_attr="wafer_api_key",
        secret=True,
    ),
    ConfigFieldSpec(
        "OPENCODE_API_KEY",
        "Chave da API OpenCode",
        "providers",
        "secret",
        settings_attr="opencode_api_key",
        secret=True,
        description=(
            "Gateway selecionado do OpenCode Zen (opencode.ai/zen/v1) e gateway de assinatura OpenCode Go "
            "(opencode.ai/zen/go/v1); chave única de opencode.ai/auth."
        ),
    ),
    ConfigFieldSpec(
        "ZAI_API_KEY",
        "Chave da API Z.ai",
        "providers",
        "secret",
        settings_attr="zai_api_key",
        secret=True,
        description="Chave da API do Z.ai Coding Plan.",
    ),
    ConfigFieldSpec(
        "FIREWORKS_API_KEY",
        "Chave da API Fireworks",
        "providers",
        "secret",
        settings_attr="fireworks_api_key",
        secret=True,
        description="Chave da API de inferência da Fireworks AI.",
    ),
    ConfigFieldSpec(
        "GEMINI_API_KEY",
        "Chave da API Gemini",
        "providers",
        "secret",
        settings_attr="gemini_api_key",
        secret=True,
        description=(
            "Chave da API Gemini do Google AI Studio (Google AI Studio / Gemini API "
            "[compatível com OpenAI](https://ai.google.dev/gemini-api/docs/openai)); "
            "o nível gratuito tem limites de taxa por modelo e os dados podem ser usados para melhorias "
            "fora do Reino Unido/CH/EEE/UE."
        ),
    ),
    ConfigFieldSpec(
        "GROQ_API_KEY",
        "Chave da API Groq",
        "providers",
        "secret",
        settings_attr="groq_api_key",
        secret=True,
        description=(
            "Chave da API compatível com OpenAI do GroqCloud ([console.groq.com/keys]("
            "https://console.groq.com/keys)); consulte a [documentação de compatibilidade com OpenAI]("
            "https://console.groq.com/docs/openai) da Groq."
        ),
    ),
    ConfigFieldSpec(
        "CEREBRAS_API_KEY",
        "Chave da API Cerebras",
        "providers",
        "secret",
        settings_attr="cerebras_api_key",
        secret=True,
        description=(
            "Chave da API de Inferência Cerebras (crie no [Cloud Console](https://cloud.cerebras.ai)); "
            "consulte o [Quickstart](https://inference-docs.cerebras.ai/quickstart) e a "
            "[compatibilidade com OpenAI](https://inference-docs.cerebras.ai/resources/openai)."
        ),
    ),
    ConfigFieldSpec(
        "LM_STUDIO_BASE_URL",
        "URL Base do LM Studio",
        "providers",
        settings_attr="lm_studio_base_url",
        default="http://localhost:1234/v1",
    ),
    ConfigFieldSpec(
        "LLAMACPP_BASE_URL",
        "URL Base do llama.cpp",
        "providers",
        settings_attr="llamacpp_base_url",
        default="http://localhost:8080/v1",
    ),
    ConfigFieldSpec(
        "OLLAMA_BASE_URL",
        "URL Base do Ollama",
        "providers",
        settings_attr="ollama_base_url",
        default="http://localhost:11434",
    ),
    ConfigFieldSpec(
        "NVIDIA_NIM_PROXY",
        "Proxy NVIDIA NIM",
        "providers",
        "secret",
        settings_attr="nvidia_nim_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "OPENROUTER_PROXY",
        "Proxy OpenRouter",
        "providers",
        "secret",
        settings_attr="open_router_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "MISTRAL_PROXY",
        "Proxy Mistral",
        "providers",
        "secret",
        settings_attr="mistral_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "CODESTRAL_PROXY",
        "Proxy Codestral",
        "providers",
        "secret",
        settings_attr="codestral_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "LMSTUDIO_PROXY",
        "Proxy do LM Studio",
        "providers",
        "secret",
        settings_attr="lmstudio_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "LLAMACPP_PROXY",
        "Proxy do llama.cpp",
        "providers",
        "secret",
        settings_attr="llamacpp_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "KIMI_PROXY",
        "Proxy Kimi",
        "providers",
        "secret",
        settings_attr="kimi_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "WAFER_PROXY",
        "Proxy Wafer",
        "providers",
        "secret",
        settings_attr="wafer_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "OPENCODE_PROXY",
        "Proxy OpenCode Zen",
        "providers",
        "secret",
        settings_attr="opencode_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "OPENCODE_GO_PROXY",
        "Proxy OpenCode Go",
        "providers",
        "secret",
        settings_attr="opencode_go_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "ZAI_PROXY",
        "Proxy Z.ai",
        "providers",
        "secret",
        settings_attr="zai_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "FIREWORKS_PROXY",
        "Proxy Fireworks",
        "providers",
        "secret",
        settings_attr="fireworks_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "GEMINI_PROXY",
        "Proxy Gemini",
        "providers",
        "secret",
        settings_attr="gemini_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "GROQ_PROXY",
        "Proxy Groq",
        "providers",
        "secret",
        settings_attr="groq_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "CEREBRAS_PROXY",
        "Proxy Cerebras",
        "providers",
        "secret",
        settings_attr="cerebras_proxy",
        secret=True,
        advanced=True,
    ),
    ConfigFieldSpec(
        "MODEL",
        "Modelo Padrão",
        "models",
        settings_attr="model",
        default="nvidia_nim/nvidia/nemotron-3-super-120b-a12b",
        description="Rota de provedor/modelo de fallback para todos os nomes de modelo Claude.",
    ),
    ConfigFieldSpec(
        "MODEL_OPUS",
        "Substituição do Opus",
        "models",
        settings_attr="model_opus",
        description="Rota de provedor/modelo opcional para solicitações Opus.",
    ),
    ConfigFieldSpec(
        "MODEL_SONNET",
        "Substituição do Sonnet",
        "models",
        settings_attr="model_sonnet",
        description="Rota de provedor/modelo opcional para solicitações Sonnet.",
    ),
    ConfigFieldSpec(
        "MODEL_HAIKU",
        "Substituição do Haiku",
        "models",
        settings_attr="model_haiku",
        description="Rota de provedor/modelo opcional para solicitações Haiku.",
    ),
    ConfigFieldSpec(
        "ENABLE_MODEL_THINKING",
        "Ativar Raciocínio",
        "thinking",
        "boolean",
        settings_attr="enable_model_thinking",
        default="true",
    ),
    ConfigFieldSpec(
        "ENABLE_OPUS_THINKING",
        "Raciocínio Opus",
        "thinking",
        "tri_boolean",
        settings_attr="enable_opus_thinking",
        description="Em branco herda 'Ativar Raciocínio'.",
    ),
    ConfigFieldSpec(
        "ENABLE_SONNET_THINKING",
        "Raciocínio Sonnet",
        "thinking",
        "tri_boolean",
        settings_attr="enable_sonnet_thinking",
        description="Em branco herda 'Ativar Raciocínio'.",
    ),
    ConfigFieldSpec(
        "ENABLE_HAIKU_THINKING",
        "Raciocínio Haiku",
        "thinking",
        "tri_boolean",
        settings_attr="enable_haiku_thinking",
        description="Em branco herda 'Ativar Raciocínio'.",
    ),
    ConfigFieldSpec(
        "ANTHROPIC_AUTH_TOKEN",
        "Token de Autenticação da API/CLI",
        "runtime",
        "secret",
        settings_attr="anthropic_auth_token",
        default="freecc",
        secret=True,
        description="Protege o acesso ao Claude/API. Não é o login da página de administração.",
    ),
    ConfigFieldSpec(
        "PROVIDER_RATE_LIMIT",
        "Limite de Taxa do Provedor",
        "runtime",
        "number",
        settings_attr="provider_rate_limit",
        default="1",
    ),
    ConfigFieldSpec(
        "PROVIDER_RATE_WINDOW",
        "Janela de Taxa do Provedor",
        "runtime",
        "number",
        settings_attr="provider_rate_window",
        default="3",
    ),
    ConfigFieldSpec(
        "PROVIDER_MAX_CONCURRENCY",
        "Máximo de Concorrência do Provedor",
        "runtime",
        "number",
        settings_attr="provider_max_concurrency",
        default="5",
    ),
    ConfigFieldSpec(
        "HTTP_READ_TIMEOUT",
        "Tempo Limite de Leitura HTTP",
        "runtime",
        "number",
        settings_attr="http_read_timeout",
        default="300",
    ),
    ConfigFieldSpec(
        "HTTP_WRITE_TIMEOUT",
        "Tempo Limite de Escrita HTTP",
        "runtime",
        "number",
        settings_attr="http_write_timeout",
        default="60",
    ),
    ConfigFieldSpec(
        "HTTP_CONNECT_TIMEOUT",
        "Tempo Limite de Conexão HTTP",
        "runtime",
        "number",
        settings_attr="http_connect_timeout",
        default="60",
    ),
    ConfigFieldSpec(
        "HOST",
        "Host do Servidor",
        "runtime",
        settings_attr="host",
        default="0.0.0.0",
        restart_required=True,
    ),
    ConfigFieldSpec(
        "PORT",
        "Porta do Servidor",
        "runtime",
        "number",
        settings_attr="port",
        default="8082",
        restart_required=True,
    ),
    ConfigFieldSpec(
        "MESSAGING_PLATFORM",
        "Plataforma de Mensagens",
        "messaging",
        "select",
        settings_attr="messaging_platform",
        default="discord",
        options=("telegram", "discord", "none"),
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "MESSAGING_RATE_LIMIT",
        "Limite de Taxa de Mensagens",
        "messaging",
        "number",
        settings_attr="messaging_rate_limit",
        default="1",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "MESSAGING_RATE_WINDOW",
        "Janela de Taxa de Mensagens",
        "messaging",
        "number",
        settings_attr="messaging_rate_window",
        default="1",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "TELEGRAM_BOT_TOKEN",
        "Token do Bot do Telegram",
        "messaging",
        "secret",
        settings_attr="telegram_bot_token",
        secret=True,
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "ALLOWED_TELEGRAM_USER_ID",
        "ID de Usuário do Telegram Permitido",
        "messaging",
        settings_attr="allowed_telegram_user_id",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "DISCORD_BOT_TOKEN",
        "Token do Bot do Discord",
        "messaging",
        "secret",
        settings_attr="discord_bot_token",
        secret=True,
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "ALLOWED_DISCORD_CHANNELS",
        "Canais do Discord Permitidos",
        "messaging",
        settings_attr="allowed_discord_channels",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "ALLOWED_DIR",
        "Diretório Permitido",
        "messaging",
        settings_attr="allowed_dir",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "MAX_MESSAGE_LOG_ENTRIES_PER_CHAT",
        "Entradas Máximas no Log de Mensagens",
        "messaging",
        "number",
        settings_attr="max_message_log_entries_per_chat",
        advanced=True,
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "VOICE_NOTE_ENABLED",
        "Notas de Voz",
        "voice",
        "boolean",
        settings_attr="voice_note_enabled",
        default="false",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "WHISPER_DEVICE",
        "Dispositivo Whisper",
        "voice",
        "select",
        settings_attr="whisper_device",
        default="nvidia_nim",
        options=("cpu", "cuda", "nvidia_nim"),
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "WHISPER_MODEL",
        "Modelo Whisper",
        "voice",
        settings_attr="whisper_model",
        default="openai/whisper-large-v3",
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "HF_TOKEN",
        "Token do Hugging Face",
        "voice",
        "secret",
        settings_attr="hf_token",
        secret=True,
        session_sensitive=True,
    ),
    ConfigFieldSpec(
        "FAST_PREFIX_DETECTION",
        "Detecção Rápida de Prefixo",
        "runtime",
        "boolean",
        settings_attr="fast_prefix_detection",
        default="true",
        advanced=True,
    ),
    ConfigFieldSpec(
        "ENABLE_NETWORK_PROBE_MOCK",
        "Mock de Sonda de Rede",
        "runtime",
        "boolean",
        settings_attr="enable_network_probe_mock",
        default="true",
        advanced=True,
    ),
    ConfigFieldSpec(
        "ENABLE_TITLE_GENERATION_SKIP",
        "Pular Geração de Título",
        "runtime",
        "boolean",
        settings_attr="enable_title_generation_skip",
        default="true",
        advanced=True,
    ),
    ConfigFieldSpec(
        "ENABLE_SUGGESTION_MODE_SKIP",
        "Pular Modo de Sugestão",
        "runtime",
        "boolean",
        settings_attr="enable_suggestion_mode_skip",
        default="true",
        advanced=True,
    ),
    ConfigFieldSpec(
        "ENABLE_FILEPATH_EXTRACTION_MOCK",
        "Mock de Extração de Caminho",
        "runtime",
        "boolean",
        settings_attr="enable_filepath_extraction_mock",
        default="true",
        advanced=True,
    ),
    ConfigFieldSpec(
        "ENABLE_WEB_SERVER_TOOLS",
        "Ferramentas do Servidor Web",
        "web_tools",
        "boolean",
        settings_attr="enable_web_server_tools",
        default="true",
    ),
    ConfigFieldSpec(
        "WEB_FETCH_ALLOWED_SCHEMES",
        "Esquemas Permitidos para Web Fetch",
        "web_tools",
        settings_attr="web_fetch_allowed_schemes",
        default="http,https",
    ),
    ConfigFieldSpec(
        "WEB_FETCH_ALLOW_PRIVATE_NETWORKS",
        "Permitir Redes Privadas",
        "web_tools",
        "boolean",
        settings_attr="web_fetch_allow_private_networks",
        default="false",
    ),
    ConfigFieldSpec(
        "DEBUG_PLATFORM_EDITS",
        "Depurar Edições da Plataforma",
        "diagnostics",
        "boolean",
        settings_attr="debug_platform_edits",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "DEBUG_SUBAGENT_STACK",
        "Depurar Pilha do Subagente",
        "diagnostics",
        "boolean",
        settings_attr="debug_subagent_stack",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "LOG_RAW_API_PAYLOADS",
        "Registrar Payloads Brutos da API",
        "diagnostics",
        "boolean",
        settings_attr="log_raw_api_payloads",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "LOG_RAW_SSE_EVENTS",
        "Registrar Eventos SSE Brutos",
        "diagnostics",
        "boolean",
        settings_attr="log_raw_sse_events",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "LOG_API_ERROR_TRACEBACKS",
        "Registrar Tracebacks de Erro da API",
        "diagnostics",
        "boolean",
        settings_attr="log_api_error_tracebacks",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "LOG_RAW_MESSAGING_CONTENT",
        "Registrar Conteúdo Bruto de Mensagens",
        "diagnostics",
        "boolean",
        settings_attr="log_raw_messaging_content",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "LOG_RAW_CLI_DIAGNOSTICS",
        "Registrar Diagnósticos Brutos da CLI",
        "diagnostics",
        "boolean",
        settings_attr="log_raw_cli_diagnostics",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "LOG_MESSAGING_ERROR_DETAILS",
        "Registrar Detalhes de Erro de Mensagens",
        "diagnostics",
        "boolean",
        settings_attr="log_messaging_error_details",
        default="false",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_NVIDIA_NIM",
        "Modelo Smoke NVIDIA NIM",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_OPEN_ROUTER",
        "Modelo Smoke OpenRouter",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_MISTRAL",
        "Modelo Smoke Mistral",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_MISTRAL_CODESTRAL",
        "Modelo Smoke Mistral Codestral",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_DEEPSEEK",
        "Modelo Smoke DeepSeek",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_LMSTUDIO",
        "Modelo Smoke LM Studio",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_LLAMACPP",
        "Modelo Smoke llama.cpp",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_OLLAMA",
        "Modelo Smoke Ollama",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_KIMI",
        "Modelo Smoke Kimi",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_WAFER",
        "Modelo Smoke Wafer",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_OPENCODE",
        "Modelo Smoke OpenCode Zen",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_OPENCODE_GO",
        "Modelo Smoke OpenCode Go",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_ZAI",
        "Modelo Smoke Z.ai",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_FIREWORKS",
        "Modelo Smoke Fireworks",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_GEMINI",
        "Modelo Smoke Gemini",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_GROQ",
        "Modelo Smoke Groq",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_MODEL_CEREBRAS",
        "Modelo Smoke Cerebras",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_NIM_MODELS",
        "Modelos Smoke NIM",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_NIM_EXTRA_MODELS",
        "Modelos Smoke NIM Extras",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_OPENROUTER_FREE_MODELS",
        "Modelos Smoke OpenRouter Gratuitos",
        "smoke",
        advanced=True,
    ),
    ConfigFieldSpec(
        "FCC_SMOKE_OPENROUTER_FREE_EXTRA_MODELS",
        "Modelos Smoke OpenRouter Gratuitos Extras",
        "smoke",
        advanced=True,
    ),
)

FIELD_BY_KEY = {field.key: field for field in FIELDS}


def repo_env_path() -> Path:
    """Return the repo-local env path."""

    return Path(".env")


def explicit_env_path() -> Path | None:
    """Return the explicit FCC_ENV_FILE path, when configured."""

    if explicit := os.environ.get("FCC_ENV_FILE"):
        return Path(explicit)
    return None


def configured_env_files() -> tuple[tuple[SourceType, Path], ...]:
    """Return dotenv files in low-to-high precedence order."""

    files: list[tuple[SourceType, Path]] = [
        ("repo_env", repo_env_path()),
        ("managed_env", managed_env_path()),
    ]
    if explicit := explicit_env_path():
        files.append(("explicit_env_file", explicit))
    return tuple(files)


def _template_text() -> str:
    import importlib.resources

    packaged = importlib.resources.files("cli").joinpath("env.example")
    if packaged.is_file():
        return packaged.read_text("utf-8")

    source_template = Path(__file__).resolve().parents[1] / ".env.example"
    if source_template.is_file():
        return source_template.read_text(encoding="utf-8")

    return ""


def _dotenv_values_from_text(text: str) -> dict[str, str]:
    values = dotenv_values(stream=StringIO(text))
    return {key: "" if value is None else value for key, value in values.items()}


def template_values() -> dict[str, str]:
    """Return .env.example values plus manifest defaults for newer fields."""

    values = _dotenv_values_from_text(_template_text())
    for field in FIELDS:
        values.setdefault(field.key, field.default)
    return values


def _dotenv_values_from_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    values = dotenv_values(path)
    return {key: "" if value is None else value for key, value in values.items()}


def _field_input_key(field: ConfigFieldSpec) -> str | None:
    if field.settings_attr is None:
        return None
    model_field = Settings.model_fields[field.settings_attr]
    alias = model_field.validation_alias
    if alias is None:
        return field.settings_attr
    return str(alias)


def _is_locked_source(source: SourceType) -> bool:
    return source in {"process", "explicit_env_file"}


def _normalize_for_env(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _display_value(field: ConfigFieldSpec, value: str) -> str:
    if field.secret and value:
        return MASKED_SECRET
    return value


def _load_value_state() -> dict[str, dict[str, Any]]:
    values = template_values()
    sources: dict[str, SourceType] = {
        key: "template" if key in values else "default" for key in FIELD_BY_KEY
    }

    for source, path in configured_env_files():
        file_values = _dotenv_values_from_file(path)
        for key, value in file_values.items():
            if key in FIELD_BY_KEY:
                values[key] = value
                sources[key] = source

    for key in FIELD_BY_KEY:
        if key in os.environ:
            values[key] = os.environ[key]
            sources[key] = "process"

    return {
        key: {
            "value": values.get(key, ""),
            "source": sources.get(key, "default"),
        }
        for key in FIELD_BY_KEY
    }


def load_config_response() -> dict[str, Any]:
    """Return manifest and current config values for the admin UI."""

    state = _load_value_state()
    fields: list[dict[str, Any]] = []
    for field in FIELDS:
        entry = state[field.key]
        source = entry["source"]
        raw_value = entry["value"]
        fields.append(
            {
                "key": field.key,
                "label": field.label,
                "section": field.section_id,
                "type": field.field_type,
                "value": _display_value(field, raw_value),
                "configured": bool(str(raw_value).strip()),
                "source": source,
                "locked": _is_locked_source(source),
                "secret": field.secret,
                "advanced": field.advanced,
                "restart_required": field.restart_required,
                "session_sensitive": field.session_sensitive,
                "options": list(field.options),
                "description": field.description,
            }
        )

    return {
        "sections": [
            {
                "id": section.section_id,
                "label": section.label,
                "description": section.description,
                "advanced": section.advanced,
            }
            for section in SECTIONS
        ],
        "fields": fields,
        "paths": {
            "managed": str(managed_env_path()),
            "repo": str(repo_env_path()),
            "explicit": str(explicit_env_path()) if explicit_env_path() else None,
        },
        "provider_status": provider_config_status(state),
    }


def _target_values_with_updates(updates: Mapping[str, Any]) -> dict[str, str]:
    state = _load_value_state()
    values = template_values()

    # Preserve existing managed values when present. If no managed config exists,
    # seed the first write from effective repo values to migrate legacy setups.
    managed_values = _dotenv_values_from_file(managed_env_path())
    if managed_values:
        values.update(
            {key: val for key, val in managed_values.items() if key in values}
        )
    else:
        for key, entry in state.items():
            if entry["source"] in {"repo_env", "template", "default"}:
                values[key] = str(entry["value"])

    for key, value in updates.items():
        field = FIELD_BY_KEY.get(key)
        if field is None:
            continue
        if _is_locked_source(state[key]["source"]):
            continue
        if field.secret and value == MASKED_SECRET:
            continue
        values[key] = _normalize_for_env(value)

    for field in FIELDS:
        values.setdefault(field.key, field.default)
    return values


def _effective_values_for_validation(
    target_values: Mapping[str, str],
) -> dict[str, str]:
    values = dict(target_values)
    for key, entry in _load_value_state().items():
        if _is_locked_source(entry["source"]):
            values[key] = str(entry["value"])
    return values


def validate_values(values: Mapping[str, str]) -> tuple[bool, list[str]]:
    """Validate proposed env values against the Settings model."""

    kwargs: dict[str, Any] = {"_env_file": None}
    for field in FIELDS:
        input_key = _field_input_key(field)
        if input_key is None:
            continue
        kwargs[input_key] = values.get(field.key, "")

    try:
        Settings(**kwargs)
    except ValidationError as exc:
        return False, _format_validation_errors(exc)
    return True, []


def _format_validation_errors(exc: ValidationError) -> list[str]:
    errors: list[str] = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", ()))
        message = str(error.get("msg", "Invalid value"))
        errors.append(f"{loc}: {message}" if loc else message)
    return errors


def validate_updates(updates: Mapping[str, Any]) -> dict[str, Any]:
    """Validate partial admin updates and return a masked generated env preview."""

    target_values = _target_values_with_updates(updates)
    effective_values = _effective_values_for_validation(target_values)
    valid, errors = validate_values(effective_values)
    return {
        "valid": valid,
        "errors": errors,
        "env_preview": render_env_file(target_values, mask_secrets=True),
    }


def changed_pending_fields(updates: Mapping[str, Any]) -> list[str]:
    """Return changed fields that require manual runtime action."""

    state = _load_value_state()
    pending: list[str] = []
    for key, value in updates.items():
        field = FIELD_BY_KEY.get(key)
        if field is None or not (field.restart_required or field.session_sensitive):
            continue
        if _normalize_for_env(value) == str(state[key]["value"]):
            continue
        pending.append(key)
    return pending


def write_managed_env(updates: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and atomically write the admin-managed env file."""

    validation = validate_updates(updates)
    if not validation["valid"]:
        return validation | {"applied": False, "pending_fields": []}

    target_values = _target_values_with_updates(updates)
    pending_fields = changed_pending_fields(updates)
    path = managed_env_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(render_env_file(target_values), encoding="utf-8")
    os.replace(temp_path, path)
    return {
        "applied": True,
        "valid": True,
        "errors": [],
        "env_preview": render_env_file(target_values, mask_secrets=True),
        "path": str(path),
        "pending_fields": pending_fields,
    }


def _quote_env_value(value: str) -> str:
    if value == "":
        return ""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    if any(char.isspace() for char in value) or any(
        char in value for char in ('"', "#", "=", "$")
    ):
        return f'"{escaped}"'
    return value


def render_env_file(values: Mapping[str, str], *, mask_secrets: bool = False) -> str:
    """Render a complete grouped env file."""

    lines: list[str] = [
        "# Managed by Free Claude Code /admin.",
        "# Edit in the server UI when possible.",
        "",
    ]
    fields_by_section: dict[str, list[ConfigFieldSpec]] = {
        section.section_id: [] for section in SECTIONS
    }
    for field in FIELDS:
        fields_by_section.setdefault(field.section_id, []).append(field)

    for section in SECTIONS:
        lines.append(f"# {section.label}")
        for field in fields_by_section.get(section.section_id, []):
            value = values.get(field.key, field.default)
            if mask_secrets and field.secret and value:
                value = MASKED_SECRET
            lines.append(f"{field.key}={_quote_env_value(value)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def provider_config_status(
    state: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return provider configuration status without making network calls."""

    state = state or _load_value_state()
    statuses: list[dict[str, Any]] = []
    for provider_id, descriptor in PROVIDER_CATALOG.items():
        if descriptor.credential_env is None:
            base_url = ""
            if descriptor.base_url_attr is not None:
                base_url = _value_for_settings_attr(state, descriptor.base_url_attr)
            statuses.append(
                {
                    "provider_id": provider_id,
                    "kind": "local",
                    "status": "missing_url" if not base_url.strip() else "unknown",
                    "label": "URL Ausente" if not base_url.strip() else "Não verificado",
                    "base_url": base_url or descriptor.default_base_url or "",
                }
            )
            continue

        value = str(state.get(descriptor.credential_env, {}).get("value", ""))
        configured = bool(value.strip())
        statuses.append(
            {
                "provider_id": provider_id,
                "kind": "remote",
                "status": "configured" if configured else "missing_key",
                if configured else "missing_key",
                "missing_key",
                "label": " "label": "Configurado" if configured else " "label": "Configurado" "label": "Configurado" if configured else "Configurado" if configured else "ChChave ausente",
                " if configured else "Chave ausente",
               Chave ausente",
                "ave ausente",
                "credential_env": descriptor.credential_env,
           credential_env": descriptor.credential "credential_env": descriptor.credentialcredential_env": descriptor.credential }
        )
    return statuses


def_env,
            }
        )
    return status_env,
            }
        )
    return_env,
            }
        )
    return statuses


def _value_for_settings_attr(
    state:es


def _value_for_settings_attr(
    statuses


def _value_for_settings_attr(
    _value_for_settings_attr(
    Mapping[str, Mapping[str, Any]], settings state: Mapping[str, Mapping[str, state: Mapping[str, Mapping[str, state: Mapping[str, Mapping[str, Any]], settings_attr: str
) -> str Any]], settings_attr: str
) Any]], settings_attr: str
) -> str:
    for field in FIELDS_attr: str
) -> str:
    for field in FIELDS:
        if:
    for field in FIELDS:
        if field.settings_attr == settings_attr -> str:
    for field in FIELDS:
        if field.settings_attr == settings_:
        if field.settings_attr == settings_attr field.settings_attr == settings_attr:
            return str(state.get(fieldattr:
            return str(state.get(field:
            return str(state.get(field:
            return str(state.get(field.key, {}).get("value", field.default))
   .key, {}).get("value",.key, {}).get("value", field.default))
   .key, {}).get("value", field.default))
    return ""


def env_keys() -> field.default))
    return ""


def env_keys() -> return ""


def env_keys() -> return ""


def env_keys() -> frozenset[str]:
    """Return env keys frozenset[str]:
    """Return frozenset[str]:
    """Return env keys owned frozenset[str]:
    """Return env keys owned owned by the admin manifest."""

    return env keys owned by the admin manifest."""

    by the admin manifest."""

    return by the admin manifest."""

    return frozenset(field.key for field return frozenset(field.key for field in FIELDS)


def fields_with_attrs frozenset(field.key for field in FIELDS frozenset(field.key for field in FIELDS)


def fields_with_attrs() -> Iterable in FIELDS)


def fields_with_attrs() -> Iterable[ConfigFieldSpec)


def fields_with_attrs() -> Iterable[ConfigFieldSpec]:
    """Yield[ConfigFieldSpec]:
    """Yield fields that validate() -> Iterable[ConfigFieldSpec]:
    """Yield fields that validate]:
    """Yield fields that validate through Settings."""

    return (field for field fields that validate through Settings."""

    return (field for field through Settings."""

    return through Settings."""

    return (field for field in FIELDS if field.settings in FIELDS if field.settings in FIELDS if field.settings_attr is not (field for field in FIELDS if field.settings_attr is not None)