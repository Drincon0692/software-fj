"""
excepciones.py — Excepciones personalizadas del sistema Software FJ
"""


class SistemaFJError(Exception):
    """Excepción base del sistema. Todas las excepciones heredan de aquí."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERICO"):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(f"[{codigo}] {mensaje}")


# ── Excepciones de Cliente ────────────────────────────────────────────────────

class ClienteError(SistemaFJError):
    """Errores relacionados con la entidad Cliente."""
    pass


class ClienteYaExisteError(ClienteError):
    def __init__(self, email: str):
        super().__init__(f"El cliente con email '{email}' ya está registrado.", "ERR_CLIENTE_DUPLICADO")


class ClienteNoEncontradoError(ClienteError):
    def __init__(self, identificador: str):
        super().__init__(f"No se encontró ningún cliente con el identificador '{identificador}'.", "ERR_CLIENTE_NOT_FOUND")


class DatosClienteInvalidosError(ClienteError):
    def __init__(self, campo: str, valor):
        super().__init__(f"El campo '{campo}' tiene un valor inválido: '{valor}'.", "ERR_DATO_INVALIDO")


# ── Excepciones de Servicio ───────────────────────────────────────────────────

class ServicioError(SistemaFJError):
    """Errores relacionados con servicios."""
    pass


class ServicioNoDisponibleError(ServicioError):
    def __init__(self, nombre: str):
        super().__init__(f"El servicio '{nombre}' no está disponible en este momento.", "ERR_SERVICIO_NO_DISPONIBLE")


class ParametroServicioInvalidoError(ServicioError):
    def __init__(self, parametro: str, detalle: str = ""):
        msg = f"Parámetro de servicio inválido: '{parametro}'."
        if detalle:
            msg += f" {detalle}"
        super().__init__(msg, "ERR_PARAM_INVALIDO")


class CalculoCostoError(ServicioError):
    def __init__(self, detalle: str):
        super().__init__(f"Error al calcular el costo del servicio: {detalle}", "ERR_CALCULO_COSTO")


# ── Excepciones de Reserva ────────────────────────────────────────────────────

class ReservaError(SistemaFJError):
    """Errores relacionados con reservas."""
    pass


class ReservaNoEncontradaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva con ID '{id_reserva}' no existe.", "ERR_RESERVA_NOT_FOUND")


class ReservaYaConfirmadaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva '{id_reserva}' ya fue confirmada y no puede modificarse.", "ERR_RESERVA_CONFIRMADA")


class ReservaCanceladaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva '{id_reserva}' ya fue cancelada.", "ERR_RESERVA_CANCELADA")


class DuracionInvalidaError(ReservaError):
    def __init__(self, duracion):
        super().__init__(f"La duración '{duracion}' horas no es válida (debe ser > 0).", "ERR_DURACION")


class CapacidadExcedidaError(ReservaError):
    def __init__(self, capacidad_max: int, solicitada: int):
        super().__init__(
            f"La capacidad solicitada ({solicitada}) excede el máximo permitido ({capacidad_max}).",
            "ERR_CAPACIDAD"
        )
