import os
import sys
import requests


API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

GEOCODING_URL = "https://graphhopper.com/api/1/geocode"
ROUTE_URL = "https://graphhopper.com/api/1/route"


def obtener_coordenadas(ciudad, pais):
    """
    Obtiene las coordenadas de una ciudad utilizando
    el servicio de geocodificación de GraphHopper.
    """
    parametros = {
        "q": f"{ciudad}, {pais}",
        "locale": "es",
        "limit": 1,
        "key": API_KEY
    }

    try:
        respuesta = requests.get(
            GEOCODING_URL,
            params=parametros,
            timeout=20
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

    except requests.exceptions.RequestException as error:
        print(f"\nError al consultar la geocodificación: {error}")
        return None

    resultados = datos.get("hits", [])

    if not resultados:
        print(f"\nNo se encontró la ciudad: {ciudad}, {pais}")
        return None

    resultado = resultados[0]
    punto = resultado.get("point", {})

    latitud = punto.get("lat")
    longitud = punto.get("lng")
    nombre = resultado.get("name", ciudad)
    region = resultado.get("state", "")
    pais_encontrado = resultado.get("country", pais)

    if latitud is None or longitud is None:
        print("\nLa API no entregó coordenadas válidas.")
        return None

    nombre_completo = ", ".join(
        valor for valor in [nombre, region, pais_encontrado] if valor
    )

    return {
        "latitud": latitud,
        "longitud": longitud,
        "nombre": nombre_completo
    }


def seleccionar_transporte():
    """
    Solicita al usuario el medio de transporte.
    """
    opciones = {
        "1": ("Automóvil", "car"),
        "2": ("Bicicleta", "bike"),
        "3": ("Caminando", "foot")
    }

    while True:
        print("\nSeleccione el medio de transporte:")
        print("1. Automóvil")
        print("2. Bicicleta")
        print("3. Caminando")
        print("s. Salir")

        opcion = input("\nIngrese una opción: ").strip().lower()

        if opcion == "s":
            return None

        if opcion in opciones:
            return opciones[opcion]

        print("\nOpción no válida. Intente nuevamente.")


def convertir_duracion(milisegundos):
    """
    Convierte milisegundos en días, horas y minutos.
    """
    minutos_totales = int(milisegundos / 60000)

    dias = minutos_totales // 1440
    horas = (minutos_totales % 1440) // 60
    minutos = minutos_totales % 60

    partes = []

    if dias > 0:
        partes.append(f"{dias} día(s)")

    if horas > 0:
        partes.append(f"{horas} hora(s)")

    partes.append(f"{minutos} minuto(s)")

    return ", ".join(partes)


def obtener_ruta(origen, destino, perfil):
    """
    Consulta la ruta entre dos puntos mediante GraphHopper.
    """
    parametros = [
        ("point", f"{origen['latitud']},{origen['longitud']}"),
        ("point", f"{destino['latitud']},{destino['longitud']}"),
        ("profile", perfil),
        ("locale", "es"),
        ("instructions", "true"),
        ("calc_points", "true"),
        ("key", API_KEY)
    ]

    try:
        respuesta = requests.get(
            ROUTE_URL,
            params=parametros,
            timeout=30
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

    except requests.exceptions.RequestException as error:
        print(f"\nError al consultar la ruta: {error}")
        return None

    rutas = datos.get("paths", [])

    if not rutas:
        mensaje = datos.get("message", "No se encontró una ruta disponible.")
        print(f"\n{mensaje}")
        return None

    return rutas[0]


def mostrar_resultados(origen, destino, transporte, ruta):
    """
    Muestra distancia, duración y narrativa del viaje.
    """
    distancia_metros = ruta.get("distance", 0)
    duracion_ms = ruta.get("time", 0)

    kilometros = distancia_metros / 1000
    millas = kilometros * 0.621371
    duracion = convertir_duracion(duracion_ms)

    print("\n" + "=" * 60)
    print("RESULTADO DEL VIAJE")
    print("=" * 60)

    print(f"\nOrigen: {origen['nombre']}")
    print(f"Destino: {destino['nombre']}")
    print(f"Medio de transporte: {transporte}")

    print("\nDistancia:")
    print(f"- {kilometros:,.2f} kilómetros")
    print(f"- {millas:,.2f} millas")

    print(f"\nDuración estimada: {duracion}")

    print("\nNarrativa del viaje:")

    instrucciones = ruta.get("instructions", [])

    if not instrucciones:
        print("- La API no entregó instrucciones narrativas.")
    else:
        for numero, instruccion in enumerate(instrucciones, start=1):
            texto = instruccion.get("text", "Instrucción no disponible")
            distancia = instruccion.get("distance", 0) / 1000

            print(f"{numero}. {texto} ({distancia:.2f} km)")

    print("=" * 60)


def main():
    if not API_KEY:
        print(
            "Error: no se encontró la variable de entorno "
            "GRAPHHOPPER_API_KEY."
        )
        print(
            'Configure la clave con: '
            'export GRAPHHOPPER_API_KEY="SU_API_KEY"'
        )
        sys.exit(1)

    while True:
        print("\n" + "=" * 60)
        print("CALCULADORA DE RUTAS ENTRE CHILE Y PERÚ")
        print("=" * 60)
        print("Escriba la letra 's' en cualquier ciudad para salir.")

        ciudad_origen = input(
            "\nIngrese la ciudad de origen en Chile: "
        ).strip()

        if ciudad_origen.lower() == "s":
            print("\nPrograma finalizado.")
            break

        ciudad_destino = input(
            "Ingrese la ciudad de destino en Perú: "
        ).strip()

        if ciudad_destino.lower() == "s":
            print("\nPrograma finalizado.")
            break

        transporte = seleccionar_transporte()

        if transporte is None:
            print("\nPrograma finalizado.")
            break

        nombre_transporte, perfil = transporte

        print("\nBuscando coordenadas de la ciudad de origen...")
        origen = obtener_coordenadas(ciudad_origen, "Chile")

        if origen is None:
            continue

        print("Buscando coordenadas de la ciudad de destino...")
        destino = obtener_coordenadas(ciudad_destino, "Perú")

        if destino is None:
            continue

        print("Calculando la ruta mediante GraphHopper...")
        ruta = obtener_ruta(origen, destino, perfil)

        if ruta is None:
            continue

        mostrar_resultados(
            origen,
            destino,
            nombre_transporte,
            ruta
        )

        opcion = input(
            "\nPresione ENTER para realizar otra consulta "
            "o escriba 's' para salir: "
        ).strip().lower()

        if opcion == "s":
            print("\nPrograma finalizado.")
            break


if __name__ == "__main__":
    main()
