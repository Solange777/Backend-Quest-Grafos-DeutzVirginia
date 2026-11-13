import json
from urllib.parse import quote_plus

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components

# ================================================================
# 1. DATOS DEL PROYECTO
# Cada habilidad tiene horas, requisitos, categoría y descripción.
# ================================================================
SKILLS = {
    'Python': {'hours': 25, 'prereqs': [], 'category': 'Bases', 'desc': 'Sintaxis, funciones, módulos y programación orientada a objetos.'},
    'Git': {'hours': 8, 'prereqs': [], 'category': 'Bases', 'desc': 'Versionado, ramas, commits y colaboración.'},
    'Linux': {'hours': 12, 'prereqs': [], 'category': 'Bases', 'desc': 'Terminal, permisos, procesos y comandos.'},
    'SQL': {'hours': 14, 'prereqs': ['Python'], 'category': 'Fundamentos', 'desc': 'Consultas, filtros, joins y agrupaciones.'},
    'REST API': {'hours': 12, 'prereqs': ['Python'], 'category': 'Fundamentos', 'desc': 'HTTP, métodos, estados y JSON.'},
    'PostgreSQL': {'hours': 18, 'prereqs': ['SQL', 'Python'], 'category': 'Especialización', 'desc': 'Tablas, índices y consultas.'},
    'FastAPI': {'hours': 22, 'prereqs': ['Python', 'REST API'], 'category': 'Especialización', 'desc': 'Endpoints, validación y documentación de APIs.'},
    'Docker': {'hours': 16, 'prereqs': ['Linux'], 'category': 'Fundamentos', 'desc': 'Imágenes, contenedores y Docker Compose.'},
    'Testing': {'hours': 14, 'prereqs': ['Python'], 'category': 'Especialización', 'desc': 'Pruebas automatizadas con pytest.'},
    'CI/CD': {'hours': 20, 'prereqs': ['Git', 'Docker'], 'category': 'Automatización', 'desc': 'Pipelines, pruebas y despliegues.'},
}

# Posiciones manuales para que el grafo se vea ordenado.
POSITIONS = {
    'Python': (145, 95), 'Git': (445, 95), 'Linux': (745, 95),
    'SQL': (90, 255), 'REST API': (320, 255), 'Docker': (735, 255),
    'PostgreSQL': (90, 420), 'FastAPI': (330, 420), 'Testing': (540, 420),
    'CI/CD': (735, 575),
}

# ================================================================
# 2. CONSTRUCCIÓN DEL GRAFO CON NETWORKX
# DiGraph significa grafo dirigido: las flechas tienen sentido.
# ================================================================
def crear_grafo():
    grafo = nx.DiGraph()
    for habilidad, datos in SKILLS.items():
        grafo.add_node(habilidad)
        for requisito in datos['prereqs']:
            grafo.add_edge(requisito, habilidad)
    return grafo


# ================================================================
# 3. CÁLCULOS DEL PROGRESO
# Usamos conjuntos, sumas y ordenamiento topológico.
# ================================================================
def calcular_progreso(grafo, completadas):
    pendientes = set(SKILLS) - completadas
    disponibles = {
        habilidad for habilidad in pendientes
        if set(SKILLS[habilidad]['prereqs']).issubset(completadas)
    }
    horas = sum(SKILLS[habilidad]['hours'] for habilidad in pendientes)
    orden = [habilidad for habilidad in nx.topological_sort(grafo) if habilidad in pendientes]
    return pendientes, disponibles, horas, orden


def buscar_video(habilidad):
    # Creamos una búsqueda de YouTube para cada habilidad.
    # No es un video específico, sino una lista de tutoriales.
    consulta = quote_plus(f'{habilidad} curso tutorial español principiantes')
    return f'https://www.youtube.com/results?search_query={consulta}'


# ================================================================
# 4. INTERFAZ PRINCIPAL DE STREAMLIT
# ================================================================
st.set_page_config(page_title='Backend Quest', page_icon='🚀', layout='wide')
st.markdown('''<style>
.stApp {background:#0b1120;color:#e2e8f0}
.block-container {padding-top:2rem;max-width:1300px}
h1,h2,h3 {color:#f8fafc!important}
[data-testid="stMetric"] {background:#17243b;border:1px solid #2c3e57;border-radius:14px;padding:16px}
[data-testid="stMetricValue"] {color:#f8fafc}
.stButton>button {border-radius:10px;border:1px solid #38bdf8;background:#075985;color:white}
.stButton>button:hover {background:#0369a1;color:white}
[data-testid="stSidebar"] {background:#111c30}
</style>''', unsafe_allow_html=True)

G = crear_grafo()
if not nx.is_directed_acyclic_graph(G):
    st.error('Hay un ciclo en los requisitos. Revisá las conexiones.')
    st.stop()

st.title('🚀 Backend Quest')
st.caption('Marcá lo que ya sabés y descubrí qué habilidades podés aprender después.')

# Las casillas conservan sus valores durante la sesión.
with st.sidebar:
    st.header('🎒 Tus habilidades')
    st.write('Seleccioná las habilidades que ya conocés:')
    for habilidad in SKILLS:
        st.checkbox(habilidad, key=f'skill_{habilidad}')
    if st.button('🔄 Reiniciar progreso', use_container_width=True):
        for habilidad in SKILLS:
            st.session_state[f'skill_{habilidad}'] = False
        st.rerun()
    st.caption('El progreso se conserva durante esta sesión.')

completadas = {h for h in SKILLS if st.session_state[f'skill_{h}']}
pendientes, disponibles, horas_restantes, orden = calcular_progreso(G, completadas)
progreso = len(completadas) / len(SKILLS)

col1, col2, col3, col4 = st.columns(4)
col1.metric('🏆 Dominadas', f'{len(completadas)}/{len(SKILLS)}')
col2.metric('⚡ Disponibles', len(disponibles))
col3.metric('⏳ Horas restantes', f'{horas_restantes} h')
col4.metric('🎯 Progreso', f'{progreso:.0%}')
st.progress(progreso)

# 5. VISUALIZACIÓN: Python prepara los datos para el mapa HTML.
st.subheader('🗺️ Mapa de habilidades')
nodos = []
for habilidad, datos in SKILLS.items():
    x, y = POSITIONS[habilidad]
    estado = 'done' if habilidad in completadas else ('ready' if habilidad in disponibles else 'locked')
    nodos.append({
        'id': habilidad, 'x': x, 'y': y, 'status': estado,
        'hours': datos['hours'], 'desc': datos['desc'],
        'prereqs': datos['prereqs'], 'video': buscar_video(habilidad)
    })

aristas = [{'source': origen, 'target': destino} for origen, destino in G.edges()]
datos_json = json.dumps({'nodes': nodos, 'edges': aristas}, ensure_ascii=False)
# Escapamos el cierre de script antes de insertar datos en HTML.
datos_json = datos_json.replace('<', '\\u003c')
# Todo el HTML, CSS y JavaScript están dentro de esta variable.
# Por eso NO necesitamos crear archivos adicionales.
html = r'''<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <style>

/* Estilos del mapa: colores, bordes y tamaños */
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:#111c30;color:#e2e8f0;font-family:system-ui,Segoe UI,sans-serif}
.wrapper{padding:15px;border:1px solid #2c3e57;border-radius:16px}
.help{font-size:13px;color:#aabbd1;margin:0 0 12px}
.scroller{overflow-x:auto;background:#0d1729;border-radius:12px;border:1px solid #273851}
svg{display:block;width:100%;min-width:820px;height:auto}
.node{cursor:pointer;outline:none}
.node:focus rect{stroke:#fbbf24;stroke-width:4}
.node:hover rect{filter:brightness(1.2)}
.detail{margin-top:12px;padding:15px;background:#1c2c46;border-radius:12px;border:1px solid #344b6c;min-height:105px}
.detail h3{margin:0 0 6px;color:#fff}
.detail p{margin:5px 0;line-height:1.5;font-size:14px}
.tag{font-weight:700;color:#7dd3fc}
.video{display:inline-block;margin-top:10px;padding:9px 13px;border-radius:9px;background:#075985;color:#fff;text-decoration:none;font-size:13px;font-weight:700}
.video:hover{background:#0369a1}
.legend{display:flex;flex-wrap:wrap;gap:15px;margin-bottom:10px;font-size:13px}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px}
.green{background:#34d399}
.blue{background:#38bdf8}
.gray{background:#64748b}


</style>
</head>
<body>
  <!-- Contenedor principal del mapa -->
  <div class="wrapper">
    <div class="legend">
      <span><i class="dot green"></i>Dominada</span>
      <span><i class="dot blue"></i>Disponible</span>
      <span><i class="dot gray"></i>Bloqueada</span>
    </div>
    <p class="help">Hacé clic en una habilidad para ver sus requisitos y encontrar un tutorial.</p>
    <!-- SVG dibuja los nodos y las flechas -->
    <div class="scroller">
      <svg viewBox="0 0 880 660" aria-label="Grafo dirigido de habilidades">
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
            <path d="M0 0 L10 5 L0 10Z" fill="#64748b"></path>
          </marker>
        </defs>
        <g id="edges"></g>
        <g id="nodes"></g>
      </svg>
    </div>
    <section id="detail" class="detail" aria-live="polite">
      <h3>Elegí una habilidad</h3>
      <p>Acá vas a ver su descripción, requisitos, horas estimadas y un enlace a YouTube.</p>
    </section>
  </div>
  <script>
    // Python reemplaza este marcador por los datos reales del grafo.
    const data = __DATA__;
    const NS = 'http://www.w3.org/2000/svg';
    const byId = Object.fromEntries(data.nodes.map(n => [n.id, n]));
    const edgeGroup = document.getElementById('edges');
    const nodeGroup = document.getElementById('nodes');
    const detail = document.getElementById('detail');

    function svgElement(tag, attributes, parent) {
      const element = document.createElementNS(NS, tag);
      for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
      parent.appendChild(element);
      return element;
    }

    // Dibujamos las flechas de los requisitos.
    for (const edge of data.edges) {
      const a = byId[edge.source];
      const b = byId[edge.target];
      const startY = a.y + 33;
      const endY = b.y - 39;
      const midY = (startY + endY) / 2;
      svgElement('path', {
        d: `M${a.x} ${startY} C${a.x} ${midY} ${b.x} ${midY} ${b.x} ${endY}`,
        fill: 'none', stroke: '#64748b', 'stroke-width': 2,
        'stroke-dasharray': '5 4', 'marker-end': 'url(#arrow)'
      }, edgeGroup);
    }

    // Dibujamos los nodos y agregamos el evento de clic.
    for (const node of data.nodes) {
      const color = node.status === 'done' ? '#34d399' : node.status === 'ready' ? '#38bdf8' : '#64748b';
      const fill = node.status === 'done' ? '#064e3b' : node.status === 'ready' ? '#0c4a6e' : '#25334a';
      const group = svgElement('g', {class: 'node', tabindex: '0', role: 'button', 'aria-label': node.id}, nodeGroup);
      svgElement('rect', {x: node.x-75, y: node.y-32, width: 150, height: 64, rx: 13, fill, stroke: color, 'stroke-width': 2}, group);
      const title = svgElement('text', {x: node.x, y: node.y-3, 'text-anchor': 'middle', fill: '#fff', 'font-size': 15, 'font-weight': 700}, group);
      title.textContent = node.id;
      const subtitle = svgElement('text', {x: node.x, y: node.y+18, 'text-anchor': 'middle', fill: color, 'font-size': 12}, group);
      const state = node.status === 'done' ? '✓ Dominada' : node.status === 'ready' ? '● Disponible' : 'Bloqueada';
      subtitle.textContent = `${state} · ${node.hours} h`;

      function showDetails() {
        // textContent evita interpretar el contenido como HTML.
        detail.replaceChildren();
        const heading = document.createElement('h3');
        heading.textContent = node.id;
        const description = document.createElement('p');
        description.textContent = node.desc;
        const requirements = document.createElement('p');
        requirements.textContent = 'Requisitos: ' + (node.prereqs.join(', ') || 'Ninguno');
        const hours = document.createElement('p');
        hours.textContent = `Tiempo estimado: ${node.hours} horas · Estado: ${state}`;
        const link = document.createElement('a');
        link.className = 'video';
        link.href = node.video;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = '▶ Buscar tutorial en YouTube';
        detail.append(heading, description, requirements, hours, link);
      }
      group.addEventListener('click', showDetails);
      group.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); showDetails();}
      });
    }
  </script>
</body>
</html>
'''

# Cambiamos __DATA__ por la información de las habilidades.
html = html.replace('__DATA__', datos_json)
components.html(html, height=810, scrolling=False)

# ================================================================
# 6. RUTA DE APRENDIZAJE Y CONCEPTOS MATEMÁTICOS
# ================================================================
st.subheader('📋 Tu ruta recomendada')
if not pendientes:
    st.success('¡Completaste todas las habilidades! 🎉')
else:
    st.write('**Podés empezar ahora con:** ' + (', '.join(sorted(disponibles)) or 'Ninguna'))
    for numero, habilidad in enumerate(orden, 1):
        datos = SKILLS[habilidad]
        estado = '🟦 Disponible' if habilidad in disponibles else '🔒 Pendiente'
        with st.expander(f'{numero}. {habilidad} · {datos["hours"]} h · {estado}'):
            st.write(datos['desc'])
            st.write('**Requisitos:** ' + (', '.join(datos['prereqs']) or 'Ninguno'))
            faltan = [r for r in datos['prereqs'] if r not in completadas]
            st.write('**Te falta antes:** ' + (', '.join(faltan) or 'Nada'))
            st.link_button('▶ Buscar tutorial en YouTube', buscar_video(habilidad))
    st.caption('Las horas son estimaciones orientativas. El orden mostrado es uno de los órdenes válidos posibles.')

with st.expander('📘 ¿Qué matemática usamos?'):
    st.write('**Nodos:** habilidades. **Aristas dirigidas:** requisitos. **DAG:** grafo sin ciclos dirigidos.')
    st.write('**Ordenamiento topológico:** coloca cada requisito antes de la habilidad que depende de él.')
    st.write(f'El grafo tiene **{G.number_of_nodes()} nodos** y **{G.number_of_edges()} aristas**.')
