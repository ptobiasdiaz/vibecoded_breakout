# t1 — Revisión del ciclo de juego y semáforo de la incidencia #15

## Estado y alcance

Revisión del código y del historial Git disponibles en el workspace. No se ha
consultado GitHub ni implementado una integración nueva. La especificación
completa de #15 no está disponible localmente: se ha solicitado al usuario su
texto o una ubicación local. Hasta recibirla, t1 queda pendiente de completar su
segundo criterio de aceptación. El comportamiento existente no se considera una
especificación autorizada de colores, tiempos ni controles.

## Puntos del ciclo identificados

| Evento | Ubicación actual | Resultado de la revisión |
| --- | --- | --- |
| Inicio de partida | `breakout/main.py:56–58`, `Game.__init__()` en `breakout/game.py:18–26` | La pantalla inicial crea `Game`, cuyo constructor llama a `start_level()`. |
| Preparación de nivel | `Game.start_level()` en `breakout/game.py:33–39` | Centraliza el reinicio del estado de cuenta atrás y coloca la pelota inmóvil sobre la pala. Es el punto existente para preparar el semáforo al iniciar un nivel. |
| Pérdida de pelota | `Game.update()` en `breakout/game.py:59–70` | No existe detección de salida de pantalla, gestión de vidas ni transición por pérdida. El movimiento solo integra la velocidad. No hay un manejador al que conectar el semáforo todavía. |
| Cambio de nivel | `Game.start_level()` y sus llamadas | Existe el método de preparación, pero el juego no detecta niveles completados ni llama a ese método para avanzar. Las llamadas adicionales solo aparecen en `test_level_state.py` y `test_countdown.py`. |

`game_state.py` solo formatea vidas y puntuación; no controla el ciclo de juego.

## Semáforo localizado y puntos de integración

El semáforo existente está repartido entre:

- `breakout/game.py`: `GameState.COUNTDOWN`, `start_level()`,
  `filled_countdown_lights` y la transición de `update()` a `BALL_ATTACHED`.
- `breakout/main.py`: `draw_countdown()` y su llamada desde el bucle principal.
- `Game.launch_ball()` y `handle_launch_input()`: autorización del lanzamiento
  según el estado y tratamiento de las entradas, respectivamente.

El flujo actual es: pantalla inicial → construcción de `Game` → `start_level()`
→ `COUNTDOWN` → `BALL_ATTACHED` → `launch_ball()` → `PLAYING`.

Como evidencia de procedencia, los mensajes locales de los commits `dcf0666`,
`bdd4765` y `ec773f4` vinculan los estados, el dibujo y el lanzamiento con tareas
de la incidencia #15. Sus descripciones están truncadas y no sustituyen el texto
de la incidencia. Las pruebas `test_level_state.py`, `test_countdown.py` y
`test_ball_launch.py` describen el comportamiento implementado, sin acreditar por
sí solas que coincida con todos los requisitos de #15.

## Información necesaria antes de integrar

Obtener el texto completo de #15 y registrar su procedencia. Debe permitir
confirmar la secuencia visual, los colores, la duración y las reglas de entrada,
además de cuándo corresponde mostrar o reiniciar el semáforo: inicio de partida,
pérdida de pelota y cambio de nivel. Cualquier aspecto omitido debe aclararse,
sin completar los requisitos a partir del código actual.

Una vez contrastada esa especificación, podrá confirmarse el uso de
`start_level()` para la preparación y de `draw_countdown()` para la presentación.
La integración con una pérdida de pelota o un avance de nivel requiere primero
que existan esas transiciones; esta revisión no las añade ni decide su política.

## Criterios de aceptación

- Puntos de inicio de partida, pérdida de pelota y cambio de nivel: revisados y
  documentados, indicando expresamente los eventos aún no implementados.
- Especificación de #15 y punto de integración: puntos existentes localizados;
  especificación pendiente de recibir y contrastar. Criterio aún no satisfecho.
