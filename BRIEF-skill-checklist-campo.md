# Encargo: skill `checklist-campo` para VICTORIA

> Pega esto como primer mensaje en la sesión donde vayas a construir la skill.
> Está escrito para alguien que no ha visto nada de lo anterior.

---

## Qué quiero construir

Un skill nuevo de VICTORIA, llamado **`checklist-campo`**, que prepare el cuestionario
de la visita técnica a un centro para una licitación, lo trabaje conmigo, y acabe
produciendo el JSON que consume nuestra app de partes de campo.

Hoy ese cuestionario lo genera `planificacion-oferta` como un `checklist-campo.yaml`
suelto que no lee nadie: lo convierto a mano. Quiero sacarlo de ahí y darle skill propia,
porque tiene cadencia distinta (la planificación se hace una vez; el checklist se rehace
por lote, por centro y después de la primera visita), porque una licitación puede tener
varios centros que visitar, y porque quitando el YAML intermedio desaparece una
traducción y un sitio donde las dos cosas se desincronizan.

## Contexto: la cadena completa

```
parseo-pliegos → analisis-pliego → planificacion-oferta
                                          ↓
                                   checklist-campo   ← ESTO ES LO QUE HAY QUE HACER
                                          ↓
                          plantilla JSON → app de partes de campo
                                          ↓
                        el técnico hace la visita en el móvil
                                          ↓
                            parte.json + parte.md + fotos
                                          ↓
                                   memoria-tecnica
```

La app de partes de campo ya existe y funciona: es una web estática (GitHub Pages),
instalable en el móvil, que trabaja sin cobertura. El técnico elige la licitación de una
lista, rellena el checklist, adjunta fotos, audios y notas **por pregunta**, captura GPS,
y al enviar produce un paquete con `parte.json`, `parte.md`, `indice.csv`, un PDF
maquetado y los medios.

## La pieza que lo ata todo: `maps_to`

En el YAML actual cada pregunta lleva un `maps_to` que apunta a un epígrafe del índice de
la oferta o a un Elemento Clave de Éxito. Ese campo sobrevive hasta el final: la app lo
guarda como `mapeaA` y cada hallazgo que vuelve de campo dice a qué apartado de la memoria
técnica alimenta.

```
- **[q05] Estado actual del servicio — Cristales y carpinterías exteriores**
  - Alimenta: 2. Diagnóstico del estado actual
```

**Esto es lo más importante de todo el diseño.** Si se rompe, la visita vuelve a ser un
montón de fotos sueltas. Toda pregunta debe acabar con su mapeo, y el identificador de
cada pregunta tiene que ser estable a lo largo de todo el proceso.

---

## Cómo debe funcionar la skill

Trabaja en **dos tiempos**, porque en medio yo me voy a Excel.

### Modo 1 — construir

**Entradas**, todas de la carpeta del expediente:

- `10.Resumen/resumen.md` — criterios de adjudicación y sus pesos, plazos, subrogación, riesgos.
- `30.Planificacion/indice.md` — los epígrafes de la memoria técnica con su puntuación máxima.
- `30.Planificacion/elementos-clave-exito.md` — los ECE, en particular los que dicen "requiere campo".
- `30.Planificacion/alertas.md` — lo que puede excluir o restar puntos.
- `30.Planificacion/estrategia-lotes.md` — si va por lotes, qué se hace una vez y qué por lote.
- Opcional: un `checklist-campo.yaml` previo, para expedientes que ya lo tengan.

**Pasos:**

1. Construye una **propuesta de checklist** a partir del índice y los ECE. No de cero:
   cada epígrafe con puntos en juego debe tener preguntas que lo sustenten, y cada ECE que
   exija evidencia debe tener su pregunta.

2. Emite el **diagnóstico de cobertura**, de golpe y en un bloque (no pregunta a pregunta):
   - epígrafes con puntos y sin ninguna pregunta que los soporte, ordenados por puntuación;
   - ECE que piden campo y no tienen pregunta;
   - preguntas que se responden leyendo el pliego, que no hace falta ir al centro para eso;
   - preguntas sin mapeo;
   - tipos mal elegidos (lo que va a acabar siendo un hallazgo tiene que ser `escala`);
   - longitud estimada del recorrido.

3. Hazme **una tanda corta de preguntas**, cinco o seis, solo de lo que no puedes saber:
   qué centros se visitan, cuánto tiempo hay, qué epígrafes quiero reforzar, si conozco
   alguna particularidad del edificio, y quién hace la visita. **No abras un interrogatorio.**

4. Genera el **Excel de trabajo** en la carpeta del expediente, con la propuesta ya aplicada.

5. Dime qué has hecho y qué esperas de mí.

### Modo 2 — cerrar

Se invoca cuando le digo que ya he terminado con el Excel.

1. Lee el Excel.
2. Valida: mapeos que existen, tipos correctos, opciones donde hacen falta, ids sin duplicar.
   Si algo falla, dímelo señalando fila y columna; no lo arregles por tu cuenta.
3. Genera la **plantilla JSON** de la app.
4. Actualiza el catálogo `plantillas/index.json`.
5. Dime exactamente qué fichero subir y a dónde.

---

## El Excel de trabajo

Es la mesa de trabajo: ahí borro filas, reordeno, cambio tipos y añado las mías.

**Hoja `checklist`**, una fila por pregunta:

| Columna | Qué es |
|---|---|
| `id` | Identificador estable. **No se regenera al editar.** Si añado una fila sin id, la skill le asigna uno nuevo sin tocar los demás. |
| `seccion` | Agrupa el recorrido: una zona o un bloque temático. |
| `orden` | Número. Reordeno cambiando estos valores. |
| `enunciado` | Lo que lee el técnico en el móvil. |
| `tipo` | Desplegable: `escala`, `opcion`, `opcion_multiple`, `texto`, `numero`, `fecha`, `adjunto`. |
| `opciones` | Separadas por `\|`. Obligatorio en `opcion` y `opcion_multiple`. |
| `mapea_a` | **Desplegable con los epígrafes reales del índice de esta licitación y sus ECE.** |
| `requerido` | Sí / No. |
| `ayuda` | Una línea de aclaración bajo el enunciado. |
| `unidad` | Solo en `numero`: m2, ml, ud, %. |
| `origen` | De dónde sale: `indice`, `ece`, `alerta`, `propuesta`, `manual`. |
| `cambio` | Qué propone la skill: `nueva`, `modificada`, `sugiero quitar`, `sin cambios`. |

Las validaciones de datos en `tipo` y `mapea_a` **no son decoración**: son lo que impide
que escriba un mapeo que no existe y rompa la cadena hasta la memoria técnica.

**Hoja `cobertura`**: una fila por epígrafe del índice y por ECE, con sus puntos y cuántas
preguntas lo sustentan. Es donde veo de un vistazo si me estoy dejando algo caro.

**Hoja `instrucciones`**: qué significa cada tipo, qué pasa si quito una pregunta, y el
aviso de que los `id` no se tocan.

---

## La plantilla JSON de salida

Es el contrato de la app. Está documentado entero en `PLANTILLAS.md` del repositorio
`AguCE/checklist`, pero en resumen:

```json
{
  "id": "exp-2026-014-l2",
  "version": 1,
  "nombre": "Visita técnica — Residencia Ntra. Sra. de la Paz",
  "expediente": {
    "codigo": "2026/014",
    "objeto": "Servicio de limpieza integral…",
    "lote": "2 — Limpieza",
    "organismo": "Agencia de Servicios Sociales…"
  },
  "centro": { "nombre": "…", "direccion": "…" },
  "escala": [
    { "v": "ok",  "l": "Bien",        "peso": 1,    "tono": "ok" },
    { "v": "mej", "l": "Mejorable",   "peso": 0.5,  "tono": "warn" },
    { "v": "nc",  "l": "No conforme", "peso": 0,    "tono": "bad" },
    { "v": "na",  "l": "N/A",         "peso": null, "tono": "na" }
  ],
  "secciones": [
    {
      "id": "z2",
      "titulo": "Estado actual del servicio",
      "preguntas": [
        {
          "id": "z2-q02",
          "enunciado": "Cristales y carpinterías exteriores",
          "tipo": "escala",
          "mapea_a": "2. Diagnóstico del estado actual",
          "requerido": true,
          "ayuda": "…"
        }
      ]
    }
  ]
}
```

Notas del contrato:

- `peso` manda: `0` genera un hallazgo **no conforme**, entre 0 y 1 uno **mejorable**,
  `1` es conforme, `null` no puntúa.
- **Solo el tipo `escala` genera hallazgos.** Lo que quiera ver en el resumen de la oferta
  no puede ser un campo de texto libre.
- `adjunto` es para preguntas que no piden respuesta sino evidencia (foto, vídeo, nota,
  ubicación): la app muestra el enunciado y los botones, y la da por respondida cuando se
  adjunta algo.
- Toda pregunta, sea del tipo que sea, admite fotos, vídeos, audios y notas.

Hay un conversor ya escrito en `herramientas/yaml-a-plantilla.py` del mismo repositorio,
que hace la traducción desde el YAML viejo. Sirve de referencia para el mapeo de tipos,
pero la skill debe ir del Excel al JSON directamente.

---

## Criterio, no solo mecánica

Lo que hace útil a esta skill no es convertir formatos, es tener criterio sobre qué merece
la pena preguntar en una visita:

- **Cobertura ponderada.** Un epígrafe de 15 puntos sin preguntas es un fallo caro; uno de
  2 puntos, no tanto. Prioriza por puntuación.
- **Si se responde con el pliego, no es pregunta de campo.** Ir al centro cuesta una mañana.
- **El tipo determina el destino.** Lo que va a ser un hallazgo, `escala`. Un cajón de
  observaciones al final de cada sección está bien, pero sale en el checklist completo, no
  en la lista de hallazgos.
- **El orden es el del recorrido físico**, no el del índice de la oferta. Treinta preguntas
  desordenadas se rellenan peor que veinticinco en el orden en que se camina el edificio.
- **Entre 20 y 40 preguntas.** Por encima, la calidad de las respuestas cae.

Y lo que la skill **no** puede saber: que en ese centro hay un sótano que no aparece en el
pliego, o que el responsable solo está por las mañanas. Eso lo pongo yo. La skill propone
y pregunta; no decide por mí.

---

## Lo que NO debe hacer

- No resumir el pliego ni extraer criterios: eso es `analisis-pliego`.
- No generar el índice, las alertas ni los ECE: eso es `planificacion-oferta`.
- No redactar la memoria: eso es `memoria-tecnica`.
- No publicar nada en el repositorio de la app por su cuenta: deja el fichero y dime qué subir.
- No arreglar en silencio lo que esté mal en el Excel: señálamelo.

## Convenciones de VICTORIA que hay que respetar

- Estructura de skill: `SKILL.md` con metadatos, PASO 0 de comprobación de entradas,
  y `references/` con `que_generar.md` y `plantillas-salida.md`.
- Conocimiento transversal en `conocimiento/licitaciones/` (no reconstruirlo de memoria).
- Idempotencia: si ya existe el trabajo hecho, informar y no pisarlo salvo `--force`.
- Todo dato crítico cita su cláusula y página cuando venga del pliego.
- Nada inventado: lo que falte se declara "No especificado en el pliego".

Hay dos skills que ayudan y conviene usar: `skill-creator` para construirla y
`revisar-skill` para auditarla antes de darla por buena.

---

## Decisiones que propongo (confírmalas o cámbialas)

1. **Nombre:** `checklist-campo`.
2. **Carpeta de trabajo:** `<Nº EXPEDIENTE>/35.Campo/`, separada de `30.Planificacion/`
   porque es otra fase y se rehace con otra cadencia.
3. **`planificacion-oferta` se deja como está de momento.** Su paso final ofrece la visita
   como siguiente paso, y `registro-proceso-licitacion` cuenta artefactos generados, así que
   probablemente espera encontrar el `checklist-campo.yaml`. Que la skill nueva lo sustituya
   de hecho; cuando lleve dos o tres expedientes funcionando, se limpia con datos en la mano.
4. **Ficheros que produce**, en `35.Campo/`:
   - `checklist-<centro>.xlsx` — la mesa de trabajo
   - `plantilla-<id>.json` — lo que se sube a la app
   - `cobertura.md` — el diagnóstico, para que quede en el expediente

## Criterios de aceptación

- Con un expediente que tenga resumen e índice, el modo 1 produce un Excel abrible con
  validaciones funcionando en `tipo` y `mapea_a`.
- El diagnóstico de cobertura señala los epígrafes con puntos y sin preguntas, ordenados
  por puntuación.
- La entrevista no pasa de seis preguntas.
- Si edito el Excel —borro filas, reordeno, cambio tipos, añado preguntas— el modo 2
  produce un JSON válido y **los mapeos de las preguntas que no toqué siguen intactos**.
- El JSON resultante lo acepta la app: se puede pegar en *Importar plantilla* sin errores.
- Un `mapea_a` que no exista en el índice se detecta y se señala con su fila.

---

## Por dónde empezar

Enséñame primero el `SKILL.md` y la estructura de ficheros que propones, antes de escribir
la lógica. Quiero ver el esqueleto y los pasos antes de entrar en el detalle del Excel.
