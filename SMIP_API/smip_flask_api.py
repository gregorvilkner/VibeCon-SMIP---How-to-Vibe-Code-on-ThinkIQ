"""SMIP Automation Template — Flask API.

Thin REST wrapper over SMIPMethods plus an agentic /api/chat endpoint backed
by Azure OpenAI. Endpoint set is derived from SMIP_MCP.smip_tools.TOOL_REGISTRY
so adding a method there automatically exposes it on /api/tool/<name>.

Surfaces:
  /            interactive Vue documentation page
  /chat        baseline chat UI
  /chat_stack  experimental "stack" chat layout
  /chat_canvas experimental canvas/timeseries chat layout
  /api/...     REST endpoints

PAGES/ are intentionally NOT registered on this app. Each page is its own
runnable .py: it adds the project root to sys.path, imports `app` from
SMIP_API.smip_flask_api, decorates it with @app.route(<page_path>, ...),
and runs the combined app on its own port. Same-origin fetches with
relative URLs (no CORS dance, no proxy). One process per page, so a buggy
or "vibe-coded" page can't break sibling pages or the backend.

Run from project root:
    python SMIP_API/smip_flask_api.py

Required env vars for /api/chat (loaded from .env at the project root):
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_API_KEY
    AZURE_OPENAI_API_VERSION   (optional, default 2025-01-01-preview)
    AZURE_OPENAI_DEPLOYMENT    (optional, default gpt-4o)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory, render_template
from openai import AzureOpenAI

from SMIP_IO.smip_client import SMIPClient
from SMIP_IO.smip_methods import SMIPMethods
from SMIP_MCP.smip_tools import OPENAI_TOOLS, TOOL_REGISTRY_PUBLIC, make_dispatch
from SMIP_MCP.agent_prompt import SYSTEM_INSTRUCTIONS

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

_HERE = Path(__file__).resolve().parent

# Jinja variable delimiters are swapped to [[ ... ]] so the documentation
# template can keep Vue's native {{ ... }} mustaches for client-side bindings.
app = Flask(__name__, template_folder=str(_HERE))
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

client  = SMIPClient()
methods = SMIPMethods(client)

# Registry-backed dispatch + LLM tool spec, derived from SMIP_MCP.smip_tools.
_CHAT_TOOLS    = OPENAI_TOOLS
_SMIP_DISPATCH = make_dispatch(methods)
_SYSTEM_PROMPT = SYSTEM_INSTRUCTIONS


def _ok(data):
    return jsonify({'ok': True, 'data': data})


def _err(e):
    return jsonify({'ok': False, 'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Documentation + chat UIs
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Interactive Vue documentation page — sections generated from TOOL_REGISTRY."""
    return render_template(
        'smip_flask_api_documentation.html',
        tools=TOOL_REGISTRY_PUBLIC,
    )


@app.route('/chat')
def chat_ui():
    return send_from_directory(str(_HERE), 'smip_chat.html')


@app.route('/chat_stack')
def chat_stack_ui():
    # Experimental "stack" layout: newest above the input, older stacks
    # upward, overflow wraps leftward into the next column.
    return send_from_directory(str(_HERE), 'smip_chat_stack.html')


@app.route('/chat_canvas')
def chat_canvas_ui():
    # Experimental canvas layout: chat as a timeseries. Two lanes (user /
    # assistant), horizontal time axis; viewport pans through history.
    return send_from_directory(str(_HERE), 'smip_chat_canvas.html')


# ---------------------------------------------------------------------------
# Generic registry-backed dispatch — every TOOL_REGISTRY entry is reachable
# at /api/tool/<name>.
# ---------------------------------------------------------------------------

@app.route('/api/tool/<name>', methods=['POST'])
def call_tool(name: str):
    """Invoke a tool from TOOL_REGISTRY by name.

    Body: {"args": { ... registry-named kwargs ... }}
    Returns the same {ok, data}/{ok, error} shape as the other endpoints.
    """
    try:
        if name not in _SMIP_DISPATCH:
            return jsonify({'ok': False, 'error': f'Unknown tool: {name}'}), 404
        body = request.get_json(force=True, silent=True) or {}
        args = body.get('args', {})
        if not isinstance(args, dict):
            return jsonify({'ok': False, 'error': 'args must be an object'}), 400
        return _ok(_SMIP_DISPATCH[name](args))
    except Exception as e:
        return _err(e)


# ---------------------------------------------------------------------------
# Chat endpoint — agentic loop backed by Azure OpenAI
# ---------------------------------------------------------------------------

@app.route('/api/chat', methods=['POST'])
def chat():
    """Agentic chat endpoint.

    Request body: { "message": "...", "history": [...] }
    Returns: { "ok": true, "data": { "response": "...", "history": [...] } }
    """
    try:
        body = request.get_json(force=True) or {}
        user_message = str(body.get('message', '')).strip()
        if not user_message:
            return jsonify({'ok': False, 'error': 'message is required'}), 400

        history = body.get('history', [])
        if not isinstance(history, list):
            history = []

        ai = AzureOpenAI(
            azure_endpoint=os.environ['AZURE_OPENAI_ENDPOINT'],
            api_key=os.environ['AZURE_OPENAI_API_KEY'],
            api_version=os.environ.get('AZURE_OPENAI_API_VERSION', '2025-01-01-preview'),
        )
        deployment = os.environ.get('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o')

        messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        for _ in range(50):
            response = ai.chat.completions.create(
                model=deployment,
                messages=messages,
                tools=_CHAT_TOOLS,
                tool_choice="auto",
            )
            choice = response.choices[0]

            if choice.finish_reason == "tool_calls":
                messages.append(choice.message.model_dump(exclude_unset=True))
                for tc in choice.message.tool_calls:
                    fn_name = tc.function.name
                    fn_args = json.loads(tc.function.arguments or '{}')
                    if fn_name in _SMIP_DISPATCH:
                        try:
                            result = _SMIP_DISPATCH[fn_name](fn_args)
                        except Exception as exc:
                            result = {"error": str(exc)}
                    else:
                        result = {"error": f"Unknown tool: {fn_name}"}
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, default=str),
                    })
            else:
                assistant_text = choice.message.content or ""
                messages.append({"role": "assistant", "content": assistant_text})
                return _ok({
                    "response": assistant_text,
                    "history": messages[1:],
                })

        return _err(Exception("Chat loop exceeded maximum tool-call iterations"))

    except KeyError as e:
        return jsonify({'ok': False, 'error': f'Missing environment variable: {e}'}), 500
    except Exception as e:
        return _err(e)


if __name__ == '__main__':
    print('SMIP Automation Template API + Documentation running at http://localhost:5000')
    app.run(debug=True, port=5000)
