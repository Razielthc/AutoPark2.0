import logging
from datetime import datetime

from decouple import AutoConfig

from procedimientos.crea_entrada_auto import nueva_entrada_auto
from procedimientos.crea_apertura import nueva_apertura
from utils.get_resorce_path import resource_path
from NetSDK.NetSDK import NetClient
from NetSDK.SDK_Struct import *
from NetSDK.SDK_Enum import *
from NetSDK.SDK_Callback import fDisConnect, fHaveReConnect, CB_FUNCTYPE

# Obtener un logger para este módulo
logger = logging.getLogger(__name__)

config = AutoConfig(resource_path('.env'))


class Device:
    def __init__(self, muestra_mensaje=None, agrega_notificacion=None):
        self.muestra_mensaje = muestra_mensaje
        self.agrega_notificacion = agrega_notificacion
        # SDK initialization
        self._loginID = None
        self.online = False
        self.m_DisConnectCallBack = fDisConnect(self._disconnected_callback)
        self.m_ReConnectCallBack = fHaveReConnect(self._reconnected_callback)
        self.sdk = NetClient()
        self.sdk.InitEx(self.m_DisConnectCallBack)
        self.sdk.SetAutoReconnect(self.m_ReConnectCallBack)

        # Registrar callback con función envoltura
        self._callback_func = CB_FUNCTYPE(None, c_long, C_LLONG, POINTER(c_char), C_DWORD, POINTER(c_char),
                                          c_long, c_int, c_long, C_LDWORD)(self._wrapped_message_callback)
        self.sdk.SetDVRMessCallBackEx1(self._callback_func, 0)

        # Default configurations
        self.ip = config('CONTROLADOR_IP')
        self.port = int(config('CONTROLADOR_PORT'))
        self.username = config('CONTROLADOR_USER')
        self.password = config('CONTROLADOR_PASS')

    # Login, logout, attach, and detach methods
    def login(self):
        if self.online is True:
            return True

        stuInParam = NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY()
        stuInParam.dwSize = sizeof(NET_IN_LOGIN_WITH_HIGHLEVEL_SECURITY)
        stuInParam.szIP = self.ip.encode()
        stuInParam.nPort = self.port
        stuInParam.szUserName = self.username.encode()
        stuInParam.szPassword = self.password.encode()
        stuInParam.emSpecCap = EM_LOGIN_SPAC_CAP_TYPE.TCP
        stuInParam.pCapParam = None

        stuOutParam = NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY()
        stuOutParam.dwSize = sizeof(NET_OUT_LOGIN_WITH_HIGHLEVEL_SECURITY)

        self._loginID, device_info, error_msg = self.sdk.LoginWithHighLevelSecurity(stuInParam, stuOutParam)
        if self._loginID != 0:
            logger.debug('Sesion iniciada en Device correctamente')
            self.online = True
            return True
        else:
            logger.warning('Error al iniciar sesion', error_msg)
            self.online = False
            return error_msg

    def logout(self):
        if self.online is True:
            self.sdk.StopListen(self._loginID)
            self.sdk.Logout(self._loginID)
            self._loginID = 0
            self.online = False
            self.sdk.Cleanup()
            logger.debug('Sesion finalizada correctamente')
        else:
            self.sdk.Cleanup()

    def attach_alarm(self):
        result = self.sdk.StartListenEx(self._loginID)
        if result:
            logger.debug(f"suscripcion a los eventos exitosa, {result}")
            return True
        else:
            logger.debug(f"Error en la suscripcion a los eventos, {result}")
            return False

    def abrir_pluma(self, canal: int, metodo_entrada: str):

        stuInParam = NET_CTRL_ACCESS_OPEN()
        stuInParam.dwSize = sizeof(NET_CTRL_ACCESS_OPEN)
        stuInParam.nChannelID = canal  # channel
        # stuInParam.emOpenDoorType = EM_OPEN_DOOR_TYPE.EM_OPEN_DOOR_TYPE_UNKNOWN
        # stuInParam.emOpenDoorType = EM_OPEN_DOOR_TYPE.EM_OPEN_DOOR_TYPE_REMOTE
        # stuInParam.emOpenDoorDirection = EM_OPEN_DOOR_DIRECTION.EM_OPEN_DOOR_DIRECTION_FROM_LEAVE
        # stuInParam.emOpenDoorDirection = EM_OPEN_DOOR_DIRECTION.EM_OPEN_DOOR_DIRECTION_FROM_ENTER

        result = self.sdk.ControlDeviceEx(self._loginID, CtrlType.ACCESS_OPEN, stuInParam, c_char(), 3000)

        if result:
            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            apertura = {
                "time_str": fecha,
                "door_channel": str(canal),
                "metodo_entrada": metodo_entrada,
                "card_number": "",
                "card_status": "",
                "error_code": "",
            }
            nueva_apertura(apertura)
            logger.debug(f"Puerta abierta")
            stuInParam = NET_CTRL_ACCESS_CLOSE()
            stuInParam.dwSize = sizeof(NET_CTRL_ACCESS_CLOSE)
            stuInParam.nChannelID = canal
            result = self.sdk.ControlDeviceEx(self._loginID, CtrlType.ACCESS_CLOSE, stuInParam, c_char(), 5000)

            if result:
                logger.debug(f"Puerta cerrada")
            else:

                logger.warning(f"Error al cerrar la puerta.  {self.sdk.GetLastErrorMessage()}")
                raise SystemError(self.sdk.GetLastErrorMessage())
        else:

            logger.warning(f"Error al abrir la puerta.  {self.sdk.GetLastErrorMessage()}")
            raise SystemError(self.sdk.GetLastErrorMessage())

        return True

    def estado_pluma(self, pluma) -> int | None:
        if not self.online:
            return None
        else:
            stuParam = NET_DOOR_STATUS_INFO()
            stuParam.dwSize = sizeof(stuParam)
            stuParam.nChannel = pluma

            nRetLen = 0
            resultado = self.sdk.QueryDevState(self._loginID, EM_QUERY_DEV_STATE_TYPE.DOOR_STATE_INFO, stuParam,
                                               sizeof(NET_DOOR_STATUS_INFO),
                                               nRetLen, 3000)
            if resultado != 0:
                return stuParam.emDoorState
            else:
                return None

    def addClient(self, clientId: str, valid_begin_time: NET_TIME, valid_end_time: NET_TIME) -> bool:
        if self._loginID == 0:
            raise ValueError("No se ha iniciado sesión en el dispositivo.")

        print("Cliente id Add", clientId)

        logger.debug(f"Inicio del método de inserción de cliente")

        # Buffer para un código de error
        stuFailCode = (C_ENUM * 1)()
        stuFailCode[0] = EM_A_NET_EM_FAILCODE.NET_EM_FAILCODE_NOERROR

        # Crear estructura para el usuario
        stuUserInfoAdd = NET_ACCESS_USER_INFO()

        # Asignar valores necesarios
        stuUserInfoAdd.szUserID = clientId.encode('utf-8')
        stuUserInfoAdd.emAuthority = EM_A_NET_ATTENDANCE_AUTHORITY.NET_ATTENDANCE_AUTHORITY_CUSTOMER
        stuUserInfoAdd.nTimeSectionNum = 1
        stuUserInfoAdd.nTimeSectionNo[0] = 255
        stuUserInfoAdd.nSpecialDaysScheduleNum = 1
        stuUserInfoAdd.nSpecialDaysSchedule[0] = 255
        stuUserInfoAdd.emUserType = EM_A_NET_ENUM_USER_TYPE.NET_ENUM_USER_TYPE_NORMAL
        stuUserInfoAdd.stuValidBeginTime = valid_begin_time
        stuUserInfoAdd.stuValidEndTime = valid_end_time
        stuUserInfoAdd.nUserTime = 0
        stuUserInfoAdd.nDoorNum = 2
        stuUserInfoAdd.nDoors[0] = 0
        stuUserInfoAdd.nDoors[1] = 1

        # Estructuras de entrada y salida
        stuUserInsertIn = NET_IN_ACCESS_USER_SERVICE_INSERT()
        stuUserInsertIn.dwSize = sizeof(NET_IN_ACCESS_USER_SERVICE_INSERT)
        stuUserInsertIn.nInfoNum = 1
        stuUserInsertIn.pUserInfo = pointer(stuUserInfoAdd)

        stuUserInsertOut = NET_OUT_ACCESS_USER_SERVICE_INSERT()
        stuUserInsertOut.dwSize = sizeof(NET_OUT_ACCESS_USER_SERVICE_INSERT)
        stuUserInsertOut.nMaxRetNum = 1
        stuUserInsertOut.pFailCode = cast(stuFailCode, POINTER(C_ENUM))

        # Llamada al SDK
        resultado = self.sdk.OperateAccessUserService(
            self._loginID,
            EM_A_NET_EM_ACCESS_CTL_USER_SERVICE.NET_EM_ACCESS_CTL_USER_SERVICE_INSERT,
            stuUserInsertIn,
            stuUserInsertOut,
            5000
        )

        if resultado:
            logger.debug("Cliente agregado correctamente al dispositivo.")
            return True
        else:
            # Obtener el código de error
            error_code = stuFailCode[0]
            error_message = self.sdk.GetLastErrorMessage()
            logger.error(f"Error al guardar cliente en el dispositivo: Código {error_code}, Mensaje: {error_message}")

            # Elevar excepción detallada
            raise RuntimeError(
                f"Error al insertar cliente en el dispositivo. Código: {error_code}. Detalles: {error_message}")

    def user_modify(self, user_id: str, valid_begin_time: NET_TIME, valid_end_time: NET_TIME,
                    timeout: int = 5000) -> bool:
        """
        Modifica la información de un usuario en el sistema de control de acceso, incluyendo las fechas de validez.

        :param user_id: ID del usuario a modificar.
        :param valid_begin_time: Fecha de inicio de validez como un objeto NET_TIME.
        :param valid_end_time: Fecha de fin de validez como un objeto NET_TIME.
        :param timeout: Tiempo de espera para la operación en milisegundos.
        :return: True si la operación fue exitosa, False en caso contrario.
        """
        logger.debug(f"Iniciando modificación para el usuario: {user_id}")

        if self._loginID == 0:
            raise ValueError("No se ha iniciado sesión en el dispositivo.")

        # Obtener la estructura del usuario
        user_info = self.busca_cliente(clientId=user_id)
        print(type(user_info))  # Confirmación del tipo

        if not user_info:
            logger.error(f"No se pudo obtener información para el usuario: {user_id}")
            return False

        logger.debug(f"Usuario encontrado: {user_info.szUserID.decode('utf-8')}. Preparando modificación.")

        # No es necesario desreferenciar 'user_info', ya que no es un puntero

        # Buffer para un código de error
        stuFailCode = (C_ENUM * 1)()
        stuFailCode[0] = EM_A_NET_EM_FAILCODE.NET_EM_FAILCODE_NOERROR

        # Asignar valores a las fechas de inicio y fin
        user_info.stuValidBeginTime = valid_begin_time
        user_info.stuValidEndTime = valid_end_time

        # Configurar estructuras de entrada y salida
        stuUserModifyIn = NET_IN_ACCESS_USER_SERVICE_INSERT()
        stuUserModifyIn.dwSize = sizeof(NET_IN_ACCESS_USER_SERVICE_INSERT)
        stuUserModifyIn.nInfoNum = 1
        stuUserModifyIn.pUserInfo = pointer(user_info)  # Ajuste aquí

        stuUserModifyOut = NET_OUT_ACCESS_USER_SERVICE_INSERT()
        stuUserModifyOut.dwSize = sizeof(NET_OUT_ACCESS_USER_SERVICE_INSERT)
        stuUserModifyOut.nMaxRetNum = 1
        stuUserModifyOut.pFailCode = cast(stuFailCode, POINTER(C_ENUM))

        # Llamada al SDK
        resultado = self.sdk.OperateAccessUserService(
            self._loginID,
            EM_A_NET_EM_ACCESS_CTL_USER_SERVICE.NET_EM_ACCESS_CTL_USER_SERVICE_INSERT,
            stuUserModifyIn,
            stuUserModifyOut,
            timeout
        )

        if resultado:
            logger.debug(f"Usuario {user_id} modificado correctamente.")
            return True
        else:
            # Obtener el código de error
            error_code = stuFailCode[0]
            error_message = self.sdk.GetLastErrorMessage()
            logger.error(f"Error al modificar usuario en el dispositivo: Código {error_code}, Mensaje: {error_message}")
            raise RuntimeError(
                f"Error al modificar usuario en el dispositivo. Código: {error_code}. Detalles: {error_message}"
            )

    def busca_cliente(self, clientId: str) -> str | None | POINTER(NET_ACCESS_USER_INFO):

        if self._loginID == 0:
            raise ValueError("No se ha iniciado sesión en el dispositivo.")

        logger.debug(f"Inicio del método de inserción de cliente")

        # Buffer para un código de error
        stuFailCode = (C_ENUM * 1)()
        stuFailCode[0] = EM_A_NET_EM_FAILCODE.NET_EM_FAILCODE_NOERROR

        # Crear estructura para el usuario
        stuUserInfo = NET_ACCESS_USER_INFO()

        # Estructuras de entrada
        stuUserGetIn = NET_IN_ACCESS_USER_SERVICE_GET()
        stuUserGetIn.dwSize = sizeof(NET_IN_ACCESS_USER_SERVICE_INSERT)
        stuUserGetIn.nUserNum = 1
        stuUserGetIn.szUserID = clientId.encode('utf-8')
        stuUserGetIn.bUserIDEx = False

        # Configurar parámetros de salida
        user_info_array = (NET_ACCESS_USER_INFO * 1)()
        output_param = NET_OUT_ACCESS_USER_SERVICE_GET()
        output_param.dwSize = sizeof(NET_OUT_ACCESS_USER_SERVICE_GET)
        output_param.nMaxRetNum = 1
        output_param.pUserInfo = cast(user_info_array, POINTER(NET_ACCESS_USER_INFO))
        output_param.pFailCode = cast(stuFailCode, POINTER(C_ENUM))

        # Llamada al SDK
        resultado = self.sdk.OperateAccessUserService(
            self._loginID,
            EM_A_NET_EM_ACCESS_CTL_USER_SERVICE.NET_EM_ACCESS_CTL_USER_SERVICE_GET,
            stuUserGetIn,
            output_param,
            5000
        )

        if not resultado:
            # Obtener el código de error
            error_code = stuFailCode[0]
            error_message = self.sdk.GetLastErrorMessage()
            logger.error(f"Error al buscar el cliente {error_code}, Mensaje: {error_message}")

            # Elevar excepción detallada
            raise RuntimeError(
                f"Error al buscar el cliente {error_code}, Mensaje: {error_message}")

        if output_param.nMaxRetNum == 0:
            print("El usuario no se encontró en el sistema")
            return None

            # Procesar el resultado del único usuario
        # user_info = output_param.pUserInfo[0]
        return output_param.pUserInfo[0]

    def card_insert(self, tarjeta_hex: str, cliente_id: str, tiempo_espera: int = 5000) -> bool:
        """
        Vincula una tarjeta al sistema de control de acceso utilizando la operación NET_EM_ACCESS_CTL_CARD_SERVICE_INSERT.

        :param tarjeta_hex: ID único de la tarjeta a vincular.
        :param cliente_id: Nombre del usuario asociado a la tarjeta.
        :param tiempo_espera: Tiempo máximo de espera para la operación en milisegundos.
        :return: True si la operación fue exitosa, False en caso contrario.
        """

        if not self.online:
            raise ValueError("No se ha iniciado sesión en el dispositivo.")

        try:

            # Crear y rellenar la información de la tarjeta
            card_info = NET_ACCESS_CARD_INFO()
            card_info.szCardNo = tarjeta_hex.encode('utf-8')
            card_info.szUserID = cliente_id.encode('utf-8')
            card_info.emType = EM_A_NET_ACCESSCTLCARD_TYPE.NET_ACCESSCTLCARD_TYPE_GENERAL

            # Estructura de entrada
            in_param = NET_IN_ACCESS_CARD_SERVICE_INSERT()
            in_param.dwSize = sizeof(NET_IN_ACCESS_CARD_SERVICE_INSERT)
            in_param.nInfoNum = 1  # Solo un registro en este caso
            in_param.pCardInfo = pointer(card_info)

            # Buffer para un código de error
            stuFailCode = (C_ENUM * 1)()
            stuFailCode[0] = EM_A_NET_EM_FAILCODE.NET_EM_FAILCODE_NOERROR

            # Estructura de salida
            out_param = NET_OUT_ACCESS_CARD_SERVICE_INSERT()
            out_param.dwSize = sizeof(NET_OUT_ACCESS_CARD_SERVICE_INSERT)
            out_param.nMaxRetNum = 1
            out_param.pFailCode = cast(stuFailCode, POINTER(C_ENUM))

            # Llamar a la función del SDK
            resultado = self.sdk.OperateAccessCardService(
                self._loginID,
                EM_A_NET_EM_ACCESS_CTL_CARD_SERVICE.NET_EM_ACCESS_CTL_CARD_SERVICE_INSERT,
                in_param,
                out_param,
                tiempo_espera
            )

            # Evaluar resultado
            if resultado:
                return True

            else:
                # Obtener el código de error
                error_code = stuFailCode[0]
                error_message = self.sdk.GetLastErrorMessage()
                logger.error(f"Error al Insertar la tarjeta en el dispositivo {error_code}, Mensaje: {error_message}")

                # Elevar excepción detallada
                raise RuntimeError(
                    f"Error al Insertar la tarjeta en el dispositivo {error_code}, Mensaje: {error_message}")

        except Exception as e:
            raise e

    def card_remove(self, tarjeta_hex: str, tiempo_espera: int = 5000) -> bool:
        """
        Vincula una tarjeta al sistema de control de acceso utilizando la operación NET_EM_ACCESS_CTL_CARD_SERVICE_INSERT.

        :param tarjeta_hex: ID único de la tarjeta a vincular.
        :param tiempo_espera: Tiempo máximo de espera para la operación en milisegundos.
        :return: True si la operación fue exitosa, False en caso contrario.
        """

        if not self.online:
            raise ValueError("No se ha iniciado sesión en el dispositivo.")

        try:

            # Estructura de entrada
            in_param = NET_IN_ACCESS_CARD_SERVICE_REMOVE()
            in_param.dwSize = sizeof(NET_IN_ACCESS_CARD_SERVICE_REMOVE)
            in_param.nCardNum = 1  # Solo un registro en este caso
            in_param.szCardNo = tarjeta_hex.encode('utf-8')

            # Buffer para un código de error
            stuFailCode = (C_ENUM * 1)()
            stuFailCode[0] = EM_A_NET_EM_FAILCODE.NET_EM_FAILCODE_NOERROR

            # Estructura de salida
            out_param = NET_OUT_ACCESS_CARD_SERVICE_REMOVE()
            out_param.dwSize = sizeof(NET_OUT_ACCESS_CARD_SERVICE_REMOVE)
            out_param.nMaxRetNum = 1
            out_param.pFailCode = cast(stuFailCode, POINTER(C_ENUM))

            # Llamar a la función del SDK
            resultado = self.sdk.OperateAccessCardService(
                self._loginID,
                EM_A_NET_EM_ACCESS_CTL_CARD_SERVICE.NET_EM_ACCESS_CTL_CARD_SERVICE_REMOVE,
                in_param,
                out_param,
                tiempo_espera
            )

            # Evaluar resultado
            if resultado:
                print("Tarjeta Eliminada", resultado)
                return True

            else:
                # Obtener el código de error
                error_code = stuFailCode[0]
                error_message = self.sdk.GetLastErrorMessage()
                logger.error(f"Error al borrar la tarjeta {error_code}, Mensaje: {error_message}")

                # Elevar excepción detallada
                raise RuntimeError(
                    f"Error al borrar la tarjeta {error_code}, Mensaje: {error_message}")

        except Exception as e:
            raise e

    def card_clear(self, tiempo_espera: int = 5000) -> bool:
        if not self.online:
            return False

        try:
            in_param = NET_IN_ACCESS_CARD_SERVICE_CLEAR()
            in_param.dwSize = sizeof(NET_IN_ACCESS_CARD_SERVICE_CLEAR)

            out_param = NET_OUT_ACCESS_CARD_SERVICE_CLEAR()
            out_param.dwSize = sizeof(NET_OUT_ACCESS_CARD_SERVICE_CLEAR)

            # Llamar a la función del SDK
            resultado = self.sdk.OperateAccessCardService(
                self._loginID,
                EM_A_NET_EM_ACCESS_CTL_CARD_SERVICE.NET_EM_ACCESS_CTL_CARD_SERVICE_CLEAR,
                in_param,
                out_param,
                tiempo_espera
            )

            # Evaluar resultado
            if resultado:
                return True
            else:
                raise SystemError("Error al borrar las tarjetas.")
        except Exception as e:
            raise e

    # Alarm processing logic

    def _process_alarm_info(self, alarm_info, alarm_type):
        # Convertir la hora (NET_TIME) a un string legible
        card_status = None
        doorStatus = None
        time_str = f"{alarm_info.stuTime.dwYear}-{alarm_info.stuTime.dwMonth:02}-{alarm_info.stuTime.dwDay:02} " \
                   f"{alarm_info.stuTime.dwHour:02}:{alarm_info.stuTime.dwMinute:02}:{alarm_info.stuTime.dwSecond:02}"

        # Número de puerta
        door_channel = str(getattr(alarm_info, "nDoor", "Desconocido"))

        # Nombre de la puerta (opcional)
        door_name = getattr(alarm_info, "szDoorName", b'').decode('utf-8').strip()

        # Tipo de evento
        event_type_map = {
            0: "Desconocido",
            1: "Entrada",
            2: "Salida",
        }
        entrada_type = event_type_map.get(getattr(alarm_info, "emEventType", -1), "Desconocido")

        # Estado del evento
        accion_status = "exito" if getattr(alarm_info, "bStatus", 0) else "fallo"

        # Metodo de entrada
        open_method_map = {
            0: "desconocido",
            2: "tarjeta",
            5: "plataforma",
            6: "boton",
        }
        metodo_entrada = open_method_map.get(getattr(alarm_info, "emOpenMethod", -1), "Desconocido")

        # Número de tarjeta
        card_number = getattr(alarm_info, "szCardNo", b'').decode('utf-8').strip()

        # Estado de `emStatus` (diferenciar según el tipo de alarma)
        if alarm_type == SDK_ALARM_TYPE.ALARM_ACCESS_CTL_EVENT:
            # Mapeo para `EM_A_NET_ACCESSCTLCARD_STATE`
            card_status_map = {
                -1: "Desconocido",
                0: "Normal",
                1: "Perdida",
                2: "Desconectada",
                4: "Congelada",
                8: "Atrasos",
                16: "Atrasado",
                32: "Pre-Atrasos (todavía se puede abrir la puerta)",
            }
            card_status = card_status_map.get(getattr(alarm_info, "emStatus", -1), "Desconocido")
        elif alarm_type == SDK_ALARM_TYPE.ALARM_ACCESS_CTL_STATUS:
            # Mapeo para `EM_A_NET_ACCESS_CTL_STATUS_TYPE`

            status_type_map = {
                0: "Desconocido",  # NET_ACCESS_CTL_STATUS_TYPE_UNKNOWN
                1: "Puerta abierta",  # NET_ACCESS_CTL_STATUS_TYPE_OPEN
                2: "Puerta cerrada",  # NET_ACCESS_CTL_STATUS_TYPE_CLOSE
                3: "Anomalía",  # NET_ACCESS_CTL_STATUS_TYPE_ABNORMAL
                4: "Bloqueo falso",  # NET_ACCESS_CTL_STATUS_TYPE_FAKELOCKED
                5: "Siempre cerrada",  # NET_ACCESS_CTL_STATUS_TYPE_CLOSEALWAYS
                6: "Siempre abierta",  # NET_ACCESS_CTL_STATUS_TYPE_OPENALWAYS
                7: "Normal",  # NET_ACCESS_CTL_STATUS_TYPE_NORMAL
            }

            doorStatus = status_type_map.get(getattr(alarm_info, "emStatus", -1), "Desconocido")

        # Código de error
        error_code_map = {
            0x00: "Sin error",
            0x10: "No autorizado",
            0x11: "Tarjeta perdida o cancelada",
            0x12: "Sin permiso para la puerta",
            0x13: "Error en el modo de desbloqueo",
            0x14: "Error en el período de validez",
            0x15: "Modo anti-reingreso activado",
            0x16: "Alarma de forzado, no desbloqueado",
            0x17: "Estado de puerta NC (Normalmente Cerrada)",
            0x18: "Estado de cerradura AB",
            0x19: "Tarjeta de patrullaje",
            0x1A: "Dispositivo en estado de alarma de intrusión",
            0x20: "Error de período",
            0x21: "Error de desbloqueo en período de vacaciones",
            0x23: "La tarjeta está vencida",
            0x30: "Verificación requerida para el derecho de primera tarjeta",
            0x40: "Tarjeta correcta, error al ingresar la contraseña",
            0x41: "Tarjeta correcta, tiempo de ingreso de contraseña agotado",
            0x42: "Tarjeta correcta, ingreso incorrecto",
            0x43: "Tarjeta correcta, tiempo de ingreso agotado",
            0x44: "Correcto, error en ingreso de contraseña",
            0x45: "Correcto, tiempo de ingreso de contraseña agotado",
            0x50: "Error en la secuencia de desbloqueo grupal",
            0x51: "Prueba requerida para desbloqueo grupal",
            0x60: "Prueba pasada, control no autorizado",
            0x61: "Tarjeta correcta, error facial",
            0x62: "Tarjeta correcta, tiempo de reconocimiento facial agotado",
            0x63: "Reingreso repetido",
            0x64: "No autorizado, requiere identificación por plataforma",
            0x65: "Alta temperatura corporal",
            0x66: "Sin mascarilla",
            0x67: "Fallo al obtener código de salud",
            0x68: "Sin entrada debido a código amarillo",
            0x69: "Sin entrada debido a código rojo",
            0x6A: "Código de salud inválido",
            0x6B: "Entrada permitida con código verde",
            0x6E: "Código verde, pero código de viaje no verde",
            0x6F: "Código verde, obteniendo información del código de salud",
            0x71: "Verificación de identificación ciudadana (plataforma emite el resultado)",
            0xA8: "No lleva casco de seguridad (personalizado)",
            0xB1: "Información de autorización insuficiente, requiere ser complementada"
        }
        error_code = error_code_map.get(getattr(alarm_info, "nErrorCode", -1), "Código de error desconocido")

        # Número de registro del evento (opcional)
        punching_rec_no = getattr(alarm_info, "nPunchingRecNo", "No disponible")

        return {
            "time_str": time_str,
            "door_channel": door_channel,
            "door_name": door_name,
            "entrada_type": entrada_type,
            "accion_status": accion_status,
            "metodo_entrada": metodo_entrada,
            "card_number": card_number,
            "card_status": card_status,
            "door_status": doorStatus,
            "error_code": error_code,
            "punching_rec_no": punching_rec_no,
        }

    # Callback functions

    def _disconnected_callback(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        self.agrega_notificacion(texto="Error, Control de barrera fuera de linea")

    def _reconnected_callback(self, lLoginID, pchDVRIP, nDVRPort, dwUser):
        self.agrega_notificacion(texto="Control de barrera en linea")

    def _wrapped_message_callback(self, lCommand, lLoginID, pBuf, dwBufLen, pchDVRIP, nDVRPort, bAlarmAckFlag,
                                  nEventID, dwUser):
        """
        Función envoltura que pasa el control a la función de instancia.
        """
        self._message_callback(lCommand, lLoginID, pBuf, dwBufLen, pchDVRIP, nDVRPort, bAlarmAckFlag, nEventID, dwUser)

    # def imprimir_estructura(self, estructura):
    #     """
    #     Recorre y muestra los campos de una estructura ctypes.
    #     """
    #     print("********************** Inicia Estructura ********************************************* \n")
    #     for campo_nombre, campo_tipo in estructura._fields_:
    #         valor = getattr(estructura, campo_nombre)
    #         print(f"{campo_nombre}: {valor}")
    #
    #     print("*********************** Fin de la estructura ******************************************** \n")

    def _message_callback(self, lCommand, lLoginID, pBuf, dwBufLen, pchDVRIP, nDVRPort, bAlarmAckFlag, nEventID,
                          dwUser):
        """
        Callback principal que maneja los eventos.
        """
        if not self.online:
            print("Dispositivo fuera de línea, callback")
            return

        if lCommand == SDK_ALARM_TYPE.ALARM_ACCESS_CTL_EVENT:
            alarm_info = cast(pBuf, POINTER(NET_A_ALARM_ACCESS_CTL_EVENT_INFO)).contents
            alarm_data = self._process_alarm_info(alarm_info, SDK_ALARM_TYPE.ALARM_ACCESS_CTL_EVENT)

            if alarm_data['metodo_entrada'] == 'boton' and alarm_data['accion_status'] == 'exito':

                try:
                    nueva_apertura(alarm_data)
                    nueva_entrada_auto()
                except Exception as e:
                    self.muestra_mensaje(title="Error",
                                         mensaje=f"Error en el dispensador {e}",
                                         tipo="error")

            if alarm_data['metodo_entrada'] == 'tarjeta' and alarm_data['accion_status'] == 'exito':
                nueva_apertura(alarm_data)

            if alarm_data['accion_status'] == 'fallo' and alarm_data['error_code'] == "Modo anti-reingreso activado":
                self.muestra_mensaje(title="Intento de Reingreso Detectado",
                                     mensaje="El acceso del cliente ha sido denegado debido a un intento de reingreso sin salida previa. Verifique el estado de salida antes de permitir un nuevo ingreso.",
                                     tipo="error")

    def test_device(self):
        if self.online:
            return True
        else:
            return False


if __name__ == "__main__":
    pass
