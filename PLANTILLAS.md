# Contrato de plantilla

Una **plantilla** es el formulario de una licitación: el JSON que decide qué preguntas
ve el técnico. La app no sabe nada del contenido; todo sale de aquí.

Este es el fichero que debe generar la skill de planificación de oferta, y el que un
humano revisa antes de publicarlo.

## Dónde vive

```
plantillas/
├── index.json          ← catálogo: la lista que ve el técnico al abrir la app
├── exp-2026-014.json   ← una plantilla por licitación
└── limpieza-base.json
```

Para dar de alta una licitación: sube su `.json` a `plantillas/` y añade una línea al
catálogo. Nada más.

## El catálogo

```json
{
  "actualizado": "2026-09-20",
  "plantillas": [
    {
      "id": "exp-2026-014",
      "fichero": "exp-2026-014.json",
      "nombre": "Visita técnica — Limpieza Residencia Ntra. Sra.",
      "expediente": { "codigo": "2026/014", "lote": "2 — Limpieza" },
      "centro": { "nombre": "Residencia Ntra. Sra. de la Paz" },
      "version": 1
    }
  ]
}
```

Solo sirve para pintar la lista. Los datos de verdad están en la plantilla.

## La plantilla

```json
{
  "id": "exp-2026-014",
  "version": 1,
  "nombre": "Visita técnica previa — Limpieza Residencia Ntra. Sra.",

  "expediente": {
    "codigo": "2026/014",
    "objeto": "Servicio de limpieza integral de los centros residenciales…",
    "lote": "2 — Limpieza",
    "organismo": "Agencia de Servicios Sociales y Dependencia de Andalucía"
  },

  "centro": {
    "nombre": "Residencia Ntra. Sra. de la Paz",
    "direccion": "Avda. de la Paz, 14 — 41010 Sevilla"
  },

  "secciones": [
    {
      "id": "superficies",
      "titulo": "Superficies y alcance",
      "preguntas": [
        { "id": "m2_totales", "enunciado": "Superficie declarada en el pliego (m²)",
          "tipo": "numero", "ayuda": "Si no cuadra con lo medido, anótalo en una nota." },
        { "id": "pavimentos", "enunciado": "Tipos de pavimento presentes",
          "tipo": "opcion_multiple", "opciones": ["Terrazo", "Gres", "PVC", "Moqueta"] },
        { "id": "general", "enunciado": "Estado general de limpieza" }
      ]
    }
  ]
}
```

### Campos

| Campo | Obligatorio | Qué es |
|---|---|---|
| `id` | sí | Identificador de la plantilla. Letras, números, punto y guion. |
| `version` | no | Número. Súbelo cuando cambies las preguntas. |
| `nombre` | sí | Título que ve el técnico. |
| `expediente` | no | `codigo`, `objeto`, `lote`, `organismo`. Se copia tal cual a cada parte. |
| `centro` | no | `nombre`, `direccion`. Aparece en la cabecera y en el PDF. |
| `cabecera` | no | Campos que rellena el técnico. Si falta, se usan técnico, fecha, tipo de visita y zona. |
| `escala` | no | La valoración de las preguntas de tipo `escala`. Si falta, se usa la de abajo. |
| `secciones` | **sí** | Los bloques del checklist, en el orden del recorrido. |

### Preguntas

| Campo | Obligatorio | Qué es |
|---|---|---|
| `id` | sí | Único dentro de su sección. |
| `enunciado` | sí | Lo que lee el técnico. |
| `tipo` | no | Por defecto `escala`. |
| `opciones` | según tipo | Obligatorio en `opcion` y `opcion_multiple`. |
| `mapea_a` | no | El epígrafe del índice de la oferta o el ECE (`ECE-NN`) que sustenta esta pregunta. La app lo conserva como `mapeaA` en cada hallazgo, y así cada evidencia sabe a qué apartado de la memoria técnica alimenta. Es la pieza que ata la visita con la oferta: escríbelo siempre. |
| `requerido` | no | `true` marca la pregunta como imprescindible (se pinta con `*`). Una de tipo `adjunto` se da por respondida cuando se adjunta algo. |
| `unidad` | no | En `numero`, la unidad (`m2`, `ml`, `ud`, `%`). Solo informativa. |
| `ayuda` | no | Una línea de aclaración bajo el enunciado. |
| `largo` | no | En `texto`, muestra un área grande. |

Tipos admitidos:

- **`escala`** — la valoración estándar. Es la única que cuenta para el porcentaje de
  cumplimiento y la que genera hallazgos.
- **`opcion`** — una opción entre varias propias.
- **`opcion_multiple`** — varias a la vez.
- **`texto`** — texto libre.
- **`numero`** — valor numérico.
- **`fecha`** — fecha.
- **`adjunto`** — no pide respuesta, pide evidencia (foto, vídeo, nota o ubicación). La app
  muestra el enunciado con los botones de adjuntar y da la pregunta por respondida en cuanto
  se añade algo. No genera hallazgo de cumplimiento (para eso, `escala`).

Toda pregunta, sea del tipo que sea, admite fotos, vídeos, audios y notas.

> El validador de *Importar plantilla* es tolerante: ignora campos que no conoce, así que
> `mapea_a`, `unidad` u `origen` no rompen nada aunque una versión antigua de este documento
> no los recogiera. Lo que sí comprueba: `id`/`nombre`/`secciones`, que cada sección tenga
> `id`, `titulo` y preguntas, que cada pregunta tenga `id` y `enunciado`, que el `tipo` sea
> uno de los de arriba, que `opcion`/`opcion_multiple` traigan `opciones`, y que **no haya
> dos preguntas con el mismo `id` dentro de la misma sección** (la unicidad es por sección,
> no global).

### La escala por defecto

```json
[
  { "v": "ok",  "l": "Bien",        "peso": 1,    "tono": "ok",   "significado": "cumple lo exigido" },
  { "v": "mej", "l": "Mejorable",   "peso": 0.5,  "tono": "warn", "significado": "cumple con deficiencias" },
  { "v": "nc",  "l": "No conforme", "peso": 0,    "tono": "bad",  "significado": "no cumple" },
  { "v": "na",  "l": "N/A",         "peso": null, "tono": "na",   "significado": "no aplica; no puntúa" }
]
```

`peso` manda: `0` genera un hallazgo **no conforme**, entre 0 y 1 uno **mejorable**,
`1` es conforme y `null` no puntúa. `tono` solo elige el color (`ok`, `warn`, `bad`, `na`).

## Cómo probar una plantilla sin publicarla

En la app, **Importar plantilla**: pegas el JSON, se valida y te dice exactamente qué
falla antes de que nadie salga a campo. Si es correcto, queda guardado en ese móvil y
aparece en la lista. Es el paso que hace el humano sobre lo que produce la skill.

## Consejos para que el resultado sirva en la oferta

Lo que el LLM recibe después son los **hallazgos**: solo las preguntas de tipo `escala`
generan hallazgos. Si quieres que algo aparezca en ese resumen, hazlo `escala`, no `texto`.

Una pregunta de tipo `texto` con `largo: true` al final de cada sección funciona bien
como cajón de observaciones, pero no esperes que salga en la lista de hallazgos: sale en
el checklist completo y en el CSV.

Los enunciados viajan enteros al JSON, al markdown y al PDF, así que escríbelos como
quieras leerlos después: mejor «Puntos de agua y desagüe suficientes por planta» que
«Agua OK».

Entre 20 y 40 preguntas es el rango razonable para una visita. Por encima, el técnico
se cansa y la calidad de las respuestas baja.
