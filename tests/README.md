# Comprobación de ESC (task-2)

El único estado implementado es la pantalla inicial de `breakout/main.py`.
ESPACIO aún no cambia de pantalla: no existen transiciones que comprobar.
Cuando se añadan estados o transiciones con procesamiento de entradas, deberán
incorporarse a esta cobertura.

`test_global_exit.py` comprueba ESC al entrar en la pantalla, después de uno o
varios fotogramas y después de ESPACIO en el mismo lote de eventos. Verifica que
el cierre detiene el procesamiento del lote, no dibuja otro fotograma ni espera
otro ciclo y llama a `pygame.quit()` una sola vez.

La prueba de integración ejecuta el juego con pygame real en procesos separados
y controladores SDL sin ventana ni sonido. Envía ESC al inicio y después de uno
y tres fotogramas. Exige salida con código cero, sin errores en stderr y con los
subsistemas de pygame cerrados; limita cada proceso a diez segundos para detectar
un bucle que no termina. Se omite explícitamente si pygame no está instalado.

Ejecutar desde la raíz, con las dependencias del proyecto instaladas:

```sh
python3 -m unittest discover -s tests -v
python3 -m unittest discover -v
```
