import re

def analyze(self, data):

class ScenarioClassifier:

    def __init__(self):

        self.header_pattern = re.compile(
            r"^\d+(?:\.\d+)+$"
        )

    def classify(self, analyses):

        escenarios = []

        escenario_actual = None

        for indice, analisis in enumerate(analyses):

            lineas = [
                linea.strip()
                for linea in analisis.splitlines()
                if linea.strip()
            ]

            codigo = None
            titulo = None
            descripcion = None

            for i, linea in enumerate(lineas):

                if self.header_pattern.match(linea):

                    codigo = linea

                    if i + 1 < len(lineas):
                        titulo = lineas[i + 1]

                    if i + 2 < len(lineas):
                        descripcion = lineas[i + 2]

                    break

            if codigo:

                if escenario_actual:
                    escenarios.append(
                        escenario_actual
                    )

                escenario_actual = {
                    "scenario_id": codigo,
                    "scenario_name": titulo or "",
                    "scenario_description": descripcion or "",
                    "scenario_type": self._detect_type(
                        titulo,
                        descripcion
                    ),
                    "screens": [indice]
                }

            elif escenario_actual:

                escenario_actual["screens"].append(
                    indice
                )

        if escenario_actual:
            escenarios.append(
                escenario_actual
            )

        return escenarios

    def _detect_type(
        self,
        title,
        description
    ):

        texto = (
            f"{title or ''} {description or ''}"
        ).lower()

        negativos = [
            "error",
            "rechazo",
            "falla",
            "fallido",
            "timeout",
            "no disponible",
            "reintentar",
            "inválido",
            "incorrecto"
        ]

        alternos = [
            "alterno",
            "opcional",
            "contingencia"
        ]

        for palabra in negativos:

            if palabra in texto:
                return "NEGATIVE"

        for palabra in alternos:

            if palabra in texto:
                return "ALTERNATE"

        return "HAPPY_PATH"

