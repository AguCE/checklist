#!/usr/bin/env python3
"""
Convierte el checklist-campo.yaml que genera la skill de planificación de oferta
en la plantilla JSON que consume la app de partes de campo.

    python3 yaml-a-plantilla.py  <expediente>/30.Planificacion/checklist-campo.yaml  \
                                 --centro "Residencia Ntra. Sra. de la Paz"           \
                                 --direccion "Avda. de la Paz, 14 — 41010 Sevilla"    \
                                 --organismo "Agencia de Servicios Sociales"          \
                                 --salida plantillas/

Deja el .json en la carpeta de salida y actualiza plantillas/index.json.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import date

try:
    import yaml
except ImportError:
    sys.exit("Falta PyYAML.  pip install pyyaml")


# El YAML de la skill trae tipos pensados para el pliego; la app tiene los suyos.
TIPOS = {
    "text":          ("texto", {}),
    "textarea":      ("texto", {"largo": True}),
    "single_select": ("opcion", {}),
    "multi_select":  ("opcion_multiple", {}),
    "boolean":       ("opcion", {"opciones": ["Sí", "No"]}),
    "number":        ("numero", {}),
    "scale":         ("escala", {}),
    "datetime":      ("fecha", {}),
    # Estos no piden una respuesta, piden evidencia. En la app toda pregunta
    # admite adjuntos, así que se convierten en un bloque solo de adjuntos.
    "geo":           ("adjunto", {}),
    "photo":         ("adjunto", {}),
    "video":         ("adjunto", {}),
    "note":          ("adjunto", {}),
}

ESCALA = [
    {"v": "ok",  "l": "Bien",        "peso": 1,    "tono": "ok",   "significado": "cumple lo exigido"},
    {"v": "mej", "l": "Mejorable",   "peso": 0.5,  "tono": "warn", "significado": "cumple con deficiencias"},
    {"v": "nc",  "l": "No conforme", "peso": 0,    "tono": "bad",  "significado": "no cumple"},
    {"v": "na",  "l": "N/A",         "peso": None, "tono": "na",   "significado": "no aplica; no puntúa"},
]


def slug(texto, largo=40):
    t = unicodedata.normalize("NFD", str(texto or ""))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:largo] or "sin-id"


def convertir(doc, centro="", direccion="", organismo="", plantilla_id=None, nombre=None):
    ch = doc.get("checklist") or doc
    exp_codigo = str(ch.get("expediente") or "").strip()
    lote = str(ch.get("lote") or "").strip()
    if lote in ("-", "None"):
        lote = ""

    pid = plantilla_id or ("exp-" + slug(exp_codigo, 24) + ("-l" + slug(lote, 6) if lote else ""))

    avisos = []
    secciones = []

    for s in ch.get("secciones") or []:
        preguntas = []
        for q in s.get("preguntas") or []:
            bruto = (q.get("type") or "scale").strip()
            if bruto not in TIPOS:
                avisos.append("Tipo desconocido «%s» en %s: se deja como texto." % (bruto, q.get("id")))
                tipo, extra = "texto", {}
            else:
                tipo, extra = TIPOS[bruto]

            p = {
                "id": slug(q.get("id") or "", 30),
                "enunciado": (q.get("label") or "").strip(),
                "tipo": tipo,
            }
            p.update(extra)

            if q.get("options"):
                p["opciones"] = [str(o) for o in q["options"]]
            if q.get("required"):
                p["requerido"] = True

            ayuda = (q.get("help") or "").strip()
            if bruto == "number" and q.get("unit"):
                ayuda = ("En %s. " % q["unit"] + ayuda).strip()
                p["unidad"] = str(q["unit"])
            if bruto in ("photo", "video", "note", "geo"):
                pista = {
                    "photo": "Adjunta las fotos con el botón Foto.",
                    "video": "Adjunta el clip con el botón Vídeo.",
                    "note":  "Escribe lo observado con el botón Nota.",
                    "geo":   "Captura la ubicación con el botón de arriba.",
                }[bruto]
                ayuda = (ayuda + " " + pista).strip()
            if ayuda:
                p["ayuda"] = ayuda

            # Lo que ata la visita con la memoria técnica: se conserva tal cual.
            if q.get("maps_to"):
                p["mapea_a"] = str(q["maps_to"]).strip()
            else:
                avisos.append("La pregunta %s no tiene maps_to: su hallazgo no sabrá a qué epígrafe alimenta." % q.get("id"))

            if not p["enunciado"]:
                avisos.append("La pregunta %s no tiene label." % q.get("id"))
            preguntas.append(p)

        if not preguntas:
            avisos.append("La sección %s se queda sin preguntas." % s.get("id"))
            continue

        secciones.append({
            "id": slug(s.get("id") or "", 20),
            "titulo": (s.get("nombre") or s.get("id") or "").strip(),
            "preguntas": preguntas,
        })

    plantilla = {
        "id": pid,
        "version": 1,
        "nombre": nombre or ("Visita técnica — " + (centro or exp_codigo or pid)),
        "origen": {
            "generadoDesde": "checklist-campo.yaml",
            "skill": "planificacion-oferta",
            "convertidoEl": date.today().isoformat(),
        },
        "expediente": {
            "codigo": exp_codigo,
            "objeto": (ch.get("objeto") or "").strip(),
            "lote": lote,
            "organismo": organismo,
        },
        "centro": {"nombre": centro, "direccion": direccion},
        "escala": ESCALA,
        "secciones": secciones,
    }
    # Fuera lo que esté vacío, para que el JSON quede limpio de revisar.
    plantilla["expediente"] = {k: v for k, v in plantilla["expediente"].items() if v}
    plantilla["centro"] = {k: v for k, v in plantilla["centro"].items() if v}

    n = sum(len(s["preguntas"]) for s in secciones)
    return plantilla, avisos, n


def actualizar_catalogo(carpeta, plantilla):
    ruta = os.path.join(carpeta, "index.json")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            cat = json.load(f)
    else:
        cat = {"actualizado": "", "plantillas": []}

    entrada = {
        "id": plantilla["id"],
        "fichero": plantilla["id"] + ".json",
        "nombre": plantilla["nombre"],
        "expediente": {k: plantilla.get("expediente", {}).get(k, "")
                       for k in ("codigo", "lote") if plantilla.get("expediente", {}).get(k)},
        "centro": {"nombre": plantilla.get("centro", {}).get("nombre", "")},
        "version": plantilla["version"],
    }
    cat["plantillas"] = [p for p in cat.get("plantillas", []) if p.get("id") != plantilla["id"]]
    cat["plantillas"].insert(0, entrada)
    cat["actualizado"] = date.today().isoformat()

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=2)
    return ruta


def main():
    ap = argparse.ArgumentParser(description="checklist-campo.yaml → plantilla de la app de partes")
    ap.add_argument("yaml", help="ruta del checklist-campo.yaml")
    ap.add_argument("--centro", default="", help="nombre del centro que se visita")
    ap.add_argument("--direccion", default="", help="dirección del centro")
    ap.add_argument("--organismo", default="", help="órgano de contratación")
    ap.add_argument("--id", default=None, help="id de la plantilla (por defecto se deduce del expediente)")
    ap.add_argument("--nombre", default=None, help="título que verá el técnico")
    ap.add_argument("--salida", default="plantillas", help="carpeta de plantillas de la app")
    ap.add_argument("--sin-catalogo", action="store_true", help="no tocar index.json")
    args = ap.parse_args()

    with open(args.yaml, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    plantilla, avisos, n = convertir(
        doc, centro=args.centro, direccion=args.direccion,
        organismo=args.organismo, plantilla_id=args.id, nombre=args.nombre
    )

    os.makedirs(args.salida, exist_ok=True)
    destino = os.path.join(args.salida, plantilla["id"] + ".json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(plantilla, f, ensure_ascii=False, indent=2)

    print("Plantilla: %s" % destino)
    print("  %d secciones, %d preguntas" % (len(plantilla["secciones"]), n))
    if not args.sin_catalogo:
        print("Catálogo:  %s" % actualizar_catalogo(args.salida, plantilla))
    if avisos:
        print("\nRevisa antes de publicar:")
        for a in avisos:
            print("  · " + a)
    else:
        print("\nSin avisos: la conversión ha salido limpia.")


if __name__ == "__main__":
    main()
