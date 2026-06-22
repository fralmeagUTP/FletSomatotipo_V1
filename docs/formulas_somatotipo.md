# Fórmulas y cálculos antropométricos

## Estado

Las fórmulas corregidas están implementadas en `src/backend/domain/anthropometry_calculator.py` y replicadas en la migración `scripts/migrations/004_correct_anthropometric_formulas.sql`.

La base de datos continúa calculando los indicadores mediante vistas SQL. La calculadora Python funciona como referencia testeable para evitar divergencias futuras.

## Contrato de unidades

| Medida | Unidad almacenada |
|--------|-------------------|
| Estatura | cm |
| Peso | kg |
| Pliegues cutáneos | mm |
| Diámetros óseos de muñeca, fémur y codo | mm |
| Perímetros de brazo y pierna | cm |
| Circunferencia de carpo | cm |

La interfaz y `src/anthropometry.py` validan este contrato. No se deben introducir diámetros como `6.4` o `9.0`; deben registrarse como `64` o `90` mm.

## Somatotipo Heath-Carter

### Endomorfismo

La suma corregida es:

```text
X = (tricipital + subescapular + suprailiaco) × 170.18 / estatura_cm
Endomorfismo = -0.7182 + 0.1451X - 0.00068X² + 0.0000014X³
```

### Mesomorfismo

Los diámetros se convierten de mm a cm. Los perímetros se corrigen con sus pliegues:

```text
brazo_corregido = brazo_cm - tricipital_mm / 10
pierna_corregida = pierna_cm - pliegue_pierna_mm / 10

Mesomorfismo = 0.858 × codo_cm
              + 0.601 × fémur_cm
              + 0.188 × brazo_corregido
              + 0.161 × pierna_corregida
              - 0.131 × estatura_cm
              + 4.5
```

### Ectomorfismo

```text
HWR = estatura_cm / raíz_cúbica(peso_kg)

HWR >= 40.75       → 0.732 × HWR - 28.58
38.25 < HWR < 40.75 → 0.463 × HWR - 17.63
HWR <= 38.25       → 0.1
```

### Somatocarta

```text
X = ectomorfismo - endomorfismo
Y = 2 × mesomorfismo - endomorfismo - ectomorfismo
```

## Composición corporal

### Yuhasz

Método principal para población deportiva:

```text
Hombres: 0.1051 × suma_6_pliegues + 2.58
Mujeres: 0.1548 × suma_6_pliegues + 3.58
```

### Faulkner

Método comparativo:

```text
Hombres: 0.153 × suma_4_pliegues + 5.783
Mujeres: 0.213 × suma_4_pliegues + 7.9
```

### Masa ósea de Rocha

La estatura y los diámetros se convierten a metros antes de aplicar:

```text
Masa ósea = 3.02 × ((estatura_m² × muñeca_m × fémur_m × 400) ^ 0.712)
```

### Masa residual

```text
Hombres: peso × 0.241
Mujeres: peso × 0.209
```

### Masa muscular derivada

```text
Mma = peso - masa grasa Yuhasz - masa ósea - masa residual
```

`Mma` es una masa derivada por diferencia, no una medición directa.

## Johnston

Los campos históricos `PorcGrasoJonson` y `PesoGrasoJhonston` se conservan en el contrato de la vista por compatibilidad, pero la migración los devuelve como `NULL`. No se muestran como referencia clínica porque no se pudo identificar una fuente metodológica verificable para los coeficientes heredados.

## Migración de datos

La migración `004_correct_anthropometric_formulas.sql`:

1. Crea `CDRBackupSomatotipoDetalleFormulaV2`.
2. Detiene la ejecución si encuentra diámetros con escalas mezcladas dentro del mismo registro.
3. Convierte a mm los registros históricos que guardaron los tres diámetros en cm.
4. Corrige estaturas almacenadas en metros.
5. Reemplaza las vistas de somatotipo, grasa, masa residual, masa ósea y masa muscular.
6. Corrige el texto descriptivo de ectomorfismo.

```powershell
cmd /c "mysql -h %DB_HOST% -P %DB_PORT% -u %DB_USER% -p %DB_NAME% < scripts\migrations\004_correct_anthropometric_formulas.sql"
```

Después de aplicarla, ejecutar la suite y comparar la vista SQL con los casos de `tests/test_anthropometry_calculator.py`.

```powershell
.\.venv\Scripts\python.exe scripts\check_anthropometric_formulas.py
```

El verificador consulta todas las valoraciones y compara somatotipo, coordenadas, grasa, masa ósea y masa residual contra la calculadora Python.

### Estado de la base activa

El 21 de junio de 2026 se aplicó la migración completa y se ejecutó el verificador contra MySQL:

- 12 sentencias de migración aplicadas.
- 76 valoraciones verificadas.
- 0 diferencias entre las vistas SQL y la calculadora Python.

Las nuevas bases o copias restauradas deben ejecutar nuevamente la migración y el verificador.

## Validación metodológica

Las ecuaciones ya tienen pruebas técnicas de referencia. Antes de utilizarlas para decisiones clínicas o deportivas definitivas, el equipo de ciencias del deporte debe aprobar formalmente el protocolo, los sitios anatómicos y la técnica de medición.
