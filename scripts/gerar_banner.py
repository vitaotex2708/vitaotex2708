"""Gera os banners do perfil (assets/banner-light.svg e assets/banner-dark.svg).

Usa a identidade do blog datawithvitor.com: Sora (títulos), Manrope (texto),
JetBrains Mono (rótulos) e a paleta #2463C7 / #24272B / #F7F8FA / #DCE5EF.
O GitHub não carrega fontes externas dentro de imagens, então as fontes vão
embutidas (base64, só com os caracteres usados).

Uso: python scripts/gerar_banner.py   (a partir da raiz do repositório)
"""
import base64
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROTULO = "DATA WITH VITOR"
NOME = "Vitor Teixeira"
FRASE_A = "Dados. Ideias. "
FRASE_B = "E o que fica entre eles."
LINHA = "dados e IA aplicada · Owner da DWV Soluções Inteligentes"
SITE = "datawithvitor.com →"

TEMAS = {
    "light": dict(bg="#F7F8FA", card="#FFFFFF", texto="#24272B", suave="#5B6470",
                  primaria="#2463C7", secundaria="#DCE5EF", borda="#E3E8EF"),
    "dark": dict(bg="#0F1216", card="#161A20", texto="#E8EBF0", suave="#9AA4B2",
                 primaria="#6C9CF0", secundaria="#22303F", borda="#252C36"),
}

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36"


def baixar(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fontes_embutidas() -> str:
    texto = "".join({ROTULO, NOME, FRASE_A, FRASE_B, LINHA, SITE})
    url = ("https://fonts.googleapis.com/css2?family=Sora:wght@600&family=Manrope:wght@500"
           "&family=JetBrains+Mono:wght@400&text=" + urllib.parse.quote(texto))
    css = baixar(url).decode()
    blocos = []
    for familia, peso, src in re.findall(
            r"font-family: '([^']+)';.*?font-weight: (\d+);.*?src: url\(([^)]+)\)", css, re.S):
        b64 = base64.b64encode(baixar(src)).decode()
        blocos.append(f"@font-face{{font-family:'{familia}';font-weight:{peso};"
                      f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    if len(blocos) != 3:
        raise SystemExit(f"Esperava 3 fontes, vieram {len(blocos)}")
    return "".join(blocos)


def barras(t: dict) -> str:
    """Pequeno gráfico de barras decorativo (o 'dados' da marca)."""
    alturas = [38, 62, 50, 88, 74, 112, 96, 140]
    x0, base, larg, gap = 900, 236, 30, 14
    partes = []
    for i, h in enumerate(alturas):
        cor = t["primaria"] if i == len(alturas) - 1 else t["secundaria"]
        partes.append(f'<rect x="{x0 + i * (larg + gap)}" y="{base - h}" width="{larg}" '
                      f'height="{h}" rx="6" fill="{cor}"/>')
    # linha de tendência
    pts = " ".join(f"{x0 + i * (larg + gap) + larg / 2},{base - h - 16}" for i, h in enumerate(alturas))
    partes.append(f'<polyline points="{pts}" fill="none" stroke="{t["primaria"]}" '
                  f'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>')
    return "".join(partes)


def svg(t: dict, fontes: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="320" viewBox="0 0 1280 320" role="img" aria-label="{NOME} — {FRASE_A}{FRASE_B}">
<style>{fontes}
.r{{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:15px;letter-spacing:3px;fill:{t["primaria"]}}}
.n{{font-family:'Sora',ui-sans-serif,system-ui,sans-serif;font-weight:600;font-size:58px;fill:{t["texto"]};letter-spacing:-1px}}
.f{{font-family:'Manrope',ui-sans-serif,system-ui,sans-serif;font-weight:500;font-size:27px;fill:{t["texto"]}}}
.l{{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:15px;fill:{t["suave"]}}}
</style>
<rect width="1280" height="320" rx="20" fill="{t["bg"]}"/>
<rect x="1" y="1" width="1278" height="318" rx="20" fill="none" stroke="{t["borda"]}"/>
<rect x="64" y="64" width="8" height="8" rx="2" fill="{t["primaria"]}"/>
<text x="84" y="73" class="r">{ROTULO}</text>
<text x="62" y="150" class="n">{NOME}</text>
<text x="64" y="200" class="f">{FRASE_A}<tspan fill="{t["primaria"]}">{FRASE_B}</tspan></text>
<text x="64" y="258" class="l">{LINHA}</text>
{barras(t)}
<text x="1238" y="284" text-anchor="end" class="l">{SITE}</text>
</svg>
'''


def main() -> None:
    fontes = fontes_embutidas()
    destino = Path(__file__).resolve().parent.parent / "assets"
    destino.mkdir(exist_ok=True)
    for nome, tema in TEMAS.items():
        arq = destino / f"banner-{nome}.svg"
        arq.write_text(svg(tema, fontes), encoding="utf-8")
        print(arq, arq.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
