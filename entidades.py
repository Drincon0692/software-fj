"""
entidades.py — Clase abstracta base y clase Cliente con encapsulación robusta
"""
import re
import uuid
from abc import ABC, abstractmethod
from typing import Optional

from excepciones import (
    DatosClienteInvalidosError,
    ClienteYaExisteError,
    ClienteNoEncontradoError,
)
import logger


# ═══════════════════════════════════════════════════════════════════════════════
# Clase abstracta base — define la interfaz común del sistema
# ═══════════════════════════════════════════════════════════════════════════════

class EntidadBase(ABC):
    """
    Clase abstracta raíz del sistema.
    Toda entidad (Cliente, Servicio, Reserva) hereda de aquí,
    garantizando una identidad única y métodos de representación uniformes.
    """

    def __init__(self):
        self._id: str = str(uuid.uuid4())[:8].upper()

    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción legible de la entidad."""
        ...

    @abstractmethod
    def validar(self) -> bool:
        """Valida el estado interno de la entidad. Lanza excepción si es inválida."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id}>"


# ═══════════════════════════════════════════════════════════════════════════════
# Cliente
# ═══════════════════════════════════════════════════════════════════════════════

class Cliente(EntidadBase):
    """
    Representa un cliente registrado en Software FJ.
    Implementa encapsulación estricta con propiedades y validaciones.
    """

    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    _TEL_RE   = re.compile(r"^\+?[\d\s\-]{7,15}$")

    def __init__(self, nombre: str, email: str, telefono: str, empresa: Optional[str] = None):
        super().__init__()
        # Usamos los setters para disparar validaciones desde el inicio
        self.nombre    = nombre
        self.email     = email
        self.telefono  = telefono
        self._empresa  = empresa.strip() if empresa else None
        self._activo   = True
        logger.info(f"Cliente creado: {self._email} (ID={self._id})")

    # ── Propiedades / Encapsulación ───────────────────────────────────────────

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise DatosClienteInvalidosError("nombre", valor)
        self._nombre = valor.strip().title()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        if not isinstance(valor, str) or not self._EMAIL_RE.match(valor.strip()):
            raise DatosClienteInvalidosError("email", valor)
        self._email = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not isinstance(valor, str) or not self._TEL_RE.match(valor.strip()):
            raise DatosClienteInvalidosError("telefono", valor)
        self._telefono = valor.strip()

    @property
    def empresa(self) -> Optional[str]:
        return self._empresa

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self):
        self._activo = False
        logger.info(f"Cliente desactivado: {self._email}")

    # ── Métodos abstractos implementados ─────────────────────────────────────

    def describir(self) -> str:
        estado = "Activo" if self._activo else "Inactivo"
        emp    = f" | Empresa: {self._empresa}" if self._empresa else ""
        return (
            f"[CLIENTE {self._id}] {self._nombre} — {self._email} "
            f"| Tel: {self._telefono}{emp} | Estado: {estado}"
        )

    def validar(self) -> bool:
        # Las validaciones ya ocurren en los setters; aquí verificamos estado activo
        if not self._activo:
            raise DatosClienteInvalidosError("activo", False)
        return True

    def __str__(self) -> str:
        return self.describir()


# ═══════════════════════════════════════════════════════════════════════════════
# Repositorio de Clientes (gestión en memoria)
# ═══════════════════════════════════════════════════════════════════════════════

class RepositorioClientes:
    """
    Gestiona la colección de clientes en memoria.
    Garantiza unicidad por email.
    """

    def __init__(self):
        self._clientes: dict[str, Cliente] = {}   # email → Cliente

    def registrar(self, cliente: Cliente) -> Cliente:
        try:
            if cliente.email in self._clientes:
                raise ClienteYaExisteError(cliente.email)
            cliente.validar()
            self._clientes[cliente.email] = cliente
            logger.info(f"Cliente registrado en repositorio: {cliente.email}")
            return cliente
        except ClienteYaExisteError:
            logger.advertencia(f"Intento de registro duplicado: {cliente.email}")
            raise
        except Exception as exc:
            logger.error(f"Error al registrar cliente: {exc}", exc)
            raise

    def buscar_por_email(self, email: str) -> Cliente:
        email = email.strip().lower()
        if email not in self._clientes:
            raise ClienteNoEncontradoError(email)
        return self._clientes[email]

    def buscar_por_id(self, id_cliente: str) -> Cliente:
        for c in self._clientes.values():
            if c.id == id_cliente.upper():
                return c
        raise ClienteNoEncontradoError(id_cliente)

    def listar(self) -> list[Cliente]:
        return list(self._clientes.values())

    def total(self) -> int:
        return len(self._clientes)
