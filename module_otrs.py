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

	
	print client.tc.TicketCreate(t,a)
	print "Ticket Creado"


cnx = mysql.connector.connect(**config)

print "+++++++++++++++++++++++++++++++++++++++++++++++++"
print "ADMINISTRADORES"
print "+++++++++++++++++++++++++++++++++++++++++++++++++"

rango_ips=getIPS(cnx,'administrador_id','administrador')
lista = readCSV('reporte.csv')
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
			createTicket(l[6],l[6],body,a[1])

print "+++++++++++++++++++++++++++++++++++++++++++++++++"
print "ESPECIALISTAS"
print "+++++++++++++++++++++++++++++++++++++++++++++++++"

rango_ips=getIPS(cnx,'especialista_id','especialista')
lista = readCSV('reporte.csv')
for l in lista:
	print "-------------------------------------------------------------------------------------------------------"
	body="ASN: "+l[0]+" IP: "+l[1]+" Fecha: "+l[2]+" Evento: "+l[3]+" Dispositivo: "+l[4]+" Identificador: "+l[5]+" Alerta: "+l[6]+" ASN nombre: " + l[7]
	print body
	espec_id=buscaIP(rango_ips,l[1])
	if espec_id != None:
		print "especialista id: "+ str(espec_id)
		especialistas=getData(cnx,'especialista','especialista_id',espec_id)
		for esp in especialistas:
			print "nombre: "+esp[0] #nombre del especialista
			print "correo: "+esp[1] #correo del especialista
			createTicket(l[6],l[6],body,esp[1])

cnx.close()