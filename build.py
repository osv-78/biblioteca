#!/usr/bin/env python3
"""
build.py — Generador estático para Alejandría.ing
Convierte apuntes en Markdown (.md) con metadatos YAML y fórmulas LaTeX
en una biblioteca web estática lista para abrir localmente o subir gratis
(GitHub Pages, Cloudflare Pages, Vercel).

Dependencias mínimas:
    pip install markdown pyyaml

Uso:
    1. Ejecuta `python build.py` una primera vez para crear carpetas y apuntes de ejemplo.
    2. Agrega tus propios .md dentro de `contenido/<materia>/`.
    3. Vuelve a ejecutar `python build.py` para regenerar `public/index.html` e `indice.json`.
"""

import json
import re
from datetime import date
from pathlib import Path

try:
    import markdown
    import yaml
except ImportError:
    raise SystemExit(
        "Faltan dependencias. Instálalas en tu entorno virtual con:\n"
        "    pip install markdown pyyaml"
    )

BASE_DIR = Path(__file__).resolve().parent
CONTENIDO_DIR = BASE_DIR / "contenido"
SOLUCIONADORES_DIR = BASE_DIR / "solucionadores"
PUBLIC_DIR = BASE_DIR / "public"


EJEMPLO_DOBLE_INTEGRACION = r"""---
id: vigas-flexion-doble-integracion
titulo: "Flexión en Vigas: Método de Doble Integración"
materia: "Mecánica de Materiales"
tema: "Deflexión y Pendiente en Vigas"
metodo: "Doble Integración (Analítico)"
fuente: "Enfoque Clásico / Libro de Texto"
autor: "O — Apuntes ITO"
fecha: "2026-11-23"
comparar_con: "vigas-flexion-area-momentos"
tags: ["vigas", "elástica", "EI", "condiciones de frontera", "deflexión"]
resumen: "Obtención de la ecuación exacta de la curva elástica v(x) integrando dos veces la relación momento-curvatura."
---

## 1. Ecuación diferencial de la curva elástica

Para una viga prismática con rigidez a la flexión $EI$ constante sometida a flexión pura o transversal (despreciando deformación por cortante), la curvatura se relaciona con el momento flexionante interno $M(x)$ mediante:

$$EI \frac{d^2 v}{dx^2} = M(x)$$

## 2. Procedimiento paso a paso

1. **Establecer el origen de coordenadas** $x$ (generalmente en el apoyo izquierdo) e identificar los tramos donde $M(x)$ es continuo.
2. **Obtener $M(x)$ por cortes** aplicando equilibrio estático $\sum M = 0$.
3. **Primera integración (pendiente $\theta$):**
   $$EI \theta(x) = EI \frac{dv}{dx} = \int M(x)\,dx + C_1$$
4. **Segunda integración (deflexión $v$):**
   $$EI v(x) = \iint M(x)\,dx\,dx + C_1 x + C_2$$
5. **Evaluar condiciones de frontera** (apoyo simple $v=0$, empotramiento $v=0$ y $\theta=0$, simetría $\theta=0$) para despejar $C_1$ y $C_2$.

## 3. Caso práctico: Viga simplemente apoyada con carga puntual al centro

Para una viga de claro $L$ con carga puntual $P$ en $x = L/2$, en el primer tramo ($0 \le x \le L/2$) el momento es $M(x) = \frac{P}{2}x$:

$$EI \frac{dv}{dx} = \frac{P}{4}x^2 + C_1$$

Por simetría en $x = L/2$, la pendiente es nula ($\theta(L/2) = 0$), de donde $C_1 = -\frac{PL^2}{16}$. Integrando nuevamente con $v(0) = 0 \Rightarrow C_2 = 0$:

$$v_{\max} = v\left(\frac{L}{2}\right) = -\frac{PL^3}{48EI}$$
"""

EJEMPLO_AREA_MOMENTOS = r"""---
id: vigas-flexion-area-momentos
titulo: "Flexión en Vigas: Teoremas de Área de Momentos"
materia: "Mecánica de Materiales"
tema: "Deflexión y Pendiente en Vigas"
metodo: "Área de Momentos (Geométrico)"
fuente: "Método Rápido de Clase / Mohr"
autor: "O — Apuntes ITO"
fecha: "2026-11-23"
comparar_con: "vigas-flexion-doble-integracion"
tags: ["vigas", "Mohr", "diagrama M/EI", "atajo", "deflexión"]
resumen: "Cálculo directo de giros y flechas puntuales usando áreas y centroides del diagrama M/EI sin resolver constantes de integración."
---

## 1. ¿Cuándo conviene sobre Doble Integración?

Cuando necesitas la **pendiente o deflexión en un punto específico** (como el centro del claro o el extremo de un voladizo) y el diagrama de momentos está formado por triángulos y rectángulos conocidos. Te ahorras plantear y despejar $C_1, C_2, C_3, C_4$.

## 2. Los dos teoremas fundamentales

* **Primer Teorema (Cambio de pendiente):** El ángulo $\theta_{B/A}$ entre las tangentes a la elástica en $A$ y $B$ es igual al área bajo el diagrama $\frac{M}{EI}$ entre ambos puntos:
  $$\theta_{B/A} = \int_A^B \frac{M(x)}{EI}\,dx$$

* **Segundo Teorema (Desviación tangencial):** La distancia vertical $t_{B/A}$ del punto $B$ a la tangente trazada desde $A$ es el momento estático del área de $\frac{M}{EI}$ respecto a $B$:
  $$t_{B/A} = \bar{x}_B \cdot \text{Área}_{A \to B}\left(\frac{M}{EI}\right)$$

## 3. Mismo problema resuelto en 3 líneas

Para la viga de claro $L$ con carga $P$ al centro:
1. El diagrama $\frac{M}{EI}$ es un triángulo simétrico de base $L$ y altura máxima $\frac{PL}{4EI}$.
2. Por simetría, la tangente en el centro $C$ ($x = L/2$) es horizontal, así que la flecha máxima coincide con $t_{A/C}$:
   $$|v_{\max}| = t_{A/C} = \underbrace{\left[\frac{1}{2} \left(\frac{L}{2}\right) \left(\frac{PL}{4EI}\right)\right]}_{\text{Área medio triángulo}} \cdot \underbrace{\left(\frac{2}{3} \cdot \frac{L}{2}\right)}_{\bar{x}\text{ desde } A} = \frac{PL^3}{48EI}$$
"""

SOLUCIONADORES_DEFAULT = [
    {
        "id": "sol-vigas-simple",
        "titulo": "Solucionador: Viga Simple (Esfuerzo y Flecha)",
        "materia": "Mecánica de Materiales",
        "tipo": "Herramienta Web Interactiva",
        "descripcion": "Calcula reacciones, momento máximo, esfuerzo normal por flexión y deflexión máxima con diagrama SVG en vivo.",
        "estado": "Integrado en web",
    },
    {
        "id": "mecmat-2d",
        "titulo": "MECMAT-2D (Armaduras, Vigas y Marcos)",
        "materia": "Análisis Estructural / Mecánica",
        "tipo": "App de Escritorio Python (PyQt6 + SymPy)",
        "descripcion": "Tu suite simbólica y gráfica con longitudes proporcionales, deformación axial/Poisson y memoria analítica paso a paso.",
        "estado": "Listo para vincular .exe / repo",
    },
]


def inicializar_estructura():
    """Crea carpetas base y apuntes de muestra si es la primera ejecución."""
    mecanica_dir = CONTENIDO_DIR / "mecanica-materiales"
    mecanica_dir.mkdir(parents=True, exist_ok=True)
    SOLUCIONADORES_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    f1 = mecanica_dir / "flexion-doble-integracion.md"
    f2 = mecanica_dir / "flexion-area-momentos.md"
    if not f1.exists():
        f1.write_text(EJEMPLO_DOBLE_INTEGRACION.strip() + "\n", encoding="utf-8")
    if not f2.exists():
        f2.write_text(EJEMPLO_AREA_MOMENTOS.strip() + "\n", encoding="utf-8")

    sol_json = SOLUCIONADORES_DIR / "catalogo.json"
    if not sol_json.exists():
        sol_json.write_text(
            json.dumps(SOLUCIONADORES_DEFAULT, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def proteger_latex(texto_md: str):
    """
    Protege bloques $$...$$ y expresiones $...$ antes de pasar por Python-Markdown
    para evitar que guiones bajos (_) o asteriscos (*) rompan el LaTeX.
    """
    bloques = []

    def guardar(match):
        idx = len(bloques)
        bloques.append(match.group(0))
        return f"@@LATEX_TOKEN_{idx}@@"

    patron = re.compile(r"(\$\$[\s\S]+?\$\$|\$[^\n$]+?\$)")
    protegido = patron.sub(guardar, texto_md)
    return protegido, bloques


def restaurar_latex(html: str, bloques: list) -> str:
    for idx, original in enumerate(bloques):
        html = html.replace(f"@@LATEX_TOKEN_{idx}@@", original)
    return html


def parsear_markdown(ruta: Path) -> dict:
    raw = ruta.read_text(encoding="utf-8")
    if raw.startswith("---"):
        partes = raw.split("---", 2)
        meta = yaml.safe_load(partes[1]) or {}
        cuerpo_md = partes[2].strip()
    else:
        meta = {}
        cuerpo_md = raw.strip()

    protegido, bloques = proteger_latex(cuerpo_md)
    html_render = markdown.markdown(
        protegido,
        extensions=["fenced_code", "tables", "sane_lists"],
    )
    html_final = restaurar_latex(html_render, bloques)

    slug = meta.get("id") or ruta.stem
    return {
        "id": slug,
        "titulo": meta.get("titulo", ruta.stem.replace("-", " ").title()),
        "materia": meta.get("materia", "General"),
        "tema": meta.get("tema", "Sin tema"),
        "metodo": meta.get("metodo", "Estándar"),
        "fuente": meta.get("fuente", "Apunte propio"),
        "autor": meta.get("autor", "O"),
        "fecha": str(meta.get("fecha", date.today())),
        "comparar_con": meta.get("comparar_con", ""),
        "tags": meta.get("tags", []),
        "resumen": meta.get("resumen", ""),
        "html": html_final,
        "markdown": cuerpo_md,
        "archivo": str(ruta.relative_to(BASE_DIR)),
    }


def recolectar_apuntes() -> list:
    apuntes = []
    for ruta_md in sorted(CONTENIDO_DIR.rglob("*.md")):
        apuntes.append(parsear_markdown(ruta_md))
    return apuntes


def cargar_solucionadores() -> list:
    sol_json = SOLUCIONADORES_DIR / "catalogo.json"
    if sol_json.exists():
        return json.loads(sol_json.read_text(encoding="utf-8"))
    return SOLUCIONADORES_DEFAULT


def generar_html(apuntes: list, solucionadores: list) -> str:
    datos_json = json.dumps(
        {"apuntes": apuntes, "solucionadores": solucionadores},
        ensure_ascii=False,
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Alejandría.ing — Biblioteca &amp; Solucionadores</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
  <style>
    :root {{
      --bg: #0d1117;
      --panel: #161b22;
      --panel-2: #1f2630;
      --border: #30363d;
      --text: #e6edf3;
      --muted: #8b949e;
      --accent: #38bdf8;
      --accent-2: #34d399;
      --warn: #fbbf24;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}
    header {{
      border-bottom: 1px solid var(--border);
      background: rgba(22, 27, 34, 0.92);
      position: sticky;
      top: 0;
      z-index: 20;
      backdrop-filter: blur(8px);
    }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 0 20px; }}
    .topbar {{
      display: flex; flex-wrap: wrap; align-items: center;
      justify-content: space-between; gap: 12px; padding: 14px 0;
    }}
    .brand {{ font-weight: 700; font-size: 1.15rem; letter-spacing: 0.3px; }}
    .brand span {{ color: var(--accent); }}
    .controls {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
    input, select, button {{
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 0.92rem;
    }}
    input:focus, select:focus {{ outline: 1px solid var(--accent); }}
    button {{ cursor: pointer; transition: 0.15s; }}
    button:hover {{ border-color: var(--accent); }}
    button.primary {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent);
      color: var(--accent);
      font-weight: 600;
    }}
    .tabs {{ display: flex; gap: 8px; margin: 18px 0; }}
    .tab.active {{
      background: var(--accent);
      color: #081018;
      font-weight: 700;
      border-color: var(--accent);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
      gap: 16px;
      padding-bottom: 40px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 12px;
    }}
    .card:hover {{ border-color: #4b5563; }}
    .badge-row {{ display: flex; flex-wrap: wrap; gap: 6px; font-size: 0.76rem; }}
    .badge {{
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--panel-2);
      border: 1px solid var(--border);
      color: var(--accent);
    }}
    .badge.alt {{ color: var(--accent-2); }}
    .card h3 {{ margin: 4px 0; font-size: 1.06rem; }}
    .muted {{ color: var(--muted); font-size: 0.88rem; }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{ font-size: 0.75rem; color: var(--muted); }}
    .reader {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 40px;
    }}
    .reader-head {{
      display: flex; flex-wrap: wrap; justify-content: space-between;
      align-items: center; gap: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 14px; margin-bottom: 18px;
    }}
    .solver-box {{
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 20px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    @media (max-width: 780px) {{
      .solver-box {{ grid-template-columns: 1fr; }}
    }}
    .field {{ display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }}
    .field label {{ font-size: 0.82rem; color: var(--muted); }}
    .kpi-row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; }}
    .kpi {{
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 14px;
      min-width: 140px;
    }}
    .kpi small {{ display: block; color: var(--muted); font-size: 0.75rem; }}
    .kpi strong {{ font-size: 1.1rem; color: var(--accent-2); }}
    table {{ width: 100%; border-collapse: collapse; margin: 14px 0; }}
    th, td {{ border: 1px solid var(--border); padding: 8px 10px; text-align: left; }}
    th {{ background: var(--panel-2); }}
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <div class="brand">Alejandría<span>.ing</span> — Biblioteca &amp; Solucionadores</div>
      <div class="controls">
        <input id="searchInput" type="search" placeholder="Buscar tema, fórmula, método, tag..." />
        <select id="materiaFilter">
          <option value="">Todas las materias</option>
        </select>
      </div>
    </div>
  </header>

  <main class="wrap">
    <div class="tabs">
      <button class="tab active" data-view="apuntes">📚 Apuntes &amp; Perspectivas</button>
      <button class="tab" data-view="solucionadores">⚙️ Solucionadores</button>
    </div>

    <section id="viewApuntes">
      <div id="readerContainer" style="display:none;"></div>
      <div id="cardsGrid" class="grid"></div>
    </section>

    <section id="viewSolucionadores" style="display:none;">
      <div class="solver-box">
        <div>
          <h3 style="margin-top:0;">Viga Simple (Carga Puntual Central)</h3>
          <div class="field"><label>Claro L (m)</label><input id="inL" type="number" step="0.1" value="4.0"></div>
          <div class="field"><label>Carga P (kN)</label><input id="inP" type="number" step="1" value="20"></div>
          <div class="field"><label>Módulo E (GPa)</label><input id="inE" type="number" step="1" value="200"></div>
          <div class="field"><label>Inercia I (cm⁴)</label><input id="inI" type="number" step="100" value="8500"></div>
          <div class="field"><label>Fibra extrema c (cm)</label><input id="inC" type="number" step="0.5" value="15"></div>
        </div>
        <div>
          <svg id="beamSvg" viewBox="0 0 520 150" style="width:100%; background:#0b0f14; border-radius:8px; border:1px solid var(--border);"></svg>
          <div class="kpi-row">
            <div class="kpi"><small>Reacción R_A = R_B</small><strong id="outR">—</strong></div>
            <div class="kpi"><small>Momento Máx M_max</small><strong id="outM">—</strong></div>
            <div class="kpi"><small>Esfuerzo σ_max</small><strong id="outSigma">—</strong></div>
            <div class="kpi"><small>Deflexión δ_max</small><strong id="outDelta">—</strong></div>
          </div>
          <p class="muted" id="outFormula" style="margin-top:12px;"></p>
        </div>
      </div>

      <div id="solversGrid" class="grid"></div>
    </section>
  </main>

  <script>
    const DB = {datos_json};
    const renderMath = (el = document.body) => {{
      if (window.renderMathInElement) {{
        renderMathInElement(el, {{
          delimiters: [
            {{ left: "$$", right: "$$", display: true }},
            {{ left: "$", right: "$", display: false }}
          ],
          throwOnError: false
        }});
      }}
    }};

    const materiaSelect = document.getElementById("materiaFilter");
    [...new Set(DB.apuntes.map(a => a.materia))].forEach(m => {{
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      materiaSelect.appendChild(opt);
    }});

    function renderCards() {{
      const q = document.getElementById("searchInput").value.toLowerCase().trim();
      const mat = materiaSelect.value;
      const grid = document.getElementById("cardsGrid");
      const filtrados = DB.apuntes.filter(a => {{
        const matchMat = !mat || a.materia === mat;
        const blob = `${{a.titulo}} ${{a.materia}} ${{a.tema}} ${{a.metodo}} ${{a.fuente}} ${{a.tags.join(" ")}} ${{a.resumen}}`.toLowerCase();
        return matchMat && (!q || blob.includes(q));
      }});

      grid.innerHTML = filtrados.map(a => `
        <article class="card">
          <div>
            <div class="badge-row">
              <span class="badge">${{a.materia}}</span>
              <span class="badge alt">${{a.metodo}}</span>
            </div>
            <h3>${{a.titulo}}</h3>
            <p class="muted">${{a.resumen}}</p>
          </div>
          <div>
            <div class="tags">${{a.tags.map(t => `<span class="tag">#${{t}}</span>`).join(" ")}}</div>
            <div style="margin-top:10px; display:flex; gap:8px;">
              <button class="primary" onclick="abrirApunte('${{a.id}}')">Abrir apunte</button>
              ${{a.comparar_con ? `<button onclick="abrirApunte('${{a.comparar_con}}')">Ver otro enfoque</button>` : ""}}
            </div>
          </div>
        </article>
      `).join("") || `<p class="muted">No hay apuntes que coincidan con la búsqueda.</p>`;
    }}

    function abrirApunte(id) {{
      const a = DB.apuntes.find(x => x.id === id);
      if (!a) return;
      const alt = a.comparar_con ? DB.apuntes.find(x => x.id === a.comparar_con) : null;
      const box = document.getElementById("readerContainer");
      box.style.display = "block";
      box.innerHTML = `
        <div class="reader">
          <div class="reader-head">
            <div>
              <div class="badge-row">
                <span class="badge">${{a.materia}}</span>
                <span class="badge alt">${{a.metodo}}</span>
                <span class="badge">${{a.fuente}}</span>
              </div>
              <h2 style="margin:8px 0 2px;">${{a.titulo}}</h2>
              <span class="muted">Archivo fuente: ${{a.archivo}} · Actualizado: ${{a.fecha}}</span>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              ${{alt ? `<button class="primary" onclick="abrirApunte('${{alt.id}}')">⇄ Comparar con: ${{alt.metodo}}</button>` : ""}}
              <button onclick="copiarMd('${{a.id}}')">Copiar Markdown</button>
              <button onclick="document.getElementById('readerContainer').style.display='none'">Cerrar</button>
            </div>
          </div>
          <div id="readerBody">${{a.html}}</div>
        </div>
      `;
      renderMath(box);
      box.scrollIntoView({{ behavior: "smooth" }});
    }}

    function copiarMd(id) {{
      const a = DB.apuntes.find(x => x.id === id);
      if (a) navigator.clipboard.writeText(a.markdown);
    }}

    document.querySelectorAll(".tab").forEach(btn => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const v = btn.dataset.view;
        document.getElementById("viewApuntes").style.display = v === "apuntes" ? "block" : "none";
        document.getElementById("viewSolucionadores").style.display = v === "solucionadores" ? "block" : "none";
      }});
    }});

    function calcViga() {{
      const L = parseFloat(document.getElementById("inL").value) || 1;
      const P = parseFloat(document.getElementById("inP").value) || 0;
      const E = (parseFloat(document.getElementById("inE").value) || 200) * 1e9;
      const I = (parseFloat(document.getElementById("inI").value) || 8500) * 1e-8;
      const c = (parseFloat(document.getElementById("inC").value) || 15) * 1e-2;

      const R = P / 2;
      const Mmax = (P * L) / 4;
      const sigma = ((Mmax * 1e3) * c / I) / 1e6;
      const delta = (((P * 1e3) * Math.pow(L, 3)) / (48 * E * I)) * 1e3;

      document.getElementById("outR").textContent = `${{R.toFixed(2)}} kN`;
      document.getElementById("outM").textContent = `${{Mmax.toFixed(2)}} kN·m`;
      document.getElementById("outSigma").textContent = `${{sigma.toFixed(2)}} MPa`;
      document.getElementById("outDelta").textContent = `${{delta.toFixed(3)}} mm`;

      const sag = Math.min(38, Math.max(4, delta * 2.5));
      document.getElementById("beamSvg").innerHTML = `
        <line x1="60" y1="70" x2="460" y2="70" stroke="#475569" stroke-width="2" stroke-dasharray="4 4"/>
        <path d="M 60 70 Q 260 ${{70 + sag * 2}} 460 70" fill="none" stroke="#38bdf8" stroke-width="3"/>
        <polygon points="60,70 50,90 70,90" fill="#34d399"/>
        <circle cx="460" cy="78" r="8" fill="#34d399"/>
        <line x1="260" y1="20" x2="260" y2="66" stroke="#fbbf24" stroke-width="3"/>
        <polygon points="260,68 254,56 266,56" fill="#fbbf24"/>
        <text x="268" y="34" fill="#fbbf24" font-size="13">P = ${{P}} kN</text>
        <text x="235" y="135" fill="#94a3b8" font-size="12">L = ${{L}} m</text>
      `;
    }}

    ["inL", "inP", "inE", "inI", "inC"].forEach(id => {{
      document.getElementById(id).addEventListener("input", calcViga);
    }});

    document.getElementById("solversGrid").innerHTML = DB.solucionadores.map(s => `
      <article class="card">
        <div>
          <div class="badge-row">
            <span class="badge">${{s.materia}}</span>
            <span class="badge alt">${{s.estado}}</span>
          </div>
          <h3>${{s.titulo}}</h3>
          <p class="muted">${{s.descripcion}}</p>
        </div>
        <div class="tag">${{s.tipo}}</div>
      </article>
    `).join("");

    document.getElementById("searchInput").addEventListener("input", renderCards);
    materiaSelect.addEventListener("change", renderCards);
    window.addEventListener("DOMContentLoaded", () => {{
      renderCards();
      calcViga();
      renderMath();
    }});
  </script>
</body>
</html>
"""


def main():
    inicializar_estructura()
    apuntes = recolectar_apuntes()
    solucionadores = cargar_solucionadores()

    html_final = generar_html(apuntes, solucionadores)
    (PUBLIC_DIR / "index.html").write_text(html_final, encoding="utf-8")

    indice_ligero = [
        {k: v for k, v in a.items() if k not in ("html", "markdown")}
        for a in apuntes
    ]
    (PUBLIC_DIR / "indice.json").write_text(
        json.dumps(indice_ligero, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Sitio generado en: {PUBLIC_DIR / 'index.html'}")
    print(f"[OK] Apuntes procesados: {len(apuntes)}")


if __name__ == "__main__":
    main()