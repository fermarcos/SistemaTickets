#!/usr/bin/python
#-----------------------------------------
#Proyecto Final de Modulo 2
#Modulo de integracion con el sistema OTRS
#Integrantes:
#	Fernando Marcos Parra Arroyo
#-----------------------------------------
import mysql.connector
from netaddr import iter_iprange,IPNetwork
import csv

#datos para la conexion a la base de datos
config = {
  'user': 'otrs',
  'password': 'hola123,',
  'host': '127.0.0.1',
  'database': 'adminUNAM',
  'raise_on_warnings': True,
}

#funcion que obtiene el rango de ip por cada administrador
def getIPS( conn ) :
    cur = conn.cursor()
    cur.execute( "SELECT segmento_red,rango_inicial,rango_final,administrador_id FROM administrador" )
    lista_ips=[]
    for segmento_red,rango_inicial,rango_final,administrador_id in cur.fetchall():
    	rangos=[str(segmento_red),str(rango_inicial),str(rango_final),administrador_id]
        lista_ips.append(rangos)
        print segmento_red,rango_inicial,rango_final
    return lista_ips

#funcion que optiene los datos de un administrador
def dataAdmin( conn , admin_id):
    cur = conn.cursor()
    cur.execute( "SELECT correo FROM administrador WHERE administrador_id="+str(admin_id) )
    for correo in cur.fetchall():
        print str(correo)

#funcion que obtiene el id del administrador al cual petenece una determinadad IP
def buscaIP (ips,encontrar) :
    for ip in ips:
		print ip
		hosts=[]
		for ipn in IPNetwork(ip[0]).iter_hosts():
			hosts.append(str(ipn))
			#print '%s' % ip
		inicio= hosts.index(ip[1])
		fin= hosts.index(ip[2])+1
		hosts = hosts[inicio:fin:1]
		#generator = iter_iprange(ip[1], ip[2], step=1)
		for m in hosts:
		#	print p
			if m==encontrar:
				print m
				print "ENCONTRADAAAAA :D"
				return ip[3]
			
#Funcion recibe como parametro un archivo csv y regresa una lista con los campos
def readCSV(archivo):
	with open(archivo, 'rb') as csvfile:
		spamreader = csv.reader(csvfile,delimiter=',', quotechar='|')
		lista = []
		for row in spamreader:
			if row[0] == '278':
				lista.append(row)
	return lista

cnx = mysql.connector.connect(**config)

rango_ips=getIPS(cnx)
#admin_id=buscaIP(rango_ips,'10.0.0.5')
#print admin_id
#dataAdmin(cnx,admin_id)
lista = readCSV('ejemplo.csv')
for l in lista:
	print "-------------------------------------------------------------------------------------------------------"
	body="ASN: "+l[0]+" IP: "+l[1]+" Fecha: "+l[2]+" Evento: "+l[3]+" Dispositivo: "+l[4]+" Identificador: "+l[5]+" Alerta: "+l[6]+" ASN nombre: " + l[7]
	print body
	admin_id=buscaIP(rango_ips,l[1])
	if admin_id != None:
		print "admin id: "+ str(admin_id)
		dataAdmin(cnx,admin_id)
cnx.close()

