import pandas as pd 
from time import sleep
from os import system, name 
from datetime import datetime

from lifestore_file import *

# Diccionario que contiene los usuarios disponibles y sus respectivas contraseñas 
# {'usuario':'contaseña'}
user_credentials = {'admin':'adminpass', 
                    'client':'clientpass', 
                    'general_user':'genuserpass'}

alive = True # Valor bandera para controlar el cierre del ciclo while del programa  
active_session = False # Nos indica si una sesión esta activa o inactiva 
user_on_session = None # Se almacena el usuario que ha iniciado sesión
pre_signin_menu_printed = False # Almacenamos si el menu pre inicio de sesión ha sido mostrado
post_signin_menu_printed = False # Almacenamos si el menu post inicio de sesión ha sido mostrado

# Conversión de lista de listas a DataFrames
df_lifestore_products = pd.DataFrame(lifestore_products, columns=['id_product', 'name', 'price', 'category', 'stock'])
df_lifestore_sales = pd.DataFrame(lifestore_sales, columns=['id_sale', 'id_product', 'score', 'date', 'refund'])
df_lifestore_searches = pd.DataFrame(lifestore_searches, columns=['id_search', 'id_product'])

df_lifestore_products.set_index('id_product', inplace=True) # Se configura la columna id_product como indice
df_lifestore_sales['date'] = pd.to_datetime(df_lifestore_sales['date'], format='%d/%m/%Y') # Se transforma la columna 'date'
                                                                                           # en 'datetime'
# Obtención de estadísticas de ventas 
sales_statistics = df_lifestore_sales.groupby(by='id_product').agg({'id_product': ['count'], 
                                                                    'refund': ['sum'],
                                                                    'score': ['mean']})
sales_statistics.columns = sales_statistics.columns.map('_'.join)
sales_statistics = sales_statistics.rename(columns={"id_product_count": "total_sales", 
                                                    "refund_sum": "total_refunds"})  # Se renombran columnas a nombres 
                                                                                     # más significativos
sales_statistics['score_mean'] = sales_statistics['score_mean'].round(1) # Se redondea el score promedio a una decima 

# Obtención de estadísticas de busquedas 
searches_statistics = df_lifestore_searches.groupby(by='id_product').agg({'id_product':['count']})
searches_statistics.columns = searches_statistics.columns.map('_'.join)
searches_statistics = searches_statistics.rename(columns={"id_product_count": "total_searches"}) # Se renombran columnas a nombres 
                                                                                                 # más significativos

# Unión de estádisticos a dataframe de productos 
df_lifestore_products = df_lifestore_products.join(sales_statistics).join(searches_statistics)  # Se realiza un join con los estádisticos
                                                                                                # de ventas y busquedas.
df_lifestore_products[['total_sales', 'total_refunds', 'total_searches']] = \
    df_lifestore_products[['total_sales', 'total_refunds', 'total_searches']].fillna(0).astype(int) # Los valores NaN pasan ser 0 y
                                                                                                    # se convierte a entero los registros 
                                                                                                    # de las columnas correspondientes

# Obtención de estadísticos de ventas mensuales
start_date = datetime(2020, 1, 1) # Fecha a partir de la cual se tomará información
df_merged = pd.merge(df_lifestore_sales,             # Se realiza un merge para unir el precio correspondiente 
                     df_lifestore_products['price'], # al id del producto
                     left_on='id_product', 
                     right_index=True)
df_merged = df_merged.loc[df_merged['refund']==0] # Se filtran solo los registros que no hayan tenido devoluciones

month_statistics = df_merged.groupby(pd.Grouper(key="date", freq='M')).agg({'id_product': ['count'], 
                                                                            'price': ['sum']})
month_statistics.columns = month_statistics.columns.map('_'.join)
month_statistics = month_statistics.rename(columns={"id_product_count": "sales",
                                                    "price_sum": "income"})

month_statistics = month_statistics.loc[~(month_statistics==0).all(axis=1)] # Se filtran solo los meses que tengan información
month_statistics = month_statistics.loc[month_statistics.index > start_date] # Se filtra la información a partir de 'start_date'

# Función que limpia la consola
def clear():
    # Para windows
    if name == 'nt':
        system('cls')
    # Para mac y linux (aqui, os.name es 'posix')
    else:
        system('clear')


if __name__ == '__main__':

    # Limpiamos la consola antes de iniciar el ciclo del programa
    clear() 

    while alive:  

        attemps = 0 # Contador para almacenar el numéro de intentos de inicio de sesión
        attemps_limit = 3 # Límite de intentos para inicio de sesión

        if not active_session: # Sesión inactiva

            if not pre_signin_menu_printed:
                print("\t¡Bienvenido a Podruct Analysis Tool! \n")
                print("Ingresa el número de la opcion deseada:\n")
                print("1) INICIAR SESION")
                print("2) SALIR\n")
                pre_signin_menu_printed = True

            option_selected = input("-> ") # Almacena la opcion del menu seleccionada

            try:
                if int(option_selected) == 1:
                    clear()
                    print("\nIngresa tus credenciales:\n")

                    # Se arranca un subciclo while para el inicio de sesión
                    while attemps < attemps_limit:
                        user = input("-> USER: ") # Se captura el nombre del usuario 
                        password = input("-> PASSWORD: ") # Se captura la contraseña del nombre del usuario ingresado

                        if user in user_credentials and user_credentials[user] == password:
                            active_session = True # Se actualiza ante un inicio de sesión exitoso
                            user_on_session = user
                            clear()
                            break                 # Se detiene el subciclo while para el inicio de sesión
                        else: 
                            # Ante inicio de sesión fallidos se acumulan los intentos evaluando si se ha llegado
                            # a un límite
                            if attemps < attemps_limit - 1:
                                print("\nEl usuario o la contraseña son invalidos... :'(")
                                print("Ingresa tu credenciales nuevamente:\n")
                                attemps += 1
                            else:
                                print("\nNumero de intentos límite alcanzado ...")
                                print("Volviendo al menu principal ^.^")
                                sleep(2)
                                attemps += 1
                                pre_signin_menu_printed = False
                                clear()

                elif int(option_selected) == 2:
                    print("\nGracias por tu visita, esperamos verte pronto :') ...")
                    alive = False
                
            except ValueError:
                print("\nLa opción ingresada no es valida.")
                print("Ingresa una opción valida...\n")

        elif active_session: # Sesión activa
            if not post_signin_menu_printed:
                print(f"¡Hola {user_on_session}!")
                print("Elige una de las opciones de análisis disponibes:\n")
                print("1)  PRODUCTOS CON MÁS VENTAS")
                print("2)  PRODUCTOS CON MÁS BUSQUEDAS")
                print("3)  PRODUCTOS CON MENOS VENTAS")
                print("4)  PRODUCTOS CON MENOS BUSQUEDAS")
                print("5)  PRODUCTOS REZAGADOS")
                print("6)  PRODUCTOS CON BUENAS RESEÑAS")
                print("7)  PRODUCTOS CON MALAS RESEÑAS")
                print("8)  VENTAS MENSUALES")
                print("9)  Cerrar sesion")
                print("10) Salir\n")
                post_signin_menu_printed = True

            option_selected = input("-> ")

            try:
                # Se despliegan los 10 productos con más ventas 
                if int(option_selected) == 1:
                    clear()
                    top_sales = df_lifestore_products[['name',     
                                                       'category', 
                                                       'total_sales']].nlargest(10, 'total_sales')
                    print(f"\n\t\t\t\t\t\t ************** PRODUCTOS CON MAYORES VENTAS **************\n")
                    print(top_sales.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()

                # Se despliegan los 10 productos con más busquedas 
                elif int(option_selected) == 2:
                    clear()
                    top_searches = df_lifestore_products[['name', 
                                                          'category', 
                                                          'total_searches']].nlargest(10, 'total_searches')
                    print(f"\n\t\t\t\t\t\t ************** PRODUCTOS CON MAS BUSQUEDAS **************\n")
                    print(top_searches.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()

                # Se despliegan los 10 productos con menos ventas 
                elif int(option_selected) == 3:
                    clear()
                    # Se eliminan las filas que contengan ceros en la columna 'total_sales'
                    df_non_zero_sales = df_lifestore_products.loc[~(df_lifestore_products['total_sales']==0)]
                    bottom_sales = df_non_zero_sales[['name', 
                                                      'category', 
                                                      'total_sales']].nsmallest(10, 'total_sales')
                    print(f"\n\t\t\t\t\t\t ************** PRODUCTOS CON MENORES VENTAS **************\n")
                    print(bottom_sales.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()

                # Se despliegan los 10 productos con menos busquedas 
                elif int(option_selected) == 4:
                    clear()
                    # Se eliminan las filas que contengan ceros en la columna 'total_searches'
                    df_non_zero_searches = df_lifestore_products.loc[~(df_lifestore_products['total_searches']==0)]
                    bottom_searches = df_non_zero_searches[['name', 
                                                            'category', 
                                                            'total_searches']].nsmallest(10, 'total_searches')
                    print(f"\n\t\t\t\t\t\t ************** PRODUCTOS CON MENORES BUSQUEDAS **************\n")
                    print(bottom_searches.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()

                # Se despliegan todos los productos rezagados que tienen 0 ventas 
                elif int(option_selected) == 5:
                    clear()
                    # Se filtran aquellos productos que no han tenido ventas
                    df_zero_sales = df_lifestore_products.loc[(df_lifestore_products[['total_sales']]==0).all(axis=1), \
                                                              ['name', 'category', 'stock', 'total_sales']]
                    print(f"\n\t\t\t\t\t\t\t ***************** PRODUCTOS REZAGADOS *****************\n")
                    print(df_zero_sales.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()

                # Se despliegan los productos con las mejores reseñas, en donde se calculo 
                # un promedio del score de las reseñas que ha tenido un producto
                elif int(option_selected) == 6:
                    clear()
                    top_scores = df_lifestore_products[['name', 
                                                        'category', 
                                                        'total_refunds', 
                                                        'score_mean']].nlargest(10, 'score_mean')
                    print(f"\n\t\t\t\t\t\t\t\t ************ PRODUCTOS CON BUENAS RESEÑAS ************\n")
                    print(top_scores.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()                    
                
                # Se despliegan los productos con las peores reseñas, en donde se calculo 
                # un promedio del score de las reseñas que ha tenido un producto
                elif int(option_selected) == 7:
                    clear()
                    bottom_scores = df_lifestore_products[['name', 
                                                           'category', 
                                                           'total_refunds', 
                                                           'score_mean']].nsmallest(5, 'score_mean')
                    print(f"\n\t\t\t\t\t\t\t\t ************ PRODUCTOS CON MALAS RESEÑAS ************\n")
                    print(bottom_scores.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False    
                    clear()

                # Se despliega una tabla con ventas mensuales del 2020, ya que solo de este año
                # se cuenta con información concisa
                elif int(option_selected) == 8:
                    clear()
                    print(f"\n********** VENTAS MENSUALES 2020 **********\n")
                    print(month_statistics.to_markdown())
                    input("\nPresiona enter para volver al menu principal :)")
                    post_signin_menu_printed = False
                    clear()

                # Se cierra sesión
                elif int(option_selected) == 9:
                    print(f"\nCerrando sesión, adios {user_on_session}! ...")
                    active_session = False
                    pre_signin_menu_printed = False
                    post_signin_menu_printed = False
                    sleep(2)
                    clear()

                # El programa termina 
                elif int(option_selected) == 10:
                    print(f"\nGracias por tu visita, esperamos verte pronto {user_on_session} :') ...")
                    alive = False

            except ValueError:
                print("\nLa opción ingresada no es valida.")
                print("Ingresa una opción valida...\n")



