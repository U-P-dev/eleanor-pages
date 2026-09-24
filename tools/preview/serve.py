"""公開前の目視・アクセシビリティ試験用の配信（開発用。サイトには含まれない）。

  python3 tools/preview/serve.py            # → http://localhost:4321/
  - dist/ を / で、このフォルダを /__preview/ で配る（同じオリジンなので iframe の中を JS で調べられる）
  - /__preview/one.html?p=/services.html&w=375   … 幅を指定して1ページ表示（&s=0.6 で縮小）
  - /__preview/a11y.html → DevTools か Chrome 拡張で `await runAll()` … 全ページの試験（DESIGN.md §7）
  - /__preview/og.html → `await draw(); await save()` … OGP 画像を描き直して out/ に保存
    （POST /__save/<name> を out/<name> に書く。できた PNG は public/ へ手で移す）
/mnt/c 上では astro preview が起動待ちで失敗するので、これを使う。
"""
import http.server, os, sys, functools
DIST = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "dist")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

class H(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split("?", 1)[0].split("#", 1)[0]
        if p.startswith("/__preview/"):
            return os.path.join(HERE, p[len("/__preview/"):])
        return super().translate_path(path)
    def do_POST(self):
        if not self.path.startswith("/__save/"):
            self.send_error(404); return
        name = os.path.basename(self.path[len("/__save/"):])
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with open(os.path.join(OUT, name), "wb") as f:
            f.write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b"saved %d" % len(data))
    def log_message(self, *a):
        pass

http.server.ThreadingHTTPServer(("0.0.0.0", 4321), functools.partial(H, directory=DIST)).serve_forever()
