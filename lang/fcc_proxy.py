#!/usr/bin/env python3
"""
fcc_proxy.py — Proxy reverso para o Free Claude Code com i18n dinâmico.

Intercepta GET /admin/api/config e aplica traduções do pt_BR.json
mantendo todos os valores dinâmicos (value, configured, source, locked)
vindos do FCC original. Todo o restante das rotas é passado transparentemente.

Estrutura esperada:
    /home/<user>/.fcc/
        fcc_proxy.py           ← este arquivo
        locales/
            pt_BR.json         ← arquivo de tradução

Uso:
    python3 /home/godoy/.fcc/fcc_proxy.py [--lang pt_BR] [--port 8083]

Acesse a UI traduzida em: http://127.0.0.1:8083
O FCC original continua em:  http://127.0.0.1:8082
"""

import json
import argparse
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ── Configurações ─────────────────────────────────────────────────────────────

FCC_BASE       = "http://127.0.0.1:8082"
PROXY_HOST     = "127.0.0.1"
PROXY_PORT     = 8083
LANG           = "pt_BR"
INTERCEPT_PATH = "/admin/api/config"

# Diretório base: ~/.fcc/
FCC_DATA_DIR = Path(__file__).resolve().parent


# ── Carregamento de tradução ──────────────────────────────────────────────────

def _translation_path(lang: str) -> Path:
    return FCC_DATA_DIR / "locales" / f"{lang}.json"


def _build_index(tr: dict) -> tuple[dict, dict, dict]:
    """Constrói índices de lookup por id/key para aplicação O(1)."""
    sections = {
        s["id"]: {"label": s.get("label", ""), "description": s.get("description", "")}
        for s in tr.get("sections", [])
    }
    fields = {
        f["key"]: {"label": f.get("label", ""), "description": f.get("description", "")}
        for f in tr.get("fields", [])
    }
    providers = {
        p["provider_id"]: {"label": p.get("label", "")}
        for p in tr.get("provider_status", [])
    }
    return sections, fields, providers


def load_translation(lang: str) -> tuple[dict, dict, dict]:
    path = _translation_path(lang)
    if not path.is_file():
        print(f"[proxy] ⚠️  Tradução não encontrada: {path}")
        print(f"[proxy]    Coloque o {lang}.json em: {path.parent}/")
        return {}, {}, {}
    with path.open(encoding="utf-8") as f:
        tr = json.load(f)
    s, fi, p = _build_index(tr)
    print(f"[proxy] ✅ Tradução '{lang}' carregada — {len(s)} seções / {len(fi)} campos / {len(p)} provedores")
    return s, fi, p


# ── Lógica de mesclagem ───────────────────────────────────────────────────────

def translate_config(original: dict, sections_tr: dict, fields_tr: dict, providers_tr: dict) -> dict:
    """
    Mescla dados dinâmicos do FCC com textos traduzidos.
    Apenas label e description são sobrescritos — value, configured,
    source, locked e todos os demais campos são sempre preservados do FCC.
    """
    result = dict(original)

    result["sections"] = [
        {**s, **sections_tr.get(s.get("id", ""), {})}
        for s in result.get("sections", [])
    ]
    result["fields"] = [
        {**f, **fields_tr.get(f.get("key", ""), {})}
        for f in result.get("fields", [])
    ]
    result["provider_status"] = [
        {**p, **providers_tr.get(p.get("provider_id", ""), {})}
        for p in result.get("provider_status", [])
    ]

    return result


# ── Handler HTTP ──────────────────────────────────────────────────────────────

class ProxyHandler(BaseHTTPRequestHandler):

    sections_tr:  dict = {}
    fields_tr:    dict = {}
    providers_tr: dict = {}

    def log_message(self, fmt, *args):
        pass  # silencia o log padrão; ative para debug

    def _read_body(self) -> bytes | None:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else None

    def _forward(self, method: str, body: bytes | None = None) -> tuple[int, dict, bytes]:
        url = FCC_BASE + self.path
        headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in ("host", "content-length")
        }
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, dict(resp.headers), resp.read()
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read()
        except Exception as exc:
            print(f"[proxy] ❌ Erro ao encaminhar {method} {self.path}: {exc}")
            return 502, {"Content-Type": "application/json"}, b'{"error":"proxy_error"}'

    def _send(self, status: int, headers: dict, body: bytes):
        skip_headers = {
            "content-length",
            "content-encoding",
            "transfer-encoding",
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "upgrade",
        }

        self.send_response(status)

        for k, v in headers.items():
            if k.lower() not in skip_headers:
                self.send_header(k, v)

        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)
        
    
    def do_GET(self):
        status, headers, body = self._forward("GET")

        if self.path.split("?")[0] == INTERCEPT_PATH and status == 200:
            try:
                original = json.loads(body)
                translated = translate_config(
                    original,
                    self.__class__.sections_tr,
                    self.__class__.fields_tr,
                    self.__class__.providers_tr,
                )
                body = json.dumps(translated, ensure_ascii=False).encode("utf-8")
                headers["Content-Type"] = "application/json; charset=utf-8"
                print(f"[proxy] 🌐 GET {INTERCEPT_PATH} → traduzido e enviado")
            except Exception as exc:
                print(f"[proxy] ⚠️  Falha na tradução: {exc} — enviando resposta original")

        self._send(status, headers, body)

    def do_POST(self):
        status, headers, body = self._forward("POST", self._read_body())
        self._send(status, headers, body)

    def do_PUT(self):
        status, headers, body = self._forward("PUT", self._read_body())
        self._send(status, headers, body)

    def do_PATCH(self):
        status, headers, body = self._forward("PATCH", self._read_body())
        self._send(status, headers, body)

    def do_DELETE(self):
        status, headers, body = self._forward("DELETE")
        self._send(status, headers, body)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FCC i18n Proxy")
    parser.add_argument("--lang", default=LANG,       help="Código do idioma (ex: pt_BR)")
    parser.add_argument("--port", default=PROXY_PORT, type=int, help="Porta do proxy (padrão: 8083)")
    args = parser.parse_args()

    s, fi, p = load_translation(args.lang)
    ProxyHandler.sections_tr  = s
    ProxyHandler.fields_tr    = fi
    ProxyHandler.providers_tr = p

    server = HTTPServer((PROXY_HOST, args.port), ProxyHandler)
    print(f"[proxy] 🚀 Ouvindo em    http://{PROXY_HOST}:{args.port}")
    print(f"[proxy] 🔀 FCC original   {FCC_BASE}")
    print(f"[proxy] 🌐 Interceptando  GET {INTERCEPT_PATH}")
    print(f"[proxy] 📄 Idioma ativo   {args.lang}  →  {_translation_path(args.lang)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[proxy] 🛑 Encerrado")
        server.server_close()


if __name__ == "__main__":
    main()