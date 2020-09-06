from users import allowed_users
from lifestore_file import lifestore_products, lifestore_sales, lifestore_searches
import os
import numpy as np

####### LOGIN SECTION #######
print('\n******* Bienvenido a LIFESTORE *******\n')
print('Para poder continuar, necesita identificarse')

attemps = 0
user_validated = False

# El usuario tendrá tres intentos para identificarse
while not user_validated and attemps < 3:

    # El usuario ingresa el nombre y la constraseña, para poder ingresar
    name_input = input('Nombre de usuario: ')
    password_input = input('Contraseña: ')

    # Se compara el usuario y contraseña ingresados con los usuarios registrados
    for user, password, role in allowed_users:
        if user == name_input and password == password_input:
            print('[+] Usuario conectado correctamente.\n')
            user_validated = True
            is_admin = role == 1
            
    # Si no se valida el usuario, manda mensaje de error y sale del programa
    if not user_validated:
        print('[-] Usuario incorrecto, verifique el nombre y la contraseña para ingresar.\n')
        attemps += 1

# Si el usuario no se pudo validar lo sacamos del programa
if not user_validated:
    exit(-1)

####### DATA TRANSFORM SECTION #######

### SELLED PRODUCTS ANALYSIS ##

# Se creará una lista con el siguiente formato:
# [id_product, sum_score, times_refund, quantity_sold, count_searches] en el caso de que haya tenido ventas
# en el caso de no tener ventas, se guardará [id_product, quantity_sold(0), count_searches]
sales_analysis = [None] * len(lifestore_products)

# Se creará una lista que almacene el mes y el en que fue vendido cada producto
date_sales = []

for product_sale in lifestore_sales:
    product_position = product_sale[1] - 1

    month, year = int(product_sale[3][3:5]), int(product_sale[3][6:])
    date_sales.append([product_sale[1], month, year])

    # Sí no está en la lista, agrego los datos que me interesan, y agrego la cantidad de veces que se vendió
    if sales_analysis[product_position] == None:
        sales_analysis[product_position] = product_sale[1:3] + product_sale[4:] 
        sales_analysis[product_position].append(1)

    # En caso de que ya este en la lista, se revisa si tuvo alguna devolución, en caso de que sí
    # agrego uno a la cantidad de veces regresado, además se suma el score que le dieron al 
    # producto y se agrega uno a la cantidad de veces que se vendió
    else:
        sales_analysis[product_position][-2] += product_sale[-1] # Refunds
        sales_analysis[product_position][1] += product_sale[2]   # Score
        sales_analysis[product_position][-1] += 1                # Quantity Sold

# Esta lista almacenara únicamente los productos vendidos, su formato será este
# [id_product, mean_score, times_refund, date_sale, quantity_sold]
selled_products = []

for i, product in enumerate(sales_analysis):
    if product != None:
        product[1] /= (product[-1] + product[-2]) # Mean Score (Score / (quantity_sold + refunds))
        selled_products.append(product)
    else:
        sales_analysis[i] = [i + 1, 0]

    # Este cero que se agrega al final será el contador de las busquedas
    sales_analysis[i].append(0)

def take_last_second_thrid(elem):
    return (elem[-2], elem[-3])
    
selled_products.sort(key = take_last_second_thrid, reverse = True)

## SEARCH PRODUCTS ANALYSIS ##

# Ahora se sumará la cantidad de veces que los productos fueron buscados
# y se agregará a la lista sales_analysis
for search in lifestore_searches:
    position = search[1] - 1
    sales_analysis[position][-1] += 1

def take_second(elem):
    return elem[1]

def take_third(elem):
    return elem[2]

def take_four(elem):
    return elem[3]

def take_last(elem):
    return elem[-1]

def take_second_last(elem):
    return elem[-2]

## DATE SALES ANALYSIS ##
# Se ordena la lista por mes y por año
date_sales.sort(key = take_second)
date_sales.sort(key = take_third)

date_total_sales = []
actual_month = date_sales[0][1]
actual_year = date_sales[0][2]
total_amount = 0
product_count = 0

# Se hará guardará la cantidad de productos e ingresos por mes
for id_product, month, year in date_sales:
    if actual_month == month:
        product_count += 1
        total_amount += lifestore_products[id_product - 1][2]
    else:
        date_total_sales.append([actual_month, actual_year, product_count, total_amount])
        actual_year = year
        actual_month = month
        total_amount = 0
        product_count = 0

year_total_sales = []
year_amount = 0
actual_year = date_sales[0][2]
for date_sale in date_total_sales:
    if actual_year == date_sale[1]:
        year_amount += date_sale[-1]
    else:
        year_total_sales.append([actual_year, year_amount])
        actual_year = date_sale[1]
        year_amount = 0
year_total_sales.append([actual_year, year_amount])

## CATEGORY ANALYSIS ##
# Se creara una lista que almacenará los siguientes datos
# [category_product, total_sale_by_category, quantity_product_by_category, total_sales_quantity_relation]

category_analysis = []
categories = []

for product in sorted(sales_analysis, key = take_second_last, reverse=True):
    id_product = product[0] - 1
    if lifestore_products[id_product][3] not in categories:
        categories.append(lifestore_products[id_product][3])
        category_analysis.append([lifestore_products[id_product][3], lifestore_products[id_product][2] * product[-2], 1])
    else:
        category_position = categories.index(lifestore_products[id_product][3])
        category_analysis[category_position][1] += lifestore_products[id_product][2] * product[-2]
        category_analysis[category_position][2] += 1

for category_sale in category_analysis:
    category_sale.append( category_sale[1] / (category_sale[2] * 100) )

category_analysis.sort(key=take_four, reverse=True)


    
####### USER DATA VIEW #######
while user_validated and is_admin:
    os.system('clear')
    print('**** LifeStore Panel (Administrador) [{}] ****\n'.format(name_input))
    option = input('''Seleccione el número con la opción deseada:
1. Mostrar productos por ventas
2. Mostrar productos por cantidad de búsquedas
3. Mostrar productos por reseñas
4. Mostrar ingresos por fecha
5. Mostrar resumen por categorias
6. Cerrar Sesión
>> ''')

    if option == '1':
        print('\nSeleccione como filtrar las ventas:', 
              '1. Productos más vendidos', 
              '2. Productos menos ventas', 
              '3. Productos rezagados',
              'Otro. Regresar al menú anterior', sep = '\n')
        sale_filter = input('>> ')

        middle_position = len(selled_products) // 2

        if sale_filter == '1':
            print('PRODUCTO', ' ' * 110, '| VENDIDO \t| STOCK \t| PRECIO')
            print('-' * 160)
            for product in selled_products[:middle_position]:
                id_product = lifestore_products[product[0] - 1]
                print(id_product[1], ' ' * (119 - len(id_product[1])) + '|' ,product[-2], '\t\t|', id_product[-1], '\t\t|', id_product[-3])

        elif sale_filter == '2':
            print('PRODUCTO', ' ' * 110, '| VENDIDO \t| STOCK \t| PRECIO')
            print('-' * 160)
            for product in selled_products[middle_position:]:
                id_product = lifestore_products[product[0] - 1]
                print(id_product[1], ' ' * (119 - len(id_product[1])) + '|' ,product[-2], '\t\t|', id_product[-1], '\t\t|', id_product[-3])

        elif sale_filter == '3':
            print('PRODUCTO', ' ' * 110, '| STOCK \t| PRECIO')
            print('-' * 145)
            for product in sales_analysis:
                if product[-2] == 0:
                    id_product = lifestore_products[product[0] - 1]
                    print(id_product[1], ' ' * (119 - len(id_product[1])) + '|', id_product[-1], '\t\t|', id_product[-3])
        else:
            continue

        input('\nPresiona ENTER para regresar al menú principal.\n')

    elif option == '2':
        print('\nMostrar productos por:', 
              '1. Más buscados', 
              '2. Menos buscados', 
              'Otro. Regresar al menú anterior', sep = '\n')
        search_filter = input('>> ')

        most_searched = search_filter == '1'

        if search_filter == '1' or search_filter == '2':
            print('PRODUCTO', ' ' * 110, '| # BUSCADOS \t| VENDIDOS')
            print('-' * 146)
            for product in sorted(sales_analysis, key=take_last, reverse=most_searched):
                id_product = lifestore_products[product[0] - 1]
                print(id_product[1], ' ' * (119 - len(id_product[1])) + '|', product[-1], '\t\t|', product[-2])
        else:
            continue

        input('\nPresiona ENTER para regresar al menú principal.\n')

    elif option == '3':
        print('\nMostrar productos por:', 
              '1. Mejor valoración', 
              '2. Menor valoración', 
              'Otro. Regresar al menú anterior', sep = '\n')
        score_filter = input('>> ')

        best_rated = score_filter == '1'

        if score_filter == '1' or score_filter == '2':
            print('PRODUCTO', ' ' * 110, '| SCORE \t| VENDIDOS \t| DEVUELTOS')
            print('-' * 163)
            for mean_score in sorted(selled_products, key = take_second, reverse=best_rated)[:20]:
                id_product = lifestore_products[mean_score[0] - 1]
                print(id_product[1], ' ' * (119 - len(id_product[1])) + '| {:.2f}'.format(mean_score[1]), '\t\t|', mean_score[-2], '\t\t|', mean_score[-3])
        else:
            continue

        input('\nPresiona ENTER para regresar al menú principal.\n')
    
    elif option == '4':
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        print('\n**** VENTAS MENSUALES ****')
        print('FECHA \t\t\t| CANTIDAD \t| VENTA TOTAL')
        print('-' * 55)
        for date_sale in date_total_sales:
            print(f'{ months[ date_sale[0] - 1 ] } del { date_sale[1] }', ' ' * (2) , f'\t| { date_sale[2] }\t\t| ${ date_sale[3] }.00')

        print('\n**** VENTAS ANUALES ****')
        for sales_year in year_total_sales:
            print(f'En { sales_year[0] } se obtuvo un ingreso de ${ sales_year[1] }.00')
        
        print('\n**** VENTAS MENSUALES CON MEJORES INGRESOS ****')
        print('FECHA \t\t\t| CANTIDAD \t| VENTA TOTAL')
        print('-' * 55)
        for date_sale in sorted(date_total_sales, key = take_four, reverse=True):
            print(f'{ months[ date_sale[0] - 1 ] } del { date_sale[1] }', ' ' * (2) , f'\t| { date_sale[2] }\t\t| ${ date_sale[3] }.00')


        input('\nPresiona ENTER para regresar al menú principal.\n')
    
    elif option == '5':
        print('CATEGORIA \t     | VENTA TOTAL \t| # PRODUCTOS \t| RELACION')
        print('-' * 66)
        for category in category_analysis:
            print(category[0], ' ' * (20 - len(category[0])) + '|' ,category[1], '\t\t|',category[2], '\t\t| {:.2f}'.format(category[3]))

        input('\nPresiona ENTER para regresar al menú principal.\n')

    elif option == '6':
        print('¡Hasta luego, {}!'.format(name_input))
        user_validated = False
    
while user_validated:
    os.system('clear')
    print('**** Bienvenido a LifeStore, {} ****\n'.format(name_input))
    option = input('''Seleccione el número con la opción deseada:
1. Mostrar lista de productos
2. Cerrar Sesión
>> ''')

    if option == '1':
        print('PRODUCTO', ' ' * 110, '| CATEGORIA \t\t| PRECIO \t| STOCK')
        print('-' * 170)
        for product in lifestore_products:
            print(product[1], ' ' * (119 - len(product[1])) + '|', product[3], ' ' * (20 - len(product[3])) + ' |', product[2], ' ' * (13 - len(str(product[2]))) + '|', product[4])

        input('\nPresiona ENTER para regresar al menú principal.\n')

    elif option == '2':
        user_validated = False


# datos = np.asarray(l)
            
#             np.savetxt("most_selled.csv",   # Archivo de salida
#                      datos,
#                      fmt="%s",
#                      delimiter=",") 