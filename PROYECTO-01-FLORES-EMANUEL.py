####### LOGIN SECTION #######

# Los usuarios permitidos se guardaran en una lista, de la siguiente forma:
# [user, password]
allowed_users = [
    ['Emanuel', 'asdfqwer'],
    ['Samantha', 'qwerasdf']
]

print('\n******* Bienvenido a LIFESTORE *******\n')
print('Para poder continuar, necesita identificarse')
user_validated = False

# El usuario ingresa el nombre y la constraseña, para poder ingresar
name_input = input('Nombre de usuario: ')
password_input = input('Contraseña: ')

# Hacemos una consulta sobre la lista de usuarios permitidos, 
# en caso de que el nombre y la contraseña ingresados esten en la lista se les permitirá el acceso
for user, password in allowed_users:
    if user == name_input and password == password_input:
        print('[+] Usuario conectado correctamente.')
        user_validated = True

if not user_validated:
    print('[-] Usuario incorrecto, verifique el nombre y la contraseña para ingresar.')
    exit(-1)





    

