import ollama

class ScenarioAnalyzer:

    def __init__(self):

        self.model = "qwen2.5:7b"

        self.prompt = """
Eres un Analista QA Senior especializado en análisis funcional.

Recibirás evidencia consolidada de varias pantallas
que pertenecen a una misma casuística.

Las pantallas ya fueron procesadas previamente.

NO describas cada pantalla por separado.

Tu responsabilidad es reconstruir la funcionalidad completa
que representa el flujo.

Piensa como si recibieras una especificación funcional
incompleta y tuvieras que entender:

- Qué quiere lograr el usuario.
- Qué pasos sigue.
- Qué funcionalidades existen.
- Qué validaciones están documentadas.
- Qué reglas de negocio aparecen.
- Qué riesgos funcionales existen.
- Qué cobertura funcional está documentada.

IMPORTANTE:

1. Consolida información repetida.

2. Elimina ruido generado por navegación,
menús y encabezados.

3. Prioriza únicamente la funcionalidad principal.

4. Distingue información observada
de información inferida.

5. No generes todavía casos de prueba.

6. Construye una historia funcional coherente.

Responde EXACTAMENTE con el siguiente formato:

CASUISTICA:
...

OBJETIVO DE NEGOCIO:
...

FLUJO FUNCIONAL:
1.
2.
3.

FUNCIONALIDADES:
- ...

DATOS RELEVANTES CAPTURADOS:
- ...

VALIDACIONES OBSERVADAS:
- ...

VALIDACIONES INFERIDAS:
- ...

REGLAS DE NEGOCIO OBSERVADAS:
- ...

REGLAS DE NEGOCIO INFERIDAS:
- ...

RIESGOS FUNCIONALES:
- ...

COBERTURA OBSERVADA:
- ...

ESCENARIOS EXPLICITOS DETECTADOS:
- ...

TIPO DE CASUISTICA:
HAPPY_PATH | NEGATIVE | ALTERNATE | MIXED

REQUIERE INFERENCIA:
SI | NO

JUSTIFICACION:
...
"""

    def analyze(
        self,
        scenario_info,
        screen_analyses
    ):

        scenario_name = scenario_info.get(
            "scenario_name",
            "Sin nombre"
        )

        scenario_id = scenario_info.get(
            "scenario_id",
            "FLOW"
        )

        evidencia = "\n\n".join(
            screen_analyses
        )

        contenido = f"""
CASUISTICA

ID:
{scenario_id}

NOMBRE:
{scenario_name}

EVIDENCIA EXTRAIDA:

{evidencia}
"""

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.prompt
                },
                {
                    "role": "user",
                    "content": contenido
                }
            ]
        )

        return response["message"]["content"]
