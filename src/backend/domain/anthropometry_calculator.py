from dataclasses import dataclass


@dataclass(frozen=True)
class SomatotypeResult:
    endomorphy: float
    mesomorphy: float
    ectomorphy: float
    x: float
    y: float


def normalized_sex(sex: str) -> str:
    value = str(sex or "").strip().upper()
    if value not in {"M", "F"}:
        raise ValueError("El sexo debe ser M o F")
    return value


def endomorphy(
    height_cm: float,
    triceps_mm: float,
    subscapular_mm: float,
    supraspinale_mm: float,
) -> float:
    corrected_sum = (triceps_mm + subscapular_mm + supraspinale_mm) * 170.18 / height_cm
    return (
        -0.7182
        + 0.1451 * corrected_sum
        - 0.00068 * corrected_sum**2
        + 0.0000014 * corrected_sum**3
    )


def mesomorphy(
    height_cm: float,
    humerus_breadth_mm: float,
    femur_breadth_mm: float,
    flexed_arm_girth_cm: float,
    calf_girth_cm: float,
    triceps_mm: float,
    calf_skinfold_mm: float,
) -> float:
    corrected_arm_girth = flexed_arm_girth_cm - triceps_mm / 10
    corrected_calf_girth = calf_girth_cm - calf_skinfold_mm / 10
    return (
        0.858 * (humerus_breadth_mm / 10)
        + 0.601 * (femur_breadth_mm / 10)
        + 0.188 * corrected_arm_girth
        + 0.161 * corrected_calf_girth
        - 0.131 * height_cm
        + 4.5
    )


def ectomorphy(height_cm: float, weight_kg: float) -> float:
    height_weight_ratio = height_cm / weight_kg ** (1 / 3)
    if height_weight_ratio >= 40.75:
        return 0.732 * height_weight_ratio - 28.58
    if height_weight_ratio > 38.25:
        return 0.463 * height_weight_ratio - 17.63
    return 0.1


def heath_carter_somatotype(
    *,
    height_cm: float,
    weight_kg: float,
    triceps_mm: float,
    subscapular_mm: float,
    supraspinale_mm: float,
    humerus_breadth_mm: float,
    femur_breadth_mm: float,
    flexed_arm_girth_cm: float,
    calf_girth_cm: float,
    calf_skinfold_mm: float,
) -> SomatotypeResult:
    endomorph = endomorphy(height_cm, triceps_mm, subscapular_mm, supraspinale_mm)
    mesomorph = mesomorphy(
        height_cm,
        humerus_breadth_mm,
        femur_breadth_mm,
        flexed_arm_girth_cm,
        calf_girth_cm,
        triceps_mm,
        calf_skinfold_mm,
    )
    ectomorph = ectomorphy(height_cm, weight_kg)
    return SomatotypeResult(
        endomorphy=endomorph,
        mesomorphy=mesomorph,
        ectomorphy=ectomorph,
        x=ectomorph - endomorph,
        y=2 * mesomorph - endomorph - ectomorph,
    )


def rocha_bone_mass_kg(
    height_cm: float,
    wrist_breadth_mm: float,
    femur_breadth_mm: float,
) -> float:
    height_m = height_cm / 100
    wrist_m = wrist_breadth_mm / 1000
    femur_m = femur_breadth_mm / 1000
    return 3.02 * ((height_m**2 * wrist_m * femur_m * 400) ** 0.712)


def residual_mass_kg(weight_kg: float, sex: str) -> float:
    return weight_kg * (0.241 if normalized_sex(sex) == "M" else 0.209)


def faulkner_fat_percent(
    *,
    sex: str,
    triceps_mm: float,
    subscapular_mm: float,
    supraspinale_mm: float,
    abdominal_mm: float,
) -> float:
    skinfold_sum = triceps_mm + subscapular_mm + supraspinale_mm + abdominal_mm
    if normalized_sex(sex) == "M":
        return 0.153 * skinfold_sum + 5.783
    return 0.213 * skinfold_sum + 7.9


def yuhasz_fat_percent(
    *,
    sex: str,
    triceps_mm: float,
    subscapular_mm: float,
    supraspinale_mm: float,
    abdominal_mm: float,
    thigh_mm: float,
    calf_mm: float,
) -> float:
    skinfold_sum = triceps_mm + subscapular_mm + supraspinale_mm + abdominal_mm + thigh_mm + calf_mm
    if normalized_sex(sex) == "M":
        return 0.1051 * skinfold_sum + 2.58
    return 0.1548 * skinfold_sum + 3.58


def fat_mass_kg(weight_kg: float, fat_percent: float) -> float:
    return weight_kg * fat_percent / 100
