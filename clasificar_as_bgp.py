# Script para clasificar un número de Sistema Autónomo BGP

def clasificar_as(numero_as):
    if numero_as < 1 or numero_as > 4294967295:
        return "El número ingresado no corresponde a un AS válido."

    if 64512 <= numero_as <= 65534:
        return "El AS pertenece al rango privado de 16 bits."

    if 4200000000 <= numero_as <= 4294967294:
        return "El AS pertenece al rango privado de 32 bits."

    if numero_as == 23456:
        return "El AS 23456 está reservado como AS_TRANS."

    if numero_as == 65535 or numero_as == 4294967295:
        return "El número de AS está reservado."

    return "El AS pertenece al rango público."


while True:
    entrada = input(
        "Ingrese un número de AS BGP o escriba 's' para salir: "
    ).strip()

    if entrada.lower() == "s":
        print("Programa finalizado.")
        break

    try:
        numero_as = int(entrada)
        resultado = clasificar_as(numero_as)
        print(resultado)

    except ValueError:
        print("Error: debe ingresar un número entero o la letra 's'.")
