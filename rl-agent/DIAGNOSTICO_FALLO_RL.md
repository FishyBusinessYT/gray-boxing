# 🧠 Reporte de Diagnóstico: El Caso del Humanoide Suicida

El problema no era un error de programación simple, sino una "tormenta perfecta" de tres factores que hacían que, matemáticamente, la mejor estrategia para tu agente fuera **tirarse al suelo lo más rápido posible.**

---

### 1. El Incentivo al "Suicidio" (Recompensa Neta Negativa)
Este es el error más crítico en Reinforcement Learning (RL). El agente intenta maximizar la suma total de recompensas de todo el episodio.

*   **Tu configuración inicial:**
    *   Recompensa por estar vivo (`healthy_reward`): **+5.0**
    *   Costo de contacto (en tu caso): **-10.0**
    *   **Resultado neto:** **-5.0 por cada frame que el agente pasaba de pie.**

**El problema:** Si vivir "duele" (-5 puntos por paso), el agente calcula: 
*   *"Si aguanto 1000 frames de pie, terminaré con -5000 puntos."*
*   *"Si me caigo ahora mismo en el frame 37, terminaré con solo -185 puntos."*

**Conclusión del agente:** Morir rápido es la mejor forma de ahorrar puntos negativos. El agente no fallaba por ser torpe, ¡era un genio matemático optimizando su miseria!

---

### 2. El Desastre del Escalado (Grados vs. Rango Normalizado)
Los algoritmos como PPO funcionan bajo la premisa de que las acciones están en un rango de **[-1, 1]**.

*   **Lo que pasaba:** Tus actuadores en el XML esperaban grados (ej. `-70` a `70`).
*   **El fallo:** PPO mandaba un `0.5` (que para él es "la mitad de mi fuerza"). Pero MuJoCo interpretaba ese `0.5` como **0.5 grados**. 
*   **Consecuencia:** El humanoide estaba "fofo" (limp). No tenía la fuerza suficiente para contrarrestar la gravedad porque sus movimientos estaban limitados a +/- 1 grado, aunque él creyera que estaba usando el 50% de su capacidad.

**El Fix:** Ahora el entorno escala ese `[-1, 1]` de PPO al rango real de grados del XML internamente. Si PPO manda `1.0`, el código lo traduce a `70.0` grados.

---

### 3. El Costo de Control Abrumador
Incluso cuando subimos la recompensa de supervivencia a +20, había otro problema matemático con los grados:

*   **Cálculo del costo:** `0.1 * sum(cuadrado(accion))`
*   **Si la acción eran grados:** Un movimiento de solo 40 grados resultaba en $40^2 \times 0.1 = 160$ puntos de penalización.
*   **La trampa:** ¡160 de penalización es muchísimo más que los +20 que ganas por vivir! 

**Resultado:** El agente aprendía que intentar equilibrarse era "carísimo". El humanoide prefería quedarse rígido como una estatua hasta que la gravedad lo matara, porque cualquier intento de corregir su postura le quitaba más puntos de los que ganaba por seguir vivo.

---

### 4. Inestabilidad Física (Explosiones NaN/Inf)
Tu personaje es masivo (un torso de 1m x 1m x 0.5m pesa cientos de kilos en MuJoCo).

*   **El problema:** Mover una masa tan grande con un `damping` (amortiguación) de solo **2** es como intentar frenar un camión con frenos de bicicleta. 
*   Cualquier pequeño movimiento generaba oscilaciones violentas que crecían exponencialmente hasta que el simulador detectaba aceleraciones infinitas y lanzaba el error de **instabilidad**.

**El Fix:** Subimos el `damping` a **20** y el `armature` a **1.0**. Esto le da a las articulaciones una "resistencia viscosa" e inercia virtual, haciendo que los movimientos sean fluidos y la simulación sea sólida.

---

### 📝 Resumen del Fix Final

| Problema | Solución aplicada |
| :--- | :--- |
| **Incentivo al suicidio** | Subimos `healthy_reward` a **20** y bajamos el costo de contacto. |
| **Humanoide fofo** | Escalamos el rango `[-1, 1]` de PPO a los grados reales del actuador. |
| **Costo de control masivo** | Calculamos el costo sobre el rango normalizado `[-1, 1]`, no sobre grados. |
| **Muerte instantánea** | Ampliamos el rango de altura (Z) de **0.3m** de margen a **2.7m**. |
| **Explosiones NaN** | Aumentamos `damping` y `armature` para estabilizar la masa. |

Con este nuevo balance, ahora **quedarse parado es rentable** y **moverse es barato**, por lo que el agente finalmente tiene la libertad de aprender a mantener el equilibrio.
