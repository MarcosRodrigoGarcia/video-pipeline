"""Plantillas de prompts para cada tipo de documento."""


MEETING_NOTES = """Eres un asistente experto en documentación. Tu tarea es transformar una transcripción de vídeo en un documento estructurado con formato de acta o notas de reunión.

REGLAS:
- Responde SOLO con el documento en formato Markdown, sin explicaciones ni comentarios adicionales.
- Usa encabezados ## para cada sección temática que identifiques.
- Dentro de cada sección, resume los puntos clave de forma clara y concisa.
- Si hay opiniones o argumentos, atribúyelos al hablante cuando sea posible.
- Incluye una sección final de "Conclusiones" o "Puntos clave" con los elementos más importantes.
- Escribe en el mismo idioma que la transcripción.
- No inventes información que no esté en la transcripción.
- El título del documento debe ser un encabezado # que resuma el tema principal.

TRANSCRIPCIÓN:
{transcription}

DOCUMENTO ESTRUCTURADO:"""


SUMMARY = """Eres un asistente experto en documentación. Tu tarea es generar un resumen ejecutivo a partir de una transcripción de vídeo.

REGLAS:
- Responde SOLO con el resumen en formato Markdown, sin explicaciones ni comentarios adicionales.
- Usa un encabezado # como título.
- Incluye una sección "Resumen" con 2-3 párrafos que capturen la esencia del contenido.
- Incluye una sección "Puntos clave" con los elementos más importantes como lista.
- Escribe en el mismo idioma que la transcripción.
- No inventes información que no esté en la transcripción.

TRANSCRIPCIÓN:
{transcription}

RESUMEN EJECUTIVO:"""


TUTORIAL = """Eres un asistente experto en documentación técnica. Tu tarea es transformar una transcripción de vídeo tutorial en un documento paso a paso.

REGLAS:
- Responde SOLO con el documento en formato Markdown, sin explicaciones ni comentarios adicionales.
- Usa un encabezado # como título del tutorial.
- Organiza el contenido en pasos secuenciales con ## para cada paso.
- Dentro de cada paso, explica qué hacer de forma clara y directa.
- Si se mencionan herramientas, comandos o configuraciones, inclúyelos.
- Incluye una sección de "Requisitos previos" si aplica.
- Escribe en el mismo idioma que la transcripción.
- No inventes información que no esté en la transcripción.

TRANSCRIPCIÓN:
{transcription}

TUTORIAL:"""


# Mapa de tipos disponibles
PROMPT_TEMPLATES = {
    "meeting_notes": MEETING_NOTES,
    "summary": SUMMARY,
    "tutorial": TUTORIAL,
}


def get_prompt(doc_type: str, transcription: str) -> str:
    """
    Genera el prompt completo para un tipo de documento.
    
    Args:
        doc_type: Tipo de documento (meeting_notes, summary, tutorial).
        transcription: Texto de la transcripción.
    
    Returns:
        Prompt completo listo para enviar al LLM.
    """
    if doc_type not in PROMPT_TEMPLATES:
        raise ValueError(f"Tipo '{doc_type}' no válido. Usa: {list(PROMPT_TEMPLATES.keys())}")
    
    return PROMPT_TEMPLATES[doc_type].format(transcription=transcription)