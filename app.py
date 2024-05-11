from flask import Flask, request, make_response, jsonify
from dotenv import load_dotenv, dotenv_values
from flask import send_from_directory
from flask_cors import cross_origin
from datetime import date, datetime
from decimal import Decimal
import mysql.connector
import os

# Carregando as variaveis de ambiente, evitar expor no código as infos de conexão.
load_dotenv()

# Vai ficar sujo o código pq estou aprendendo!
mydb = mysql.connector.connect(
    host=os.getenv("JAWSDB_HOST"),
    user=os.getenv("JAWSDB_USER"),
    password=os.getenv("JAWSDB_PASS"),
    database=os.getenv("JAWSDB_DATABASE"),
)

try:
  if mydb.is_connected():
    print(" * Log: Conectado ao banco de dados!")
  else:
    print(" * Log: Falha ao conectar ao banco de dados!")
except mysql.connector.Error as err:
  print("Erro:", err)

# Inicializa o aplicativo.
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# METODOS GET - Consulta do banco de dados.
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
def documento():
    return "API"

# Criando a rota para teste.
@app.route('/bemvindo')
def teste():
    return "Bem vindo ao projeto flask. <br>Foi dificil, mas eu consegui \U0001F923 <br> Alessandro Almada Leal </br>"

# Retorna os dados do usuário mediante a passagem do e-mail como parametro.
@app.route('/dados=<email>')
def getUserData(email):

    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT * "
    sql += "FROM (SELECT id_adm AS id, ds_nome, ds_email, ds_senha, True AS is_admin FROM tb_adm "
    sql +=       "UNION ALL "
    sql +=       "SELECT id_emp AS id, ds_nome, ds_email, ds_senha, False AS is_adm FROM tb_emp) AS t "
    sql += "WHERE LOWER(ds_email) = LOWER(%s)"
    
    cursor.execute(sql, (email, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'id': item[0],
                    'nome': item[1],
                    'email': item[2],
                    'token': item[3],
                    'ad': item[4],
                }
            )

        return make_response( 
            jsonify(
                mensagem='Usuário encontrado',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Não encontrado',
            ), 403
        )
    
@app.route('/logMeIn=<email>/<hash>')
def getMeIn(email, hash):

    cursor = mydb.cursor()

    sql  = "SELECT id_adm, ds_senha, True AS is_adm FROM tb_adm WHERE LOWER(ds_email) = LOWER(%(email_str)s) "
    sql += "UNION ALL "
    sql += "SELECT id_emp, ds_senha, False AS is_adm FROM tb_emp WHERE ds_email = LOWER(%(email_str)s)"
    
    cursor.execute(sql, {'email_str': email})
    resultado = cursor.fetchall()

    if not(resultado):
        return make_response( 
            jsonify(
                mensagem='Acesso negado',
            ), 403
        )

    if resultado[0][1] == hash:
        itens = list()
        itens.append(
                {     
                    'id': resultado[0][0],
                    'Auth': True,
                    'is_ad': resultado[0][2]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Login liberado',
                dados=itens
            ), 200
        )
    
    else:
        return make_response( 
            jsonify(
                mensagem='Acesso negado',
            ), 403
        )

@app.route('/tbEmp=<id_adm>')
def getMeusEmpreendedores(id_adm):
    
    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT id_emp, ds_nome, ds_email, ds_cnpj, dt_nascimento, ds_telefone FROM tb_emp WHERE id_adm = %s"
    
    cursor.execute(sql, (id_adm, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'id': item[0],
                    'nome': item[1],
                    'email': item[2],
                    'cnpj': item[3],
                    'nascimento': item[4],
                    'telefone': item[5]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Empreendedores cadastrados',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Administrador não encontrado',
            ), 403
        )

@app.route('/comboServ=<id_emp>')
def getServicosBox(id_emp):
    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT CONCAT (ds_codigo, ' - ', ds_desc) AS seus_servicos, MAX(id_ser) AS id "
    sql += "FROM tb_catserv WHERE id_emp = %s GROUP BY seus_servicos"

    cursor.execute(sql, (id_emp, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'servico': item[0],
                    'id': item[1]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Servicos cadastrados',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Nenhum serviço encontrado',
            ), 403
        )

@app.route('/tbServ=<id_emp>')
def getServicosTable(id_emp):
    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT MAX(id_ser) as id, ds_codigo, ds_desc, dt_vig, mn_valor "
    sql += "FROM tb_catserv WHERE id_emp = %s GROUP BY ds_codigo "

    
    cursor.execute(sql, (id_emp, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'cod': item[0],
                    'categoria': item[1],
                    'descricao': item[2],
                    'vigencia': item[3],
                    'valor': item[4]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Servicos cadastrados',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Nenhum serviço encontrado',
            ), 403
        )

@app.route('/comboCli=<id_emp>')
def getClienteBox(id_emp):

    cursor = mydb.cursor()
    
    # Query
    sql = "SELECT id_cli, CONCAT (id_cli,' - ',ds_nome) AS seu_cliente FROM tb_cli "
    sql += "WHERE id_emp = %s ORDER BY id_cli "

    cursor.execute(sql, (id_emp, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retorne um json.
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'id': item[0],
                    'nome': item[1]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Clientes cadastrados',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Nenhum cliente encontrado para este empreendedor.',
            ), 403
        )

@app.route('/tbCli=<id_emp>')
def getClienteTable(id_emp):
    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT id_cli, ds_nome, ds_email, dt_nascimento, dt_cadastro, ds_telefone "
    sql += "FROM tb_cli "
    sql += "WHERE id_emp = %s "
    sql += "ORDER BY dt_cadastro "
    
    cursor.execute(sql, (id_emp, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'cod': item[0],
                    'nome': item[1],
                    'email': item[2],
                    'nascimento': item[3],
                    'cadastro': item[4],
                    'telefone': item[5]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Clientes cadastrados',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Nenhum cliente encontrado para este empreendedor.',
            ), 403
        )

@app.route('/tbAgenda=<id_emp>')
def getAgenda(id_emp):
    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT A.id_agenda, A.dt_data, A.hr_ini, A.hr_fim, A.id_cli, B.ds_nome "
    sql += "FROM tb_agenda A, tb_cli B "
    sql += "WHERE A.id_emp = %s AND A.id_cli = B.id_cli "
    
    cursor.execute(sql, (id_emp, ))
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'id': item[0],
                    'data': item[1],
                    'hora_ini': item[2],
                    'hora_fim': item[3],
                    'cliente_id': item[4],
                    'cliente_nome': item[5]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Agendamentos encontrados',
                dados=itens
            ), 200
        )
    
    # Se o resultado for vazio, retornar None
    else:
        return make_response( 
            jsonify(
                mensagem='Nenhum agendamento localizado.',
            ), 403
        )
    
@app.route('/comboStatus')
def getStatus():
    cursor = mydb.cursor()

    #Forma compacta de escrever a query.
    sql  = "SELECT * FROM tb_status"
    
    cursor.execute(sql)
    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'id': item[0],
                    'status_description': item[1]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Status disponiveis',
                dados=itens
            ), 200
        )
    
    else:
        return make_response( 
            jsonify(
                mensagem='Sem status',
            ), 403
        )

@app.route('/historico=<id_emp>/', defaults={'dt_ini': None, 'dt_fim': None})
@app.route('/historico=<id_emp>/<dt_ini>/', defaults={'dt_fim': None})
@app.route('/historico=<id_emp>/<dt_ini>/<dt_fim>')
def getFaturamento(id_emp, dt_ini, dt_fim):

    cursor = mydb.cursor()

    #Caso batem na API e esqueçam de por data fim.
    if dt_ini != None and dt_fim == None:
        today = datetime.now()
        dt_fim = str(today.day) + "-" + str(today.month) + "-" + str(today.year)
        
    #Quando a API estiver com todos os dados corretamente inseridos
    if dt_ini and dt_fim != None:
        
        d1 = dt_ini.split("-")
        d2 = dt_fim.split("-")
        dt1 = date(int(d1[2]),int(d1[1]),int(d1[0]))
        dt2 = date(int(d2[2]),int(d2[1]),int(d2[0]))

        #Forma compacta de escrever a query.
        sql  = "SELECT	A.id_hist, B.ds_nome, C.dt_data, C.hr_ini, C.hr_fim, D.ds_nome, E.ds_desc, E.mn_valor, F.ds_status "
        sql += "FROM	tb_historico A, tb_emp B, tb_agenda C, "
        sql +=         "tb_cli D, tb_catserv E, tb_status F "
        sql += "WHERE	A.id_emp = B.id_emp AND A.id_agenda = C.id_agenda AND C.id_cli = D.id_cli "
        sql +=     "AND A.id_ser = E.id_ser AND A.id_status = F.id_status AND A.id_emp = %s "
        sql += "AND C.dt_data >= %s AND C.dt_data <= %s ORDER BY A.id_hist "

        data = (id_emp, dt1, dt2)
        cursor.execute(sql, data)

    else:
        
        sql  = 'SELECT A.id_hist, B.ds_nome, C.dt_data, C.hr_ini, C.hr_fim, D.ds_nome, E.ds_desc, E.mn_valor, F.ds_status '
        sql += 'FROM tb_historico A, tb_emp B, tb_agenda C, '
        sql += 'tb_cli D, tb_catserv E, tb_status F '
        sql += 'WHERE A.id_emp = B.id_emp AND A.id_agenda = C.id_agenda AND C.id_cli = D.id_cli '
        sql += 'AND A.id_ser = E.id_ser AND A.id_status = F.id_status AND A.id_emp = %(id_emp)s ORDER BY A.id_hist '
        sql += 'LIMIT 370 '

        cursor.execute(sql, {'id_emp': id_emp})

    resultado = cursor.fetchall()

    # Se o resultado não for vazio, retornar os dados do usuário em um dicionário
    if resultado:
        itens = list()
        for item in resultado:
            itens.append(
                {     
                    'id_hist': item[0],
                    'nome_empreendedor': item[1],
                    'data_agendada': item[2],
                    'hora_inicio': item[3],
                    'hora_fim': item[4],
                    'cliente': item[5],
                    'servico': item[6],
                    'valor': item[7],
                    'status': item[8]
                }
            )

        return make_response( 
            jsonify(
                mensagem='Seu faturamento',
                dados=itens
            ), 200
        )
    
    else:
        return make_response( 
            jsonify(
                mensagem='Não há faturamento',
            ), 403
        )
    
#METODOS POST - Inserir no banco de dados ou atualizar.
@app.route('/novoEmp=<nome>/<email>/<cnpj>/<nasc>/<tel>/<hash>/<id_adm>', methods=['POST'])
def postNovoEmp(nome,email,cnpj,nasc,tel,hash,id_adm):
    
    d1 = nasc.split("-")
    dt = date(int(d1[2]),int(d1[1]),int(d1[0]))

    cursor = mydb.cursor()

    try:
        
        sql  = "INSERT INTO tb_emp (ds_nome, ds_email, ds_cnpj, dt_nascimento, ds_telefone, ds_senha, id_adm) "
        sql += "VALUES (%s, %s, %s, %s, %s, %s, %s);" 

        data = (nome, email, cnpj, dt, tel, hash, int(id_adm))
        cursor.execute(sql, data)
        mydb.commit()
   
    except Exception as error:

        print(error)
        return make_response( 
            jsonify(
                mensagem= error
            ), 403
        )

    else:        
        return make_response( 
            jsonify(
                mensagem='Empreendedor cadastrado com sucesso'
            ), 200
        )
    

@app.route('/novoCli=<nome>/<email>/<nasc>/<tel>/<id_emp>', methods=['POST'])
def postNovoCli(nome,email,nasc,tel,id_emp):
    
    d1 = nasc.split("-")
    d2 = datetime.now()
    
    dt1 = date(int(d1[2]),int(d1[1]),int(d1[0]))
    dt2 = date(d2.year,d2.month,d2.day)

    cursor = mydb.cursor()

    try:
        
        sql  = "INSERT INTO tb_cli (ds_nome, ds_email, dt_nascimento, dt_cadastro, ds_telefone, id_emp) "
        sql += "VALUES (%s, %s, %s, %s, %s, %s);" 

        data = (nome, email, dt1, dt2, tel, int(id_emp))
        cursor.execute(sql, data)
        mydb.commit()
        
    except Exception as error:

        print(error)
        return make_response( 
            jsonify(
                mensagem= error
            ), 403
        )

    else:        
        return make_response( 
            jsonify(
                mensagem='Cliente cadastrado com sucesso'
            ), 200
        )
    
@app.route('/novoServ=<desc>/<valor>/<id_emp>', methods=['POST'])
def postNovoServico(desc,valor,id_emp):
    
    d1 = datetime.now()
    dt1 = date(d1.year,d1.month,d1.day)

    v1 = Decimal(valor.replace(',','.'))

    cursor = mydb.cursor()

    try:

        sql  = "SELECT ds_codigo FROM tb_catserv WHERE id_emp = %s ORDER BY ds_codigo DESC LIMIT 1"
        cursor.execute(sql, (id_emp, ))
        resultado = cursor.fetchall()
        print(resultado)
        cod = int(resultado[0][0])
        cod += 1
        print(cod)


        sql  = "INSERT INTO tb_catserv (ds_codigo, dt_vig, ds_desc, mn_valor, id_emp) "
        sql += "VALUES (%s, %s, %s, %s, %s);" 

        data = (cod, dt1, desc, v1, int(id_emp))
        cursor.execute(sql, data)
        mydb.commit()
        
    except Exception as error:

        print(error)
        return make_response( 
            jsonify(
                mensagem= error
            ), 403
        )

    else:        
        return make_response( 
            jsonify(
                mensagem='Serviço cadastrado com sucesso'
            ), 200
        )
    
# Complexo registro do agendamento
@app.route('/novaAgenda=<id_emp>/<id_cli>/<dt_agenda>/<hr_ini>/<hr_fim>/<id_ser>', methods=['POST'])
def postNovoAgendamento(id_emp, id_cli, dt_agenda, hr_ini, hr_fim, id_ser):
    
    d1 = dt_agenda.split("-")    
    dt1 = date(int(d1[2]),int(d1[1]),int(d1[0]))

    cursor = mydb.cursor()
    
    try:
        
        #Registro na tb_agenda
        sql  = "INSERT INTO tb_agenda (dt_data, hr_ini, hr_fim, id_emp, id_cli) "
        sql += "VALUES (%s, %s, %s, %s, %s);" 

        data = (dt1, hr_ini, hr_fim, int(id_emp), int(id_cli))
        cursor.execute(sql, data)
        mydb.commit()

        #Cosulta o id_agenda deste ultimo registro
        sql = "SELECT MAX(id_agenda) FROM tb_agenda WHERE id_emp = %s "
        cursor.execute(sql, (id_emp, ))
        resultado = cursor.fetchall()
        id_agenda = resultado[0][0]

        print(id_agenda)

        #Registro na tb_historico
        sql  = "INSERT INTO tb_historico (id_emp, id_agenda, id_ser, id_status) "
        sql += "VALUES (%s, %s, %s, %s);" 
        data = (int(id_emp), int(id_agenda), int(id_ser), 1)
        cursor.execute(sql, data)
        mydb.commit()

    except Exception as error:

        print(error)
        return make_response( 
            jsonify(
                mensagem= error
            ), 403
        )

    else:        
        return make_response( 
            jsonify(
                mensagem='Agendamento cadastrado com sucesso'
            ), 200
        )

# Precificar um serviço existente.    
@app.route('/precificar=<id_ser>/<mn_valor>', methods=['POST'])
def postNovoPreco(id_ser, mn_valor):

    d1 = datetime.now()
    dt1 = date(d1.year,d1.month,d1.day)
    v1 = Decimal(mn_valor.replace(',','.'))

    cursor = mydb.cursor()

    try:
        sql = "SELECT * FROM tb_catserv WHERE id_ser = %s "
        cursor.execute(sql, (id_ser, ))
        resposta = cursor.fetchall()

        codigo = resposta[0][1]
        desc = resposta[0][3]
        id_emp = resposta[0][5]

        sql  = "INSERT INTO tb_catserv (ds_codigo, dt_vig, ds_desc, mn_valor, id_emp) "
        sql += "VALUES(%s, %s, %s, %s, %s) " 
        data = (codigo, dt1, desc, v1, id_emp)
        
        print(data)
        
        cursor.execute(sql, data)
        mydb.commit()
    
    except Exception as error:

        print(error)
        return make_response( 
            jsonify(
                mensagem= error
            ), 403
        )

    else:        
        return make_response( 
            jsonify(
                mensagem='Servico precificado com sucesso!'
            ), 200
        )

#PUT - Atualização de valores
#Atualizar o status de uma atividade
@app.route('/historico=<id_emp>/<id_hist>/<id_status>', methods=['PUT'])
def putStatus(id_emp, id_hist, id_status):
    
    cursor = mydb.cursor()
    
    try:
        #Cosulta o id_agenda deste ultimo registro
        sql = "UPDATE tb_historico SET id_status = %s WHERE id_hist = %s AND id_emp = %s "
        data = (int(id_status), int(id_hist), int(id_emp))
        cursor.execute(sql, data)
        mydb.commit()
    
    except Exception as error:

        print(error)
        return make_response( 
            jsonify(
                mensagem= error
            ), 403
        )
    
    else:        
        return make_response( 
            jsonify(
                mensagem='Serviço atualizado com sucesso!'
            ), 200
        )

# Garante que app sera iniciado quado o escopo "main"
# for empilhado na fila de execução do interpretador
if (__name__ == '__main__'):
    app.run()