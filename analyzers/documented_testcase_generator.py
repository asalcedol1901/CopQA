import json

import ollama

class DocumentedTestCaseGenerator:

    def __init__(self):
        self.model = "qwen2.5:7b"

        self.prompt = """
Eres un Analista QA Senior.

Toma como fuente de verdad el ALCANCE y el ANALISIS FUNCIONAL.
La estrategia solo indica prioridades; no es evidencia de que un dato,
control o comportamiento exista.

Devuelve únicamente JSON válido con esta estructura:
{
  "test_cases": [
    {
      "id": "CP-001",
      "name": "Nombre del caso",
      "input_data": ["Dato documentado"],
      "steps": [
        {
          "action": "Acción documentada",
          "expected_result": "Consecuencia específica de esa acción"
        }
      ]
    }
  ],
  "no_cases_reason": []
}

REGLAS OBLIGATORIAS:
- Genera casos únicamente para funcionalidades y escenarios dentro del
  alcance. Excluye lo marcado fuera de alcance.
- Usa solo acciones y comportamientos expresamente descritos en el
  análisis funcional. No inventes pantallas, botones, menús,
  confirmaciones, mensajes ni transiciones.
- No inventes valores de entrada, límites, tasas, CAT, resultados, reglas
  de negocio ni datos de prueba. Usa únicamente valores literales del
  alcance o de la evidencia.
- No conviertas datos visualizados en datos capturados.
- Las inferencias y los riesgos no prueban que exista una validación;
  no los presentes como comportamiento esperado.
- Si el resultado esperado no está documentado, escribe
  "No especificado en la evidencia"; no deduzcas un mensaje, rechazo,
  cálculo ni éxito.
- Si un escenario en alcance carece de acciones o resultados
  documentados suficientes, omítelo. No completes los huecos.
- Cada elemento de "steps" debe contener una sola acción y su
  "expected_result" correspondiente. La consecuencia esperada debe
  referirse específicamente a esa acción, no a otra ni a todo el flujo.
- No crees listas separadas de pasos y resultados: cada acción y su
  resultado esperado deben permanecer en el mismo objeto JSON.
- No agregues casos negativos, alternos o de borde salvo que estén
  explícitamente en alcance y documentados.
- Agrupa campos relacionados; no generes un paso por campo.

CRITERIOS SEGÚN EL TIPO DE PRUEBA:
- ACEPTACION: prioriza los flujos exitosos documentados que demuestran el
  cumplimiento del objetivo de negocio. No agregues pruebas negativas
  salvo que estén explícitamente solicitadas y documentadas.
- REGRESION: genera casos solo para funcionalidades existentes que podrían
  verse afectadas por un cambio identificado en la evidencia. No inventes el
  cambio ni las áreas impactadas. Si no se identifica el cambio o el impacto,
  devuelve "test_cases": [] y explica en "no_cases_reason" qué información
  falta; no presentes la cobertura como completa.
- INTEGRACION: valida únicamente interacciones entre componentes y contratos
  documentados en el análisis funcional. No inventes componentes,
  integraciones ni contratos. Si no hay interacciones documentadas, devuelve
  "test_cases": [] y explica esa limitación en "no_cases_reason".

La estrategia orienta las prioridades, pero no sustituye la evidencia
necesaria para identificar cambios, impactos o integraciones.

Si no hay casos sustentados por evidencia, usa "test_cases": [] y explica
en "no_cases_reason" qué información falta.
"""

    def generate(
            self,
            test_type,
            scope_analysis,
            functional_analysis,
            strategy_analysis
    ):
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.prompt
                },
                {
                    "role": "user",
                    "content": f"""
TIPO DE PRUEBA SOLICITADO:
{test_type}

ALCANCE ANALIZADO:
{scope_analysis}

ANALISIS FUNCIONAL (FUENTE DE EVIDENCIA):
{functional_analysis}

ESTRATEGIA (SOLO COMO PRIORIDAD, NO COMO EVIDENCIA):
{strategy_analysis}
"""
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

        content = response["message"]["content"]

        try:
            result = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"El generador no devolvió JSON válido: {content}"
            ) from error

        if not isinstance(result, dict):
            raise ValueError(
                "La respuesta del generador debe ser un objeto JSON."
            )

        test_cases = result.get("test_cases")
        if not isinstance(test_cases, list):
            raise ValueError(
                "La respuesta debe incluir una lista 'test_cases'."
            )

        if not test_cases:
            reasons = result.get("no_cases_reason", [])
            if not isinstance(reasons, list):
                raise ValueError(
                    "'no_cases_reason' debe ser una lista."
                )
            reason_text = "\n".join(
                f"- {reason}" for reason in reasons
            )
            if not reason_text:
                reason_text = (
                    "- La evidencia no especifica acciones y resultados "
                    "suficientes para construir casos."
                )
            return f"NO SE GENERARON CASOS:\n{reason_text}"

        rendered_cases = []
        for case in test_cases:
            if not isinstance(case, dict):
                raise ValueError(
                    "Cada caso de prueba debe ser un objeto JSON."
                )

            case_id = self._required_text(case, "id")
            name = self._required_text(case, "name")
            input_data = case.get("input_data")
            steps = case.get("steps")

            if not isinstance(input_data, list) or not all(
                isinstance(item, str) and item.strip()
                for item in input_data
            ):
                raise ValueError(
                    f"'input_data' inválido en el caso {case_id}."
                )

            if not isinstance(steps, list) or not steps:
                raise ValueError(
                    f"El caso {case_id} debe tener al menos un paso."
                )

            actions = []
            expected_results = []
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    raise ValueError(
                        f"El paso {index} del caso {case_id} "
                        "debe ser un objeto JSON."
                    )

                actions.append(
                    self._required_text(step, "action", case_id, index)
                )
                expected_results.append(
                    self._required_text(
                        step,
                        "expected_result",
                        case_id,
                        index
                    )
                )

            lines = [
                "CASO DE PRUEBA:",
                case_id,
                "",
                "NOMBRE DEL CASO:",
                name,
                "",
                "DATOS DE ENTRADA:"
            ]
            lines.extend(
                f"- {item}" for item in input_data
            )
            if not input_data:
                lines.append("- No especificados en la evidencia")

            lines.extend([
                "",
                "PASOS:"
            ])
            lines.extend(
                f"{index}. {action}"
                for index, action in enumerate(actions, start=1)
            )
            lines.extend([
                "",
                "RESULTADO ESPERADO:"
            ])
            lines.extend(
                f"{index}. {expected_result}"
                for index, expected_result in enumerate(
                    expected_results,
                    start=1
                )
            )
            rendered_cases.append("\n".join(lines))

        return "\n\n---\n\n".join(rendered_cases)

    @staticmethod
    def _required_text(data, key, case_id=None, step_number=None):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            location = ""
            if case_id is not None:
                location = f" en paso {step_number} del caso {case_id}"
            elif "id" in data:
                location = f" en el caso {data['id']}"
            raise ValueError(
                f"El campo '{key}' debe ser texto no vacío{location}."
            )
        return value.strip()