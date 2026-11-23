---
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
