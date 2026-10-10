#!/usr/bin/env python3
"""Bundle authentic Zelda3 Wasm and JS in one local-opening HTML file.

No Zelda ROM, graphics, game resources, or saves are bundled. The user must
select a locally extracted zelda3_assets.dat file in the browser.
"""
from pathlib import Path
import base64
import re
import sys

def build(source_dir, target_file):
    root = Path(source_dir)
    html = (root / "browser/index.html").read_text(encoding="utf-8")
    js = (root / "zelda3.js").read_text(encoding="utf-8")
    wasm = (root / "zelda3.wasm").read_bytes()
    if not wasm.startswith(b"\x00asm"):
        raise ValueError("Expected a real WebAssembly binary, not a placeholder.")
    if "var Module=" not in html or '<script src="zelda3.js"></script>' not in html:
        raise ValueError("Browser entrypoint structure changed.")
    # Put Wasm bytes in the browser's memory before the actual Emscripten JS initializes.
    # No fetch, cross-origin hosting, or GitHub user assets are necessary.
    encoded = base64.b64encode(wasm).decode("ascii")
    loader = ("<script>\n"
              "Module.wasmBinary = Uint8Array.from(atob('" + encoded + "'), c => c.charCodeAt(0));\n"
              "</script>\n")
    # Inline the compiler-generated original-engine loader; do not replace its game code.
    safe_js = re.sub(r"</script", r"<\\/script", js, flags=re.IGNORECASE)
    output = html.replace('<script src="zelda3.js"></script>',
                          loader + "<script>\n" + safe_js + "\n</script>", 1)
    out = Path(target_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(output, encoding="utf-8")
    print(f"Bundled true Zelda3 native engine: HTML={out.stat().st_size} bytes; wasm={len(wasm)} bytes")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python3 browser/package_single_html.py ROOT OUT.html")
    build(sys.argv[1], sys.argv[2])
