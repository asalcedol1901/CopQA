from openpyxl import Workbook
from openpyxl.styles import Font


class ExcelExporter:

    def export(self, test_cases, output_file):

        wb = Workbook()

        ws = wb.active

        ws.title = "Casos de Prueba"

        headers = [
            "Identificador único (ID)",
            "Condición y datos de entrada",
            "Descripción del caso",
            "Resultado esperado"
        ]

        for col, value in enumerate(headers, 1):

            cell = ws.cell(
                row=1,
                column=col
            )

            cell.value = value
            cell.font = Font(bold=True)

        row = 2

        for case in test_cases:

            condition = (
                f"Tipo de prueba: {case['tipo']} | "
                f"{case['condicion']}"
            )

            for idx, step in enumerate(case["pasos"]):

                if idx == 0:

                    ws.cell(row,1,case["id"])
                    ws.cell(row,2,condition)

                ws.cell(
                    row,
                    3,
                    step["descripcion"]
                )

                ws.cell(
                    row,
                    4,
                    step["resultado"]
                )

                row += 1

        wb.save(output_file)