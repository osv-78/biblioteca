---
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
