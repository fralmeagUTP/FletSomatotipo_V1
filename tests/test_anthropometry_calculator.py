import pytest

from src.backend.domain.anthropometry_calculator import (
    ectomorphy,
    faulkner_fat_percent,
    fat_mass_kg,
    heath_carter_somatotype,
    residual_mass_kg,
    rocha_bone_mass_kg,
    yuhasz_fat_percent,
)


def test_recalculates_recent_female_record_with_canonical_units():
    result = heath_carter_somatotype(
        height_cm=165,
        weight_kg=59,
        triceps_mm=9.5,
        subscapular_mm=11.8,
        supraspinale_mm=7.5,
        humerus_breadth_mm=64,
        femur_breadth_mm=90,
        flexed_arm_girth_cm=28.5,
        calf_girth_cm=36.5,
        calf_skinfold_mm=6.5,
    )

    assert result.endomorphy == pytest.approx(3.03, abs=0.01)
    assert result.mesomorphy == pytest.approx(4.74, abs=0.01)
    assert result.ectomorphy == pytest.approx(2.44, abs=0.01)
    assert result.x == pytest.approx(-0.59, abs=0.01)
    assert result.y == pytest.approx(4.00, abs=0.01)


def test_ectomorphy_uses_all_three_heath_carter_branches():
    assert ectomorphy(158, 72.2) == pytest.approx(0.1)
    assert ectomorphy(170, 78) == pytest.approx(0.79, abs=0.01)
    assert ectomorphy(176, 68.2) == pytest.approx(2.95, abs=0.01)


def test_body_composition_equations_are_sex_specific():
    female_faulkner = faulkner_fat_percent(
        sex="F", triceps_mm=9.5, subscapular_mm=11.8, supraspinale_mm=7.5, abdominal_mm=8.8
    )
    female_yuhasz = yuhasz_fat_percent(
        sex="F",
        triceps_mm=9.5,
        subscapular_mm=11.8,
        supraspinale_mm=7.5,
        abdominal_mm=8.8,
        thigh_mm=15.5,
        calf_mm=6.5,
    )
    male_yuhasz = yuhasz_fat_percent(
        sex="M",
        triceps_mm=6.2,
        subscapular_mm=8,
        supraspinale_mm=6,
        abdominal_mm=6.8,
        thigh_mm=12.5,
        calf_mm=5,
    )

    assert female_faulkner == pytest.approx(15.91, abs=0.01)
    assert female_yuhasz == pytest.approx(12.81, abs=0.01)
    assert male_yuhasz == pytest.approx(7.26, abs=0.01)
    assert residual_mass_kg(59, "F") == pytest.approx(12.33, abs=0.01)
    assert residual_mass_kg(68.2, "M") == pytest.approx(16.44, abs=0.01)


def test_rocha_bone_mass_uses_millimetre_breadths():
    bone_mass = rocha_bone_mass_kg(165, 54, 90)

    assert bone_mass == pytest.approx(9.89, abs=0.01)
    assert fat_mass_kg(59, 12.81) == pytest.approx(7.56, abs=0.01)
