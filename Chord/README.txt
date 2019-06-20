servidor
finger_table -> tiene los sucesores junto con sus intervalos: 
sucesor_address -> Dirección del sucesor: string
interval_hashes -> Intervalo de hashes por los que el servidor es responsable: [hash1, hash2]
socket_to_listen -> socket para escuchar mensajes que lleguen al servidor

metodos
contructor(puerto_to_listen, sucesor_address?)
Debe crear el socket_to_listen, creo un hash que seria mi hash1 (direccion mac + puerto) y si exite sucesor_address le avisa que quiere entrar para que retorne quien es dueño
de ese hash1 y negocia con ese servidor... (al final declaro mi intervalo de hashes por los que soy responsable)

listen()
Escucho todos los mensaje que me llegan al puerto y puedo ejecutar los siguientes metodos (get_file, send_file, get_hashes_interval, get_sucesor_for_hash, change_the_sucesor, update_finger_table)


get_file
Guardo un archivo en mi directorio de archivos

send_file
Envio un archivo de mi directorio de archivos

get_hash_interval
Devuelvo mi intervalo de hashes

get_sucesor_for_hash
Devuelve el nodo mas cercano al que pertenece ese hash

change_the_sucesor
Cambio mi sucesor y le entrego todos los hashes de los que era responsable en mi intervalo, tambien notifico a los demas nodos del cambio

update_finger_table
Actualiza el finger_table cuando un servidor cambia su intervalo de hashes
