"""
main.py — Demostración del Sistema Integral Software FJ
Simula 10+ operaciones completas (exitosas y fallidas) con manejo de excepciones.
"""
import os
import sys

# Asegurar que el directorio del proyecto esté en el path
sys.path.insert(0, os.path.dirname(__file__))

from entidades import Cliente, RepositorioClientes
from servicios import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from reservas import Reserva, RepositorioReservas, EstadoReserva
from excepciones import (
    SistemaFJError,
    ClienteYaExisteError,
    DatosClienteInvalidosError,
    ServicioNoDisponibleError,
    ParametroServicioInvalidoError,
    CapacidadExcedidaError,
    ReservaYaConfirmadaError,
    ReservaCanceladaError,
)
import logger

# ── Colores ANSI para salida en terminal ──────────────────────────────────────
VERDE   = "\033[92m"
ROJO    = "\033[91m"
AMARILLO= "\033[93m"
AZUL    = "\033[94m"
CYAN    = "\033[96m"
BOLD    = "\033[1m"
RESET   = "\033[0m"

repo_clientes = RepositorioClientes()
repo_reservas = RepositorioReservas()

operacion_num = 0


def titulo(texto: str):
    global operacion_num
    operacion_num += 1
    print(f"\n{BOLD}{AZUL}{'═'*65}{RESET}")
    print(f"{BOLD}{AZUL}  OP {operacion_num:02d} │ {texto}{RESET}")
    print(f"{BOLD}{AZUL}{'═'*65}{RESET}")


def ok(msg: str):
    print(f"  {VERDE}✔ {msg}{RESET}")


def fallo(msg: str):
    print(f"  {ROJO}✘ {msg}{RESET}")


def info(msg: str):
    print(f"  {CYAN}ℹ {msg}{RESET}")


def separador():
    print(f"  {AMARILLO}{'─'*60}{RESET}")


def main():
    print(f"\n{BOLD}{'═'*65}")
    print(f"      SOFTWARE FJ — Sistema Integral de Gestión")
    print(f"{'═'*65}{RESET}\n")
    logger.info("═══ Inicio de demostración del sistema Software FJ ═══")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 01 — Registro válido de clientes
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Registro VÁLIDO de clientes")
    clientes_datos = [
        ("Ana García",    "ana.garcia@empresa.co",    "+57 300 1234567", "TechCorp SA"),
        ("Luis Martínez", "luis.martinez@gmail.com",  "+57 311 9876543", None),
        ("Carla Rojas",   "carla.rojas@consulting.co","+57 320 5551234", "Consulting Pro"),
    ]
    clientes_ok = []
    for nombre, email, tel, emp in clientes_datos:
        try:
            c = Cliente(nombre, email, tel, emp)
            repo_clientes.registrar(c)
            clientes_ok.append(c)
            ok(f"Cliente registrado: {c.nombre} ({c.email})")
        except SistemaFJError as e:
            fallo(f"Error inesperado: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 02 — Registro inválido: email malformado
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Registro INVÁLIDO — email malformado")
    try:
        c = Cliente("Pedro Inválido", "no-es-un-email", "+57 300 0000001")
        repo_clientes.registrar(c)
        fallo("Debió lanzar excepción por email inválido.")
    except DatosClienteInvalidosError as e:
        ok(f"Excepción capturada correctamente → {e}")
    except Exception as e:
        fallo(f"Excepción inesperada: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 03 — Registro inválido: nombre muy corto
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Registro INVÁLIDO — nombre demasiado corto")
    try:
        c = Cliente("X", "valido@correo.com", "+57 300 0000002")
        repo_clientes.registrar(c)
        fallo("Debió lanzar excepción por nombre corto.")
    except DatosClienteInvalidosError as e:
        ok(f"Excepción capturada correctamente → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 04 — Registro duplicado
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Registro INVÁLIDO — cliente duplicado")
    try:
        duplicado = Cliente("Ana García", "ana.garcia@empresa.co", "+57 300 9999999")
        repo_clientes.registrar(duplicado)
        fallo("Debió detectar el duplicado.")
    except ClienteYaExisteError as e:
        ok(f"Duplicado detectado → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 05 — Creación válida de servicios
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Creación VÁLIDA de servicios")
    sala_a       = None
    equipo_b     = None
    asesoria_c   = None
    try:
        sala_a = ReservaSala(
            nombre="Sala Innovación A",
            precio_hora=150_000,
            capacidad_max=12,
            equipada=True,
        )
        ok(f"Sala creada: {sala_a.describir()}")

        equipo_b = AlquilerEquipo(
            nombre="Laptop HP ProBook",
            precio_hora=45_000,
            tipo_equipo="Laptop",
            unidades_disponibles=10,
        )
        ok(f"Equipo creado: {equipo_b.describir()}")

        asesoria_c = AsesoriaEspecializada(
            nombre="Asesoría Cloud Computing",
            precio_hora=200_000,
            especialidad="Infraestructura en la nube",
            nivel_asesor="experto",
        )
        ok(f"Asesoría creada: {asesoria_c.describir()}")

    except SistemaFJError as e:
        fallo(f"Error al crear servicio: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 06 — Creación inválida de servicio: nivel asesor inválido
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Creación INVÁLIDA — nivel de asesor incorrecto")
    try:
        mal = AsesoriaEspecializada(
            "Asesoría X", 100_000, "IT", nivel_asesor="dios"
        )
        fallo("Debió rechazar el nivel 'dios'.")
    except ParametroServicioInvalidoError as e:
        ok(f"Nivel inválido capturado → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 07 — Servicio no disponible
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Servicio NO DISPONIBLE")
    sala_cerrada = None
    try:
        sala_cerrada = ReservaSala(
            nombre="Sala Mantenimiento",
            precio_hora=100_000,
            capacidad_max=8,
            disponible=False,
        )
        sala_cerrada.calcular_costo(2, personas=4)
        fallo("Debió indicar que el servicio no está disponible.")
    except ServicioNoDisponibleError as e:
        ok(f"Servicio no disponible detectado → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 08 — Reserva EXITOSA con cálculo de costo y confirmación
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Reserva EXITOSA — Sala de reuniones con IVA y descuento")
    reserva1 = None
    if clientes_ok and sala_a:
        try:
            reserva1 = Reserva(
                cliente=clientes_ok[0],
                servicio=sala_a,
                horas=3,
                personas=8,
            )
            repo_reservas.agregar(reserva1)
            desglose = reserva1.confirmar(descuento=0.10, tasa_iva=0.19)
            ok(f"Reserva confirmada: {reserva1.id}")
            separador()
            info(f"Subtotal   : ${desglose['subtotal']:>12,.2f}")
            info(f"Descuento  : ${desglose['descuento']:>12,.2f}")
            info(f"Base impon.: ${desglose['base_imponible']:>12,.2f}")
            info(f"IVA (19 %) : ${desglose['iva']:>12,.2f}")
            info(f"TOTAL      : ${desglose['total']:>12,.2f}")
        except SistemaFJError as e:
            fallo(f"Error en reserva: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 09 — Reserva FALLIDA: capacidad excedida
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Reserva FALLIDA — Capacidad excedida")
    if clientes_ok and sala_a:
        try:
            r_cap = Reserva(
                cliente=clientes_ok[1],
                servicio=sala_a,
                horas=2,
                personas=sala_a.capacidad_max + 5,   # excede la capacidad
            )
            repo_reservas.agregar(r_cap)
            r_cap.confirmar()
            fallo("Debió detectar exceso de capacidad.")
        except CapacidadExcedidaError as e:
            ok(f"Capacidad excedida detectada → {e}")
        except SistemaFJError as e:
            ok(f"Error del sistema capturado → {type(e).__name__}: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 10 — Reserva de equipo y cancelación
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Reserva EQUIPO + cancelación posterior")
    reserva2 = None
    if len(clientes_ok) >= 2 and equipo_b:
        try:
            reserva2 = Reserva(
                cliente=clientes_ok[1],
                servicio=equipo_b,
                horas=4,
                unidades=6,   # >5 → descuento 10 %
            )
            repo_reservas.agregar(reserva2)
            desglose2 = reserva2.confirmar(descuento=0.05)
            ok(f"Reserva de equipo confirmada: {reserva2.id} | Total: ${desglose2['total']:,.2f}")

            # Cancelar
            reserva2.cancelar("Cliente cambió de plan")
            ok(f"Reserva {reserva2.id} cancelada. Estado: {reserva2.estado.value}")
        except SistemaFJError as e:
            fallo(f"Error: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 11 — Reconfirmar reserva cancelada (debe fallar)
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Intento de confirmar reserva YA CANCELADA")
    if reserva2:
        try:
            reserva2.confirmar()
            fallo("Debió rechazar la confirmación.")
        except ReservaCanceladaError as e:
            ok(f"Cancelada detectada correctamente → {e}")
        except SistemaFJError as e:
            ok(f"Error del sistema → {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 12 — Asesoría con paquete de sesiones y descuento automático
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Asesoría — Paquete 4 sesiones (descuento 15 %)")
    if len(clientes_ok) >= 3 and asesoria_c:
        try:
            r_ases = Reserva(
                cliente=clientes_ok[2],
                servicio=asesoria_c,
                horas=2,
                sesiones=4,
            )
            repo_reservas.agregar(r_ases)
            desglose3 = r_ases.confirmar(tasa_iva=0.19)
            ok(f"Asesoría confirmada: {r_ases.id}")
            separador()
            info(f"Subtotal   : ${desglose3['subtotal']:>12,.2f}")
            info(f"IVA (19 %) : ${desglose3['iva']:>12,.2f}")
            info(f"TOTAL      : ${desglose3['total']:>12,.2f}")
        except SistemaFJError as e:
            fallo(f"Error: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # OP 13 — Reserva con duración inválida (0 horas)
    # ══════════════════════════════════════════════════════════════════════════
    titulo("Reserva INVÁLIDA — duración de 0 horas")
    if clientes_ok and sala_a:
        try:
            r_dur = Reserva(clientes_ok[0], sala_a, horas=0)
            fallo("Debió rechazar la duración 0.")
        except Exception as e:
            ok(f"Duración inválida detectada → {type(e).__name__}: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════════════════════════════════════════════
    print(f"\n{BOLD}{CYAN}{'═'*65}")
    print(f"  RESUMEN DEL SISTEMA")
    print(f"{'═'*65}{RESET}")
    print(f"  {BOLD}Clientes registrados :{RESET} {repo_clientes.total()}")
    print(f"  {BOLD}Reservas creadas     :{RESET} {repo_reservas.total()}")

    confirmadas = len(repo_reservas.listar_por_estado(EstadoReserva.CONFIRMADA))
    canceladas  = len(repo_reservas.listar_por_estado(EstadoReserva.CANCELADA))
    pendientes  = len(repo_reservas.listar_por_estado(EstadoReserva.PENDIENTE))

    print(f"  {VERDE}Confirmadas          : {confirmadas}{RESET}")
    print(f"  {ROJO}Canceladas           : {canceladas}{RESET}")
    print(f"  {AMARILLO}Pendientes           : {pendientes}{RESET}")

    print(f"\n  {BOLD}Clientes:{RESET}")
    for c in repo_clientes.listar():
        print(f"    • {c.describir()}")

    print(f"\n  {BOLD}Reservas:{RESET}")
    for r in repo_reservas.listar():
        estado_color = VERDE if r.estado == EstadoReserva.CONFIRMADA else (
            ROJO if r.estado == EstadoReserva.CANCELADA else AMARILLO
        )
        costo = f"${r.costo:,.2f}" if r.costo else "N/A"
        print(f"    • [{estado_color}{r.estado.value}{RESET}] {r.id} — {r.servicio.nombre} ({r.horas}h) — {costo}")

    print(f"\n  {BOLD}Log de eventos:{RESET} {logger.LOG_PATH}")
    logger.info("═══ Fin de demostración del sistema Software FJ ═══")
    print(f"\n{CYAN}  Sistema finalizado sin interrupciones. ✔{RESET}\n")


if __name__ == "__main__":
    main()
