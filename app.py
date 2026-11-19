import os
import unicodedata

from analyzers.documented_testcase_generator import (
    DocumentedTestCaseGenerator
)

from analyzers.scope_analyzer import (
    ScopeAnalyzer
)

from analyzers.testing_strategy_analyzer import (
    TestingStrategyAnalyzer
)

# Nombre del flujo
nombre_escenario = input(
    "Nombre del escenario o flujo: "
).strip()

if not nombre_escenario:
    nombre_escenario = "Flujo Evaluado"


# Alcance QA
scope = input(
    """
Ingresa el alcance:
"""
).strip()

if not scope:
    scope = nombre_escenario


# Tipo de prueba
print(
    """
Tipos de prueba disponibles:

1. ACEPTACION
2. REGRESION
3. INTEGRACION
"""
)

opciones_prueba = {
    "1": "ACEPTACION",
    "2": "REGRESION",
    "3": "INTEGRACION"
}

while True:
    entrada_tipo_prueba = input(
        "Selecciona tipo de prueba: "
    ).strip()

    tipo_normalizado = unicodedata.normalize(
        "NFKD",
        entrada_tipo_prueba
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    ).upper()
    tipo_normalizado = "_".join(
        tipo_normalizado.split()
    )

    if tipo_normalizado in opciones_prueba:
        test_type = opciones_prueba[tipo_normalizado]
        break

    if tipo_normalizado in opciones_prueba.values():
        test_type = tipo_normalizado
        break

    print(
        "Opción no válida. Ingresa 1-3 o el nombre del tipo "
        "(ACEPTACION, REGRESION, INTEGRACION)."
    )

# Fuente del análisis funcional
print(
    """
¿Cómo quieres obtener el análisis funcional?

1. Analizar nuevas maquetas y crear un archivo consolidado
2. Reutilizar un análisis consolidado existente
"""
)

while True:
    opcion_analisis = input(
        "Selecciona una opción (1-2): "
    ).strip()

    if opcion_analisis in ("1", "2"):
        break

    print("Opción no válida. Ingresa 1 o 2.")

generar_analisis = opcion_analisis == "1"

# Archivos generados
sufijo_flujo = (
    nombre_escenario.lower().replace(" ", "_")
)
sufijo_tipo_prueba = test_type.lower()

if generar_analisis:
    nombre_base_analisis = (
        f"analisis_consolidado_{sufijo_flujo}"
    )
    archivo_analisis = f"{nombre_base_analisis}.txt"
    version_analisis = 2

    while os.path.exists(archivo_analisis):
        archivo_analisis = (
            f"{nombre_base_analisis}_v{version_analisis:03d}.txt"
        )
        version_analisis += 1
else:
    archivo_analisis = input(
        "Ruta del archivo de análisis consolidado (.txt): "
    ).strip()

    if not os.path.isfile(archivo_analisis):
        raise FileNotFoundError(
            f"No se encontró el archivo de análisis: {archivo_analisis}"
        )

version = 1

while True:
    sufijo_salida = (
        f"{sufijo_flujo}_{sufijo_tipo_prueba}_v{version:03d}"
    )

    archivo_scope = (
        f"scope_analysis_{sufijo_salida}.txt"
    )

    archivo_strategy = (
        f"testing_strategy_{sufijo_salida}.txt"
    )

    archivo_casos = (
        f"casos_prueba_{sufijo_salida}.txt"
    )

    if not any(
        os.path.exists(archivo)
        for archivo in (
            archivo_scope,
            archivo_strategy,
            archivo_casos
        )
    ):
        break

    version += 1

# ===================================================
# ANALISIS FUNCIONAL
# ===================================================

resultado = None

if generar_analisis:
    from analyzers.vision_analyzer import (
        VisionAnalyzer
    )

    from analyzers.scenario_analyzer import (
        ScenarioAnalyzer
    )

    carpeta = input(
        "Ruta de carpeta con evidencias: "
    ).strip()

    if not os.path.isdir(carpeta):
        raise FileNotFoundError(
            f"No existe la carpeta de evidencias: {carpeta}"
        )

    imagenes = []

    for archivo in sorted(
        os.listdir(carpeta)
    ):

        if archivo.lower().endswith(
            (
                ".png",
                ".jpg",
                ".jpeg"
            )
        ):

            imagenes.append(
                os.path.join(
                    carpeta,
                    archivo
                )
            )

    if not imagenes:
        raise FileNotFoundError(
            f"No se encontraron imágenes en la carpeta: {carpeta}"
        )

    print(
        f"\nSe encontraron {len(imagenes)} imágenes."
    )

    vision = VisionAnalyzer()

    analisis_pantallas = []

    for indice, imagen in enumerate(
        imagenes,
        start=1
    ):

        print(
            f"\nAnalizando pantalla {indice}/{len(imagenes)}"
        )

        analisis = vision.analyze(
            [imagen]
        )

        analisis_pantallas.append(
            analisis
        )

    print(
        "\nGenerando análisis funcional...\n"
    )

    scenario_analyzer = (
        ScenarioAnalyzer()
    )

    escenario = {
        "scenario_name":
            nombre_escenario
    }

    resultado = scenario_analyzer.analyze(
        escenario,
        analisis_pantallas
    )

    with open(
        archivo_analisis,
        "w",
        encoding="utf-8"
    ) as archivo:

        archivo.write(
            resultado
        )

else:
    print(
        f"\nCargando análisis previo desde: {archivo_analisis}"
    )

    with open(
        archivo_analisis,
        "r",
        encoding="utf-8"
    ) as archivo:

        resultado = archivo.read()

if not isinstance(resultado, str) or not resultado.strip():
    raise ValueError(
        "El análisis funcional está vacío; no se puede continuar."
    )

# ===================================================
# SCOPE ANALYZER
# ===================================================

print(
    "\nAplicando ScopeAnalyzer..."
)

scope_analyzer = (
    ScopeAnalyzer()
)

scope_result = (
    scope_analyzer.analyze(
        scope,
        resultado
    )
)

with open(
    archivo_scope,
    "w",
    encoding="utf-8"
) as archivo:

    archivo.write(
        scope_result
    )

# ===================================================
# TESTING STRATEGY ANALYZER
# ===================================================

print(
    "\nGenerando estrategia de pruebas..."
)

strategy_analyzer = (
    TestingStrategyAnalyzer()
)

strategy_result = (
    strategy_analyzer.analyze(
        test_type,
        scope_result,
        resultado
    )
)

with open(
    archivo_strategy,
    "w",
    encoding="utf-8"
) as archivo:

    archivo.write(
        strategy_result
    )

# ===================================================
# TEST CASE GENERATION
# ===================================================

print(
    "\nGenerando casos de prueba..."
)

testcase_generator = (
    DocumentedTestCaseGenerator()
)

casos_prueba = (
    testcase_generator.generate(
        test_type,
        scope_result,
        resultado,
        strategy_result
    )
)

with open(
    archivo_casos,
    "w",
    encoding="utf-8"
) as archivo:

    archivo.write(
        casos_prueba
    )

# ===================================================
# SALIDA
# ===================================================

print(
    "\n" + "=" * 80
)

print(
    "TESTING STRATEGY"
)

print(
    "=" * 80 + "\n"
)

print(
    strategy_result
)

print(
    "\n" + "=" * 80
)

print(
    "CASOS DE PRUEBA"
)

print(
    "=" * 80 + "\n"
)

print(
    casos_prueba
)

print(
    "\n" + "=" * 80
)

print(
    "ARCHIVOS GENERADOS"
)

print(
    "=" * 80
)

print(
    f"\n- {archivo_analisis}"
)

print(
    f"- {archivo_scope}"
)

print(
    f"- {archivo_strategy}"
)

print(
    f"- {archivo_casos}"
)

print(
    "\nProceso finalizado correctamente."
)