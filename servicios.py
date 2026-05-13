"""
servicios.py — Clase abstracta Servicio y servicios especializados con polimorfismo.

Servicios implementados:
  1. ReservaSala       — alquiler de salas de reuniones
  2. AlquilerEquipo    — renta de equipos tecnológicos
  3. AsesoriaEspecializada — consultoría profesional
"""
from abc import abstractmethod
from typing import Optional

from entidades import EntidadBase
from excepciones import (
    ServicioNoDisponibleError,
    ParametroServicioInvalidoError,
    CalculoCostoError,
    CapacidadExcedidaError,
)
import logger

# Tasa de impuesto por defecto (IVA Colombia 19 %)
IVA_DEFAULT = 0.19


# ═══════════════════════════════════════════════════════════════════════════════
# Clase abstracta Servicio
# ═══════════════════════════════════════════════════════════════════════════════

class Servicio(EntidadBase):
    """
    Clase abstracta que representa cualquier servicio ofrecido por Software FJ.
    Define la interfaz que todos los servicios deben implementar (polimorfismo).
    """

    def __init__(self, nombre: str, precio_hora: float, disponible: bool = True):
        super().__init__()
        self._nombre       = nombre.strip()
        self._precio_hora  = self._validar_precio(precio_hora)
        self._disponible   = disponible

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio_hora(self) -> float:
        return self._precio_hora

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = valor

    # ── Helpers internos ─────────────────────────────────────────────────────

    @staticmethod
    def _validar_precio(precio) -> float:
        try:
            precio = float(precio)
        except (TypeError, ValueError) as exc:
            raise ParametroServicioInvalidoError(
                "precio_hora", "Debe ser un número positivo."
            ) from exc
        if precio <= 0:
            raise ParametroServicioInvalidoError("precio_hora", f"Valor '{precio}' no es positivo.")
        return precio

    def _verificar_disponible(self):
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)

    # ── Métodos abstractos ───────────────────────────────────────────────────

    @abstractmethod
    def calcular_costo(self, horas: float, **kwargs) -> float:
        """Calcula el costo del servicio para la duración dada (con opciones)."""
        ...

    @abstractmethod
    def describir(self) -> str:
        ...

    @abstractmethod
    def validar(self) -> bool:
        ...

    # ── Método sobrecargado simulado ─────────────────────────────────────────
    # Python no soporta sobrecarga directa, la simulamos con parámetros opcionales.

    def calcular_costo_con_impuesto(
        self,
        horas: float,
        tasa_iva: float = IVA_DEFAULT,
        descuento: float = 0.0,
        **kwargs
    ) -> dict:
        """
        Variante de cálculo que incluye IVA y descuento.
        Retorna un desglose detallado del costo.
        """
        try:
            if not 0 <= descuento < 1:
                raise CalculoCostoError(f"El descuento ({descuento}) debe estar entre 0 y 1 (exclusivo).")
            if not 0 <= tasa_iva <= 1:
                raise CalculoCostoError(f"La tasa IVA ({tasa_iva}) debe estar entre 0 y 1.")

            subtotal    = self.calcular_costo(horas, **kwargs)
            desc_valor  = subtotal * descuento
            base        = subtotal - desc_valor
            impuesto    = base * tasa_iva
            total       = base + impuesto

            return {
                "subtotal":    round(subtotal, 2),
                "descuento":   round(desc_valor, 2),
                "base_imponible": round(base, 2),
                "iva":         round(impuesto, 2),
                "total":       round(total, 2),
                "tasa_iva":    tasa_iva,
            }
        except CalculoCostoError:
            raise
        except Exception as exc:
            raise CalculoCostoError(str(exc)) from exc

    def __str__(self) -> str:
        return self.describir()


# ═══════════════════════════════════════════════════════════════════════════════
# Servicio 1: Reserva de Sala
# ═══════════════════════════════════════════════════════════════════════════════

class ReservaSala(Servicio):
    """
    Alquiler de salas de reuniones.
    Parámetros extra: capacidad_max (personas), equipada (proyector, etc.)
    """

    CAPACIDAD_ABSOLUTA = 50

    def __init__(
        self,
        nombre: str,
        precio_hora: float,
        capacidad_max: int,
        equipada: bool = False,
        disponible: bool = True,
    ):
        super().__init__(nombre, precio_hora, disponible)
        self._capacidad_max = self._validar_capacidad(capacidad_max)
        self._equipada      = equipada

    @staticmethod
    def _validar_capacidad(cap) -> int:
        try:
            cap = int(cap)
        except (TypeError, ValueError) as exc:
            raise ParametroServicioInvalidoError("capacidad_max", "Debe ser un entero.") from exc
        if cap <= 0 or cap > ReservaSala.CAPACIDAD_ABSOLUTA:
            raise ParametroServicioInvalidoError(
                "capacidad_max",
                f"Debe estar entre 1 y {ReservaSala.CAPACIDAD_ABSOLUTA}."
            )
        return cap

    @property
    def capacidad_max(self) -> int:
        return self._capacidad_max

    # ── Polimorfismo ─────────────────────────────────────────────────────────

    def calcular_costo(self, horas: float, personas: int = 1, **kwargs) -> float:
        """
        Costo base = precio_hora × horas.
        Si la sala está equipada, se aplica un recargo del 20 %.
        """
        self._verificar_disponible()
        try:
            horas    = float(horas)
            personas = int(personas)
        except (TypeError, ValueError) as exc:
            raise ParametroServicioInvalidoError("horas/personas", str(exc)) from exc

        if horas <= 0:
            raise ParametroServicioInvalidoError("horas", "Debe ser positivo.")
        if personas > self._capacidad_max:
            raise CapacidadExcedidaError(self._capacidad_max, personas)

        costo = self._precio_hora * horas
        if self._equipada:
            costo *= 1.20
        return round(costo, 2)

    def describir(self) -> str:
        equip = "Con equipamiento" if self._equipada else "Sin equipamiento"
        disp  = "✓ Disponible" if self._disponible else "✗ No disponible"
        return (
            f"[SALA {self._id}] {self._nombre} | Capacidad: {self._capacidad_max} personas "
            f"| {equip} | ${self._precio_hora:,.0f}/hr | {disp}"
        )

    def validar(self) -> bool:
        self._verificar_disponible()
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# Servicio 2: Alquiler de Equipo
# ═══════════════════════════════════════════════════════════════════════════════

class AlquilerEquipo(Servicio):
    """
    Renta de equipos tecnológicos (laptops, proyectores, servidores, etc.)
    Parámetros extra: unidades (cuántos equipos se alquilan)
    """

    UNIDADES_MAX = 20

    def __init__(
        self,
        nombre: str,
        precio_hora: float,
        tipo_equipo: str,
        unidades_disponibles: int,
        disponible: bool = True,
    ):
        super().__init__(nombre, precio_hora, disponible)
        if not tipo_equipo or not isinstance(tipo_equipo, str):
            raise ParametroServicioInvalidoError("tipo_equipo", "No puede estar vacío.")
        self._tipo_equipo          = tipo_equipo.strip()
        self._unidades_disponibles = self._validar_unidades(unidades_disponibles)

    @staticmethod
    def _validar_unidades(u) -> int:
        try:
            u = int(u)
        except (TypeError, ValueError) as exc:
            raise ParametroServicioInvalidoError("unidades_disponibles", str(exc)) from exc
        if u < 0 or u > AlquilerEquipo.UNIDADES_MAX:
            raise ParametroServicioInvalidoError(
                "unidades_disponibles",
                f"Debe estar entre 0 y {AlquilerEquipo.UNIDADES_MAX}."
            )
        return u

    @property
    def unidades_disponibles(self) -> int:
        return self._unidades_disponibles

    # ── Polimorfismo ─────────────────────────────────────────────────────────

    def calcular_costo(self, horas: float, unidades: int = 1, **kwargs) -> float:
        """
        Costo = precio_hora × horas × unidades.
        Descuento por volumen: >5 unidades → 10 %.
        """
        self._verificar_disponible()
        try:
            horas    = float(horas)
            unidades = int(unidades)
        except (TypeError, ValueError) as exc:
            raise ParametroServicioInvalidoError("horas/unidades", str(exc)) from exc

        if horas <= 0:
            raise ParametroServicioInvalidoError("horas", "Debe ser positivo.")
        if unidades <= 0:
            raise ParametroServicioInvalidoError("unidades", "Debe ser al menos 1.")
        if unidades > self._unidades_disponibles:
            raise CapacidadExcedidaError(self._unidades_disponibles, unidades)

        costo = self._precio_hora * horas * unidades
        if unidades > 5:
            costo *= 0.90   # 10 % descuento por volumen
        return round(costo, 2)

    def describir(self) -> str:
        disp = "✓ Disponible" if self._disponible else "✗ No disponible"
        return (
            f"[EQUIPO {self._id}] {self._nombre} | Tipo: {self._tipo_equipo} "
            f"| Unidades: {self._unidades_disponibles} | ${self._precio_hora:,.0f}/hr | {disp}"
        )

    def validar(self) -> bool:
        self._verificar_disponible()
        if self._unidades_disponibles == 0:
            raise ServicioNoDisponibleError(self._nombre)
        return True


# ═══════════════════════════════════════════════════════════════════════════════
# Servicio 3: Asesoría Especializada
# ═══════════════════════════════════════════════════════════════════════════════

NIVELES_ASESORIA = {"junior": 1.0, "senior": 1.5, "experto": 2.0}


class AsesoriaEspecializada(Servicio):
    """
    Consultoría / asesoría profesional por un especialista.
    Parámetros extra: nivel_asesor (junior/senior/experto), sesiones (cantidad)
    """

    def __init__(
        self,
        nombre: str,
        precio_hora: float,
        especialidad: str,
        nivel_asesor: str = "senior",
        disponible: bool = True,
    ):
        super().__init__(nombre, precio_hora, disponible)
        if not especialidad or not isinstance(especialidad, str):
            raise ParametroServicioInvalidoError("especialidad", "No puede estar vacía.")
        nivel = nivel_asesor.strip().lower()
        if nivel not in NIVELES_ASESORIA:
            raise ParametroServicioInvalidoError(
                "nivel_asesor",
                f"Debe ser uno de: {list(NIVELES_ASESORIA.keys())}."
            )
        self._especialidad  = especialidad.strip()
        self._nivel_asesor  = nivel

    @property
    def nivel_asesor(self) -> str:
        return self._nivel_asesor

    # ── Polimorfismo ─────────────────────────────────────────────────────────

    def calcular_costo(self, horas: float, sesiones: int = 1, **kwargs) -> float:
        """
        Costo = precio_hora × multiplicador_nivel × horas × sesiones.
        Paquete de >=4 sesiones: 15 % de descuento.
        """
        self._verificar_disponible()
        try:
            horas   = float(horas)
            sesiones = int(sesiones)
        except (TypeError, ValueError) as exc:
            raise ParametroServicioInvalidoError("horas/sesiones", str(exc)) from exc

        if horas <= 0:
            raise ParametroServicioInvalidoError("horas", "Debe ser positivo.")
        if sesiones <= 0:
            raise ParametroServicioInvalidoError("sesiones", "Debe ser al menos 1.")

        multiplicador = NIVELES_ASESORIA[self._nivel_asesor]
        costo = self._precio_hora * multiplicador * horas * sesiones
        if sesiones >= 4:
            costo *= 0.85
        return round(costo, 2)

    def describir(self) -> str:
        disp = "✓ Disponible" if self._disponible else "✗ No disponible"
        mult = NIVELES_ASESORIA[self._nivel_asesor]
        return (
            f"[ASESORÍA {self._id}] {self._nombre} | Especialidad: {self._especialidad} "
            f"| Nivel: {self._nivel_asesor.upper()} (x{mult}) "
            f"| ${self._precio_hora:,.0f}/hr base | {disp}"
        )

    def validar(self) -> bool:
        self._verificar_disponible()
        return True
