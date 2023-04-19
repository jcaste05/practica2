# PRÁCTICA 2 PROBLEMA DEL PUENTE
El archivo Python practica2_solucion_basica.py consiste en una primera solución para controlar el paso de vehículos en dos direcciones y peatones por un puento de un solo carril. En el main se crean tres procesos que simulan la llegada al puente de vehículos en cada dirección y de peatones. El control para el acceso al uso del puente está regulado por un monitor sencillo que garantiza la exclusión mutua pero presenta problemas de justicia e inanición.

El archivo Python practica2.py consiste en una solución más sofisticada que la anterior corrigiendo los problemas de inanición y justicia incorporando turnos. De esta manera, un individuo podrá entrar al puente si es su turno o no hay ninguno de los otros esperando, y el puente está libre del resto.

En el PDF practica2_PDF.pdf se explica de forma manuscrita los monitores que se usan en cada una de las soluciones as
