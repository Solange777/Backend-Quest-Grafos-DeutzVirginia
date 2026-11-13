import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt #importa una herramienta que permite crear graficos y dibujos en python

#creo un diccionario con las habilidades y sus requisitos
habilidades = {"Python": [], "Git": [], "Linux": [], "SQL": ["Python"], "REST API": ["Python"],
    "PostgreSQL": ["SQL", "Python"], "FastAPI": ["Python", "REST API"], "Docker": ["Linux"],
    "Testing": ["Python"], "CI/CD": ["Git", "Docker"]}

#se crear un grafo dirigido
grafo = nx.DiGraph()

#agrego nodos y conexiones
for habilidad, requisitos in habilidades.items():
    grafo.add_node(habilidad)

    for requisito in requisitos:
        grafo.add_edge(requisito, habilidad)

#titulo traido de streamlit
st.title("Backend Quest")
st.write("Grafo de habilidades para aprender Backend")

# Seleccionar habilidades completadas
st.subheader("Habilidades aprendidas")

completadas = st.multiselect(
    "Seleccioná las habilidades que ya aprendiste:",
    list(habilidades.keys())
)

# Calcular progreso
progreso = len(completadas) / len(habilidades) * 100

st.write("Progreso:", round(progreso, 1), "%")
st.progress(progreso / 100)

# Verificar habilidades disponibles
st.subheader("Habilidades disponibles")

disponibles = []

for habilidad, requisitos in habilidades.items():

    if habilidad not in completadas:

        if all(r in completadas for r in requisitos):
            disponibles.append(habilidad)

if disponibles:
    for habilidad in disponibles:
        st.write("-", habilidad)
else:
    st.write("No hay habilidades disponibles.")

# Dibujar el grafo
st.subheader("Grafo de habilidades")

colores = []

for habilidad in grafo.nodes:

    if habilidad in completadas:
        colores.append("lightgreen")

    elif habilidad in disponibles:
        colores.append("lightblue")

    else:
        colores.append("lightgray")

fig, ax = plt.subplots(figsize=(10, 6))

pos = nx.spring_layout(grafo, seed=42)

nx.draw(
    grafo,
    pos,
    with_labels=True,
    node_color=colores,
    node_size=2200,
    font_size=9,
    arrows=True,
    ax=ax
)

st.pyplot(fig)
plt.close(fig)

st.write("Verde: aprendida")
st.write("Azul: disponible")
st.write("Gris: pendiente")

# Mostrar requisitos
st.subheader("Requisitos de cada habilidad")

for habilidad, requisitos in habilidades.items():

    if requisitos:
        st.write(habilidad, "requiere:", ", ".join(requisitos))
    else:
        st.write(habilidad, "no tiene requisitos")

# Orden de aprendizaje
st.subheader("Orden de aprendizaje")

orden = list(nx.topological_sort(grafo))

for numero, habilidad in enumerate(orden, 1):
    st.write(numero, "-", habilidad)
