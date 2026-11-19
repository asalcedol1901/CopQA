from generators.testcase_generator import TestCaseGenerator

with open(
    "../analisis_flujo.txt",
    "r",
    encoding="utf-8"
) as archivo:

    analisis_flujo = archivo.read()

print("Análisis cargado.")

generator = TestCaseGenerator()

resultado = generator.generate(
    analisis_flujo[:2500] ##Provisional
)

print("\nTIPO RESULTADO:")
print(type(resultado))

print("\nRESULTADO:")
print(resultado)