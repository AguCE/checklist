# Partes de campo — UNEI

Aplicación web para que los técnicos de campo rellenen partes de control en el móvil:
checklist por secciones, fotos, vídeos, audios y notas colgando de cada pregunta,
ubicación GPS y salida en JSON.

No necesita servidor ni base de datos. Es un fichero HTML servido como página estática.

## Publicar

1. Sube los ficheros de esta carpeta a la raíz del repositorio.
2. En el repositorio: **Settings → Pages**.
3. En *Source*, elige **Deploy from a branch**, rama `main` y carpeta `/ (root)`. Guarda.
4. A los pocos minutos la app estará en `https://<usuario>.github.io/<repositorio>/`.

## Instalar en el móvil

Abre esa dirección en Chrome y elige **Añadir a pantalla de inicio**. A partir de ahí
funciona como una app: icono propio, pantalla completa y abre sin cobertura.

## Configurar

Todo lo configurable está al principio del `<script>` de `index.html`.

### `CONFIG` — a dónde se envía el parte

```js
destino: "compartir"   // "compartir" | "flow" | "graph"
```

- **`compartir`** (por defecto): genera un ZIP con `parte.json` y los medios, y abre la
  hoja de compartir del móvil. No hay que montar nada.
- **`flow`**: envía el paquete a un flujo de Power Automate. Rellena `flowUrl`.
  El flujo recibe el ZIP en `zipBase64` y lo escribe en SharePoint con
  `base64ToBinary(triggerBody()?['zipBase64'])`.
  **Atención:** esa URL queda visible en el código publicado; cualquiera que la lea
  puede escribir en la carpeta de destino.
- **`graph`**: el técnico inicia sesión con su cuenta de UNEI y el parte sube
  directamente a una biblioteca de SharePoint. Rellena el bloque `graph` con los datos
  del registro de aplicación de Entra ID. No expone ningún secreto.

### `PLANTILLA` — el contenido del checklist

Secciones, preguntas y tipos de respuesta. Cambiar el checklist, o crear el de
jardinería o conserjería, es editar este objeto: no hay que tocar el resto del código.

Tipos de pregunta admitidos:

| tipo | qué muestra |
|---|---|
| `escala` | Bien / Mejorable / No conforme / N/A (cuenta para el % de cumplimiento) |
| `opcion` | una sola opción de las que definas |
| `opcion_multiple` | varias opciones a la vez |
| `texto` | texto libre (añade `largo: true` para un área grande) |
| `numero` | valor numérico |

## Cómo salen los datos

```
parte_ResidenciaNtraSra_20260918_b7f3a1c2.zip
├── parte.json
└── media/
    ├── foto-1a2b3c4d.jpg
    └── audio-5e6f7a8b.webm
```

`parte.json` lleva la cabecera de la visita, el GPS, y por cada pregunta su enunciado,
su respuesta, sus notas y la lista de adjuntos con la ruta al fichero correspondiente.

## Actualizar la app

Sube la versión nueva de `index.html` y **sube el número de `CACHE` en `sw.js`**
(por ejemplo de `partes-unei-v1` a `partes-unei-v2`). Los móviles se actualizarán
solos la próxima vez que abran la app con datos.
