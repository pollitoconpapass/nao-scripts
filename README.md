# Entorno NAOqi en macOS

Guía para instalar y usar el SDK de **NAOqi** (SoftBank Robotics) en macOS con Apple Silicon, utilizando Rosetta 2 y Python 2.7.

## Contenido

- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
  - [1. Instalar Rosetta 2](#1-instalar-rosetta-2)
  - [2. Instalar Python 2.7](#2-instalar-python-27)
  - [3. Instalar el SDK de SoftBank](#3-instalar-el-sdk-de-softbank)
  - [4. Crear el script de activación](#4-crear-el-script-de-activación)
  - [5. Crear el alias `naoqi-shell`](#5-crear-el-alias-naoqi-shell)
  - [6. Verificar la instalación](#6-verificar-la-instalación)
- [Uso diario](#uso-diario)

---

## Requisitos previos

| Requisito | Detalle                      |
| --------- | ---------------------------- |
| macOS     | Apple Silicon (M1/M2/M3)     |
| Rosetta 2 | Traducción x86_64 → ARM      |
| Python    | 2.7 (última versión: 2.7.18) |
| Terminal  | `zsh` (por defecto en macOS) |

> **Nota:** el SDK de NAOqi solo existe para x86_64 y Python 2.7, por eso es necesario Rosetta 2.

---

## Instalación

### 1. Instalar Rosetta 2

```sh
softwareupdate --install-rosetta --agree-to-license
```

### 2. Instalar Python 2.7

1. Descarga el `.pkg` desde la [página oficial de Python 2.7.18](https://www.python.org/downloads/release/python-2718/).
2. Abre el `.pkg` y acepta las opciones por defecto.
3. Verifica que quedó instalado:

```sh
/usr/local/bin/python2.7 --version
# Python 2.7.18
```

### 3. Instalar el SDK de SoftBank

Clona el repositorio con todas las dependencias necesarias:

```sh
git clone https://github.com/cristianrubioa/pynaoqi-installation-for-mac
```

Muévelo a una ubicación limpia y fija:

```sh
mv /ruta/donde/clonaste/pynaoqi-installation-for-mac ~/Documents/pynaoqi
```

Revisa la estructura del SDK:

```sh
ls ~/Documents/pynaoqi/pynaoqi
# bin  lib  share

ls ~/Documents/pynaoqi/pynaoqi/lib/python2.7/site-packages
# debe incluir: naoqi.py, almath.py, _qi.so, qi, ...
```

La raíz del SDK queda en: `~/Documents/pynaoqi/pynaoqi`

### 4. Crear el script de activación

```sh
nano ~/activate_naoqi.sh
```

Pega este contenido:

```bash
#!/bin/bash

PYNAOQI_PATH="$HOME/Documents/pynaoqi/pynaoqi"

export PYTHONPATH="${PYNAOQI_PATH}/lib/python2.7/site-packages:${PYTHONPATH}"
export DYLD_LIBRARY_PATH="${PYNAOQI_PATH}/lib:${DYLD_LIBRARY_PATH}"
export QI_SDK_PREFIX="${PYNAOQI_PATH}"

echo "✅ NAOqi environment activated."
echo "   PYTHONPATH        -> $PYTHONPATH"
echo "   DYLD_LIBRARY_PATH -> $DYLD_LIBRARY_PATH"
echo "   QI_SDK_PREFIX     -> $QI_SDK_PREFIX"
```

Guarda con `Ctrl + O` y sal con `Ctrl + X`. Luego dale permisos de ejecución:

```sh
chmod +x ~/activate_naoqi.sh
```

### 5. Crear el alias `naoqi-shell`

```sh
nano ~/.zshrc
```

Agrega al final del archivo:

```sh
alias naoqi-shell='arch -x86_64 /bin/bash --init-file ~/activate_naoqi.sh'
```

Recarga la configuración:

```sh
source ~/.zshrc
```

> A partir de aquí, escribir `naoqi-shell` abrirá un entorno con el SDK activado, listo para ejecutar scripts del robot.

### 6. Verificar la instalación

```sh
naoqi-shell
/usr/local/bin/python2.7 -c "import naoqi; print('NAOqi loaded successfully')"
```

Si ves `NAOqi loaded successfully`, todo quedó instalado correctamente.

---

## Uso diario

### Iniciar el entorno

```sh
naoqi-shell
```

### Ejecutar un script

```sh
/usr/local/bin/python2.7 facetrack.py
```

### Instalar una dependencia

```sh
/usr/local/bin/python2.7 -m pip install <library>
```

> **Importante:** todas las dependencias deben instalarse con este `python2.7`, no con el Python del sistema.
