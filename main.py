import requests
import oracledb as orcl
import json

# Conectar ao Banco de Dados Oracle
def conectar_BD():
    try:
        str_dados_serv = orcl.makedsn("oracle.fiap.com.br", "1521", "ORCL")
        str_autentic = orcl.connect(user="RM557888", password="021205", dsn=str_dados_serv)
        inst_SQL = str_autentic.cursor()
    except Exception as e:
        print("Erro de conexão: ", e)
        return False, None, None
    return True, inst_SQL, str_autentic
def consulta_tabela(cursor, query, colunas, exportar=False, nome_arquivo="consulta.json"):
    try:
        cursor.execute(query)
        dados = cursor.fetchall()
        registros = [dict(zip(colunas, dado)) for dado in dados]

        # Exibe os dados na tela
        for registro in registros:
            print(registro)

        # Exporta para JSON se solicitado
        if exportar:
            with open(nome_arquivo, 'w') as file:
                json.dump(registros, file, indent=4)
            print(f"Dados exportados para {nome_arquivo}")
    except Exception as e:
        print(f"Erro na consulta: {e}")

# Funções de exportação para JSON
def exportar_clientes(inst_SQL):
    query = "SELECT email, nome, senha, numero, endereco FROM cliente"
    colunas = ["email", "nome", "senha", "numero", "endereco"]
    consulta_tabela(inst_SQL, query, colunas, exportar=True, nome_arquivo="clientes.json")

def exportar_carros_por_cliente(inst_SQL):
    query = "SELECT chassi, marca, modelo, ano, email_cliente FROM carros"
    colunas = ["chassi", "marca", "modelo", "ano", "email_cliente"]
    consulta_tabela(inst_SQL, query, colunas, exportar=True, nome_arquivo="carros_por_cliente.json")


# Função para buscar endereço pelo CEP
def buscar_endereco_por_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    requisicao = requests.get(url)
    if requisicao.status_code == 200:
        return requisicao.json()
    else:
        print("CEP inválido.")
        return None

# CRUD de Clientes
def inserir_cliente(inst_SQL, str_autentic):
    try:
        email = input("Digite o email do cliente: ")
        nome = input("Digite o nome do cliente: ")
        senha = input("Digite a senha do cliente: ")
        telefone = int(input("Digite o telefone: "))
        cep = input("Digite o CEP: ")
        
        # Busca e insere endereço usando ViaCEP
        endereco_data = buscar_endereco_por_cep(cep)
        if endereco_data:
            endereco = f"{endereco_data.get('logradouro', '')}, {endereco_data.get('bairro', '')}, {endereco_data.get('localidade', '')}, {endereco_data.get('uf', '')}"
            
            str_insert = f"""
            INSERT INTO cliente (email, nome, senha, numero, endereco)
            VALUES ('{email}', '{nome}', '{senha}', {telefone}, '{endereco}')
            """
            insert_tabela(inst_SQL, str_autentic, str_insert)
            print("Cliente inserido com sucesso!")
    except ValueError:
        print("Erro: Dados numéricos incorretos.")
    
def alterar_cliente(inst_SQL, str_autentic, email):
    try:
        nome = input("Digite o novo nome do cliente: ")
        telefone = int(input("Digite o novo telefone: "))
        str_update = f"""
        UPDATE cliente SET nome='{nome}', numero={telefone}
        WHERE email='{email}'
        """
        update_tabela(inst_SQL, str_autentic, str_update)
    except ValueError:
        print("Erro: Dados numéricos incorretos.")
        
def excluir_cliente(inst_SQL, str_autentic, email):
    str_delete = f"DELETE FROM cliente WHERE email='{email}'"
    delete_tabela(inst_SQL, str_autentic, str_delete)

def listar_clientes(inst_SQL):
    try:
        str_select = "SELECT * FROM cliente"
        inst_SQL.execute(str_select)
        clientes = inst_SQL.fetchall()
        print("Clientes cadastrados:")
        for cliente in clientes:
            print(f"Email: {cliente[0]}, Nome: {cliente[1]}, Telefone: {cliente[3]}, Endereço: {cliente[4]}")
    except Exception as e:
        print("Erro ao listar clientes: ", e)

# CRUD de Carros
def inserir_carro(inst_SQL, str_autentic):
    try:
        email_cliente = input("Digite o email do cliente: ")
        chassi = input("Digite o número do chassi: ")
        marca = input("Digite a marca: ")
        modelo = input("Digite o modelo: ")
        ano = int(input("Digite o ano de fabricação (AAAA): "))

        str_insert = f"""
        INSERT INTO carros (chassi, marca, modelo, ano, email_cliente)
        VALUES ('{chassi}', '{marca}', '{modelo}', {ano}, '{email_cliente}')
        """
        insert_tabela(inst_SQL, str_autentic, str_insert)
        print("Carro inserido com sucesso!")
    except ValueError:
        print("Erro: Dados numéricos incorretos.")

def alterar_carro(inst_SQL, str_autentic, chassi):
    try:
        marca = input("Digite a nova marca: ")
        modelo = input("Digite o novo modelo: ")
        str_update = f"""
        UPDATE carros SET marca='{marca}', modelo='{modelo}'
        WHERE chassi='{chassi}'
        """
        update_tabela(inst_SQL, str_autentic, str_update)
    except ValueError:
        print("Erro: Dados numéricos incorretos.")

def excluir_carro(inst_SQL, str_autentic, chassi):
    str_delete = f"DELETE FROM carros WHERE chassi='{chassi}'"
    delete_tabela(inst_SQL, str_autentic, str_delete)

def listar_carros_por_cliente(inst_SQL, email_cliente):
    try:
        str_select = f"SELECT * FROM carros WHERE email_cliente='{email_cliente}'"
        inst_SQL.execute(str_select)
        carros = inst_SQL.fetchall()
        if carros:
            print(f"Carros vinculados ao cliente {email_cliente}:")
            for carro in carros:
                print(f"Chassi: {carro[0]}, Marca: {carro[1]}, Modelo: {carro[2]}, Ano: {carro[3]}")
        else:
            print("Nenhum carro encontrado para este cliente.")
    except Exception as e:
        print("Erro ao listar carros: ", e)

# Funções de Inserção, Atualização e Exclusão
def insert_tabela(inst_SQL, str_autentic, str_insert):
    try:
        inst_SQL.execute(str_insert)
        str_autentic.commit()
    except Exception as e:
        print("Erro ao inserir dados: ", e)

def update_tabela(inst_SQL, str_autentic, str_update):
    try:
        inst_SQL.execute(str_update)
        str_autentic.commit()
    except Exception as e:
        print("Erro ao atualizar dados: ", e)

def delete_tabela(inst_SQL, str_autentic, str_delete):
    try:
        inst_SQL.execute(str_delete)
        str_autentic.commit()
    except Exception as e:
        print("Erro ao excluir dados: ", e)

# Menus do sistema
def menu_clientes(inst_SQL, str_autentic):
    while True:
        print("\nMenu de Clientes")
        print("1 - Inserir Cliente")
        print("2 - Alterar Cliente")
        print("3 - Excluir Cliente")
        print("4 - Voltar ao Menu Principal")
        opcao = int(input("Escolha uma opção: "))

        if opcao == 1:
            inserir_cliente(inst_SQL, str_autentic)
        elif opcao == 2:
            email = input("Digite o email do cliente: ")
            alterar_cliente(inst_SQL, str_autentic, email)
        elif opcao == 3:
            email = input("Digite o email do cliente: ")
            excluir_cliente(inst_SQL, str_autentic, email)
        elif opcao == 4:
            break
        else:
            print("Opção inválida!")

def menu_carros(inst_SQL, str_autentic):
    while True:
        print("\nMenu dos Carros")
        print("1 - Inserir Carro")
        print("2 - Alterar Carro")
        print("3 - Excluir Carro")
        print("4 - Voltar ao Menu Principal")
        opcao = int(input("Escolha uma opção: "))

        if opcao == 1:
            inserir_carro(inst_SQL, str_autentic)
        elif opcao == 2:
            chassi = input("Digite o número do chassi do carro: ")
            alterar_carro(inst_SQL, str_autentic, chassi)
        elif opcao == 3:
            chassi = input("Digite o número do chassi do carro: ")
            excluir_carro(inst_SQL, str_autentic, chassi)
        elif opcao == 4:
            break
        else:
            print("Opção inválida!")

            
def main():
    conexao, inst_SQL, str_autentic = conectar_BD()
    if conexao:
        while True:
            print("\nMenu Principal")
            print("1 - Menu de Clientes")
            print("2 - Menu dos Carros")
            print("3 - Listar Todos os Clientes")
            print("4 - Listar Todos os Carros por Cliente")
            print("5 - Exportar Todos os Clientes para JSON")
            print("6 - Exportar Todos os Carros por Cliente para JSON")
            print("7 - Sair")
            opcao = int(input("Escolha uma opção: "))

            if opcao == 1:
                menu_clientes(inst_SQL, str_autentic)
            elif opcao == 2:
                menu_carros(inst_SQL, str_autentic)
            elif opcao == 3:
                listar_clientes(inst_SQL)
            elif opcao == 4:
                email_cliente = input("Digite o email do cliente: ")
                listar_carros_por_cliente(inst_SQL, email_cliente)
            elif opcao == 5:
                exportar_clientes(inst_SQL)
            elif opcao == 6:
                exportar_carros_por_cliente(inst_SQL)
            elif opcao == 7:
                print("Saindo...")
                break
            else:
                print("Opção inválida!")

if __name__ == "_main_":
    main()