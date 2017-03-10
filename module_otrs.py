#!/usr/bin/python
#-----------------------------------------
#Proyecto Final de Modulo 2
#Modulo de integracion con el sistema OTRS
#Integrantes:
#	Fernando Marcos Parra Arroyo
#   Jenifer Martínez Casares 
#	Fernando Reyes Alberdo
#-----------------------------------------
import mysql.connector
from netaddr import iter_iprange,IPNetwork
import csv
from otrs.ticket.template import GenericTicketConnectorSOAP
from otrs.client import GenericInterfaceClient
from otrs.ticket.objects import Ticket, Article, DynamicField, Attachment
import random
#nombre de archivo a analizar
filename="ejemplo.csv"

#error log
archivo=open('error.log','a')


#datos para la conexion a la base de datos
config = {
  'user': 'otrs',
  'password': 'hola123,',
  'host': '127.0.0.1',
  'database': 'adminUNAM',
  'raise_on_warnings': True,
}

#funcion que obtiene el rango de ip por cada administrador
def getIPS( conn ,campo_id,tabla) :
    cur = conn.cursor()
    cur.execute( "SELECT segmento_red,rango_inicial,rango_final,"+campo_id+ " FROM "+tabla )
    lista_ips=[]
    for segmento_red,rango_inicial,rango_final,administrador_id in cur.fetchall():
    	rangos=[str(segmento_red),str(rango_inicial),str(rango_final),administrador_id]
        lista_ips.append(rangos)
        #print segmento_red,rango_inicial,rango_final
    #regresa una lista con segmento de red,rango inicial, rango final y id de administrador
    return lista_ips

#funcion que optiene los datos de un administrador
def getData( conn ,table,field_id ,value_id):
    cur = conn.cursor()
    cur.execute( "SELECT nombre,correo FROM "+table+" WHERE "+ field_id +"="+str(value_id) )
    results=[]
    for nombre,correo in cur.fetchall():
    	datos=[str(nombre),str(correo)]
    	results.append(datos)
        #print nombre,correo
    return results

#funcion que obtiene el id del administrador  al cual petenece una determinadad IP
def buscaIP (ips,encontrar) :
	for ip in ips:
		#print ip
		hosts=[]
		for ipn in IPNetwork(ip[0]).iter_hosts():
			hosts.append(str(ipn))
			#print '%s' % ip
		inicio= hosts.index(ip[1])
		fin= hosts.index(ip[2])+1
		hosts = hosts[inicio:fin:1]
		for m in hosts:
		#	print p
			if m==encontrar:
				print "ip encontrada: " +m
				#print "ENCONTRADAAAAA :D"
				return ip[3]
	archivo.write("ip: "+encontrar+" no encontrada\n")	 
	print "ip: "+encontrar+" no encontrada"
			
#Funcion recibe como parametro un archivo csv y regresa una lista con los campos
def readCSV(archivo):
	with open(archivo, 'rb') as csvfile:
		spamreader = csv.reader(csvfile,delimiter=',', quotechar='|')
		lista = []
		for row in spamreader:
			if row[0] == '278':
				lista.append(row)
	return lista

#Iniciar sesion con un usuario del sistema de tckets
def initSession(user,passwd):
	server_uri = r'http://localhost/otrs/nph-genericinterface.pl'
	webservice_name = 'GenericTicketConnectorSOAP'
	client = GenericInterfaceClient(server_uri, tc=GenericTicketConnectorSOAP(webservice_name))

	client.tc.SessionCreate(user_login=user, password=passwd)

	return client

#funcion que crea un ticket
def createTicket(cliente,titulo,asunto,cuerpo,responsable):
	import mimetypes
	import base64

	priorities=	['1 very low', '2 low', '3 normal', '4 high', '5 very high']
	prior=random.choice(priorities)
	print prior

	lock=	['lock','unlock']
	bloqueado=random.choice(lock)
	print bloqueado

	states = ['new', 'open', 'closed successful', 'closed unsuccessful', 'merged','pending auto close+','pending auto close-','pending reminder','removed']
	state=random.choice(states)
	print state

	t = Ticket(State=state, Priority=prior, Queue='Postmaster',Title=titulo, CustomerUser='fernando@gmail.com',Responsible=responsable,Lock=bloqueado)
	a = Article(NoAgentNotify=1,Subject=asunto,Body=cuerpo,Charset='UTF8',MimeType='text/plain',SenderType='customer',ArticleType='email-external',From='fernando@gmail.com',To=responsable)

	print cliente.tc.TicketCreate(t,a)
	print "Ticket Creado"

def main():
	cnx = mysql.connector.connect(**config)
	cliente=initSession('jmartinez','hola123,')

	print "+++++++++++++++++++++++++++++++++++++++++++++++++"
	print "ADMINISTRADORES"
	print "+++++++++++++++++++++++++++++++++++++++++++++++++"

	rango_ips=getIPS(cnx,'administrador_id','administrador')
	lista = readCSV(filename)
	for l in lista:
		print "-------------------------------------------------------------------------------------------------------"
		body="ASN: "+l[0]+" IP: "+l[1]+" Fecha: "+l[2]+" Evento: "+l[3]+" Dispositivo: "+l[4]+" Identificador: "+l[5]+" Alerta: "+l[6]+" ASN nombre: " + l[7]
		print body
		admin_id=buscaIP(rango_ips,l[1])
		if admin_id != None:
			print "admin id: "+ str(admin_id)
			admins=getData(cnx,'administrador','administrador_id',admin_id)
			for a in admins:
				print "nombre: "+a[0] #nombre del admin
				print "correo: "+a[1] #correo del admin
				createTicket(cliente,l[6],l[6],body,a[1])
	#cerramos la conexion a la base de datos
	cnx.close()
	#se cierra el archivo de error
	archivo.close()

main()