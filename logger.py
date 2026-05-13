"""
logger.py — Registro de eventos y errores en archivo de logs
"""
import datetime
import os
import traceback

LOG_PATH = os.path.join(os.path.dirname(__file__), "sistema_fj.log")


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _escribir(nivel: str, mensaje: str, exc: Exception = None) -> None:
    lineas = [f"[{_timestamp()}] [{nivel}] {mensaje}"]
    if exc is not None:
        tb = traceback.format_exc()
        if tb and tb.strip() != "NoneType: None":
            lineas.append(f"    TRACEBACK: {tb.strip()}")
    entrada = "\n".join(lineas) + "\n"
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entrada)
    except OSError:
        # Si no se puede escribir el log, no detenemos la app
        pass


def info(mensaje: str) -> None:
    _escribir("INFO", mensaje)


def advertencia(mensaje: str, exc: Exception = None) -> None:
    _escribir("ADVERTENCIA", mensaje, exc)


def error(mensaje: str, exc: Exception = None) -> None:
    _escribir("ERROR", mensaje, exc)


def critico(mensaje: str, exc: Exception = None) -> None:
    _escribir("CRÍTICO", mensaje, exc)


def leer_logs() -> str:
    """Retorna el contenido del archivo de log."""
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(El archivo de log aún no ha sido creado.)"
    except OSError as e:
        return f"(No se pudo leer el log: {e})"
