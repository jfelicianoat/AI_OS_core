# PC IA: lo que hay que hacer para que nadie pegue tokens (AI OS Core 0.4.0)

Desde el 19-oct-2026 el token del AI Broker lo reparte AI OS Core a todas las apps del PC
principal. Lo recibe del runner de Agora, que vive en el PC IA junto al Broker y lo lee del
llavero de Windows. En el código del Broker **no hay que cambiar nada**. En el PC IA hay que
hacer esto:

## 1. Broker: comprobar que publica su token en el llavero (sin cambios de código)

En la configuración del Broker tiene que estar:

```yaml
server:
  publish_session_token: keyring
```

Al arrancar, el Broker deja su token de sesión en el llavero de Windows del usuario con el que
corre: servicio `ai-broker`, cuenta `session_admin_token` (Client_API.md, 3.1). El runner de
Agora ya lo lee de ahí desde la 0.2.x. **El runner tiene que correr con el mismo usuario de
Windows que el Broker**, o no verá esa entrada.

Comprobación (en el PC IA, con el Python del runner):

```
C:\Agora\venv\Scripts\python.exe -c "import keyring; print(bool(keyring.get_password('ai-broker','session_admin_token')))"
```

Tiene que imprimir `True` con el Broker arrancado.

## 2. Runner: actualizar a 0.2.15 y conectarlo a Core por HTTPS (un fichero, doble clic)

1. En el PC principal, el usuario ejecuta `AI_OS_core\Abrir Core a la red.bat` (pide permiso de
   administrador). Abre el puerto 8443 (HTTPS) solo a la red local y genera
   `AI_OS_core\dist\Conectar runner a Core.bat`, que ya incluye el runner 0.2.15, la URL
   `https://<IP del PC principal>:8443` y el token del runner ante Core.
2. Ese fichero se copia al PC IA y se le hace doble clic. Para la tarea del runner, instala la
   0.2.15, la vuelve a registrar con `--core-url https://…:8443` y `AGORA_CORE_TOKEN`, la
   arranca y hace `--check`.
3. **Borrar el fichero después**: lleva el token del runner.

Qué hace el runner 0.2.15 de nuevo:
- En cada vuelta lee el token del llavero. Si ha cambiado (el Broker se reinició), o si ha
  pasado un minuto (Core pudo reiniciarse y lo guarda solo en memoria), lo envía a Core:
  `PUT /api/v1/credentials/broker`.
- Comprueba el certificado HTTPS de Core con la CA de Agora que ya usa para el tablero
  (`--ca-cert`). No hace falta copiar ningún certificado nuevo.
- Si Core no contesta, no se detiene: lo vuelve a intentar en la vuelta siguiente.

En el log del runner tiene que aparecer `AI OS Core: token del broker publicado` al arrancar
y cada vez que el Broker se reinicie.

## 3. HTTPS también en el Broker (puerto 8765)

El tráfico apps → Broker lleva la cabecera `X-Admin-Token`; en HTTP va en claro por la red
local. Las apps del PC principal ya saben hablar HTTPS con el Broker (20-oct-2026): confían
**solo para el Broker** en la «AI Broker CA» (`C:\Agora\pki-broker\ca.crt`, o la ruta de
`AI_BROKER_CA_CERT`), sin `SSL_CERT_FILE` global.

La AI Broker CA es una CA aparte, creada el 20-oct-2026 porque se perdió la frase de la CA de
Agora. Ella y el certificado del Broker caducan en 2126. Su clave (`ca.key`) solo está en el PC
principal, cifrada con una frase aleatoria que guarda el Administrador de credenciales de Windows
(servicio `agora-broker-ca`, usuario `passphrase`): no hay que recordarla. La CA de Agora sigue
firmando el tablero y Core.

1. **Ficheros para el PC IA (ya emitidos):** `C:\Agora\deploy\broker-https\` contiene
   `server.crt`, `server.key` y `ca.crt`, válidos para `192.168.1.52`, `127.0.0.1` y
   `localhost`. Para volver a emitirlos: `Agora\Emitir certificado del Broker.bat`.
2. **PC IA: servir HTTPS.** Copiar `server.crt` y `server.key` (nunca `ca.key`) y pasarlos a
   uvicorn como `ssl_certfile` / `ssl_keyfile`, en el mismo puerto 8765. Comprobar desde el PC
   IA: `curl --cacert ca.crt https://127.0.0.1:8765/health`.
3. **PC IA: runner de Agora 0.2.16.** Copiar `Agora\dist\Actualizar runner Agora 0.2.16.bat`
   y ejecutarlo como `"Actualizar runner Agora 0.2.16.bat" -BrokerHttps`. El paquete trae
   `broker-ca.crt`, lo instala junto al runner y lo pasa como `--broker-ca-cert`; el runner
   pasa entonces a `https://127.0.0.1:8765`. Las actualizaciones siguientes lo conservan.
4. **PC principal: cambiar las URLs.** Doble clic en `AI_OS_core\Pasar apps a Broker
   HTTPS.bat`. Antes de tocar nada comprueba que el Broker contesta por HTTPS con un
   certificado de la AI Broker CA; si no, no cambia nada. Cambia la URL en Athena, Gestión
   Tareas IA, Knowledge Orchestrator, Trading AI (cada workspace), Model_Drift, ChatyGPT y el
   monitor de Core, y deja una copia `.antes-https.bak` de cada fichero. Para deshacerlo:
   `"Pasar apps a Broker HTTPS.bat" -Revertir`. Local AI Lab guarda la URL en su
   propia ventana: se cambia allí una vez a `https://192.168.1.52:8765`.

**Pendiente aparte:** el certificado HTTPS del tablero y de Core (`C:\Agora\pki\server.crt`, CA
de Agora) caduca el 7-oct-2027 y no se puede renovar sin la frase perdida. Antes de esa
fecha habrá que pasarlos también a una CA nueva.
