import ollama


class TestingStrategyAnalyzer:

    def __init__(self):
        self.model = "qwen2.5:7b"

        self.prompt = """
            Eres un QA Lead especializado en diseño de estrategias de prueba.
            
            Recibirás:
            
            1. Tipo de prueba.
            2. Alcance filtrado.
            3. Análisis funcional.
            
            Tu responsabilidad es definir QUÉ debe probarse.
            
            NO generes todavía casos de prueba.
            
            NO describas pasos detallados.
            
            NO generes escenarios negativos inventados.
            
            Debes construir una estrategia que posteriormente
            será utilizada por un generador de casos.
            
            Analiza dependiendo del tipo solicitado:
            
            - ACEPTACION: cubrir los flujos exitosos que demuestran el cumplimiento
              del objetivo de negocio, dentro del alcance. No priorizar escenarios
              negativos salvo que se soliciten explícitamente.
              
            - REGRESION: volver a validar funcionalidades existentes que podrían
              verse afectadas por un cambio. No inventar cambios ni áreas impactadas;
              si no se proporciona información del cambio, indicarlo.
              
            - INTEGRACION: validar las interacciones entre componentes que estén
              identificadas en el análisis funcional. No inventar componentes ni
              contratos de integración.
                        
            IMPORTANTE:
            
            Las maquetas suelen representar
            principalmente happy paths.
            
            Si determinada información no está presente en la maqueta,
            indícalo explícitamente.
            
            Responde EXACTAMENTE con el siguiente formato:
            
            TIPO DE PRUEBA:
            ...
            
            OBJETIVO:
            ...
            
            OBJETOS DE PRUEBA:
            - ...
            
            FUNCIONALIDADES A VALIDAR:
            - ...
            
            CASUISTICAS A CUBRIR:
            - ...
            
            VALIDACIONES PRIORITARIAS:
            - ...
            
            DATOS CRITICOS:
            - ...
            
            EXCLUSIONES:
            - ...
            
            RIESGOS PRINCIPALES:
            - ...
            
            CRITERIO DE COBERTURA:
            ...
            
            RECOMENDACION QA:
            ...
            """

    def analyze(
            self,
            test_type,
            scope_analysis,
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
TIPO DE PRUEBA:

{test_type}

ALCANCE ANALIZADO:

{scope_analysis}

ANALISIS FUNCIONAL:

{scenario_analysis}
"""
                }
            ]
        )

        return response["message"]["content"]