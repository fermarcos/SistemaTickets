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
from otrs.ticket.template import GenericTicketConnectorSOAP
from otrs.client import GenericInterfaceClient
from otrs.ticket.objects import Ticket, Article, DynamicField, Attachment

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
    cur.execute( "SELECT nombre,correo FROM administrador WHERE administrador_id="+str(admin_id) )
    admins=[]
    for nombre,correo in cur.fetchall():
    	datos=[str(nombre),str(correo)]
    	admins.append(datos)
        print nombre,correo
    return admins

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


#funcion que crea un ticket
def createTicket(titulo,asunto,cuerpo,responsable):
	server_uri = r'http://localhost/otrs/nph-genericinterface.pl'
	webservice_name = 'GenericTicketConnectorSOAP'
	client = GenericInterfaceClient(server_uri, tc=GenericTicketConnectorSOAP(webservice_name))

	client.tc.SessionCreate(user_login='jmartinez', password='hola123,')

	import mimetypes
	import base64

	t = Ticket(State='new', Priority='3 normal', Queue='Postmaster',Title=titulo, CustomerUser='fernando@gmail.com',Responsible=responsable)
	a = Article(NoAgentNotify=1,Subject=asunto,Body=cuerpo,Charset='UTF8',MimeType='text/plain',SenderType='customer',ArticleType='email-external',From='fernando@gmail.com',To=responsable)

	print "Ticket Creado"
	print client.tc.TicketCreate(t,a)



cnx = mysql.connector.connect(**config)

rango_ips=getIPS(cnx)
#admin_id=buscaIP(rango_ips,'10.0.0.5')
#print admin_id
#dataAdmin(cnx,admin_id)
lista = readCSV('reporte.csv')
for l in lista:
	print "-------------------------------------------------------------------------------------------------------"
	body="ASN: "+l[0]+" IP: "+l[1]+" Fecha: "+l[2]+" Evento: "+l[3]+" Dispositivo: "+l[4]+" Identificador: "+l[5]+" Alerta: "+l[6]+" ASN nombre: " + l[7]
	print body
	admin_id=buscaIP(rango_ips,l[1])
	if admin_id != None:
		print "admin id: "+ str(admin_id)
		admins=dataAdmin(cnx,admin_id)
		for a in admins:
			print a[0]
			print a[1]
			createTicket(l[6],l[6],body,a[1])
cnx.close()

