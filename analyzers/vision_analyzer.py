import ollama


class VisionAnalyzer:

    def __init__(self):
        self.model = "qwen2.5vl:7b-q8_0"

        self.prompt = self.prompt = self.prompt = self.prompt = """
            Eres un extractor de evidencia funcional.
            
            Analiza la evidencia visual proporcionada.
            
            Tu responsabilidad NO es actuar como Analista QA.
            
            NO generes:
            
            - objetivos funcionales
            - funcionalidades del negocio
            - validaciones
            - reglas de negocio
            - riesgos
            - cobertura
            - escenarios de prueba
            - inferencias
            - conclusiones
            
            Tu única responsabilidad es extraer evidencia observable.
            
            INSTRUCCIONES:
            
            1. Describe únicamente la funcionalidad principal mostrada en el área central de la pantalla.
            
            2. Ignora:
               - menús superiores
               - menús laterales
               - encabezados corporativos
               - pie de página
               - navegación global
               - accesos rápidos
               - información repetitiva
            
            3. Si existen varios elementos visibles, prioriza únicamente aquellos relacionados con el flujo analizado.
            
            4. No repitas información.
            
            5. Si un texto aparece varias veces:
               reporta únicamente una ocurrencia.
            
            6. No interpretes el propósito de negocio.
            
            7. No expliques para qué sirve la pantalla.
            
            8. Extrae únicamente información visible.
            
            9. Si un dato no es visible, no lo inventes.
            
            10. Resume la evidencia relevante para que posteriormente sea procesada por otro analizador.
            
            Responde EXACTAMENTE con el siguiente formato:
            
            PANTALLA:
            Breve nombre descriptivo de la pantalla.
            
            DATOS OBSERVADOS:
            - ...
            
            ACCIONES DISPONIBLES:
            - ...
            
            MENSAJES OBSERVADOS:
            - ...
            
            OBSERVACIONES:
            - ...
            """

    def analyze(self, image_paths):
        response = ollama.chat(
            model=self.model,
            options={
                "num_ctx": 8192
            },
            messages=[
                {
                    "role": "user",
                    "content": self.prompt,
                    "images": image_paths
                }
            ]
        )

        resultado = response["message"]["content"]

        print("\n=== ANALISIS DE PANTALLA ===\n")
        print(resultado)

        return resultado