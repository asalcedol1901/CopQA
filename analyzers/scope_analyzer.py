import ollama



class ScopeAnalyzer:

    def __init__(self):
        self.model = "qwen2.5:7b"

        self.prompt = """
            Eres un Líder QA.
            
            Recibirás:
            
            1. Un alcance de pruebas.
            2. Un análisis funcional.
            
            Tu objetivo es determinar qué funcionalidades
            están dentro y fuera del alcance.
            
            NO generes casos de prueba.
            
            NO generes cobertura.
            
            NO infieras funcionalidades inexistentes.
            
            Responde exactamente con el formato:
            
            ALCANCE:
            ...
            
            FUNCIONALIDADES EN ALCANCE:
            - ...
            
            FUNCIONALIDADES FUERA DE ALCANCE:
            - ...
            
            ESCENARIOS EN ALCANCE:
            - ...
            
            ESCENARIOS FUERA DE ALCANCE:
            - ...
            
            JUSTIFICACION:
            ...
            """

    def analyze(
            self,
            scope,
            scenario_analysis
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
ALCANCE:

{scope}

ANALISIS FUNCIONAL:

{scenario_analysis}
"""
                }
            ]
        )

        return response["message"]["content"]

