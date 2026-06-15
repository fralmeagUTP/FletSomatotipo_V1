import flet as ft
from datetime import datetime
from app_config import show_snack
from src.frontend.components import (
    danger_icon_button,
    edit_icon_button,
    page_header,
    responsive_padding,
    set_busy,
)
from src.frontend.api_client import ApiClient, ApiError
from src.frontend.form_helpers import build_measurement_detail, build_somatotipo_payload
from src.frontend.navigation import show_dashboard
from src.frontend import theme
from src.anthropometry import MEASUREMENT_RULES, validate_measurement_value


def ValoracionView(page: ft.Page):
    PRIMARY_COLOR = theme.PRIMARY_COLOR
    BG_COLOR = theme.BACKGROUND_COLOR
    CARD_BG = theme.CARD_BACKGROUND
    TEXT_COLOR = theme.TEXT_COLOR
    SUCCESS_COLOR = ft.Colors.GREEN_700
    MUTED_COLOR = theme.SUBTITLE_COLOR
    ERROR_COLOR = ft.Colors.RED_600

    selected_athlete_id = None
    added_details_list = []
    editing_detail = None
    current_loaded_somatotipo_id = None
    stored_valuations = []
    api = ApiClient(page)
    current_step = 0
    last_detail = None

    STEPS = [
        {"title": "Datos Básicos", "icon": ft.Icons.INFO_OUTLINE},
        {"title": "Revisar y Guardar", "icon": ft.Icons.CHECK_CIRCLE},
    ]

    def num_field(label, suffix=""):
        field = ft.TextField(
            label=label,
            suffix_text=suffix,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
        )
        field.on_change = lambda e: validate_field(e.control)
        return field

    def validate_field(field):
        raw = str(field.value or "").strip()
        if not raw:
            field.error_text = None
            field.border_color = None
            return
        try:
            field_name = getattr(field, "data", None)
            if field_name in MEASUREMENT_RULES:
                validate_measurement_value(field_name, raw)
            elif float(raw.replace(",", ".")) <= 0:
                raise ValueError("Debe ser mayor a 0")
            field.error_text = None
            field.border_color = None
        except ValueError:
            field.error_text = "Valor fuera de rango"
            field.border_color = ERROR_COLOR

    def is_field_valid(field):
        raw = str(field.value or "").strip()
        if not raw:
            return False
        try:
            field_name = getattr(field, "data", None)
            if field_name in MEASUREMENT_RULES:
                validate_measurement_value(field_name, raw)
                return True
            return float(raw.replace(",", ".")) > 0
        except ValueError:
            return False

    estatura = num_field("Estatura *", "cm")
    peso = num_field("Peso *", "kg")

    p_tricipital = num_field("Tricipital *", "mm")
    p_subescapular = num_field("Subescapular *", "mm")
    p_suprailiaco = num_field("Suprailiaco *", "mm")
    p_abdominal = num_field("Abdominal *", "mm")
    p_muslo = num_field("Muslo Anterior *", "mm")
    p_pierna = num_field("Pierna Medial *", "mm")

    d_muneca = num_field("Biepicondilar Muñeca *", "mm")
    d_femur = num_field("Biepicondilar Fémur *", "mm")
    d_codo = num_field("Codo *", "mm")
    c_carpo = num_field("Circunferencia Carpo *", "mm")
    perim_bicep = num_field("Bíceps Contraído *", "cm")
    perim_pierna = num_field("Pierna *", "cm")

    measurement_fields = {
        "estatura": estatura, "peso": peso,
        "p_tricipital": p_tricipital, "p_subescapular": p_subescapular,
        "p_suprailiaco": p_suprailiaco, "p_abdominal": p_abdominal,
        "p_muslo": p_muslo, "p_pierna": p_pierna,
        "d_muneca": d_muneca, "d_femur": d_femur,
        "d_codo": d_codo, "c_carpo": c_carpo,
        "perim_bicep": perim_bicep, "perim_pierna": perim_pierna,
    }

    detail_to_field_keys = {
        "ESTA_USER_CM": "estatura", "PESO_kg": "peso",
        "PLIEGUE_TRICIPITAL": "p_tricipital", "PLIEGUE_SUBESCAPULAR": "p_subescapular",
        "PLIEGUE_SUPRAILIACO": "p_suprailiaco", "PLIEGUE_ABDOMINAL": "p_abdominal",
        "PLIEGUE_MUSLO_ANT": "p_muslo", "PLIEGUE_MEDIAL_PIERNA": "p_pierna",
        "DIAMETRO_BIEPI_MUNECA": "d_muneca", "DIAMETRO_BIEPI_FEMUR": "d_femur",
        "DIAMETRO_CODO": "d_codo", "CIRCUNFERENCIA_CARPO": "c_carpo",
        "PERIMETRO_BICED_CONTRAIDO": "perim_bicep", "PERIMETRO_PIERNA": "perim_pierna",
    }
    for detail_key, field_key in detail_to_field_keys.items():
        measurement_fields[field_key].data = detail_key

    fecha_medida = ft.TextField(
        label="Fecha Medición *",
        value=datetime.now().strftime('%Y-%m-%d'),
    )

    def on_date_change(e):
        if date_picker.value:
            fecha_medida.value = date_picker.value.strftime('%Y-%m-%d')
            fecha_medida.update()

    date_picker = ft.DatePicker(on_change=on_date_change, first_date=datetime(1900, 1, 1))
    if hasattr(page, "overlay") and date_picker not in page.overlay:
        page.overlay.append(date_picker)

    fecha_medida_btn = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, on_click=lambda _: page.open(date_picker))

    observaciones = ft.TextField(label="Observaciones", multiline=True, min_lines=2, max_lines=4)

    athlete_search_button = ft.IconButton(ft.Icons.SEARCH)
    athlete_search = ft.TextField(
        label="Buscar Deportista (ID o Nombre) *",
        suffix=athlete_search_button,
        on_submit=lambda e: search_athlete(e.control.value),
    )

    athlete_info_text = ft.Text("Ningún deportista seleccionado", color="red", size=13)

    # Athlete info card components
    athlete_photo = ft.Image(
        src="https://via.placeholder.com/120",
        width=120,
        height=120,
        fit=ft.ImageFit.COVER,
        border_radius=10,
    )
    info_id = ft.Text("-", size=12, color=MUTED_COLOR)
    info_nombre = ft.Text("-", weight="bold", size=16)
    info_edad = ft.Text("-", size=13)
    info_direccion = ft.Text("-", size=13)
    info_email = ft.Text("-", size=13)
    info_ciudad = ft.Text("-", size=13)
    info_depto = ft.Text("-", size=13)

    athlete_info_container = ft.Container(
        content=ft.Row(
            [
                # Photo column
                ft.Container(
                    content=athlete_photo,
                    padding=ft.padding.all(4),
                ),
                # Info column
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Text("ID:", weight="bold", size=12, color=MUTED_COLOR),
                                info_id,
                            ], spacing=4),
                            ft.Row([
                                ft.Text("Nombre:", weight="bold", size=12, color=MUTED_COLOR),
                                info_nombre,
                            ], spacing=4),
                            ft.ResponsiveRow([
                                ft.Container(
                                    ft.Row([
                                        ft.Text("Edad:", weight="bold", size=12, color=MUTED_COLOR),
                                        info_edad,
                                    ], spacing=4),
                                    col={"xs": 6, "sm": 4},
                                ),
                                ft.Container(
                                    ft.Row([
                                        ft.Text("Email:", weight="bold", size=12, color=MUTED_COLOR),
                                        info_email,
                                    ], spacing=4),
                                    col={"xs": 6, "sm": 8},
                                ),
                            ]),
                            ft.Row([
                                ft.Text("Dirección:", weight="bold", size=12, color=MUTED_COLOR),
                                info_direccion,
                            ], spacing=4),
                            ft.ResponsiveRow([
                                ft.Container(
                                    ft.Row([
                                        ft.Text("Ciudad:", weight="bold", size=12, color=MUTED_COLOR),
                                        info_ciudad,
                                    ], spacing=4),
                                    col={"xs": 6, "sm": 6},
                                ),
                                ft.Container(
                                    ft.Row([
                                        ft.Text("Depto:", weight="bold", size=12, color=MUTED_COLOR),
                                        info_depto,
                                    ], spacing=4),
                                    col={"xs": 6, "sm": 6},
                                ),
                            ]),
                        ],
                        spacing=4,
                    ),
                    expand=True,
                    padding=ft.padding.only(left=8),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
        padding=12,
        visible=False,
    )

    stored_valuations_status = ft.Text("Busca un deportista para ver valoraciones almacenadas.", color=MUTED_COLOR, size=12)
    stored_valuations_list = ft.ResponsiveRow(spacing=10, run_spacing=10)
    stored_valuations_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Valoraciones almacenadas", color=PRIMARY_COLOR, weight="bold", size=16),
                stored_valuations_status,
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
            stored_valuations_list,
        ], spacing=8),
        visible=False,
    )

    measurements_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO)
    measurements_count_text = ft.Text("Sin mediciones agregadas", color=MUTED_COLOR, size=13)

    step_indicator = ft.Row(spacing=8)
    step_content = ft.Container()
    add_btn = ft.ElevatedButton("Agregar Medición", icon=ft.Icons.ADD_CHART, bgcolor=ft.Colors.GREEN_600, color="white")
    cancel_edit_btn = ft.OutlinedButton("Cancelar edición", icon=ft.Icons.CANCEL, visible=False)
    duplicate_btn = ft.OutlinedButton("Duplicar anterior", icon=ft.Icons.CONTENT_COPY, visible=False)
    new_valuation_btn = ft.OutlinedButton("Nueva Toma", icon=ft.Icons.ADD)
    save_btn = ft.ElevatedButton(
        "Guardar Valoración", icon=ft.Icons.SAVE,
        style=ft.ButtonStyle(bgcolor=PRIMARY_COLOR, color="white"),
    )
    prev_step_btn = ft.OutlinedButton("Anterior", icon=ft.Icons.ARROW_BACK, visible=False)
    next_step_btn = ft.ElevatedButton("Siguiente", icon=ft.Icons.ARROW_FORWARD, bgcolor=PRIMARY_COLOR, color="white")
    save_action_slot = ft.Container()

    def calculate_age(birth_date_str, measure_date_str):
        if not birth_date_str:
            return "Sin fecha nacimiento"
        try:
            birth = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            measure = datetime.strptime(measure_date_str, '%Y-%m-%d').date()
            age = measure.year - birth.year - ((measure.month, measure.day) < (birth.month, birth.day))
            return f"{age} años"
        except Exception:
            return "Error Calc."

    def search_athlete(query):
        nonlocal selected_athlete_id, current_loaded_somatotipo_id, added_details_list, stored_valuations, last_detail
        if not query:
            return
        set_busy(page, [athlete_search_button], True, athlete_info_text, "Buscando deportista...")
        try:
            data = api.list_deportistas(query)
            if data:
                first_match = data[0]
                selected_athlete_id = first_match["IDENTI_DEPORTISTA"]
                
                # Update all athlete info fields
                info_id.value = selected_athlete_id
                info_nombre.value = first_match.get("NOMBRE_DEPORTISTA", "-")
                info_edad.value = calculate_age(first_match.get("FECHA_NAC"), fecha_medida.value)
                info_direccion.value = first_match.get("DIRECC_RESI") or "N/A"
                info_email.value = first_match.get("E_MAIL") or "N/A"
                info_ciudad.value = first_match.get("CIUDAD_RESI") or "N/A"
                info_depto.value = first_match.get("DEPARTA_RESI") or "N/A"
                
                # Update photo
                foto_url = first_match.get("FOTO_DEPORTISTA")
                if foto_url:
                    athlete_photo.src = foto_url
                else:
                    athlete_photo.src = "https://via.placeholder.com/120"
                
                athlete_info_container.visible = True
                athlete_info_text.visible = False
                current_loaded_somatotipo_id = None
                added_details_list = []
                last_detail = None
                reset_edit_mode()
                render_measurements()
                load_stored_valuations(selected_athlete_id)
                update_step_content()
            else:
                selected_athlete_id = None
                current_loaded_somatotipo_id = None
                added_details_list = []
                stored_valuations = []
                stored_valuations_list.controls.clear()
                stored_valuations_container.visible = False
                reset_edit_mode()
                render_measurements()
                athlete_info_text.value = "No se encontraron deportistas."
                athlete_info_text.color = "red"
                athlete_info_text.visible = True
                athlete_info_container.visible = False
        except ApiError as error:
            show_snack(page, str(error))
            athlete_info_text.value = "Error al buscar."
            athlete_info_text.visible = True
        except Exception as e:
            athlete_info_text.value = f"Error: {e}"
            athlete_info_text.visible = True
        finally:
            set_busy(page, [athlete_search_button], False)
        page.update()

    athlete_search_button.on_click = lambda e: search_athlete(athlete_search.value)

    def load_measurement_into_form(detail):
        for detail_key, field_key in detail_to_field_keys.items():
            value = detail.get(detail_key)
            measurement_fields[field_key].value = "" if value is None else str(value)
            measurement_fields[field_key].error_text = None
            measurement_fields[field_key].border_color = None

    def clear_measurement_form():
        for field in measurement_fields.values():
            field.value = ""
            field.error_text = None
            field.border_color = None

    def all_fields_valid():
        for field in measurement_fields.values():
            if not is_field_valid(field):
                field.error_text = field.error_text or "Obligatorio"
                field.border_color = ERROR_COLOR
                return False
        return True

    def start_new_valuation(e=None):
        nonlocal current_loaded_somatotipo_id, added_details_list, last_detail
        current_loaded_somatotipo_id = None
        added_details_list = []
        last_detail = None
        fecha_medida.value = datetime.now().strftime('%Y-%m-%d')
        observaciones.value = ""
        clear_measurement_form()
        reset_edit_mode()
        render_measurements()
        update_step_content()
        page.update()

    def reset_edit_mode():
        nonlocal current_step, editing_detail
        editing_detail = None
        add_btn.text = "Agregar Medición"
        add_btn.icon = ft.Icons.ADD_CHART
        cancel_edit_btn.visible = False
        duplicate_btn.visible = bool(last_detail and not editing_detail)

    def render_measurements():
        measurements_list.controls.clear()
        if not added_details_list:
            measurements_count_text.value = "Sin mediciones agregadas"
            measurements_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY_COLOR, size=20),
                        ft.Text("Agrega una medición para revisar el resumen antes de guardar.", color=MUTED_COLOR),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=12,
                )
            )
        else:
            measurements_count_text.value = f"{len(added_details_list)} medicion(es) agregada(s)"
            for index, detail in enumerate(added_details_list, start=1):
                measurements_list.controls.append(build_measurement_card(detail, index))

        duplicate_btn.visible = bool(last_detail and not editing_detail)
        if current_loaded_somatotipo_id:
            save_btn.text = "Valoración cargada"
            save_btn.disabled = True
        else:
            save_btn.text = "Guardar Valoración"
            save_btn.disabled = False
        page.update()

    def build_measurement_card(detail, index):
        fields_summary = [
            f"Peso: {detail.get('PESO_kg', '-')} kg",
            f"Estatura: {detail.get('ESTA_USER_CM', '-')} cm",
        ]
        pliegues = []
        for label, key in [("Tricipital", "PLIEGUE_TRICIPITAL"), ("Subescapular", "PLIEGUE_SUBESCAPULAR"),
                           ("Suprailiaco", "PLIEGUE_SUPRAILIACO"), ("Abdominal", "PLIEGUE_ABDOMINAL"),
                           ("Muslo Ant.", "PLIEGUE_MUSLO_ANT"), ("Pierna Med.", "PLIEGUE_MEDIAL_PIERNA")]:
            v = detail.get(key)
            if v is not None:
                pliegues.append(f"{label}: {v}mm")
        diameters = []
        for label, key in [("Muñeca", "DIAMETRO_BIEPI_MUNECA"), ("Fémur", "DIAMETRO_BIEPI_FEMUR"),
                           ("Codo", "DIAMETRO_CODO"), ("Carpo", "CIRCUNFERENCIA_CARPO")]:
            v = detail.get(key)
            if v is not None:
                diameters.append(f"{label}: {v}mm")
        perimeters = []
        for label, key in [("Bíceps", "PERIMETRO_BICED_CONTRAIDO"), ("Pierna", "PERIMETRO_PIERNA")]:
            v = detail.get(key)
            if v is not None:
                perimeters.append(f"{label}: {v}cm")

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        ft.Text(f"Toma #{index}", weight="bold", color=PRIMARY_COLOR, size=14),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        border_radius=6,
                    ),
                    ft.Text(f"{detail.get('PESO_kg', '-')} kg · {detail.get('ESTA_USER_CM', '-')} cm", color=MUTED_COLOR, size=12, expand=True),
                ]),
                ft.Text(" · ".join(fields_summary), size=12, color=TEXT_COLOR),
                ft.Text("Pliegues: " + " | ".join(pliegues), size=11, color=MUTED_COLOR),
                ft.Text("Diámetros: " + " | ".join(diameters), size=11, color=MUTED_COLOR),
                ft.Text("Perímetros: " + " | ".join(perimeters), size=11, color=MUTED_COLOR),
                ft.Row([
                    edit_icon_button(on_click=lambda e, d=detail: edit_medicion(d)),
                    danger_icon_button(on_click=lambda e, d=detail: confirm_remove(d)),
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=4),
            padding=12,
            border=ft.border.all(1, "#e0e0e0"),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
        )

    def confirm_remove(det):
        def close_dlg(e):
            page.close(dlg)

        def on_delete(e):
            remove_medicion(det)
            close_dlg(e)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Estás seguro de eliminar esta medición?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dlg),
                ft.TextButton("Eliminar", on_click=on_delete, style=ft.ButtonStyle(color=ERROR_COLOR)),
            ],
        )
        page.open(dlg)

    def load_stored_valuations(athlete_id):
        nonlocal stored_valuations
        stored_valuations = []
        try:
            editable_result = api.list_somatotipos_editables(str(athlete_id))
            if isinstance(editable_result, dict):
                stored_valuations = editable_result.get("items") or editable_result.get("data") or []
            else:
                stored_valuations = editable_result or []
        except ApiError as error:
            try:
                stored_valuations = stored_valuations_from_history(api.get_historial_vista_all(str(athlete_id)))
            except ApiError:
                show_snack(page, str(error))
        if not stored_valuations:
            try:
                stored_valuations = stored_valuations_from_history(api.get_historial_vista_all(str(athlete_id)))
            except ApiError:
                pass
        render_stored_valuations()

    def stored_valuations_from_history(rows):
        grouped = {}
        measurement_fields = [
            "ESTA_USER_CM",
            "PESO_kg",
            "PLIEGUE_TRICIPITAL",
            "PLIEGUE_SUBESCAPULAR",
            "PLIEGUE_SUPRAILIACO",
            "PLIEGUE_ABDOMINAL",
            "PLIEGUE_MUSLO_ANT",
            "PLIEGUE_MEDIAL_PIERNA",
            "DIAMETRO_BIEPI_MUNECA",
            "DIAMETRO_BIEPI_FEMUR",
            "DIAMETRO_CODO",
            "PERIMETRO_BICED_CONTRAIDO",
            "PERIMETRO_PIERNA",
            "CIRCUNFERENCIA_CARPO",
        ]
        for row in rows or []:
            somatotipo_id = row.get("id_Somatotipo")
            if somatotipo_id is None:
                continue
            record = grouped.setdefault(
                somatotipo_id,
                {
                    "id_Somatotipo": somatotipo_id,
                    "FECHA_MEDIDA": row.get("FECHA_MEDIDA"),
                    "IDENTI_DEPORTISTA": row.get("IDENTI_DEPORTISTA"),
                    "OBSERV": row.get("OBSERV") or "",
                    "DETALLES": [],
                    "_source": "historial",
                },
            )
            detail = {
                "id_Somatotipo": somatotipo_id,
                **{field: row.get(field) for field in measurement_fields},
            }
            if any(detail.get(field) is not None for field in measurement_fields):
                record["DETALLES"].append(detail)
        return list(grouped.values())

    def render_stored_valuations():
        stored_valuations_list.controls.clear()
        stored_valuations_container.visible = bool(selected_athlete_id)
        if not selected_athlete_id:
            stored_valuations_status.value = "Busca un deportista para ver valoraciones almacenadas."
            return
        if not stored_valuations:
            stored_valuations_status.value = "Sin valoraciones almacenadas."
            stored_valuations_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY_COLOR, size=18),
                        ft.Text("Este deportista no tiene valoraciones guardadas. Puedes registrar una nueva.", color=MUTED_COLOR, size=12),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                )
            )
            return
        stored_valuations_status.value = f"{len(stored_valuations)} valoracion(es)"
        for valuation in stored_valuations:
            valuation_id = valuation.get("id_Somatotipo")
            detail_count = len(valuation.get("DETALLES") or [])
            stored_valuations_list.controls.append(
                ft.Container(
                    content=ft.ResponsiveRow([
                        ft.Container(
                            ft.Column([
                                ft.Text(f"ID {valuation_id} | Fecha: {valuation.get('FECHA_MEDIDA') or 'Sin fecha'}", weight="bold", color=TEXT_COLOR, size=13),
                                ft.Text(f"{detail_count} medicion(es) editable(s)", color=MUTED_COLOR, size=12),
                            ], spacing=2),
                            col={"xs": 12, "sm": 7, "md": 8},
                        ),
                        ft.Container(
                            ft.Row([
                                ft.OutlinedButton("Cargar", icon=ft.Icons.DOWNLOAD, disabled=detail_count == 0,
                                                  on_click=lambda e, sid=valuation_id: load_stored_somatotipo(sid)),
                                danger_icon_button(on_click=lambda e, sid=valuation_id: delete_stored_somatotipo(sid)),
                            ], spacing=8),
                            col={"xs": 12, "sm": 5, "md": 4},
                            alignment=ft.alignment.center_right,
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=12,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=10,
                    bgcolor=CARD_BG,
                    col={"xs": 12, "lg": 6},
                )
            )

    def load_stored_somatotipo(somatotipo_id):
        nonlocal current_loaded_somatotipo_id, added_details_list, last_detail, editing_detail
        try:
            try:
                record = api.get_somatotipo_editable(somatotipo_id)
            except ApiError:
                record = next(
                    (
                        item
                        for item in stored_valuations
                        if str(item.get("id_Somatotipo")) == str(somatotipo_id)
                    ),
                    None,
                )
                if record is None:
                    raise
            current_loaded_somatotipo_id = record.get("id_Somatotipo")
            fecha_medida.value = record.get("FECHA_MEDIDA") or fecha_medida.value
            observaciones.value = record.get("OBSERV") or record.get("OBSERVACIONES") or ""
            added_details_list = list(record.get("DETALLES") or [])
            last_detail = added_details_list[-1] if added_details_list else None
            reset_edit_mode()
            if added_details_list:
                first_detail = added_details_list[0]
                load_measurement_into_form(first_detail)
                if first_detail.get("ID"):
                    editing_detail = first_detail
                    add_btn.text = "Actualizar Medición"
                    add_btn.icon = ft.Icons.SAVE
                    cancel_edit_btn.visible = True
            render_measurements()
            update_step_content()
            show_snack(page, "Valoración cargada. Edita una medición y actualízala.")
        except ApiError as error:
            show_snack(page, str(error))
        page.update()

    def delete_stored_somatotipo(somatotipo_id):
        nonlocal current_loaded_somatotipo_id, added_details_list, last_detail
        try:
            api.delete_somatotipo(somatotipo_id)
            if current_loaded_somatotipo_id == somatotipo_id:
                current_loaded_somatotipo_id = None
                added_details_list = []
                last_detail = None
                reset_edit_mode()
                render_measurements()
            if selected_athlete_id:
                load_stored_valuations(selected_athlete_id)
            show_snack(page, "Valoración eliminada")
        except ApiError as error:
            show_snack(page, str(error))
        page.update()

    def add_medicion(e):
        nonlocal editing_detail, last_detail
        if not all_fields_valid():
            show_snack(page, "Revisa los campos marcados en rojo")
            return
        set_busy(page, [add_btn, cancel_edit_btn, save_btn], True)
        try:
            det = build_measurement_detail(measurement_fields)
            if editing_detail is not None and editing_detail in added_details_list:
                index = added_details_list.index(editing_detail)
                detail_id = editing_detail.get("ID")
                if detail_id:
                    updated_detail = api.update_somatotipo_detalle(detail_id, det)
                    det.update({
                        "ID": updated_detail.get("ID", detail_id),
                        "id_Somatotipo": updated_detail.get("id_Somatotipo", current_loaded_somatotipo_id),
                    })
                    if selected_athlete_id:
                        load_stored_valuations(selected_athlete_id)
                added_details_list[index] = det
                reset_edit_mode()
                message = "Medición actualizada"
            else:
                if current_loaded_somatotipo_id:
                    created_detail = api.create_somatotipo_detalle(current_loaded_somatotipo_id, det)
                    added_details_list.append(created_detail)
                    if selected_athlete_id:
                        load_stored_valuations(selected_athlete_id)
                    message = "Toma agregada a la valoración cargada"
                else:
                    added_details_list.append(det)
                    message = "Medición agregada"
            last_detail = dict(det)
            clear_measurement_form()
            render_measurements()
            show_snack(page, message)
        except ValueError as ex:
            show_snack(page, str(ex))
        finally:
            set_busy(page, [add_btn, cancel_edit_btn, save_btn], False)
        page.update()

    def remove_medicion(det):
        nonlocal editing_detail, last_detail
        if det.get("ID"):
            try:
                api.delete_somatotipo_detalle(det["ID"])
                if det in added_details_list:
                    added_details_list.remove(det)
                if editing_detail is det:
                    reset_edit_mode()
                if selected_athlete_id:
                    load_stored_valuations(selected_athlete_id)
                render_measurements()
                show_snack(page, "Toma eliminada")
            except ApiError as error:
                show_snack(page, str(error))
            page.update()
            return
        if det in added_details_list:
            added_details_list.remove(det)
            if editing_detail is det:
                reset_edit_mode()
            render_measurements()
            page.update()

    def edit_medicion(det):
        nonlocal current_step, editing_detail
        editing_detail = det
        load_measurement_into_form(det)
        add_btn.text = "Actualizar Medición"
        add_btn.icon = ft.Icons.SAVE
        cancel_edit_btn.visible = True
        duplicate_btn.visible = False
        current_step = 0
        update_step_content()
        show_snack(page, "Medición cargada para edición. Ajusta los datos y presiona Actualizar.")
        page.update()

    def cancel_edit_medicion(e):
        reset_edit_mode()
        clear_measurement_form()
        page.update()

    def duplicate_last(e):
        if last_detail:
            load_measurement_into_form(last_detail)
            show_snack(page, "Valores de la última medición cargados")
            page.update()

    def save_valoracion(e):
        if current_loaded_somatotipo_id:
            show_snack(page, "La valoración cargada se actualiza desde cada medición.")
            page.update()
            return
        if not selected_athlete_id:
            show_snack(page, "Debe seleccionar un deportista primero")
            page.update()
            return
        current_user = page.session.get("login_user")
        if not current_user:
            show_snack(page, "Sesión expirada. Inicia sesión nuevamente.")
            page.update()
            return
        if not added_details_list:
            show_snack(page, "Debe agregar al menos una medición a la lista")
            page.update()
            return
        duplicate_valuation = next(
            (
                valuation
                for valuation in stored_valuations
                if valuation.get("FECHA_MEDIDA") == fecha_medida.value
            ),
            None,
        )
        if duplicate_valuation:
            show_snack(
                page,
                "Ya existe una valoración en esa fecha. Cárgala y agrega la toma como detalle.",
            )
            page.update()
            return
        set_busy(page, [add_btn, save_btn], True)
        try:
            payload = build_somatotipo_payload(
                selected_athlete_id, current_user,
                fecha_medida.value, observaciones.value, added_details_list,
            )
            api.create_somatotipo(payload)
            show_snack(page, "Valoración guardada exitosamente")
            page.update()
            go_back(e)
        except ValueError:
            show_snack(page, "Por favor verifique que todos los campos numéricos sean válidos")
        except ApiError as error:
            show_snack(page, str(error))
        except Exception as ex:
            show_snack(page, f"Error de conexión: {ex}")
        finally:
            set_busy(page, [add_btn, save_btn], False)
        page.update()

    add_btn.on_click = add_medicion
    cancel_edit_btn.on_click = cancel_edit_medicion
    duplicate_btn.on_click = duplicate_last
    new_valuation_btn.on_click = start_new_valuation
    save_btn.on_click = save_valoracion

    def go_back(e):
        show_dashboard(page)

    def update_step_indicators():
        step_indicator.controls.clear()
        for i, step in enumerate(STEPS):
            is_active = i == current_step
            is_done = i < current_step
            color = PRIMARY_COLOR if is_active else (SUCCESS_COLOR if is_done else MUTED_COLOR)
            step_indicator.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(step["icon"], color=color, size=18),
                        ft.Text(step["title"], color=color, size=12, weight="bold" if is_active else "normal"),
                    ], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    bgcolor=ft.Colors.BLUE_50 if is_active else ft.Colors.TRANSPARENT,
                    border_radius=6,
                    ink=True,
                    on_click=lambda e, idx=i: go_to_step(idx),
                )
            )
            if i < len(STEPS) - 1:
                step_indicator.controls.append(ft.Icon(ft.Icons.CHEVRON_RIGHT, color=MUTED_COLOR, size=16))

    def go_to_step(idx):
        nonlocal current_step
        if idx > current_step and not validate_current_step():
            return
        current_step = idx
        update_step_content()
        page.update()

    def validate_current_step():
        if current_step == 0:
            if not selected_athlete_id:
                show_snack(page, "Selecciona un deportista primero")
                return False
            if not fecha_medida.value:
                fecha_medida.error_text = "Obligatorio"
                fecha_medida.border_color = ERROR_COLOR
                show_snack(page, "La fecha es obligatoria")
                return False
            if not added_details_list and not all_fields_valid():
                show_snack(page, "Completa las medidas obligatorias")
                return False
        return True

    def next_step(e):
        nonlocal current_step
        if validate_current_step():
            if current_step < len(STEPS) - 1:
                current_step += 1
                update_step_content()
                page.update()

    def prev_step(e):
        nonlocal current_step
        if current_step > 0:
            current_step -= 1
            update_step_content()
            page.update()

    prev_step_btn.on_click = prev_step
    next_step_btn.on_click = next_step

    def update_step_content():
        update_step_indicators()
        prev_step_btn.visible = current_step > 0
        next_step_btn.visible = current_step < len(STEPS) - 1
        save_action_slot.content = save_btn if current_step == len(STEPS) - 1 else None
        if current_step == 0:
            step_content.content = ft.Column([
                ft.Text("Datos del Deportista", color=PRIMARY_COLOR, weight="bold", size=18),
                ft.Container(height=10),
                ft.ResponsiveRow([
                    ft.Container(content=athlete_search, col={"xs": 12, "md": 6}),
                    ft.Container(content=ft.Column([athlete_info_text, athlete_info_container]), col={"xs": 12, "md": 6}),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Container(height=10),
                stored_valuations_container,
                ft.Divider(),
                ft.Text("Datos de la Medición", color=PRIMARY_COLOR, weight="bold", size=16),
                ft.Container(height=10),
                ft.ResponsiveRow([
                    ft.Container(content=fecha_medida, col={"xs": 10, "sm": 5, "md": 4}),
                    ft.Container(content=fecha_medida_btn, col={"xs": 2, "sm": 1, "md": 1}),
                    ft.Container(content=estatura, col={"xs": 6, "sm": 3, "md": 4}),
                    ft.Container(content=peso, col={"xs": 6, "sm": 3, "md": 3}),
                ]),
                ft.Container(height=10),
                ft.ResponsiveRow([
                    ft.Container(content=observaciones, col={"xs": 12}),
                ]),
                ft.Divider(),
                ft.Text("Pliegues cutaneos (mm)", color=PRIMARY_COLOR, weight="bold", size=16),
                ft.ResponsiveRow([
                    ft.Container(content=p_tricipital, col={"xs": 6, "md": 4}),
                    ft.Container(content=p_subescapular, col={"xs": 6, "md": 4}),
                    ft.Container(content=p_suprailiaco, col={"xs": 6, "md": 4}),
                    ft.Container(content=p_abdominal, col={"xs": 6, "md": 4}),
                    ft.Container(content=p_muslo, col={"xs": 6, "md": 4}),
                    ft.Container(content=p_pierna, col={"xs": 6, "md": 4}),
                ], spacing=10, run_spacing=10),
                ft.Text("Diametros y perimetros", color=PRIMARY_COLOR, weight="bold", size=16),
                ft.ResponsiveRow([
                    ft.Container(content=d_muneca, col={"xs": 6, "sm": 4, "md": 3}),
                    ft.Container(content=d_femur, col={"xs": 6, "sm": 4, "md": 3}),
                    ft.Container(content=d_codo, col={"xs": 6, "sm": 4, "md": 3}),
                    ft.Container(content=c_carpo, col={"xs": 6, "sm": 4, "md": 3}),
                    ft.Container(content=perim_bicep, col={"xs": 6, "sm": 6, "md": 6}),
                    ft.Container(content=perim_pierna, col={"xs": 6, "sm": 6, "md": 6}),
                ], spacing=10, run_spacing=10),
                ft.Row([
                    cancel_edit_btn,
                    duplicate_btn,
                    add_btn,
                ], alignment=ft.MainAxisAlignment.END, spacing=8),
                ft.Divider(),
                ft.Text("Tomas de la valoracion", color=PRIMARY_COLOR, weight="bold", size=16),
                measurements_count_text,
                measurements_list,
            ], spacing=10)
        elif current_step == 1:
            step_content.content = ft.Column([
                ft.Text("Revisar y Guardar", color=PRIMARY_COLOR, weight="bold", size=18),
                ft.Container(height=10),
                ft.Row([
                    ft.Text(f"Deportista: ", weight="bold"),
                    ft.Text(info_nombre.value if selected_athlete_id else "No seleccionado"),
                ]),
                ft.Row([
                    ft.Text("Fecha: ", weight="bold"),
                    ft.Text(fecha_medida.value or "-"),
                ]),
                ft.Row([
                    ft.Text("Mediciones: ", weight="bold"),
                    ft.Text(f"{len(added_details_list)}"),
                ]),
                ft.Divider(),
                ft.Text("Mediciones agregadas:", weight="bold", size=14),
                measurements_count_text,
                measurements_list,
                ft.Container(height=10),
                ft.Row([
                    new_valuation_btn,
                    duplicate_btn,
                ], spacing=8),
                ft.Container(height=10),
                ft.Row([
                    cancel_edit_btn,
                    add_btn,
                ], alignment=ft.MainAxisAlignment.END, spacing=8),
            ], spacing=10)
        page.update()

    update_step_content()

    return ft.Container(
        content=ft.Column([
            page_header("Valoración Corporal", on_back=go_back, color=TEXT_COLOR),
            ft.Container(height=16),
            step_indicator,
            ft.Container(height=16),
            ft.Container(
                content=step_content,
                bgcolor=CARD_BG,
                padding=responsive_padding(page, desktop=30, tablet=20, mobile=12),
                border_radius=theme.RADIUS_MEDIUM,
                shadow=theme.card_shadow(),
            ),
            ft.Container(height=16),
            ft.Row([
                prev_step_btn,
                ft.Container(expand=True),
                next_step_btn,
                save_action_slot,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ], scroll=ft.ScrollMode.AUTO),
        padding=responsive_padding(page, desktop=20, tablet=16, mobile=10),
        bgcolor=BG_COLOR,
        expand=True,
    )
