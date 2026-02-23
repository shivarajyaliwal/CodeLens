from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from analyzer import explain_code

DEFAULT_CODE = """def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a
"""


def render_page(code: str, result=None, error: str | None = None) -> str:
    def esc(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    result_block = ""
    if error:
        result_block += f'<section class="panel error">{esc(error)}</section>'

    if result:
        steps = "".join(f"<li>{esc(step)}</li>" for step in result.step_by_step)
        outline = "".join(f"<li><code>{esc(node)}</code></li>" for node in result.ast_outline)
        alts = "".join(f"<li>{esc(item)}</li>" for item in result.alternatives)
        result_block += f"""
        <section class="grid">
          <article class="panel">
            <h2>Summary</h2>
            <p>{esc(result.summary)}</p>
            <h3>Step-by-step explanation</h3>
            <ol>{steps}</ol>
          </article>
          <article class="panel">
            <h2>AST Outline</h2>
            <ul>{outline}</ul>
            <h3>Complexity estimate</h3>
            <p>{esc(result.complexity)}</p>
            <h3>Alternative implementation hints</h3>
            <ul>{alts}</ul>
          </article>
        </section>
        """

    css = open("static/style.css", "r", encoding="utf-8").read()
    return f"""<!doctype html>
<html lang='en'>
<head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Interactive Code Explanation Bot</title>
<style>{css}</style></head>
<body>
<main class='container'>
  <h1>Interactive Code Explanation Bot</h1>
  <p class='subtitle'>AST-driven step-by-step code explanation, complexity hints, and optimization ideas.</p>
  <section class='panel'>
    <form method='post'>
      <label for='code'>Paste Python code</label>
      <textarea id='code' name='code' rows='14'>{esc(code)}</textarea>
      <button type='submit'>Explain Code</button>
    </form>
  </section>
  {result_block}
  <section class='panel'>
    <h2>Research & design notes</h2>
    <ul>
      <li>Uses AST structure to avoid skipping branches and loops.</li>
      <li>Designed to align with CodeSearchNet, Code2Doc, SelfCode, CodeExp, and CodeXGLUE evaluation directions.</li>
      <li>Can be extended with LLM backends for richer natural-language generation and dataset-backed benchmarking.</li>
    </ul>
  </section>
</main>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = render_page(DEFAULT_CODE).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        code = parse_qs(raw).get("code", [""])[0]
        error = None
        result = None
        try:
            result = explain_code(code)
        except SyntaxError as exc:
            error = f"Syntax error: {exc}"

        body = render_page(code, result=result, error=error).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Serving on http://0.0.0.0:8000")
    server.serve_forever()
