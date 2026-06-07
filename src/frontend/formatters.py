from datetime import date, datetime


def display_value(value, fallback: str = "-") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        value = value.strip()
    return str(value) if value else fallback


def age_from_birth_date(value, today: date | None = None) -> str:
    if not value:
        return "-"
    if today is None:
        today = date.today()
    if isinstance(value, str):
        try:
            birth_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return "-"
    elif isinstance(value, date):
        birth_date = value
    else:
        return "-"

    age = today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )
    return str(age) if age >= 0 else "-"
