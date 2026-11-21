"""PROYECTO FASE 4
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Autor: Daniel Herrera Ocampo
Programa: Ingeniería de Sistemas - UNAD"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging

# CONFIGURACIÓN DEL ARCHIVO DE REGISTRO

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# EXCEPCIONES PERSONALIZADAS

class SistemaFJError(Exception):
    """Excepción general para los errores controlados del sistema."""
    pass

class DatosInvalidosError(SistemaFJError):
    """Se presenta cuando los datos ingresados no cumplen las reglas."""
    pass

class ServicioNoDisponibleError(SistemaFJError):
    """Se presenta cuando se intenta reservar un servicio no disponible."""
    pass

class ReservaError(SistemaFJError):
    """Se presenta cuando una reserva no puede procesarse."""
    pass

# CLASE ABSTRACTA GENERAL

class Entidad(ABC):
    """Representa una entidad general que debe tener un identificador."""

    def __init__(self, identificador):
        if not str(identificador).strip():
            raise DatosInvalidosError("El identificador no puede estar vacío.")
        self._identificador = str(identificador)

    @property
    def identificador(self):
        """Permite consultar el identificador sin modificarlo directamente."""
        return self._identificador

    @abstractmethod
    def mostrar_informacion(self):
        """Cada entidad concreta debe implementar este método."""
        pass

# CLASE CLIENTE

class Cliente(Entidad):
    """Almacena los datos básicos de un cliente con atributos encapsulados."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)

        # Se validan los datos antes de almacenarlos.
        if not nombre or not nombre.strip():
            raise DatosInvalidosError("El nombre del cliente es obligatorio.")
        if not correo or "@" not in correo or "." not in correo.split("@")[-1]:
            raise DatosInvalidosError("El correo electrónico no tiene un formato válido.")
        if not telefono or not telefono.strip() or not telefono.replace("+", "").isdigit():
            raise DatosInvalidosError("El teléfono debe contener números y puede iniciar con +.")

        self.__nombre = nombre.strip()
        self.__correo = correo.strip().lower()
        self.__telefono = telefono.strip()

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    @property
    def telefono(self):
        return self.__telefono

    def mostrar_informacion(self):
        return (
            f"Cliente: {self.__nombre} | ID: {self.identificador} | "
            f"Correo: {self.__correo} | Teléfono: {self.__telefono}"
        )

# CLASE ABSTRACTA SERVICIO

class Servicio(Entidad):
    """Clase base para los diferentes servicios ofrecidos por Software FJ."""

    def __init__(self, identificador, nombre, tarifa, disponible=True):
        super().__init__(identificador)
        if not nombre or not nombre.strip():
            raise DatosInvalidosError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa, (int, float)) or tarifa <= 0:
            raise DatosInvalidosError("La tarifa debe ser un número mayor que cero.")

        self.nombre = nombre.strip()
        self.tarifa = float(tarifa)
        self.disponible = bool(disponible)

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """Calcula el costo según las reglas del servicio."""
        pass

    @abstractmethod
    def describir(self):
        """Devuelve la descripción del servicio."""
        pass

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duración debe ser un número mayor que cero.")
        if not self.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{self.nombre}' no se encuentra disponible."
            )

    def mostrar_informacion(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return f"{self.nombre} - Tarifa: ${self.tarifa:,.0f} - {estado}"

# SERVICIOS ESPECIALIZADOS: HERENCIA Y POLIMORFISMO

class ReservaSala(Servicio):
    """Servicio de alquiler de salas por hora."""

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa * duracion
        return subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)

    def describir(self):
        return "Reserva de sala por horas para reuniones o actividades."

class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por día."""

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa * duracion
        return subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)

    def describir(self):
        return "Alquiler de equipos tecnológicos por días."

class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría especializada por hora."""

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa * duracion
        return subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)

    def describir(self):
        return "Asesoría especializada brindada por personal capacitado."

# CLASE RESERVA

class Reserva(Entidad):
    """Relaciona un cliente con un servicio, una duración y un estado."""

    ESTADOS_VALIDOS = ("Pendiente", "Confirmada", "Cancelada")

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("La reserva debe tener un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva debe tener un servicio válido.")
        servicio.validar_parametros(duracion)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.costo = 0.0

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaError("Solo se pueden confirmar reservas pendientes.")
        self.servicio.validar_parametros(self.duracion)
        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaError("La reserva ya se encuentra cancelada.")
        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self, impuesto=0, descuento=0):
        """Procesa la reserva y registra el costo; demuestra encadenamiento."""
        try:
            if self.estado != "Confirmada":
                raise ValueError("La reserva debe estar confirmada antes de procesarse.")
            self.costo = self.servicio.calcular_costo(
                self.duracion, impuesto, descuento
            )
            logging.info(
                "Reserva %s procesada. Costo: %.2f",
                self.identificador, self.costo
            )
            return self.costo
        except (ValueError, SistemaFJError) as error:
            logging.exception("Error al procesar la reserva %s.", self.identificador)
            # Encadenamiento: la excepción original queda asociada a ReservaError.
            raise ReservaError("No fue posible procesar la reserva.") from error
        finally:
            logging.info("Finalizó el intento de procesamiento de reserva %s.",
                         self.identificador)

    def mostrar_informacion(self):
        return (
            f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | "
            f"Estado: {self.estado} | Costo: ${self.costo:,.0f}"
        )

# GESTOR DEL SISTEMA: LISTAS INTERNAS, REGISTRO Y OPERACIONES

class SistemaFJ:
    """Administra clientes, servicios y reservas usando listas en memoria."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El objeto no corresponde a un cliente.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatosInvalidosError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s.", cliente.identificador)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El objeto no corresponde a un servicio.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatosInvalidosError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s.", servicio.identificador)
        return servicio

    def crear_reserva(self, identificador, cliente, servicio, duracion):
        reserva = Reserva(identificador, cliente, servicio, duracion)
        if any(r.identificador == identificador for r in self.reservas):
            raise DatosInvalidosError("Ya existe una reserva con ese identificador.")
        self.reservas.append(reserva)
        logging.info("Reserva creada: %s.", identificador)
        return reserva

    def listar_datos(self):
        print("\n--- CLIENTES ---")
        for cliente in self.clientes:
            print(cliente.mostrar_informacion())
        print("\n--- SERVICIOS ---")
        for servicio in self.servicios:
            print(servicio.mostrar_informacion())
        print("\n--- RESERVAS ---")
        for reserva in self.reservas:
            print(reserva.mostrar_informacion())

# DEMOSTRACIÓN DE OPERACIONES (MÁS DE 10 CASOS)

def ejecutar_demostracion():
    sistema = SistemaFJ()
    print("=" * 65)
    print("SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("Demostración de operaciones y manejo de excepciones")
    print("=" * 65)

    # Operación 1: registro correcto de cliente.
    cliente1 = sistema.registrar_cliente(
        Cliente("C001", "Laura Gómez", "laura@gmail.com", "3001234567")
    )
    print("\n1. Cliente válido registrado correctamente.")

    # Operación 2: otro cliente válido.
    cliente2 = sistema.registrar_cliente(
        Cliente("C002", "Carlos Pérez", "carlos@hotmail.com", "3107654321")
    )
    print("2. Segundo cliente válido registrado.")

    # Operación 3: intento de crear un cliente con correo inválido.
    try:
        Cliente("C003", "Andrés Ruiz", "correo_incorrecto", "3005551111")
    except DatosInvalidosError as error:
        print("3. Registro inválido controlado:", error)
        logging.warning("Intento de registro de cliente inválido: %s", error)

    # Operación 4: registrar servicio de sala.
    sala = sistema.registrar_servicio(
        ReservaSala("S001", "Sala de reuniones", 50000)
    )
    print("4. Servicio de reserva de sala registrado.")

    # Operación 5: registrar alquiler de equipo.
    equipo = sistema.registrar_servicio(
        AlquilerEquipo("S002", "Computador portátil", 80000)
    )
    print("5. Servicio de alquiler de equipo registrado.")

    # Operación 6: registrar asesoría.
    asesoria = sistema.registrar_servicio(
        AsesoriaEspecializada("S003", "Asesoría de software", 100000)
    )
    print("6. Servicio de asesoría registrado.")

    # Operación 7: intento de crear servicio con tarifa inválida.
    try:
        ReservaSala("S004", "Sala económica", -1000)
    except DatosInvalidosError as error:
        print("7. Creación de servicio inválida controlada:", error)
        logging.warning("Intento de servicio inválido: %s", error)

    # Operación 8: crear y confirmar una reserva válida.
    reserva1 = sistema.crear_reserva("R001", cliente1, sala, 2)
    reserva1.confirmar()
    print("8. Reserva R001 creada y confirmada.")

    # Operación 9: procesar la reserva con impuesto del 19%.
    costo = reserva1.procesar(impuesto=19)
    print(f"9. Reserva R001 procesada. Total con impuesto: ${costo:,.0f}")

    # Operación 10: crear y confirmar alquiler de equipo con descuento.
    reserva2 = sistema.crear_reserva("R002", cliente2, equipo, 3)
    reserva2.confirmar()
    costo = reserva2.procesar(descuento=10)
    print(f"10. Reserva R002 procesada con descuento. Total: ${costo:,.0f}")

    # Operación 11: crear una reserva con duración incorrecta.
    try:
        sistema.crear_reserva("R003", cliente1, asesoria, 0)
    except DatosInvalidosError as error:
        print("11. Reserva con duración inválida controlada:", error)
        logging.warning("Intento de reserva inválida: %s", error)

    # Operación 12: intentar procesar una reserva sin confirmarla.
    reserva3 = sistema.crear_reserva("R004", cliente1, asesoria, 1)
    try:
        reserva3.procesar()
    except ReservaError as error:
        print("12. Procesamiento sin confirmar controlado:", error)
        print("    Excepción original encadenada:", repr(error.__cause__))

    # Operación 13: servicio no disponible.
    servicio_no_disponible = ReservaSala(
        "S005", "Sala ocupada", 60000, disponible=False
    )
    try:
        sistema.crear_reserva("R005", cliente2, servicio_no_disponible, 1)
    except ServicioNoDisponibleError as error:
        print("13. Servicio no disponible controlado:", error)
        logging.warning("Intento de reservar servicio no disponible: %s", error)

    # Operación 14: cancelar una reserva.
    reserva2.cancelar()
    print("14. Reserva R002 cancelada correctamente.")

    # Operación 15: intentar confirmar una reserva cancelada.
    try:
        reserva2.confirmar()
    except ReservaError as error:
        print("15. Operación no permitida controlada:", error)
        logging.warning("Operación no permitida: %s", error)

    # Operación 16: demostrar try/except/else/finally.
    print("\n16. Validación usando try/except/else/finally:")
    try:
        valor = float("25000")
    except ValueError as error:
        print("No se pudo convertir el valor:", error)
    else:
        print("Conversión realizada correctamente:", valor)
    finally:
        print("La validación terminó y el programa continúa.")

    # Listado final.
    sistema.listar_datos()
    print("\nLa demostración finalizó sin detener el programa.")
    print("Los eventos y errores quedaron registrados en software_fj.log.")

if __name__ == "__main__":
    ejecutar_demostracion()
