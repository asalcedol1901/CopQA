# Guía técnica de CopQA

## 1. Propósito

CopQA es una herramienta de línea de comandos que utiliza modelos locales de
Ollama para analizar maquetas de una aplicación y preparar documentación de QA.
El flujo principal extrae evidencia visible de las pantallas, consolida esa
evidencia como un análisis funcional, filtra el alcance, propone una estrategia
de pruebas y genera casos de prueba documentados.

La herramienta ayuda a preparar el trabajo de QA; los resultados del modelo
deben revisarse contra las maquetas y la información del producto antes de
usarlos como especificación o evidencia de aprobación.

## 2. Flujo principal

El punto de entrada es `app.py`. Se ejecuta como programa interactivo y realiza
las etapas siguientes:

1. Solicita el nombre del flujo, por ejemplo, "Alta de cliente".
2. Solicita el alcance de las pruebas. Si se deja vacío, usa el nombre del flujo.
3. Solicita el tipo de prueba: `ACEPTACION`, `REGRESION` o `INTEGRACION`. Acepta
   el número de la opción o el nombre del tipo, normalizando mayúsculas y
   acentos.
4. Pregunta si se analizarán maquetas nuevas o se reutilizará un análisis
   consolidado existente.
5. Obtiene el análisis funcional:
   - **Maquetas nuevas:** solicita una carpeta, analiza las imágenes compatibles
     que están directamente dentro de ella (`.png`, `.jpg`, `.jpeg`) y crea un
     análisis consolidado.
   - **Análisis existente:** solicita la ruta de un archivo de texto y lo carga.
6. Ejecuta `ScopeAnalyzer` para separar funcionalidades y escenarios dentro y
   fuera del alcance.
7. Ejecuta `TestingStrategyAnalyzer` para proponer qué validar de acuerdo con el
   tipo de prueba.
8. Ejecuta `DocumentedTestCaseGenerator` para producir los casos de prueba.
9. Guarda los resultados y muestra la estrategia y los casos en la terminal.

Al procesar maquetas nuevas, todas las imágenes de la carpeta se consideran
parte del mismo flujo. La aplicación no recorre subcarpetas ni agrupa
automáticamente imágenes de varios flujos.

## 3. Módulos del flujo principal

### `analyzers/vision_analyzer.py`

`VisionAnalyzer` analiza una imagen a la vez con el modelo visual
`qwen2.5vl:7b-q8_0`. Su prompt le pide extraer evidencia observable, como datos,
acciones, mensajes y observaciones, sin inferir reglas de negocio ni generar
casos de prueba. `app.py` imprime cada resultado y lo pasa al analizador
funcional.

### `analyzers/scenario_analyzer.py`

`ScenarioAnalyzer` recibe el nombre del flujo y las descripciones de las
pantallas. Las concatena y usa `qwen2.5:7b` para redactar una interpretación
funcional consolidada: objetivo, flujo, funcionalidades, datos, validaciones,
reglas, riesgos y cobertura observada. También pide distinguir lo observado de
lo inferido. El resultado se guarda en el archivo `analisis_consolidado_...txt`.

### `analyzers/scope_analyzer.py`

`ScopeAnalyzer` recibe el alcance indicado por la persona usuaria y el análisis
funcional. Con `qwen2.5:7b`, clasifica funcionalidades y escenarios dentro y
fuera del alcance y agrega una justificación. No genera casos de prueba. Su
resultado se guarda en `scope_analysis_...txt`.

### `analyzers/testing_strategy_analyzer.py`

`TestingStrategyAnalyzer` recibe el tipo de prueba, el alcance filtrado y el
análisis funcional. Propone objetivo, objetos de prueba, funcionalidades,
casuísticas, validaciones prioritarias, datos críticos, exclusiones, riesgos,
criterio de cobertura y recomendación QA. Sus criterios son:

- **Aceptación:** priorizar flujos exitosos documentados que demuestren el
  objetivo de negocio.
- **Regresión:** volver a validar funcionalidades existentes posiblemente
  afectadas por un cambio identificado; no inventar el cambio ni su impacto.
- **Integración:** centrarse en interacciones y contratos entre componentes
  identificados en el análisis funcional.

Este módulo define la estrategia, no los pasos de los casos. Su resultado se
guarda en `testing_strategy_...txt`.

### `analyzers/documented_testcase_generator.py`

`DocumentedTestCaseGenerator` envía el tipo, el alcance, el análisis funcional y
la estrategia a `qwen2.5:7b`. Solicita una respuesta JSON con casos, datos de
entrada y pasos con resultados esperados. El prompt indica que el alcance y la
evidencia funcional son la fuente de verdad; la estrategia solo orienta
prioridades. También restringe la invención de controles, valores, reglas y
resultados.

El módulo analiza el JSON, verifica que su estructura y campos principales sean
válidos y convierte los casos a texto. Si el modelo no propone casos, devuelve
las razones indicadas o un mensaje predeterminado. El resultado se guarda en
`casos_prueba_...txt`.

## 4. Archivos y resultados generados

Los archivos se crean en el directorio de trabajo desde el que se ejecuta
`app.py`:

- `analisis_consolidado_<flujo>.txt`: análisis funcional de las maquetas nuevas.
  Si ya existe, se crea una versión `_v002`, `_v003`, etc., para no sobrescribirlo.
- `scope_analysis_<flujo>_<tipo>_v001.txt`: clasificación del alcance.
- `testing_strategy_<flujo>_<tipo>_v001.txt`: estrategia de pruebas.
- `casos_prueba_<flujo>_<tipo>_v001.txt`: casos de prueba documentados.

Los archivos de alcance, estrategia y casos también incrementan su versión si
los nombres correspondientes ya existen. Al reutilizar un análisis existente,
la aplicación no modifica ese archivo.

## 5. Otros módulos del repositorio

Estos archivos no son invocados por el flujo de `app.py` en su estado actual:

- `analyzers/scenario_classifier.py`: contiene una clase experimental para
  agrupar análisis de pantallas por identificadores numéricos y clasificar
  casuísticas con palabras clave. Actualmente el archivo tiene un error de
  indentación y no compila. No debe importarse ni considerarse parte del flujo
  ejecutable hasta corregirlo y probarlo.
- `generators/testcase_generator.py`: generador alternativo que llama a Ollama
  mediante una petición HTTP con `requests`. Usa un prompt y una estructura JSON
  distintos de los del generador principal.
- `generators/test_generator.py`: script de prueba para el generador
  alternativo; espera encontrar `analisis_flujo.txt` en una ruta relativa y
  procesa solo los primeros 2500 caracteres como prueba provisional.
- `exporters/excel_exporter.py`: exporta casos con el formato esperado por el
  generador alternativo a un archivo Excel. `app.py` no lo utiliza y los datos
  del generador principal tienen una estructura diferente.
- `readers/document_reader.py`: extrae texto de archivos PDF, imagen, DOCX y
  TXT. Usa OCR para imágenes y para PDF con poco texto. No forma parte del flujo
  actual de análisis de maquetas, que usa el modelo visual.
- `prueba/test_vision.py`: prueba manual que llama a Ollama con nombres de
  imágenes fijos (`Foto1.jpeg`, etc.); no es una prueba automatizada ni se
  ejecuta desde `app.py`.

## 6. Requisitos y ejecución

El repositorio no contiene actualmente un `requirements.txt` ni otro manifiesto
de dependencias. Para el flujo principal se necesita:

- Python 3.
- Ollama instalado y ejecutándose localmente.
- Los modelos `qwen2.5vl:7b-q8_0` y `qwen2.5:7b` disponibles en Ollama.
- El paquete Python `ollama`.

Una preparación típica del entorno de Ollama es:

```bash
ollama pull qwen2.5vl:7b-q8_0
ollama pull qwen2.5:7b
```

Instala el cliente de Python en el entorno virtual y ejecuta la aplicación
desde la raíz del repositorio:

```bash
python -m pip install ollama
python app.py
```

Los módulos auxiliares tienen dependencias adicionales si se van a usar:
`requests`, `openpyxl`, `pdfplumber`, `pytesseract`, `Pillow`, `python-docx` y
`pdf2image`. El OCR de Tesseract y la conversión de PDF mediante Poppler también
requieren sus programas del sistema, no solo los paquetes de Python.

## 7. Limitaciones y consideraciones para quien lo mantenga

- Los resultados dependen del modelo local y pueden variar; deben revisarse.
- La generación principal no está cubierta por pruebas automatizadas en el
  repositorio.
- El análisis consolidado combina todas las imágenes encontradas en la carpeta
  en un único flujo. Para analizar varios flujos por separado, usar carpetas y
  nombres de flujo distintos.
- En regresión, la evidencia debe identificar el cambio y su impacto; de otro
  modo, el generador está instruido para no inventar cobertura.
- En integración, solo deben proponerse casos cuando las interacciones estén
  documentadas.
- Antes de publicar el repositorio en GitHub, verificar que no se incluyan
  maquetas, datos internos, archivos generados, credenciales, el entorno
  virtual `.venv11` ni archivos locales del IDE que no deban compartirse.
- Conviene agregar un manifiesto de dependencias y corregir o retirar módulos
  experimentales antes de presentarlos como funcionalidad soportada.
