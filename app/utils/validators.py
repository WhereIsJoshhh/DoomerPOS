from decimal import Decimal, InvalidOperation
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def limpiar_texto(valor, max_len=255):
    valor = (valor or "").strip()
    return valor[:max_len]


def requerido(valor, campo="campo"):
    valor = limpiar_texto(valor)
    if not valor:
        raise ValueError(f"El campo {campo} es obligatorio.")
    return valor


def decimal_positivo(valor, campo="valor"):
    try:
        numero = Decimal(str(valor or "0"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {campo} debe ser numérico.")
    if numero <= 0:
        raise ValueError(f"El campo {campo} debe ser mayor que cero.")
    return numero.quantize(Decimal("0.01"))


def decimal_no_negativo(valor, campo="valor"):
    try:
        numero = Decimal(str(valor or "0"))
    except (InvalidOperation, ValueError):
        raise ValueError(f"El campo {campo} debe ser numérico.")
    if numero < 0:
        raise ValueError(f"El campo {campo} no puede ser negativo.")
    return numero.quantize(Decimal("0.01"))


def entero_opcional(valor):
    if valor in (None, "", "None"):
        return None
    try:
        return int(valor)
    except ValueError:
        raise ValueError("Valor entero no válido.")


def validar_email_opcional(valor):
    valor = limpiar_texto(valor, 120)
    if valor and not EMAIL_RE.match(valor):
        raise ValueError("El correo electrónico no tiene un formato válido.")
    return valor


def validar_password_seguro(password: str):
    password = password or ""
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if not any(c.isdigit() for c in password):
        raise ValueError("La contraseña debe incluir al menos un número.")
    if not any(c.isalpha() for c in password):
        raise ValueError("La contraseña debe incluir letras.")
    return password
