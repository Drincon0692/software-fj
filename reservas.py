"""
reservas.py — Clase Reserva con confirmación, cancelación y manejo de excepciones.
"""
import datetime
from enum import Enum
from typing import Optional

from entidades import EntidadBase, Cliente
from servicios import Servicio
from excepciones import (
    ReservaYaConfirmadaError,
    ReservaCanceladaError,
    DuracionInvalidaError,
    ReservaNoEncontradaError,
    SistemaFJError,
)
import logger


class EstadoReserva(Enum):
    PENDIENTE   = "PENDIENTE"
    CONFIRMADA  = "CONFIRMADA"
    CANCELADA   = "CANCELADA"
    PROCESANDO  = "PROCESANDO"


# ═══════════════════════════════════════════════════════════════════════════════
# Clase Reserva
# ═══════════════════════════════════════════════════════════════════════════════

class Reserva(EntidadBase):
    """
    Integra un Cliente, un Servicio, duración y estado.
    Implementa confirmación, cancelación y cálculo de costo con excepciones.
    """

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        horas: float,
        notas: str = "",
        **kwargs_servicio,
    ):
        super().__init__()
        # ── Validaciones de entrada ──────────────────────────────────────────
        if not isinstance(cliente, Cliente):
            raise TypeError("El parámetro 'cliente' debe ser una instancia de Cliente.")
        if not isinstance(servicio, Servicio):
            raise TypeError("El parámetro 'servicio' debe ser una instancia de Servicio.")
        try:
            horas = float(horas)
        except (TypeError, ValueError) as exc:
            raise DuracionInvalidaError(horas) from exc
        if horas <= 0:
            raise DuracionInvalidaError(horas)

        self._cliente           = cliente
        self._servicio          = servicio
        self._horas             = horas
        self._kwargs_servicio   = kwargs_servicio
        self._notas             = notas.strip()
        self._estado            = EstadoReserva.PENDIENTE
        self._fecha_creacion    = datetime.datetime.now()
        self._fecha_confirmacion: Optional[datetime.datetime] = None
        self._fecha_cancelacion: Optional[datetime.datetime] = None
        self._costo_calculado: Optional[float] = None

        logger.info(
            f"Reserva creada: ID={self._id} | Cliente={self._cliente.email} "
            f"| Servicio={self._servicio.nombre} | Horas={self._horas}"
        )

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def costo(self) -> Optional[float]:
        return self._costo_calculado

    # ── Operaciones principales ───────────────────────────────────────────────

    def confirmar(self, descuento: float = 0.0, tasa_iva: float = 0.19) -> dict:
        """
        Confirma la reserva y calcula el costo final con impuesto y descuento.
        Usa try/except/else/finally para manejo completo de excepciones.
        """
        try:
            # Verificar que no esté ya confirmada o cancelada
            if self._estado == EstadoReserva.CONFIRMADA:
                raise ReservaYaConfirmadaError(self._id)
            if self._estado == EstadoReserva.CANCELADA:
                raise ReservaCanceladaError(self._id)

            self._estado = EstadoReserva.PROCESANDO

            # Validar cliente y servicio
            self._cliente.validar()
            self._servicio.validar()

            # Calcular costo con desglose
            desglose = self._servicio.calcular_costo_con_impuesto(
                self._horas,
                tasa_iva=tasa_iva,
                descuento=descuento,
                **self._kwargs_servicio,
            )
            self._costo_calculado = desglose["total"]

        except (ReservaYaConfirmadaError, ReservaCanceladaError):
            # Re-lanzar sin modificar estado
            self._estado = EstadoReserva.PENDIENTE
            logger.advertencia(f"Intento inválido de confirmar reserva {self._id}: ya en estado {self._estado.value}")
            raise

        except SistemaFJError as exc:
            # Encadenamiento de excepción: envolvemos en contexto de reserva
            self._estado = EstadoReserva.PENDIENTE
            logger.error(f"Error al confirmar reserva {self._id}: {exc}", exc)
            raise ReservaYaConfirmadaError.__new__(ReservaYaConfirmadaError) from exc

        except Exception as exc:
            self._estado = EstadoReserva.PENDIENTE
            logger.critico(f"Error inesperado al confirmar reserva {self._id}: {exc}", exc)
            raise

        else:
            # Solo se ejecuta si no hubo excepción
            self._estado             = EstadoReserva.CONFIRMADA
            self._fecha_confirmacion = datetime.datetime.now()
            logger.info(
                f"Reserva confirmada: {self._id} | Total: ${self._costo_calculado:,.2f}"
            )
            return desglose

        finally:
            # Siempre se ejecuta: garantiza que el estado no quede en PROCESANDO
            if self._estado == EstadoReserva.PROCESANDO:
                self._estado = EstadoReserva.PENDIENTE
                logger.advertencia(f"Reserva {self._id} regresó a PENDIENTE por error en confirmación.")

    def cancelar(self, motivo: str = "No especificado") -> bool:
        """
        Cancela la reserva. Usa try/except/finally.
        """
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise ReservaCanceladaError(self._id)
            if self._estado == EstadoReserva.CONFIRMADA:
                # Cancelar confirmada es costoso: advertencia
                logger.advertencia(
                    f"Cancelación de reserva ya confirmada: {self._id} | Motivo: {motivo}"
                )
        except ReservaCanceladaError:
            logger.advertencia(f"Intento de cancelar reserva ya cancelada: {self._id}")
            raise
        finally:
            pass  # En un sistema real: liberaría recursos aquí siempre

        self._estado           = EstadoReserva.CANCELADA
        self._fecha_cancelacion = datetime.datetime.now()
        logger.info(f"Reserva cancelada: {self._id} | Motivo: {motivo}")
        return True

    # ── Representación ───────────────────────────────────────────────────────

    def describir(self) -> str:
        costo_str = f"${self._costo_calculado:,.2f}" if self._costo_calculado else "Por calcular"
        return (
            f"[RESERVA {self._id}]\n"
            f"  Cliente  : {self._cliente.nombre} ({self._cliente.email})\n"
            f"  Servicio : {self._servicio.nombre}\n"
            f"  Duración : {self._horas} hora(s)\n"
            f"  Estado   : {self._estado.value}\n"
            f"  Costo    : {costo_str}\n"
            f"  Creada   : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def validar(self) -> bool:
        return self._estado not in (EstadoReserva.CANCELADA,)

    def __str__(self) -> str:
        return self.describir()


# ═══════════════════════════════════════════════════════════════════════════════
# Repositorio de Reservas (gestión en memoria)
# ═══════════════════════════════════════════════════════════════════════════════

class RepositorioReservas:

    def __init__(self):
        self._reservas: dict[str, Reserva] = {}

    def agregar(self, reserva: Reserva) -> Reserva:
        self._reservas[reserva.id] = reserva
        return reserva

    def buscar(self, id_reserva: str) -> Reserva:
        r = self._reservas.get(id_reserva.upper())
        if not r:
            raise ReservaNoEncontradaError(id_reserva)
        return r

    def listar(self) -> list[Reserva]:
        return list(self._reservas.values())

    def listar_por_estado(self, estado: EstadoReserva) -> list[Reserva]:
        return [r for r in self._reservas.values() if r.estado == estado]

    def total(self) -> int:
        return len(self._reservas)
