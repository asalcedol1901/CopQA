import json
import re
import requests

PROMPT_QA = """
Actúa como un Analista QA Senior especializado en banca digital.

Analiza la evidencia proporcionada y genera el número de casos de prueba funcionales de happy path, negative cases y edge cases mínimos necesarios para una no afectación, utilizando únicamente la información observada.

Objetivo:

Reconstrucción del flujo

La evidencia contiene múltiples capturas consecutivas del mismo flujo.

- Debes reconstruir el flujo completo respetando el orden de aparición de las capturas.
- No adelantar acciones observadas en pantallas posteriores.
- No utilizar información de una pantalla futura para generar pasos anteriores.

Durante el análisis identifica:

- Acciones realizadas por el usuario.
- Información mostrada por el sistema.
- Elementos de captura.
- Opciones disponibles.
- Cambios de estado de la pantalla.
- Mensajes.
- Resultados.
- Comprobantes.

Cuando una acción provoque cambios en la pantalla:

- Generar pasos de validación.
- Validar la información mostrada como resultado de dicha acción.

Cuando una pantalla muestre información relevante:

- Incluir dicha información en los resultados esperados.
- Evitar resultados genéricos.

Los resultados esperados deben describir claramente qué información debe visualizarse después de cada acción.

Devuelve exclusivamente JSON válido con la estructura:

{
  "test_cases": [
    {
      "id": "CP-001",
      "tipo": " ",
      "condicion": "",
      "pasos": [
        {
          "descripcion": "",
          "resultado": ""
        }
      ]
    }
  ]
}

EVIDENCIA:

{requirements}
"""


class TestCaseGenerator:

    def __init__(self):
        self.url = "http://localhost:11434/api/generate"

        # CAMBIA ESTE NOMBRE SI DESCARGASTE OTRO MODELO
        self.model = "qwen2.5:7b"

    def generate(self, requirements):

        if not requirements or requirements.strip() == "":
            raise ValueError(
                "El texto de los requerimientos está vacío."
            )

        prompt_final = PROMPT_QA.replace(
            "{requirements}",
            requirements
        )

        print("Llamando a Ollama...")
        print("Modelo utilizado:", self.model)

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt_final,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            }
        )

        response.raise_for_status()

        contenido = response.json()["response"]

        print("Respuesta recibida de Ollama")
        print(contenido)

        resultado = self._extraer_json(contenido)

        if "test_cases" not in resultado:
            raise ValueError(
                f"Ollama no devolvió la clave test_cases:\n{contenido}"
            )

        return resultado

    def _extraer_json(self, texto):

        try:
            return json.loads(texto)

        except json.JSONDecodeError:

            patron = r"\{.*\}"

            coincidencia = re.search(
                patron,
                texto,
                re.DOTALL
            )

            if coincidencia:
                return json.loads(
                    coincidencia.group()
                )

            raise ValueError(
                f"No se encontró JSON válido:\n{texto}"
            )