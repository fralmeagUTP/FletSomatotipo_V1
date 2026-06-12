# Fórmulas y cálculos de somatotipo

## Estado actual

La aplicación Python no calcula actualmente los indicadores clínicos de somatotipo.

El flujo actual es:

1. El frontend captura mediciones antropométricas.
2. El backend guarda encabezado y detalle en:
   - `CDRTablaSomatotipo`
   - `CDRDetalleSomatotipo`
3. El historial consulta `CDRVistaValoracionCorporal`.
4. Los valores calculados se muestran desde esa vista SQL.

Por tanto, la fuente efectiva de las fórmulas es la base de datos, no el código Python.

## Campos calculados consumidos por la app

La vista `CDRVistaValoracionCorporal` expone, entre otros:

- `PorcRasoYuasz`
- `PorcGrasoFaulker`
- `PorcGrasoJonson`
- `PesoRasoYuazs`
- `PesoRasoFaulker`
- `PesoGrasoJhonston`
- `PesoOseo`
- `PesoResidual`
- `Mma`
- `IMC`
- `EstadoIMC`
- `Complexion`
- `TipoComplexion`
- `Endomorfismo`
- `EscalaEndomorfismo`
- `Mesomorfismo`
- `EscalaMesomorfismo`
- `Ectomorfismo`
- `EscalaEctomorfismo`
- `X`
- `Y`

Estos campos están mapeados en `src/backend/models.py` dentro de `VistaValoracionCorporal`.

## Implicación arquitectónica

Mientras las fórmulas vivan en la vista SQL:

- los tests Python solo validan captura, persistencia, consulta y paginación;
- la precisión clínica depende de la definición SQL de `CDRVistaValoracionCorporal`;
- cualquier cambio de fórmula debe auditarse en la base de datos;
- el backend no puede garantizar por sí solo que los cálculos sean clínicamente correctos.

## Checklist de validación clínica

Antes de considerar validados los cálculos:

1. Obtener la definición SQL de `CDRVistaValoracionCorporal`.
2. Identificar cada fórmula usada para:
   - composición corporal;
   - masas corporales;
   - IMC;
   - complexión;
   - endomorfismo;
   - mesomorfismo;
   - ectomorfismo;
   - coordenadas `X`, `Y`.
3. Comparar cada fórmula contra la fuente metodológica esperada.
4. Crear casos de prueba con mediciones conocidas y resultados esperados.
5. Ejecutar esos casos contra la vista SQL.
6. Documentar versión, fuente y supuestos de cada fórmula.

Para inspeccionar columnas y definición SQL desde el entorno local:

```powershell
.\.venv\Scripts\python.exe scripts\inspect_somatotipo_view.py
```

El script usa las variables de `.env` mediante `src/backend/database.py` y no imprime credenciales.

## Riesgos detectados

- Algunos nombres de campos parecen tener errores ortográficos históricos, por ejemplo `Faulker`, `Jonson`, `Yuasz`, `Raso`.
- Si esos nombres corresponden a columnas reales, cambiarlos rompería compatibilidad.
- Se recomienda mantener nombres técnicos existentes y mejorar solo las etiquetas visibles en UI.

## Recomendación futura

Si se requiere control total desde la app:

1. Crear un módulo Python de cálculo, por ejemplo `src/backend/domain/somatotipo_calculator.py`.
2. Implementar fórmulas puras y testeables.
3. Agregar pruebas con datos clínicos conocidos.
4. Decidir si la vista SQL queda solo como reporte o si se elimina dependencia de cálculos en DB.

Hasta que eso ocurra, la vista SQL debe considerarse la fuente de verdad de los cálculos.
