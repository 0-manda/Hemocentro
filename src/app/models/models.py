from config.database import get_db_manager
from datetime import datetime
import bcrypt

class UsuarioModel:
    @staticmethod
    def criar_usuario(nome, email, cpf_cnpj, senha, telefone, tipo_usuario, data_nascimento, tipo_sanguineo, ativo):
        with get_db_manager () as db:
            senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            sql = """
                INSERT INTO Usuario (nome, email, cpf_cnpj, senha, telefone, tipo_usuario, data_nascimento, tipo_sanguineo, ativo, data_cadastro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            valores = (nome, email, cpf_cnpj, senha, telefone, tipo_usuario, data_nascimento, tipo_sanguineo, ativo, data_cadastro)
            db.execute(sql, valores)
            return db.lastrowid
    @staticmethod
    def autenticar(cpf_cnpj, senha):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Usuario
                WHERE cpf_cnpj = %s
                """
            resultado = db.execute(sql, (cpf_cnpj,))
            usuario = resultado.fetchone()
            if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha'].encode('utf-8')):
                return usuario
            return None
        
    @staticmethod
    def buscar_por_id(usuario_id):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Usuario
                WHERE usuario_id = %s
                """
            valores = (usuario_id,)
            resultado = db.execute(sql, valores)
            return resultado.fetchone()
        
    @staticmethod
    def buscar_por_email(email):
        """NOVO: Verifica se email já existe"""
        with get_db_manager() as db:
            sql = "SELECT usuario_id FROM Usuario WHERE email = %s"
            resultado = db.execute(sql, (email,))
            return resultado.fetchone()
    
    @staticmethod
    def buscar_por_cpf_cnpj(cpf_cnpj):
        """NOVO: Verifica se CPF/CNPJ já existe"""
        with get_db_manager() as db:
            sql = "SELECT usuario_id FROM Usuario WHERE cpf_cnpj = %s"
            resultado = db.execute(sql, (cpf_cnpj,))
            return resultado.fetchone()
    
    @staticmethod
    def atualizar_senha(usuario_id, senha_nova):
        """NOVO: Atualiza senha do usuário"""
        with get_db_manager() as db:
            senha_hash = bcrypt.hashpw(senha_nova.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            sql = "UPDATE Usuario SET senha = %s WHERE usuario_id = %s"
            db.execute(sql, (senha_hash, usuario_id))
        return db.rowcount
            
class HemocentroModel:
    @staticmethod
    def criar_hemocentro(nome, email, telefone, endereco, cidade, estado, cep, site, data_cadastro, ativo, cnpj):
        with get_db_manager() as db:
            sql = """
                INSERT INTO Hemocentros (nome, email, telefone, endereco, cidade, estado, cep, site, data_cadastro, ativo, cnpj)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            valores = (nome, email, telefone, endereco, cidade, estado, cep, site, data_cadastro, ativo, cnpj)
            db.execute(sql, valores)
            return db.lastrowid
    
    @staticmethod
    def buscar_por_cnpj(cnpj):
        """NOVO: Busca hemocentro por CNPJ"""
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE cnpj = %s"
            resultado = db.execute(sql, (cnpj,))
            return resultado.fetchone()
    
    @staticmethod
    def buscar_por_id(hemocentro_id):
        """NOVO: Busca hemocentro por ID (você provavelmente não tinha)"""
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE hemocentro_id = %s"
            resultado = db.execute(sql, (hemocentro_id,))
            return resultado.fetchone()
    @staticmethod
    def listar_ativos(cidade=None, estado=None):
        """NOVO: Lista hemocentros ativos com filtros"""
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE ativo = TRUE"
            params = []
            
            if cidade:
                sql += " AND cidade = %s"
                params.append(cidade)
            
            if estado:
                sql += " AND estado = %s"
                params.append(estado)
            
            sql += " ORDER BY nome"
            
            resultado = db.execute(sql, tuple(params))
            return resultado.fetchall()
    
    @staticmethod
    def atualizar(hemocentro_id, campos):
        """NOVO: Atualiza campos do hemocentro"""
        with get_db_manager() as db:
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE Hemocentros SET {set_clause} WHERE hemocentro_id = %s"
            valores = list(campos.values()) + [hemocentro_id]
            db.execute(sql, tuple(valores))
        return db.rowcount
    
class HorarioFuncionamentoModel:
    @staticmethod
    def criar_horario(id_hemocentro, dia_semana, horario_abertura, horario_fechamento, observacao, ativo):
        with get_db_manager() as db:
            sql = """
                INSERT INTO HorarioFuncionamento (id_hemocentro, dia_semana, horario_abertura, horario_fechamento, observacao, ativo)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
            valores = (id_hemocentro, dia_semana, horario_abertura, horario_fechamento, observacao, ativo)
            db.execute(sql, valores)
            return db.lastrowid
    @staticmethod
    def buscar_por_hemocentro_e_dia(id_hemocentro, dia_semana):
        """NOVO: Verifica se já existe horário para este dia"""
        with get_db_manager() as db:
            sql = """
                SELECT * FROM HorarioFuncionamento 
                WHERE id_hemocentro = %s AND dia_semana = %s
            """
            resultado = db.execute(sql, (id_hemocentro, dia_semana))
            return resultado.fetchone()
    
    @staticmethod
    def listar_por_hemocentro(id_hemocentro, incluir_inativos=False):
        """NOVO: Lista horários do hemocentro"""
        with get_db_manager() as db:
            sql = """
                SELECT * FROM HorarioFuncionamento 
                WHERE id_hemocentro = %s
            """
            
            if not incluir_inativos:
                sql += " AND ativo = TRUE"
            
            sql += " ORDER BY dia_semana"
            
            resultado = db.execute(sql, (id_hemocentro,))
            return resultado.fetchall()
    
    @staticmethod
    def buscar_por_id(horario_id):
        """NOVO: Busca horário por ID"""
        with get_db_manager() as db:
            sql = "SELECT * FROM HorarioFuncionamento WHERE horario_id = %s"
            resultado = db.execute(sql, (horario_id,))
            return resultado.fetchone()
    
    @staticmethod
    def atualizar(horario_id, campos):
        """NOVO: Atualiza campos do horário"""
        with get_db_manager() as db:
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE HorarioFuncionamento SET {set_clause} WHERE horario_id = %s"
            valores = list(campos.values()) + [horario_id]
            db.execute(sql, tuple(valores))
        return db.rowcount
    
    @staticmethod
    def deletar(horario_id):
        """NOVO: Deleta horário"""
        with get_db_manager() as db:
            sql = "DELETE FROM HorarioFuncionamento WHERE horario_id = %s"
            db.execute(sql, (horario_id,))
        
class EstoqueModel:
    @staticmethod
    def adicionar_estoque(hemocentro_id, tipo_sanguineo, quantidade):
        """Adiciona quantidade ao estoque (cria ou atualiza)"""
        with get_db_manager() as db:
            # Verificar se já existe registro
            sql_check = """
                SELECT * FROM Estoque 
                WHERE hemocentro_id = %s AND tipo_sanguineo = %s
            """
            estoque_existente = db.fetchone(sql_check, (hemocentro_id, tipo_sanguineo))
            
            if estoque_existente:
                # Atualizar estoque existente
                sql_update = """
                    UPDATE Estoque 
                    SET quantidade = quantidade + %s, data_atualizacao = %s
                    WHERE hemocentro_id = %s AND tipo_sanguineo = %s
                """
                db.execute(sql_update, (quantidade, datetime.now(), hemocentro_id, tipo_sanguineo))
            else:
                # Criar novo registro
                sql_insert = """
                    INSERT INTO Estoque (hemocentro_id, tipo_sanguineo, quantidade, data_criacao, data_atualizacao)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db.execute(sql_insert, (hemocentro_id, tipo_sanguineo, quantidade, datetime.now(), datetime.now()))
            
            # Registrar no histórico
            EstoqueModel._registrar_historico(hemocentro_id, tipo_sanguineo, quantidade, 'entrada', 'doacao')
            
            # Retornar estoque atualizado
            return EstoqueModel.buscar_estoque(hemocentro_id, tipo_sanguineo)
    
    @staticmethod
    def remover_estoque(hemocentro_id, tipo_sanguineo, quantidade, motivo='uso'):
        """Remove quantidade do estoque"""
        with get_db_manager() as db:
            sql = """
                UPDATE Estoque 
                SET quantidade = quantidade - %s, data_atualizacao = %s
                WHERE hemocentro_id = %s AND tipo_sanguineo = %s AND quantidade >= %s
            """
            db.execute(sql, (quantidade, datetime.now(), hemocentro_id, tipo_sanguineo, quantidade))
            
            # Registrar no histórico
            EstoqueModel._registrar_historico(hemocentro_id, tipo_sanguineo, quantidade, 'saida', motivo)
            
            return EstoqueModel.buscar_estoque(hemocentro_id, tipo_sanguineo)
    
    @staticmethod
    def listar_estoque_hemocentro(hemocentro_id):
        """Lista todo o estoque de um hemocentro"""
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Estoque 
                WHERE hemocentro_id = %s
                ORDER BY tipo_sanguineo
            """
            results = db.fetchall(sql, (hemocentro_id,))
            
            estoques = []
            for row in results:
                estoques.append({
                    'tipo_sanguineo': row['tipo_sanguineo'],
                    'quantidade': row['quantidade'],
                    'data_atualizacao': row['data_atualizacao'],
                    'nivel': EstoqueModel._classificar_nivel(row['quantidade'])
                })
            
            return estoques
    
    @staticmethod
    def listar_estoques_criticos(limite_critico=10):
        """Lista estoques abaixo do limite crítico"""
        with get_db_manager() as db:
            sql = """
                SELECT e.*, h.nome as nome_hemocentro, h.endereco, h.telefone
                FROM Estoque e
                INNER JOIN Hemocentro h ON e.hemocentro_id = h.id
                WHERE e.quantidade <= %s AND h.ativo = 1
                ORDER BY e.quantidade ASC
            """
            results = db.fetchall(sql, (limite_critico,))
            
            estoques = []
            for row in results:
                estoques.append({
                    'hemocentro_id': row['hemocentro_id'],
                    'nome_hemocentro': row['nome_hemocentro'],
                    'endereco': row['endereco'],
                    'telefone': row['telefone'],
                    'tipo_sanguineo': row['tipo_sanguineo'],
                    'quantidade': row['quantidade'],
                    'nivel': 'CRÍTICO'
                })
            
            return estoques
    
    @staticmethod
    def _classificar_nivel(quantidade):
        """Classifica nível do estoque"""
        if quantidade <= 5:
            return 'CRÍTICO'
        elif quantidade <= 15:
            return 'BAIXO'
        elif quantidade <= 30:
            return 'NORMAL'
        else:
            return 'BOM'

class CampanhaModel:
    @staticmethod
    def criar_campanha(id_hemocentro, nome, descricao, data_inicio, data_fim, tipo_sanguineo_necessario, quantidade_meta, quantidade_atual, objetivo_campanha, ativa, destaque, data_criacao):
        with get_db_manager() as db:
            sql = """
                INSERT INTO Campanha (id_hemocentro, nome, descricao, data_inicio, data_fim, tipo_sanguineo_necessario, quantidade_meta, quantidade_atual, objetivo_campanha, ativa, destaque, data_criacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            valores = (id_hemocentro, nome, descricao, data_inicio, data_fim, tipo_sanguineo_necessario, quantidade_meta, quantidade_atual, objetivo_campanha, ativa, destaque, data_criacao)
            db.execute(sql, valores)
            return db.lastrowid
    
    @staticmethod
    def listar_ativas(hemocentro_id=None, tipo_sanguineo=None, apenas_destaque=False):
        """NOVO: Lista campanhas ativas com filtros opcionais"""
        with get_db_manager() as db:
            sql = """
                SELECT c.*, h.nome as hemocentro_nome, h.cidade, h.estado
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.hemocentro_id
                WHERE c.ativa = TRUE AND c.data_fim >= CURDATE()
            """
            params = []
            
            if hemocentro_id:
                sql += " AND c.id_hemocentro = %s"
                params.append(hemocentro_id)
            
            if tipo_sanguineo:
                sql += " AND (c.tipo_sanguineo_necessario = %s OR c.tipo_sanguineo_necessario = 'Todos')"
                params.append(tipo_sanguineo)
            
            if apenas_destaque:
                sql += " AND c.destaque = TRUE"
            
            sql += " ORDER BY c.destaque DESC, c.data_inicio DESC"
            
            resultado = db.execute(sql, tuple(params))
            return resultado.fetchall()
    
    @staticmethod
    def buscar_por_id(campanha_id):
        """NOVO: Busca campanha por ID"""
        with get_db_manager() as db:
            sql = """
                SELECT c.*, h.nome as hemocentro_nome, h.endereco, h.cidade, h.estado, h.telefone
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.hemocentro_id
                WHERE c.campanha_id = %s
            """
            resultado = db.execute(sql, (campanha_id,))
            return resultado.fetchone()
    
    @staticmethod
    def listar_por_hemocentro(hemocentro_id):
        """NOVO: Lista todas as campanhas de um hemocentro (ativas e inativas)"""
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Campanha
                WHERE id_hemocentro = %s
                ORDER BY data_criacao DESC
            """
            resultado = db.execute(sql, (hemocentro_id,))
            return resultado.fetchall()
    
    @staticmethod
    def atualizar(campanha_id, campos):
        """NOVO: Atualiza campos específicos da campanha"""
        with get_db_manager() as db:
            # Constrói UPDATE dinamicamente
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            sql = f"UPDATE Campanha SET {set_clause} WHERE campanha_id = %s"
            valores = list(campos.values()) + [campanha_id]
            db.execute(sql, tuple(valores))
        return db.rowcount
    
    @staticmethod
    def desativar(campanha_id):
        """NOVO: Desativa campanha (soft delete)"""
        with get_db_manager() as db:
            sql = "UPDATE Campanha SET ativa = FALSE WHERE campanha_id = %s"
            db.execute(sql, (campanha_id,))
        
class AgendamentoModel:
    @staticmethod
    def criar_agendamento(id_usuario, id_campanha, id_hemocentro, data_hora, status, tipo_doacao, observacoes, data_criacao, data_atualizacao):
        with get_db_manager() as db:
            sql = """
                INSERT INTO Agendamento (id_usuario, id_campanha, id_hemocentro, data_hora, status, tipo_doacao, observacoes, data_criacao, data_atualizacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            valores = (id_usuario, id_campanha, id_hemocentro, data_hora, status, tipo_doacao, observacoes, data_criacao, data_atualizacao)
            db.execute(sql, valores)
            return db.lastrowid
    @staticmethod
    def atualizar_agendamento(agendamento_id, dados):
        """Atualiza campos de um agendamento"""
        with get_db_manager() as db:
            # Construir SQL dinamicamente baseado nos campos fornecidos
            campos = []
            valores = []
            
            for campo, valor in dados.items():
                campos.append(f"{campo} = %s")
                valores.append(valor)
            
            # Adicionar data_atualizacao
            campos.append("data_atualizacao = %s")
            valores.append(datetime.now())
            
            # Adicionar ID no final
            valores.append(agendamento_id)
            
            sql = f"""
                UPDATE Agendamento 
                SET {', '.join(campos)}
                WHERE id_agendamento = %s
            """
            
            db.execute(sql, tuple(valores))
            
            # Retornar agendamento atualizado
            return AgendamentoModel.buscar_por_id(agendamento_id)
    
    
    @staticmethod
    def cancelar_agendamento(agendamento_id):
        """Cancela um agendamento (muda status para 'cancelado')"""
        with get_db_manager() as db:
            sql = """
                UPDATE Agendamento 
                SET status = 'cancelado', data_atualizacao = %s
                WHERE id_agendamento = %s
            """
            db.execute(sql, (datetime.now(), agendamento_id))
    
    
    @staticmethod
    def atualizar_status(agendamento_id, status):
        """Atualiza apenas o status do agendamento"""
        with get_db_manager() as db:
            sql = """
                UPDATE Agendamento 
                SET status = %s, data_atualizacao = %s
                WHERE id_agendamento = %s
            """
            db.execute(sql, (status, datetime.now(), agendamento_id))
        return db.rowcount

class HistoricoModel:
    @staticmethod
    def historico_doacao(id_usuario, id_hemocentro, id_agendamento, data_doacao, quantidade_ml, tipo_doacao, observacoes, proxima_doacao_permitida, data_registro):
        with get_db_manager() as db:
            sql = """
                INSERT INTO HistoricoDoacoes (id_usuario, id_hemocentro, id_agendamento, data_doacao, quantidade_ml, tipo_doacao, observacoes, proxima_doacao_permitida, data_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            valores = (id_usuario, id_hemocentro, id_agendamento, data_doacao, quantidade_ml, tipo_doacao, observacoes, proxima_doacao_permitida, data_registro)
            db.execute(sql, valores)
            return db.lastrowid
    @staticmethod
    def buscar_por_agendamento(id_agendamento):
        """NOVO: Verifica se já existe doação para este agendamento"""
        with get_db_manager() as db:
            sql = "SELECT historico_id FROM HistoricoDoacoes WHERE id_agendamento = %s"
            resultado = db.execute(sql, (id_agendamento,))
            return resultado.fetchone()
    
    @staticmethod
    def listar_por_usuario(id_usuario):
        """NOVO: Lista histórico de doações do usuário"""
        with get_db_manager() as db:
            sql = """
                SELECT h.*, hem.nome as hemocentro_nome, hem.cidade
                FROM HistoricoDoacoes h
                INNER JOIN Hemocentros hem ON h.id_hemocentro = hem.hemocentro_id
                WHERE h.id_usuario = %s
                ORDER BY h.data_doacao DESC
            """
            resultado = db.execute(sql, (id_usuario,))
            return resultado.fetchall()
    
    @staticmethod
    def listar_por_hemocentro(hemocentro_id, data_inicio=None, data_fim=None, tipo_doacao=None):
        """NOVO: Lista doações recebidas pelo hemocentro"""
        with get_db_manager() as db:
            sql = """
                SELECT h.*, u.nome as doador_nome, u.tipo_sanguineo
                FROM HistoricoDoacoes h
                INNER JOIN Usuario u ON h.id_usuario = u.usuario_id
                WHERE h.id_hemocentro = %s
            """
            params = [hemocentro_id]
            
            if data_inicio:
                sql += " AND h.data_doacao >= %s"
                params.append(data_inicio)
            
            if data_fim:
                sql += " AND h.data_doacao <= %s"
                params.append(data_fim)
            
            if tipo_doacao:
                sql += " AND h.tipo_doacao = %s"
                params.append(tipo_doacao)
            
            sql += " ORDER BY h.data_doacao DESC"
            
            resultado = db.execute(sql, tuple(params))
            return resultado.fetchall()
    
    @staticmethod
    def buscar_por_id(historico_id):
        """NOVO: Busca doação por ID"""
        with get_db_manager() as db:
            sql = """
                SELECT h.*, 
                       u.nome as doador_nome, u.tipo_sanguineo,
                       hem.nome as hemocentro_nome
                FROM HistoricoDoacoes h
                INNER JOIN Usuario u ON h.id_usuario = u.usuario_id
                INNER JOIN Hemocentros hem ON h.id_hemocentro = hem.hemocentro_id
                WHERE h.historico_id = %s
            """
            resultado = db.execute(sql, (historico_id,))
            return resultado.fetchone()
        
class NotificacaoModel:
    @staticmethod
    def criar_notificacao(id_usuario, id_campanha, tipo, assunto, mensagem, enviado, data_agendamento, data_envio):
        with get_db_manager() as db:
            sql = """
                INSERT INTO Notificacao (id_usuario, id_campanha, tipo, assunto, mensagem, enviado, data_agendamento, data_envio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
            valores = (id_usuario, id_campanha, tipo, assunto, mensagem, enviado, data_agendamento, data_envio)
            db.execute(sql, valores)
            return db.lastrowid

class PreferenciaModel:
    @staticmethod
    def criar_preferencia(id_usuario, dia_preferencia, periodo_preferencia, data_atualizacao):
        with get_db_manager() as db:
            sql = """
                INSERT INTO PreferenciaDoacao (id_usuario, dia_preferencia, periodo_preferencia, data_atualizacao)
                VALUES (%s, %s, %s, %s)
                """
            valores = (id_usuario, dia_preferencia, periodo_preferencia, data_atualizacao)
            db.execute(sql, valores)
            return db.lastrowid

class ContatoModel:
    @staticmethod
    def criar_contato(nome, email, mensagem, id_hemocentro, data_envio):
        with get_db_manager() as db:
            sql = """
                INSERT INTO Contato (nome, email, mensagem, id_hemocentro, data_envio)
                VALUES (%s, %s, %s, %s, %s)
                """
            valores = (nome, email, mensagem, id_hemocentro, data_envio)
            db.execute(sql, valores)
            return db.lastrowid
    # Em models.py

    @staticmethod
    def listar_por_hemocentro(hemocentro_id, lida=None, limite=50):
        """NOVO: Lista contatos do hemocentro com filtros"""
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Contato
                WHERE id_hemocentro = %s
            """
            params = [hemocentro_id]
            
            # Filtro de lida/não lida
            if lida is not None:
                lida_bool = lida.lower() == 'true' if isinstance(lida, str) else lida
                sql += " AND lida = %s"
                params.append(lida_bool)
            
            sql += " ORDER BY data_envio DESC LIMIT %s"
            params.append(limite)
            
            resultado = db.execute(sql, tuple(params))
            return resultado.fetchall()
    
    @staticmethod
    def buscar_por_id(contato_id):
        """NOVO: Busca contato por ID"""
        with get_db_manager() as db:
            sql = "SELECT * FROM Contato WHERE contato_id = %s"
            resultado = db.execute(sql, (contato_id,))
            return resultado.fetchone()
    
    @staticmethod
    def contar_nao_lidas(hemocentro_id):
        """NOVO: Conta mensagens não lidas"""
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total
                FROM Contato
                WHERE id_hemocentro = %s AND lida = FALSE
            """
            resultado = db.execute(sql, (hemocentro_id,))
            row = resultado.fetchone()
            return row['total'] if row else 0
    
    @staticmethod
    def marcar_como_lida(contato_id):
        """NOVO: Marca contato como lido"""
        with get_db_manager() as db:
            sql = """
                UPDATE Contato 
                SET lida = TRUE, data_leitura = %s
                WHERE contato_id = %s
            """
            db.execute(sql, (datetime.now(), contato_id))
    
    @staticmethod
    def deletar(contato_id):
        """NOVO: Deleta contato permanentemente"""
        with get_db_manager() as db:
            sql = "DELETE FROM Contato WHERE contato_id = %s"
            db.execute(sql, (contato_id,))
    
    @staticmethod
    def obter_estatisticas(hemocentro_id):
        """NOVO: Estatísticas de contatos"""
        with get_db_manager() as db:
            sql = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN lida = FALSE THEN 1 ELSE 0 END) as nao_lidas,
                    SUM(CASE WHEN lida = TRUE THEN 1 ELSE 0 END) as lidas,
                    COUNT(CASE WHEN DATE(data_envio) = CURDATE() THEN 1 END) as hoje,
                    COUNT(CASE WHEN data_envio >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as ultimos_7_dias
                FROM Contato
                WHERE id_hemocentro = %s
            """
            resultado = db.execute(sql, (hemocentro_id,))
            return resultado.fetchone()