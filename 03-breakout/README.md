# PODER ORIGINAL: PALETA MAGNETICA

este poder permite, durante la duracion del mismo, atraer a la pelota a la coordenada x central de la paleta.

se presenta un efecto visual en el fondo del videojuego como rayos magneticos siendo atraidos hacia la paleta.

se reestructuro la logica del estado PlayState como estados de una maquina de estados contenida en este.
se separo el codigo en funciones que contienen fragmentos distintos de la logica que hace funcionar el juego, todos estos contenidos en un estado base. Y por cada poder se implemento un estado concreto que sobreescribe solo las funciones o fragmentos de logica relevantes para el comportamiento unico del poder.
esto significa que no pueden haber dos poderes activos al mismo tiempo, si se consume un objeto powerup, si es el mismo powerup ya activo, se reinicia su duracion, si es un powerup distinto o no habia powerup activo, se cambia al estado correspondiente en la maquina de estados dentro del estado PlayState.

El poder de paleta magnetica sobreescribe principalmente la funcion encargada de actualizar las pelotas en juego. Aqui se calcula la distancia en el eje X de la pelota al centro de la paleta, a partir de este valor se calcula una aceleracion horizontal hacia el centro de la paleta, limitando su efecto para no acelerar de mas la pelota, y se aplica esta aceleracion a la velocidad horizontal de la misma.
esto causa un efecto que visualmente parece atraer a la pelota horizontalmente hacia la paleta, y al estar lo suficientemente cerca y con la velocidad correcta causa un efecto como de oscilar hacia un lado y hacia el otro mientras viaja verticalmente.
