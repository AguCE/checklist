# Partes de campo — UNEI

Aplicación web para que los técnicos rellenen en el móvil el parte de una visita a un
centro: checklist por secciones, fotos, vídeos, audios y notas colgando de cada pregunta,
ubicación GPS, y salida pensada para que la analice tanto una persona como un modelo.

Un formulario distinto por licitación. Sin servidor, sin base de datos: son ficheros
estáticos servidos como página web.

## Publicar

1. Sube todos los ficheros de esta carpeta, con la carpeta `plantillas/` dentro, a la
   raíz del repositorio.
2. **Settings → Pages**, *Deploy from a branch*, rama `main`, carpeta `/ (root)`.
3. En unos minutos está en `https://<usuario>.github.io/<repositorio>/`.

Para actualizar la app: sube el `index.html` nuevo y **sube el número de `CACHE` en
`sw.js`**. Los móviles cogerán la versión nueva solos.

## Instalar en el móvil

Abre la dirección en Chrome y elige **Añadir a pantalla de inicio**. Queda como una app:
icono propio, pantalla completa, y abre sin cobertura.

## Trabajar sin cobertura

Funciona entero sin red: rellenar, hacer fotos, grabar audio, generar el PDF y el paquete.
Solo hace falta conexión para dos cosas:

- la primera vez que se abre la app, y
- para **descargar la licitación** antes de salir a campo.

Cada licitación se descarga una vez desde la pantalla de inicio (el botón *descargar*
pasa a decir *offline*) y a partir de ahí vive en el móvil. Los partes se guardan
continuamente en el propio teléfono; si el envío falla, el parte queda *pendiente* y se
reintenta luego. No se pierde nada aunque se cierre la app o se acabe la batería.

## Dar de alta una licitación

Ver **[PLANTILLAS.md](PLANTILLAS.md)**: es el contrato del JSON que genera la skill de
planificación de oferta, con todos los campos y tipos de pregunta.

En resumen: dejas `plantillas/exp-XXXX.json` en el repositorio y añades una línea a
`plantillas/index.json`. Antes de publicar, el JSON se puede validar desde la propia app
con **Importar plantilla**.

## Qué sale de cada parte

```
2026-014-20260920-1921.zip
├── parte.json      ← los datos, con guía de lectura y lista de hallazgos
├── parte.md        ← el mismo parte en markdown, para dárselo a un LLM
├── indice.csv      ← una fila por adjunto y por nota, para Power Query
├── 2026-014-…​.pdf  ← el parte escrito y maquetado, con las fotos
└── media/
    ├── q09-01.jpg
    ├── q09-02.jpg
    └── q14-01.webm
```

**`qNN-MM.ext`**: NN es el número de pregunta y MM el del adjunto dentro de ella. Corto,
ordenable, y el JSON y el CSV dicen a qué corresponde cada uno.

**`parte.json`** abre con un bloque `_guia` que explica en castellano cómo leerlo, para
que un modelo no tenga que adivinar la estructura. Después:

- `expediente` y `centro`: a qué licitación pertenece la visita.
- `hallazgos`: la lista plana de lo que **no** está bien, ordenada por gravedad, cada uno
  con su valoración, las notas del técnico y las rutas de sus fotos. Esto es lo que
  alimenta la memoria técnica.
- `secciones[].preguntas[]`: el checklist completo, con `respuesta` en crudo,
  `respuestaTexto` legible y `gravedad`.
- `adjuntos` y `notas`: índices planos donde cada entrada repite su pregunta y enunciado.

**`parte.md`** es el mismo contenido en prosa y tablas. Para pedirle a un modelo que
redacte la memoria, este es el fichero que le das.

## Configurar el envío

Al principio del `<script>` de `index.html`:

```js
destino: "compartir"   // "compartir" | "flow" | "graph"
```

- **`compartir`** — abre la hoja de compartir del móvil con el PDF, el markdown y las
  fotos. No hay que montar nada.
- **`flow`** — POST a un flujo de Power Automate. Rellena `flowUrl`. Ojo: esa URL queda
  visible en el código publicado.
- **`graph`** — el técnico inicia sesión con su cuenta de UNEI y el parte sube solo a una
  biblioteca de SharePoint, organizado por expediente. Rellena el bloque `graph` con los
  datos del registro de aplicación de Entra ID. Los ficheros de más de 4 MB suben por
  sesión de carga, así que los vídeos también pasan.

## Límites

- Una foto comprimida ocupa entre 150 y 400 KB; un minuto de audio, medio mega.
- Un vídeo de 30 segundos son 30–60 MB: úsalos con criterio.
- El paquete se construye en memoria, así que en un móvil de gama media conviene
  no pasar de **40 adjuntos** por parte. La app avisa al acercarse.
- El almacenamiento del móvil da de sobra: son varios GB.
