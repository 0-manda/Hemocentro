from config.config import get_db_manager
from datetime import datetime
from back.utils.auth_utils import only_numbers, is_cnpj, is_cpf

class AgendamentoModel:
    # ALTER TABLE Agendamento ADD COLUMN tipo_sangue_doado ENUM('sangue_total', 'plaquetas', 'plasma', 'aferese') NOT NULL DEFAULT 'sangue_total';    
    @staticmethod
    def criar(id_usuario, id_hemocentro, data_hora, tipo_sangue_doado='sangue_total',
              id_campanha=None, status='pendente', observacoes=None):
        with get_db_manager() as db:
            if id_campanha:
                tipo_doacao_enum = 'campanha'
            else:
                primeira_vez = AgendamentoModel._verificar_primeira_vez(id_usuario)
                tipo_doacao_enum = 'primeira_vez' if primeira_vez else 'espontanea'
            sql = """
                INSERT INTO Agendamento (
                    id_usuario, id_hemocentro, id_campanha, data_hora, 
                    status, tipo_doacao, tipo_sangue_doado, observacoes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                id_usuario,
                id_hemocentro,
                id_campanha,
                data_hora,
                status,
                tipo_doacao_enum,
                tipo_sangue_doado,
                observacoes
            )
            db.execute(sql, valores)
            agendamento_id = db.lastrowid
            return AgendamentoModel.buscar_por_id(agendamento_id)
    
    @staticmethod
    def _verificar_primeira_vez(id_usuario):
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total 
                FROM Agendamento 
                WHERE id_usuario = %s
            """
            db.execute(sql, (id_usuario,))
            result = db.fetchone()
            return result['total'] == 0 if result else True
    
    @staticmethod
    def buscar_por_id(agendamento_id):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    a.*,
                    u.nome as nome_usuario,
                    u.email as email_usuario,
                    u.tipo_sanguineo as tipo_sanguineo_usuario,
                    h.nome as nome_hemocentro,
                    h.endereco as endereco_hemocentro,
                    h.telefone as telefone_hemocentro,
                    c.nome as nome_campanha
                FROM Agendamento a
                JOIN Usuario u ON a.id_usuario = u.id_usuario
                JOIN Hemocentros h ON a.id_hemocentro = h.id_hemocentro
                LEFT JOIN Campanha c ON a.id_campanha = c.id_campanha
                WHERE a.id_agendamento = %s
            """
            db.execute(sql, (agendamento_id,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def listar_por_usuario(id_usuario, status=None):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    a.*,
                    h.nome as nome_hemocentro,
                    h.endereco as endereco_hemocentro,
                    h.telefone as telefone_hemocentro,
                    c.nome as nome_campanha
                FROM Agendamento a
                JOIN Hemocentros h ON a.id_hemocentro = h.id_hemocentro
                LEFT JOIN Campanha c ON a.id_campanha = c.id_campanha
                WHERE a.id_usuario = %s
            """
            params = [id_usuario]
            if status:
                sql += " AND a.status = %s"
                params.append(status)
            sql += " ORDER BY a.data_hora DESC"
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def listar_todos(status=None, id_hemocentro=None, data_inicio=None):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    a.*,
                    u.nome as nome_usuario,
                    u.email as email_usuario,
                    u.telefone as telefone_usuario,
                    u.tipo_sanguineo as tipo_sanguineo_usuario,
                    h.nome as nome_hemocentro,
                    c.nome as nome_campanha
                FROM Agendamento a
                JOIN Usuario u ON a.id_usuario = u.id_usuario
                JOIN Hemocentros h ON a.id_hemocentro = h.id_hemocentro
                LEFT JOIN Campanha c ON a.id_campanha = c.id_campanha
                WHERE 1=1
            """
            params = []
            if status:
                sql += " AND a.status = %s"
                params.append(status)
            if id_hemocentro:
                sql += " AND a.id_hemocentro = %s"
                params.append(id_hemocentro)
            if data_inicio:
                sql += " AND DATE(a.data_hora) >= %s"
                params.append(data_inicio)
            sql += " ORDER BY a.data_hora DESC"
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def buscar_ultima_doacao_realizada(id_usuario):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Agendamento
                WHERE id_usuario = %s 
                AND status = 'realizado'
                ORDER BY data_hora DESC
                LIMIT 1
            """
            db.execute(sql, (id_usuario,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def atualizar(agendamento_id, campos):
        if not campos:
            return False
        with get_db_manager() as db:
            campos_sql = ', '.join([f"{campo} = %s" for campo in campos.keys()])
            sql = f"""
                UPDATE Agendamento 
                SET {campos_sql}
                WHERE id_agendamento = %s
            """
            valores = list(campos.values()) + [agendamento_id]
            db.execute(sql, tuple(valores))
            return db.rowcount > 0
    
    @staticmethod
    def cancelar(agendamento_id):
        return AgendamentoModel.atualizar(agendamento_id, {'status': 'cancelado'})
    
    @staticmethod
    def confirmar(agendamento_id):
        return AgendamentoModel.atualizar(agendamento_id, {'status': 'confirmado'})
    
    @staticmethod
    def marcar_realizado(agendamento_id):
        return AgendamentoModel.atualizar(agendamento_id, {'status': 'realizado'})
    
    @staticmethod
    def marcar_nao_compareceu(agendamento_id):
        return AgendamentoModel.atualizar(agendamento_id, {'status': 'nao_compareceu'})
    
    @staticmethod
    def contar_por_status(id_usuario=None):
        with get_db_manager() as db:
            sql = """
                SELECT status, COUNT(*) as total 
                FROM Agendamento
            """
            params = []
            if id_usuario:
                sql += " WHERE id_usuario = %s"
                params.append(id_usuario)
            sql += " GROUP BY status"
            db.execute(sql, tuple(params))
            resultados = db.fetchall()
            contagem = {
                'pendente': 0,
                'confirmado': 0,
                'realizado': 0,
                'cancelado': 0,
                'nao_compareceu': 0
            }
            for row in resultados:
                contagem[row['status']] = row['total']
            return contagem
    
    @staticmethod
    def listar_proximos_agendamentos(id_hemocentro=None, dias=7):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    a.*,
                    u.nome as nome_usuario,
                    u.telefone as telefone_usuario,
                    u.tipo_sanguineo as tipo_sanguineo_usuario,
                    h.nome as nome_hemocentro
                FROM Agendamento a
                JOIN Usuario u ON a.id_usuario = u.id_usuario
                JOIN Hemocentros h ON a.id_hemocentro = h.id_hemocentro
                WHERE a.data_hora BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
                AND a.status IN ('pendente', 'confirmado')
            """
            params = [dias]
            if id_hemocentro:
                sql += " AND a.id_hemocentro = %s"
                params.append(id_hemocentro)
            sql += " ORDER BY a.data_hora ASC"
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def deletar(agendamento_id):
        with get_db_manager() as db:
            sql = "DELETE FROM Agendamento WHERE id_agendamento = %s"
            db.execute(sql, (agendamento_id,))
            return db.rowcount > 0
    
    @staticmethod
    def verificar_disponibilidade(id_hemocentro, data_hora):
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total
                FROM Agendamento
                WHERE id_hemocentro = %s
                AND data_hora = %s
                AND status NOT IN ('cancelado', 'nao_compareceu')
            """
            db.execute(sql, (id_hemocentro, data_hora))
            result = db.fetchone()
            return result['total'] == 0 if result else True
    
    @staticmethod
    def contar_agendamentos_dia(id_hemocentro, data):
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total
                FROM Agendamento
                WHERE id_hemocentro = %s
                AND DATE(data_hora) = %s
                AND status IN ('pendente', 'confirmado')
            """
            db.execute(sql, (id_hemocentro, data))
            result = db.fetchone()
            return result['total'] if result else 0
    
    @staticmethod
    def listar_por_campanha(id_campanha):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    a.*,
                    u.nome as nome_usuario,
                    u.email as email_usuario,
                    u.telefone as telefone_usuario,
                    u.tipo_sanguineo as tipo_sanguineo_usuario
                FROM Agendamento a
                JOIN Usuario u ON a.id_usuario = u.id_usuario
                WHERE a.id_campanha = %s
                ORDER BY a.data_hora DESC
            """
            db.execute(sql, (id_campanha,))
            return db.fetchall()
    
    @staticmethod
    def buscar_agendamentos_hoje(id_hemocentro):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    a.*,
                    u.nome as nome_usuario,
                    u.telefone as telefone_usuario,
                    u.tipo_sanguineo as tipo_sanguineo_usuario
                FROM Agendamento a
                JOIN Usuario u ON a.id_usuario = u.id_usuario
                WHERE a.id_hemocentro = %s
                AND DATE(a.data_hora) = CURDATE()
                AND a.status IN ('pendente', 'confirmado')
                ORDER BY a.data_hora ASC
            """
            db.execute(sql, (id_hemocentro,))
            return db.fetchall()

########################################################################

class CampanhaModel:
    @staticmethod
    def criar(id_hemocentro, nome, descricao, data_inicio, data_fim,
              tipo_sanguineo_necessario=None, quantidade_meta_litros=0, 
              objetivo=None, ativa=True, destaque=False):
        with get_db_manager() as db:
            sql = """
                INSERT INTO Campanha (
                    id_hemocentro, nome, descricao, data_inicio, data_fim,
                    tipo_sanguineo_necessario, quantidade_meta_litros, 
                    quantidade_atual_litros, objetivo, ativa, destaque
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                id_hemocentro,
                nome,
                descricao,
                data_inicio,
                data_fim,
                tipo_sanguineo_necessario,
                quantidade_meta_litros,
                0,
                objetivo,
                ativa,
                destaque
            )
            db.execute(sql, valores)
            campanha_id = db.lastrowid
            return CampanhaModel.buscar_por_id(campanha_id)
    
    @staticmethod
    def buscar_por_id(campanha_id):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    c.*,
                    h.nome as nome_hemocentro,
                    h.endereco as endereco_hemocentro,
                    h.cidade,
                    h.estado,
                    h.telefone as telefone_hemocentro,
                    h.email as email_hemocentro
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.id_hemocentro
                WHERE c.id_campanha = %s
            """
            db.execute(sql, (campanha_id,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def listar_ativas(id_hemocentro=None, tipo_sanguineo_necessario=None, 
                      apenas_destaque=False, apenas_ativas=True):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    c.*,
                    h.nome as nome_hemocentro,
                    h.cidade,
                    h.estado,
                    DATEDIFF(c.data_fim, CURDATE()) as dias_restantes
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.id_hemocentro
                WHERE c.data_fim >= CURDATE()
            """
            params = []
            if apenas_ativas:
                sql += " AND c.ativa = TRUE"
            if id_hemocentro:
                sql += " AND c.id_hemocentro = %s"
                params.append(id_hemocentro)
            if tipo_sanguineo_necessario:
                sql += " AND c.tipo_sanguineo_necessario LIKE %s"
                params.append(f"%{tipo_sanguineo_necessario}%")
            if apenas_destaque:
                sql += " AND c.destaque = TRUE"
            sql += " ORDER BY c.destaque DESC, c.data_inicio DESC"
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def listar_todas():
        with get_db_manager() as db:
            sql = """
                SELECT 
                    c.*,
                    h.nome as nome_hemocentro,
                    h.cidade,
                    h.estado,
                    CASE 
                        WHEN c.data_fim < CURDATE() THEN 'Expirada'
                        WHEN c.ativa = FALSE THEN 'Desativada'
                        ELSE 'Ativa'
                    END as status_calculado,
                    DATEDIFF(c.data_fim, CURDATE()) as dias_restantes
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.id_hemocentro
                ORDER BY c.data_criacao DESC
            """
            db.execute(sql)
            return db.fetchall()
    
    @staticmethod
    def listar_por_hemocentro(id_hemocentro, apenas_ativas=False):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    c.*,
                    DATEDIFF(c.data_fim, CURDATE()) as dias_restantes,
                    CASE 
                        WHEN c.data_fim < CURDATE() THEN 'Expirada'
                        WHEN c.ativa = FALSE THEN 'Desativada'
                        ELSE 'Ativa'
                    END as status_calculado
                FROM Campanha c
                WHERE c.id_hemocentro = %s
            """
            params = [id_hemocentro]
            if apenas_ativas:
                sql += " AND c.ativa = TRUE AND c.data_fim >= CURDATE()"
            sql += " ORDER BY c.data_criacao DESC"
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def atualizar(campanha_id, campos):
        if not campos:
            return False
        with get_db_manager() as db:
            set_clause = ", ".join([f"{campo} = %s" for campo in campos.keys()])
            sql = f"""
                UPDATE Campanha 
                SET {set_clause}
                WHERE id_campanha = %s
            """
            valores = list(campos.values()) + [campanha_id]    
            db.execute(sql, tuple(valores))
            return db.rowcount > 0
    
    @staticmethod
    def desativar(campanha_id):
        return CampanhaModel.atualizar(campanha_id, {'ativa': False})
    
    @staticmethod
    def ativar(campanha_id):
        return CampanhaModel.atualizar(campanha_id, {'ativa': True})
    
    @staticmethod
    def incrementar_litros(campanha_id, quantidade_litros=0.45):
        with get_db_manager() as db:
            sql = """
                UPDATE Campanha 
                SET quantidade_atual_litros = quantidade_atual_litros + %s
                WHERE id_campanha = %s
            """
            db.execute(sql, (quantidade_litros, campanha_id))
            return db.rowcount > 0
    
    @staticmethod
    def calcular_progresso(campanha_id):
        campanha = CampanhaModel.buscar_por_id(campanha_id)
        if not campanha:
            return None
        atual = campanha.get('quantidade_atual_litros', 0)
        meta = campanha.get('quantidade_meta_litros', 1)
        percentual = min((atual / meta) * 100, 100) if meta > 0 else 0
        return {
            'quantidade_atual_litros': atual,
            'quantidade_meta_litros': meta,
            'percentual': round(percentual, 2),
            'faltam_litros': max(meta - atual, 0),
            'meta_atingida': atual >= meta
        }
    
    @staticmethod
    def listar_em_destaque(limite=5):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    c.*,
                    h.nome as nome_hemocentro,
                    h.cidade,
                    h.estado,
                    DATEDIFF(c.data_fim, CURDATE()) as dias_restantes
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.id_hemocentro
                WHERE c.ativa = TRUE 
                AND c.destaque = TRUE
                AND c.data_fim >= CURDATE()
                ORDER BY c.data_inicio DESC
                LIMIT %s
            """
            db.execute(sql, (limite,))
            return db.fetchall()
    
    @staticmethod
    def deletar(campanha_id):
        with get_db_manager() as db:
            sql = "DELETE FROM Campanha WHERE id_campanha = %s"
            db.execute(sql, (campanha_id,))
            return db.rowcount > 0
    
    @staticmethod
    def contar_ativas():
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total
                FROM Campanha
                WHERE ativa = TRUE AND data_fim >= CURDATE()
            """
            db.execute(sql)
            result = db.fetchone()
            return result['total'] if result else 0
    
    @staticmethod
    def contar_doacoes_por_campanha(campanha_id):
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total
                FROM HistoricoDoacoes h
                INNER JOIN Agendamento a ON h.id_agendamento = a.id_agendamento
                WHERE a.id_campanha = %s
            """
            db.execute(sql, (campanha_id,))
            result = db.fetchone()
            return result['total'] if result else 0
    
    @staticmethod
    def buscar_campanhas_proximas_vencer(dias=7, limite=10):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    c.*,
                    h.nome as nome_hemocentro,
                    DATEDIFF(c.data_fim, CURDATE()) as dias_restantes
                FROM Campanha c
                INNER JOIN Hemocentros h ON c.id_hemocentro = h.id_hemocentro
                WHERE c.ativa = TRUE
                AND c.data_fim >= CURDATE()
                AND c.data_fim <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
                ORDER BY c.data_fim ASC
                LIMIT %s
            """
            db.execute(sql, (dias, limite))
            return db.fetchall()
        
################################################################################

class EstoqueModel:
    # níveis de estoque:
    # - critico: <= 5 unidades
    # - baixo: 6-15 unidades
    # - normal: 16-30 unidades
    # - bom: > 30 unidades
    @staticmethod
    def adicionar_estoque(id_hemocentro, tipo_sanguineo, quantidade):
        with get_db_manager() as db:
            sql_check = """
                SELECT * FROM Estoque 
                WHERE id_hemocentro = %s AND tipo_sanguineo = %s
            """
            db.execute(sql_check, (id_hemocentro, tipo_sanguineo))
            estoque_existente = db.fetchone()
            if estoque_existente:
                sql_update = """
                    UPDATE Estoque 
                    SET quantidade = quantidade + %s
                    WHERE id_hemocentro = %s AND tipo_sanguineo = %s
                """
                db.execute(sql_update, (quantidade, id_hemocentro, tipo_sanguineo))
            else:
                sql_insert = """
                    INSERT INTO Estoque (id_hemocentro, tipo_sanguineo, quantidade)
                    VALUES (%s, %s, %s)
                """
                db.execute(sql_insert, (id_hemocentro, tipo_sanguineo, quantidade))
            return EstoqueModel.buscar_estoque(id_hemocentro, tipo_sanguineo)
    
    @staticmethod
    def remover_estoque(id_hemocentro, tipo_sanguineo, quantidade):
        with get_db_manager() as db:
            estoque_atual = EstoqueModel.buscar_estoque(id_hemocentro, tipo_sanguineo)
            if not estoque_atual:
                raise ValueError(f"Estoque de {tipo_sanguineo} não encontrado")
            quantidade_disponivel = estoque_atual.get('quantidade', 0)
            if quantidade_disponivel < quantidade:
                raise ValueError(f"Estoque insuficiente. Disponível: {quantidade_disponivel}")
            sql = """
                UPDATE Estoque 
                SET quantidade = quantidade - %s
                WHERE id_hemocentro = %s AND tipo_sanguineo = %s
            """
            db.execute(sql, (quantidade, id_hemocentro, tipo_sanguineo))
            return EstoqueModel.buscar_estoque(id_hemocentro, tipo_sanguineo)
    
    @staticmethod
    def atualizar_quantidade(id_hemocentro, tipo_sanguineo, quantidade):
        with get_db_manager() as db:
            estoque_atual = EstoqueModel.buscar_estoque(id_hemocentro, tipo_sanguineo)
            if estoque_atual:
                sql_update = """
                    UPDATE Estoque 
                    SET quantidade = %s
                    WHERE id_hemocentro = %s AND tipo_sanguineo = %s
                """
                db.execute(sql_update, (quantidade, id_hemocentro, tipo_sanguineo))
            else:
                sql_insert = """
                    INSERT INTO Estoque (id_hemocentro, tipo_sanguineo, quantidade)
                    VALUES (%s, %s, %s)
                """
                db.execute(sql_insert, (id_hemocentro, tipo_sanguineo, quantidade))
            return EstoqueModel.buscar_estoque(id_hemocentro, tipo_sanguineo)
    
    @staticmethod
    def buscar_estoque(id_hemocentro, tipo_sanguineo):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Estoque 
                WHERE id_hemocentro = %s AND tipo_sanguineo = %s
            """
            db.execute(sql, (id_hemocentro, tipo_sanguineo))
            result = db.fetchone()
            if result:
                estoque = dict(result)
                estoque['nivel'] = EstoqueModel._classificar_nivel(estoque['quantidade'])
                return estoque
            return None
    
    @staticmethod
    def listar_estoque_hemocentro(id_hemocentro):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Estoque 
                WHERE id_hemocentro = %s
                ORDER BY tipo_sanguineo
            """
            db.execute(sql, (id_hemocentro,))
            results = db.fetchall()
            estoques = []
            for row in results:
                estoque = dict(row)
                estoque['nivel'] = EstoqueModel._classificar_nivel(estoque['quantidade'])
                estoques.append(estoque)
            return estoques
    
    @staticmethod
    def listar_estoques_criticos(limite_critico=10):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    e.*,
                    h.nome as nome_hemocentro,
                    h.endereco,
                    h.telefone,
                    h.cidade
                FROM Estoque e
                INNER JOIN Hemocentros h ON e.id_hemocentro = h.id_hemocentro
                WHERE e.quantidade <= %s AND h.ativo = TRUE
                ORDER BY e.quantidade ASC
            """
            db.execute(sql, (limite_critico,))
            results = db.fetchall()
            estoques = []
            for row in results:
                estoque = dict(row)
                estoque['nivel'] = 'critico'
                estoques.append(estoque)
            return estoques
    
    @staticmethod
    def _classificar_nivel(quantidade):
        if quantidade <= 5:
            return 'critico'
        elif quantidade <= 15:
            return 'baixo'
        elif quantidade <= 30:
            return 'normal'
        else:
            return 'bom'
    
    @staticmethod
    def contar_criticos(id_hemocentro):
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total
                FROM Estoque
                WHERE id_hemocentro = %s AND quantidade <= 5
            """
            db.execute(sql, (id_hemocentro,))
            result = db.fetchone()
            return result['total'] if result else 0
    
    @staticmethod
    def zerar_tipo(id_hemocentro, tipo_sanguineo):
        estoque_atual = EstoqueModel.buscar_estoque(id_hemocentro, tipo_sanguineo)
        if not estoque_atual or estoque_atual['quantidade'] == 0:
            return False
        EstoqueModel.atualizar_quantidade(
            id_hemocentro=id_hemocentro,
            tipo_sanguineo=tipo_sanguineo,
            quantidade=0
        ) 
        return True
    
    @staticmethod
    def inicializar_estoque_hemocentro(id_hemocentro):
        tipos_sanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        with get_db_manager() as db:
            for tipo in tipos_sanguineos:
                sql_check = """
                    SELECT id_estoque FROM Estoque 
                    WHERE id_hemocentro = %s AND tipo_sanguineo = %s
                """
                db.execute(sql_check, (id_hemocentro, tipo))
                existe = db.fetchone()
                if not existe:
                    sql_insert = """
                        INSERT INTO Estoque (id_hemocentro, tipo_sanguineo, quantidade)
                        VALUES (%s, %s, 0)
                    """
                    db.execute(sql_insert, (id_hemocentro, tipo))
        return True
    
    @staticmethod
    def resumo_estoque(id_hemocentro):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    COUNT(*) as tipos_cadastrados,
                    SUM(quantidade) as total_unidades,
                    SUM(CASE WHEN quantidade <= 5 THEN 1 ELSE 0 END) as criticos,
                    SUM(CASE WHEN quantidade > 5 AND quantidade <= 15 THEN 1 ELSE 0 END) as baixos,
                    SUM(CASE WHEN quantidade > 15 AND quantidade <= 30 THEN 1 ELSE 0 END) as normais,
                    SUM(CASE WHEN quantidade > 30 THEN 1 ELSE 0 END) as bons
                FROM Estoque
                WHERE id_hemocentro = %s
            """
            db.execute(sql, (id_hemocentro,))
            result = db.fetchone()
            if result:
                return {
                    'tipos_cadastrados': result['tipos_cadastrados'],
                    'total_unidades': result['total_unidades'],
                    'por_nivel': {
                        'criticos': result['criticos'],
                        'baixos': result['baixos'],
                        'normais': result['normais'],
                        'bons': result['bons']
                    }
                }
            return {
                'tipos_cadastrados': 0,
                'total_unidades': 0,
                'por_nivel': {
                    'criticos': 0,
                    'baixos': 0,
                    'normais': 0,
                    'bons': 0
                }
            }

#########################################################################################

class HemocentroModel:
    
    @staticmethod
    def criar_hemocentro(nome, cnpj, email, telefone, endereco, cidade='Campinas', 
                        estado='SP', cep=None, site=None):
        #Cria um novo hemocentro (aguarda aprovação)
        if not is_cnpj(cnpj):
            raise ValueError("CNPJ inválido")
        cnpj_limpo = only_numbers(cnpj)
        if HemocentroModel.buscar_por_cnpj(cnpj_limpo):
            raise ValueError(f"CNPJ já cadastrado")
        if HemocentroModel.buscar_por_email(email):
            raise ValueError(f"Email já cadastrado")
        #hemocentro com ativo=False (aguardando aprovação)
        with get_db_manager() as db:
            sql = """
                INSERT INTO Hemocentros (
                    nome, cnpj, email, telefone, endereco, 
                    cidade, estado, cep, site, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                nome, 
                cnpj_limpo, 
                email.lower().strip(), 
                telefone, 
                endereco,
                cidade, 
                estado, 
                cep, 
                site,
                False  # aguardando aprovação
            )
            db.execute(sql, valores)
            hemocentro_id = db.lastrowid
            print(f"[DEBUG] Hemocentro criado com ID: {hemocentro_id}")
            # Buscar dentro do mesmo bloco with
            sql_buscar = "SELECT * FROM Hemocentros WHERE id_hemocentro = %s"
            db.execute(sql_buscar, (hemocentro_id,))
            result = db.fetchone()
            if result:
                print(f"[DEBUG] Hemocentro encontrado!")
                return dict(result)
            else:
                print(f"[DEBUG] Hemocentro NÃO encontrado após inserção!")
                raise ValueError("Erro ao criar hemocentro: não foi possível recuperar os dados após inserção")

    @staticmethod
    def buscar_por_id(hemocentro_id):
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE id_hemocentro = %s"
            db.execute(sql, (hemocentro_id,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_cnpj(cnpj):
        if not cnpj:
            return None
        cnpj_limpo = only_numbers(cnpj)
        if len(cnpj_limpo) != 14:
            return None
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE cnpj = %s"
            db.execute(sql, (cnpj_limpo,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_email(email):
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE email = %s"
            db.execute(sql, (email.lower().strip(),))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def listar_ativos(cidade=None, estado=None, ativo=True):
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros WHERE ativo = %s"
            params = [ativo]
            if cidade:
                sql += " AND cidade = %s"
                params.append(cidade)
            if estado:
                sql += " AND estado = %s"
                params.append(estado)
            sql += " ORDER BY nome"
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def listar_todos():
        with get_db_manager() as db:
            sql = "SELECT * FROM Hemocentros ORDER BY nome"
            db.execute(sql)
            return db.fetchall()
    
    @staticmethod
    def atualizar(cnpj, campos):
        if not campos:
            return False
        if not is_cnpj(cnpj):
            raise ValueError("CNPJ inválido")
        cnpj_limpo = only_numbers(cnpj)
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        if not hemocentro:
            raise ValueError(f"Hemocentro com CNPJ {cnpj_limpo} não encontrado")
        with get_db_manager() as db:
            campos_sql = ', '.join([f"{campo} = %s" for campo in campos.keys()])
            sql = f"UPDATE Hemocentros SET {campos_sql} WHERE cnpj = %s"
            valores = list(campos.values()) + [cnpj_limpo]
            db.execute(sql, tuple(valores))
            return db.rowcount > 0
    
    @staticmethod
    def atualizar_por_id(hemocentro_id, campos):
        if not campos:
            return False
        with get_db_manager() as db:
            campos_sql = ', '.join([f"{campo} = %s" for campo in campos.keys()])
            sql = f"UPDATE Hemocentros SET {campos_sql} WHERE id_hemocentro = %s"
            valores = list(campos.values()) + [hemocentro_id]
            db.execute(sql, tuple(valores))
            return db.rowcount > 0
    
    @staticmethod
    def desativar(cnpj):
        return HemocentroModel.atualizar(cnpj, {'ativo': False})
    
    @staticmethod
    def reativar(cnpj):
        return HemocentroModel.atualizar(cnpj, {'ativo': True})
    
    @staticmethod
    def deletar(cnpj):
        if not is_cnpj(cnpj):
            raise ValueError("CNPJ inválido")
        cnpj_limpo = only_numbers(cnpj)
        with get_db_manager() as db:
            sql = "DELETE FROM Hemocentros WHERE cnpj = %s"
            db.execute(sql, (cnpj_limpo,))
            return db.rowcount > 0
    
    @staticmethod
    def contar_ativos():
        with get_db_manager() as db:
            sql = "SELECT COUNT(*) as total FROM Hemocentros WHERE ativo = TRUE"
            db.execute(sql)
            row = db.fetchone()
            return row['total'] if row else 0
    
    @staticmethod
    def buscar_por_cidade(cidade):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM Hemocentros 
                WHERE cidade = %s AND ativo = TRUE 
                ORDER BY nome
            """
            db.execute(sql, (cidade,))
            return db.fetchall()
    
    @staticmethod
    def verificar_cnpj_existe(cnpj):
        if not is_cnpj(cnpj):
            return False
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        return hemocentro is not None
    
    @staticmethod
    def ativar_por_cnpj(cnpj):
        if not is_cnpj(cnpj):
            raise ValueError("CNPJ inválido")
        cnpj_limpo = only_numbers(cnpj)
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        if not hemocentro:
            raise ValueError("Hemocentro não encontrado")
        return HemocentroModel.reativar(cnpj_limpo)
        
###################################################################################

class HistoricoModel:

    @staticmethod
    def criar(id_usuario, id_hemocentro, id_agendamento, quantidade_ml,
              tipo_doacao, proxima_doacao_permitida, data_doacao, observacoes=None):
        with get_db_manager() as db:
            sql = """
                INSERT INTO HistoricoDoacoes (
                    id_usuario, id_hemocentro, id_agendamento,
                    quantidade_ml, tipo_doacao, observacoes,
                    proxima_doacao_permitida, data_doacao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                id_usuario,
                id_hemocentro,
                id_agendamento,
                quantidade_ml,
                tipo_doacao,
                observacoes,
                proxima_doacao_permitida,
                data_doacao
            )
            db.execute(sql, valores)
            doacao_id = db.lastrowid
            return HistoricoModel.buscar_por_id(doacao_id)
    
    @staticmethod
    def buscar_por_id(doacao_id):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    h.*,
                    u.nome as nome_doador,
                    u.email as email_doador,
                    u.tipo_sanguineo as tipo_sanguineo_doador,
                    hem.nome as nome_hemocentro,
                    hem.endereco as endereco_hemocentro,
                    hem.cidade,
                    hem.estado,
                    a.data_hora as data_agendamento,
                    c.nome as nome_campanha
                FROM HistoricoDoacoes h
                INNER JOIN Usuario u ON h.id_usuario = u.id_usuario
                INNER JOIN Hemocentros hem ON h.id_hemocentro = hem.id_hemocentro
                LEFT JOIN Agendamento a ON h.id_agendamento = a.id_agendamento
                LEFT JOIN Campanha c ON a.id_campanha = c.id_campanha
                WHERE h.id_doacao = %s
            """
            db.execute(sql, (doacao_id,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_agendamento(id_agendamento):
        with get_db_manager() as db:
            sql = """
                SELECT id_doacao FROM HistoricoDoacoes 
                WHERE id_agendamento = %s
            """
            db.execute(sql, (id_agendamento,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def listar_por_usuario(id_usuario):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    h.*,
                    hem.nome as nome_hemocentro,
                    hem.cidade,
                    hem.endereco,
                    c.nome as nome_campanha
                FROM HistoricoDoacoes h
                INNER JOIN Hemocentros hem ON h.id_hemocentro = hem.id_hemocentro
                LEFT JOIN Agendamento a ON h.id_agendamento = a.id_agendamento
                LEFT JOIN Campanha c ON a.id_campanha = c.id_campanha
                WHERE h.id_usuario = %s
                ORDER BY h.data_doacao DESC
            """
            db.execute(sql, (id_usuario,))
            return db.fetchall()
    
    @staticmethod
    def listar_por_hemocentro(id_hemocentro, data_inicio=None, data_fim=None, 
                               tipo_doacao=None, limite=100):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    h.*,
                    u.nome as nome_doador,
                    u.tipo_sanguineo as tipo_sanguineo_doador,
                    u.email as email_doador,
                    c.nome as nome_campanha
                FROM HistoricoDoacoes h
                INNER JOIN Usuario u ON h.id_usuario = u.id_usuario
                LEFT JOIN Agendamento a ON h.id_agendamento = a.id_agendamento
                LEFT JOIN Campanha c ON a.id_campanha = c.id_campanha
                WHERE h.id_hemocentro = %s
            """
            params = [id_hemocentro]
            if data_inicio:
                sql += " AND h.data_doacao >= %s"
                params.append(data_inicio)
            if data_fim:
                sql += " AND h.data_doacao <= %s"
                params.append(data_fim)
            if tipo_doacao:
                sql += " AND h.tipo_doacao = %s"
                params.append(tipo_doacao)
            sql += " ORDER BY h.data_doacao DESC LIMIT %s"
            params.append(limite)
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def estatisticas_hemocentro(id_hemocentro, data_inicio=None):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    COUNT(*) as total_doacoes,
                    SUM(quantidade_ml) as total_ml,
                    AVG(quantidade_ml) as media_ml,
                    COUNT(DISTINCT id_usuario) as total_doadores,
                    tipo_doacao,
                    COUNT(*) as qtd_por_tipo
                FROM HistoricoDoacoes
                WHERE id_hemocentro = %s
            """
            params = [id_hemocentro]
            if data_inicio:
                sql += " AND data_doacao >= %s"
                params.append(data_inicio)
            sql += " GROUP BY tipo_doacao"
            db.execute(sql, tuple(params))
            resultados = db.fetchall()
            stats = {
                'total_doacoes': 0,
                'total_ml': 0,
                'media_ml': 0,
                'total_doadores': 0,
                'por_tipo': {}
            }
            for row in resultados:
                stats['total_doacoes'] += row.get('total_doacoes', 0)
                stats['total_ml'] += row.get('total_ml', 0)
                stats['total_doadores'] = max(stats['total_doadores'], row.get('total_doadores', 0))
                tipo = row.get('tipo_doacao', 'desconhecido')
                stats['por_tipo'][tipo] = {
                    'quantidade': row.get('qtd_por_tipo', 0),
                    'ml_total': row.get('total_ml', 0)
                }
            if stats['total_doacoes'] > 0:
                stats['media_ml'] = stats['total_ml'] / stats['total_doacoes']
            return stats
    
    @staticmethod
    def listar_doadores_frequentes(id_hemocentro, limite=10):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    u.id_usuario,
                    u.nome,
                    u.email,
                    u.tipo_sanguineo,
                    COUNT(h.id_doacao) as total_doacoes,
                    SUM(h.quantidade_ml) as total_ml,
                    MAX(h.data_doacao) as ultima_doacao,
                    MIN(h.data_doacao) as primeira_doacao
                FROM HistoricoDoacoes h
                INNER JOIN Usuario u ON h.id_usuario = u.id_usuario
                WHERE h.id_hemocentro = %s
                GROUP BY u.id_usuario, u.nome, u.email, u.tipo_sanguineo
                ORDER BY total_doacoes DESC
                LIMIT %s
            """
            db.execute(sql, (id_hemocentro, limite))
            return db.fetchall()
    
    @staticmethod
    def listar_campanhas_participadas(id_usuario):
        with get_db_manager() as db:
            sql = """
                SELECT DISTINCT
                    c.id_campanha,
                    c.nome,
                    c.descricao,
                    c.data_inicio,
                    c.data_fim,
                    c.tipo_sanguineo_necessario,
                    h.data_doacao,
                    h.quantidade_ml,
                    h.tipo_doacao,
                    hem.nome as nome_hemocentro
                FROM HistoricoDoacoes h
                INNER JOIN Agendamento a ON h.id_agendamento = a.id_agendamento
                INNER JOIN Campanha c ON a.id_campanha = c.id_campanha
                INNER JOIN Hemocentros hem ON h.id_hemocentro = hem.id_hemocentro
                WHERE h.id_usuario = %s AND a.id_campanha IS NOT NULL
                ORDER BY h.data_doacao DESC
            """
            db.execute(sql, (id_usuario,))
            return db.fetchall()
    
    @staticmethod
    def contar_por_periodo(id_hemocentro, periodo='mes'):
        with get_db_manager() as db:
            if periodo == 'dia':
                group_by = "DATE(data_doacao)"
            elif periodo == 'semana':
                group_by = "YEARWEEK(data_doacao)"
            elif periodo == 'mes':
                group_by = "DATE_FORMAT(data_doacao, '%Y-%m')"
            else:
                group_by = "YEAR(data_doacao)"
            sql = f"""
                SELECT 
                    {group_by} as periodo,
                    COUNT(*) as total,
                    SUM(quantidade_ml) as ml_total
                FROM HistoricoDoacoes
                WHERE id_hemocentro = %s
                GROUP BY {group_by}
                ORDER BY periodo DESC
                LIMIT 12
            """
            db.execute(sql, (id_hemocentro,))
            return db.fetchall()
    
    @staticmethod
    def buscar_ultima_doacao(id_usuario):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM HistoricoDoacoes
                WHERE id_usuario = %s
                ORDER BY data_doacao DESC
                LIMIT 1
            """
            db.execute(sql, (id_usuario,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def deletar(doacao_id):
        with get_db_manager() as db:
            sql = "DELETE FROM HistoricoDoacoes WHERE id_doacao = %s"
            db.execute(sql, (doacao_id,))
            return db.rowcount > 0
    
    @staticmethod
    def total_geral():
        with get_db_manager() as db:
            sql = """
                SELECT 
                    COUNT(*) as total_doacoes,
                    SUM(quantidade_ml) as total_ml,
                    COUNT(DISTINCT id_usuario) as total_doadores,
                    COUNT(DISTINCT id_hemocentro) as total_hemocentros
                FROM HistoricoDoacoes
            """
            db.execute(sql)
            result = db.fetchone()
            return dict(result) if result else {
                'total_doacoes': 0,
                'total_ml': 0,
                'total_doadores': 0,
                'total_hemocentros': 0
            }

#####################################################################################

class HorarioFuncionamentoModel:
    DIAS_VALIDOS = ['domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado']
    @staticmethod
    def validar_dia_semana(dia_semana):
        return dia_semana.lower() in HorarioFuncionamentoModel.DIAS_VALIDOS
    
    @staticmethod
    def criar(id_hemocentro, dia_semana, horario_abertura, horario_fechamento, observacao=None):
        with get_db_manager() as db:
            sql = """
                INSERT INTO HorarioFuncionamento (
                    id_hemocentro, dia_semana, horario_abertura, 
                    horario_fechamento, observacao
                )
                VALUES (%s, %s, %s, %s, %s)
            """
            valores = (
                id_hemocentro,
                dia_semana.lower(),
                horario_abertura,
                horario_fechamento,
                observacao
            )
            db.execute(sql, valores)
            horario_id = db.lastrowid
            return HorarioFuncionamentoModel.buscar_por_id(horario_id)
    
    @staticmethod
    def buscar_por_id(horario_id):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM HorarioFuncionamento 
                WHERE id_horario = %s
            """
            db.execute(sql, (horario_id,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_dia(id_hemocentro, dia_semana):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM HorarioFuncionamento 
                WHERE id_hemocentro = %s AND dia_semana = %s
            """
            db.execute(sql, (id_hemocentro, dia_semana.lower()))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def listar_por_hemocentro(id_hemocentro, incluir_inativos=False):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM HorarioFuncionamento 
                WHERE id_hemocentro = %s
            """
            if not incluir_inativos:
                sql += " AND ativo = TRUE"
            sql += """ 
                ORDER BY 
                    CASE dia_semana
                        WHEN 'domingo' THEN 1
                        WHEN 'segunda' THEN 2
                        WHEN 'terca' THEN 3
                        WHEN 'quarta' THEN 4
                        WHEN 'quinta' THEN 5
                        WHEN 'sexta' THEN 6
                        WHEN 'sabado' THEN 7
                    END
            """
            db.execute(sql, (id_hemocentro,))
            return db.fetchall()
    
    @staticmethod
    def atualizar(horario_id, campos):
        if not campos:
            return False
        if 'dia_semana' in campos:
            campos['dia_semana'] = campos['dia_semana'].lower()
        with get_db_manager() as db:
            set_clause = ", ".join([f"{campo} = %s" for campo in campos.keys()])
            sql = f"""
                UPDATE HorarioFuncionamento 
                SET {set_clause} 
                WHERE id_horario = %s
            """
            valores = list(campos.values()) + [horario_id]
            db.execute(sql, tuple(valores))
            return db.rowcount > 0
    
    @staticmethod
    def deletar(horario_id):
        with get_db_manager() as db:
            sql = "DELETE FROM HorarioFuncionamento WHERE id_horario = %s"
            db.execute(sql, (horario_id,))
            return db.rowcount > 0
    
    @staticmethod
    def desativar(horario_id):
        return HorarioFuncionamentoModel.atualizar(horario_id, {'ativo': False})
    
    @staticmethod
    def ativar(horario_id):
        return HorarioFuncionamentoModel.atualizar(horario_id, {'ativo': True})
    
    @staticmethod
    def listar_por_dia_semana(dia_semana):
        with get_db_manager() as db:
            sql = """
                SELECT 
                    h.id_hemocentro,
                    h.nome as nome_hemocentro,
                    h.cidade,
                    h.endereco,
                    hf.horario_abertura,
                    hf.horario_fechamento,
                    hf.observacao
                FROM HorarioFuncionamento hf
                INNER JOIN Hemocentros h ON hf.id_hemocentro = h.id_hemocentro
                WHERE hf.dia_semana = %s 
                AND hf.ativo = TRUE 
                AND h.ativo = TRUE
                ORDER BY h.nome
            """
            db.execute(sql, (dia_semana.lower(),))
            return db.fetchall()
    
    @staticmethod
    def verificar_conflito(id_hemocentro, dia_semana, horario_abertura, horario_fechamento, excluir_id=None):
        with get_db_manager() as db:
            sql = """
                SELECT id_horario FROM HorarioFuncionamento
                WHERE id_hemocentro = %s 
                AND dia_semana = %s
                AND ativo = TRUE
                AND (
                    (horario_abertura <= %s AND horario_fechamento > %s) OR
                    (horario_abertura < %s AND horario_fechamento >= %s) OR
                    (horario_abertura >= %s AND horario_fechamento <= %s)
                )
            """
            params = [
                id_hemocentro, dia_semana.lower(),
                horario_abertura, horario_abertura,
                horario_fechamento, horario_fechamento,
                horario_abertura, horario_fechamento
            ]
            if excluir_id:
                sql += " AND id_horario != %s"
                params.append(excluir_id)
            db.execute(sql, tuple(params))
            result = db.fetchone()
            return result is not None

###########################################################################################

class PreferenciaModel:
    @staticmethod
    def criar(id_usuario: int, dias_preferencia: list, periodos_preferencia: list) -> dict:
        with get_db_manager() as db:
            sql_check = "SELECT id_preferencia FROM PreferenciaDoacao WHERE id_usuario = %s"
            db.execute(sql_check, (id_usuario,))
        
            if db.fetchone():
                raise ValueError("Usuário já possui preferência cadastrada. Use o método atualizar().")
            dias_str = ','.join(dias_preferencia)
            periodos_str = ','.join(periodos_preferencia)
            sql = """
                INSERT INTO PreferenciaDoacao (id_usuario, dia_preferencia, periodo_preferencia)
                VALUES (%s, %s, %s)
            """
            valores = (id_usuario, dias_str, periodos_str)
            db.execute(sql, valores)
            id_preferencia = db.lastrowid
            return PreferenciaModel.buscar_por_id(id_preferencia)
    
    @staticmethod
    def atualizar(id_usuario: int, dias_preferencia: list, periodos_preferencia: list) -> dict:
        with get_db_manager() as db:
            sql_check = "SELECT id_preferencia FROM PreferenciaDoacao WHERE id_usuario = %s"
            db.execute(sql_check, (id_usuario,))
            resultado = db.fetchone()
            if not resultado:
                raise ValueError("Preferência não encontrada para este usuário.")
            dias_str = ','.join(dias_preferencia)
            periodos_str = ','.join(periodos_preferencia)
            sql = """
                UPDATE PreferenciaDoacao
                SET dia_preferencia = %s,
                    periodo_preferencia = %s
                WHERE id_usuario = %s
            """
            valores = (dias_str, periodos_str, id_usuario)
            db.execute(sql, valores)
            return PreferenciaModel.buscar_por_usuario(id_usuario)
    
    @staticmethod
    def buscar_por_id(id_preferencia: int) -> dict:
        with get_db_manager() as db:
            sql = """
                SELECT 
                    id_preferencia,
                    id_usuario,
                    dia_preferencia,
                    periodo_preferencia,
                    data_atualizacao
                FROM PreferenciaDoacao
                WHERE id_preferencia = %s
            """
            db.execute(sql, (id_preferencia,))
            resultado = db.fetchone()
            if not resultado:
                return None
            return PreferenciaModel._formatar_preferencia(resultado)
    
    @staticmethod
    def buscar_por_usuario(id_usuario: int) -> dict:
        with get_db_manager() as db:
            sql = """
                SELECT 
                    id_preferencia,
                    id_usuario,
                    dia_preferencia,
                    periodo_preferencia,
                    data_atualizacao
                FROM PreferenciaDoacao
                WHERE id_usuario = %s
            """
            db.execute(sql, (id_usuario,))
            resultado = db.fetchone()
            if not resultado:
                return None
            return PreferenciaModel._formatar_preferencia(resultado)
    
    @staticmethod
    def deletar(id_usuario: int) -> bool:
        with get_db_manager() as db:
            sql = "DELETE FROM PreferenciaDoacao WHERE id_usuario = %s"
            db.execute(sql, (id_usuario,))
            return db.rowcount > 0
    
    @staticmethod
    def listar_todas(limite: int = 100, offset: int = 0) -> list:
        with get_db_manager() as db:
            sql = """
                SELECT 
                    id_preferencia,
                    id_usuario,
                    dia_preferencia,
                    periodo_preferencia,
                    data_atualizacao
                FROM PreferenciaDoacao
                ORDER BY data_atualizacao DESC
                LIMIT %s OFFSET %s
            """
            db.execute(sql, (limite, offset))
            resultados = db.fetchall()
            return [PreferenciaModel._formatar_preferencia(row) for row in resultados]
    
    @staticmethod
    def contar_total() -> int:
        with get_db_manager() as db:
            sql = "SELECT COUNT(*) as total FROM PreferenciaDoacao"
            db.execute(sql)
            resultado = db.fetchone()
            return resultado['total'] if resultado else 0
    
    @staticmethod
    def buscar_usuarios_por_dia(dia: str) -> list:
        with get_db_manager() as db:
            sql = """
                SELECT id_usuario
                FROM PreferenciaDoacao
                WHERE FIND_IN_SET(%s, dia_preferencia) > 0
            """
            db.execute(sql, (dia,))
            resultados = db.fetchall()
            return [row['id_usuario'] for row in resultados]
    
    @staticmethod
    def buscar_usuarios_por_periodo(periodo: str) -> list:
        with get_db_manager() as db:
            sql = """
                SELECT id_usuario
                FROM PreferenciaDoacao
                WHERE FIND_IN_SET(%s, periodo_preferencia) > 0
            """
            db.execute(sql, (periodo,))
            resultados = db.fetchall()
            return [row['id_usuario'] for row in resultados]

    @staticmethod
    def buscar_usuarios_compativeis(dia: str, periodo: str) -> list:
        with get_db_manager() as db:
            sql = """
                SELECT 
                    id_preferencia,
                    id_usuario,
                    dia_preferencia,
                    periodo_preferencia,
                    data_atualizacao
                FROM PreferenciaDoacao
                WHERE FIND_IN_SET(%s, dia_preferencia) > 0
                  AND FIND_IN_SET(%s, periodo_preferencia) > 0
            """
            db.execute(sql, (dia, periodo))
            resultados = db.fetchall()
            return [PreferenciaModel._formatar_preferencia(row) for row in resultados]
    
    @staticmethod
    def _formatar_preferencia(row: dict) -> dict:
        if not row:
            return None
        dias_raw = row.get('dia_preferencia', '')
        periodos_raw = row.get('periodo_preferencia', '')
        if isinstance(dias_raw, set):
            dias_list = list(dias_raw)
        elif isinstance(dias_raw, str):
            dias_list = [d.strip() for d in dias_raw.split(',') if d.strip()] if dias_raw else []
        else:
            dias_list = []
        if isinstance(periodos_raw, set):
            periodos_list = list(periodos_raw)
        elif isinstance(periodos_raw, str):
            periodos_list = [p.strip() for p in periodos_raw.split(',') if p.strip()] if periodos_raw else []
        else:
            periodos_list = []
        return {
            'id_preferencia': row.get('id_preferencia'),
            'id_usuario': row.get('id_usuario'),
            'dias_preferencia': dias_list,
            'periodos_preferencia': periodos_list,
            'data_atualizacao': row.get('data_atualizacao').isoformat() if row.get('data_atualizacao') else None
        }

#################################################################################################

class UsuarioModel:
    @staticmethod
    def criar_doador(nome, email, senha_hash, telefone, cpf, data_nascimento=None, tipo_sanguineo=None):
        if not is_cpf(cpf):
            raise ValueError("CPF inválido")
        cpf_limpo = only_numbers(cpf)
        if UsuarioModel.buscar_por_cpf(cpf_limpo):
            raise ValueError("CPF já cadastrado")
        if UsuarioModel.buscar_por_email(email):
            raise ValueError("Email já cadastrado")
        with get_db_manager() as db:
            sql = """
                INSERT INTO Usuario (
                    nome, email, senha, telefone, tipo_usuario,
                    cpf, cnpj, data_nascimento, tipo_sanguineo, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                nome,
                email.lower().strip(),
                senha_hash,
                telefone,
                'doador',           
                cpf_limpo,          
                None,               
                data_nascimento,
                tipo_sanguineo,
                True  # Doadores já entram ativos
            )
            db.execute(sql, valores)
            usuario_id = db.lastrowid
        return UsuarioModel.buscar_por_id(usuario_id)
    
    @staticmethod
    def criar_colaborador(nome, email, senha_hash, telefone, cnpj, cpf=None):
        #validar CNPJ (obrigatório)
        if not is_cnpj(cnpj):
            raise ValueError("CNPJ inválido")
        cnpj_limpo = only_numbers(cnpj)
        # validar e limpar CPF se fornecido (opcional)
        cpf_limpo = None
        if cpf:
            if not is_cpf(cpf):
                raise ValueError("CPF inválido")
            cpf_limpo = only_numbers(cpf)
            #verificar se CPF já existe
            if UsuarioModel.buscar_por_cpf(cpf_limpo):
                raise ValueError("Este CPF já está cadastrado")
        
        # verificar se hemocentro existe e está ativo
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        if not hemocentro:
            raise ValueError("Hemocentro não encontrado")
        if not hemocentro.get('ativo'):
            raise ValueError("Hemocentro ainda não foi aprovado. Aguarde a aprovação para criar colaboradores.")
        
        # verificar duplicidades
        if UsuarioModel.buscar_por_email(email):
            raise ValueError("Email já cadastrado")
        # verificar se já existe colaborador com este CNPJ
        # (permite múltiplos colaboradores do mesmo hemocentro, mas não duplicar email)
        with get_db_manager() as db:
            sql = """
                INSERT INTO Usuario (
                    nome, email, senha, telefone, tipo_usuario,
                    cpf, cnpj, data_nascimento, tipo_sanguineo, ativo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                nome,
                email.lower().strip(),
                senha_hash,
                telefone,
                'colaborador',      
                cpf_limpo,          # CPF opcional
                cnpj_limpo,         # CNPJ obrigatório
                None,
                None,
                False  # colaboradores aguardam aprovação
            )
            db.execute(sql, valores)
            usuario_id = db.lastrowid
        return UsuarioModel.buscar_por_id(usuario_id)
    
    @staticmethod
    def buscar_por_id(usuario_id):
        with get_db_manager() as db:
            sql = "SELECT * FROM Usuario WHERE id_usuario = %s"
            db.execute(sql, (usuario_id,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_email(email):
        with get_db_manager() as db:
            sql = "SELECT * FROM Usuario WHERE email = %s"
            db.execute(sql, (email.lower().strip(),))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_cpf(cpf):
        if not cpf:
            return None
        cpf_limpo = only_numbers(cpf)
        if len(cpf_limpo) != 11:
            return None
        with get_db_manager() as db:
            sql = "SELECT * FROM Usuario WHERE cpf = %s"
            db.execute(sql, (cpf_limpo,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_por_cnpj(cnpj):
        if not cnpj:
            return None
        cnpj_limpo = only_numbers(cnpj)
        if len(cnpj_limpo) != 14:
            return None
        with get_db_manager() as db:
            # retorna o primeiro colaborador deste hemocentro
            sql = "SELECT * FROM Usuario WHERE cnpj = %s AND tipo_usuario = 'colaborador' LIMIT 1"
            db.execute(sql, (cnpj_limpo,))
            result = db.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    def buscar_colaboradores_por_cnpj(cnpj):
        if not cnpj:
            return []
        cnpj_limpo = only_numbers(cnpj)
        if len(cnpj_limpo) != 14:
            return []
        with get_db_manager() as db:
            sql = "SELECT * FROM Usuario WHERE cnpj = %s AND tipo_usuario = 'colaborador'"
            db.execute(sql, (cnpj_limpo,))
            return db.fetchall()
    
    @staticmethod
    def login_por_documento(identificador):
        identificador_limpo = only_numbers(identificador)
        
        if len(identificador_limpo) == 11:
            # CPF: pode ser doador ou colaborador
            return UsuarioModel.buscar_por_cpf(identificador_limpo)
        elif len(identificador_limpo) == 14:
            # CNPJ: busca colaborador
            return UsuarioModel.buscar_por_cnpj(identificador_limpo)
        else:
            return None
    
    @staticmethod
    def atualizar(usuario_id, campos):
        if not campos:
            return False
        
        campos_permitidos = [
            'nome', 'email', 'telefone', 'tipo_sanguineo', 
            'senha', 'data_nascimento', 'ativo'
        ]

        campos_validos = {
            k: v for k, v in campos.items() 
            if k in campos_permitidos
        }

        if not campos_validos:
            return False 
        with get_db_manager() as db:
            campos_sql = ', '.join([f"{campo} = %s" for campo in campos_validos.keys()])
            sql = f"UPDATE Usuario SET {campos_sql} WHERE id_usuario = %s"
            valores = list(campos_validos.values()) + [usuario_id]
            db.execute(sql, tuple(valores))
            return db.rowcount > 0
    
    @staticmethod
    def desativar(usuario_id):
        return UsuarioModel.atualizar(usuario_id, {'ativo': False})
    
    @staticmethod
    def reativar(usuario_id):
        return UsuarioModel.atualizar(usuario_id, {'ativo': True})
    
    @staticmethod
    def listar_todos(tipo_usuario=None, ativo=None):
        with get_db_manager() as db:
            sql = """
                SELECT id_usuario, nome, email, telefone, cpf, cnpj, 
                       tipo_usuario, ativo, data_cadastro 
                FROM Usuario 
                WHERE 1=1
            """
            params = []
            
            if tipo_usuario:
                sql += " AND tipo_usuario = %s"
                params.append(tipo_usuario)
            
            if ativo is not None:
                sql += " AND ativo = %s"
                params.append(ativo)
            
            sql += " ORDER BY data_cadastro DESC"
            
            db.execute(sql, tuple(params))
            return db.fetchall()
    
    @staticmethod
    def listar_doadores(ativo=True):
        return UsuarioModel.listar_todos(tipo_usuario='doador', ativo=ativo)
    
    @staticmethod
    def listar_colaboradores(ativo=True):
        return UsuarioModel.listar_todos(tipo_usuario='colaborador', ativo=ativo)
    
    @staticmethod
    def contar_por_tipo():
        with get_db_manager() as db:
            sql = """
                SELECT tipo_usuario, COUNT(*) as total 
                FROM Usuario 
                WHERE ativo = TRUE
                GROUP BY tipo_usuario
            """
            db.execute(sql)
            resultados = db.fetchall()
            contagem = {'doador': 0, 'colaborador': 0}
            for row in resultados:
                contagem[row['tipo_usuario']] = row['total']
            return contagem
    
    @staticmethod
    def verificar_email_existe(email):
        usuario = UsuarioModel.buscar_por_email(email)
        return usuario is not None
    
    @staticmethod
    def verificar_cpf_existe(cpf):
        if not is_cpf(cpf):
            return False
        usuario = UsuarioModel.buscar_por_cpf(cpf)
        return usuario is not None
    
    @staticmethod
    def verificar_cnpj_existe(cnpj):
        if not is_cnpj(cnpj):
            return False
        # Verifica se existe ALGUM colaborador com este CNPJ
        colaboradores = UsuarioModel.buscar_colaboradores_por_cnpj(cnpj)
        return len(colaboradores) > 0
    
    @staticmethod
    def obter_hemocentro_por_colaborador(usuario_id):
        colaborador = UsuarioModel.buscar_por_id(usuario_id)
        if not colaborador or colaborador['tipo_usuario'] != 'colaborador':
            return None
        cnpj = colaborador.get('cnpj')
        if not cnpj:
            return None
        return HemocentroModel.buscar_por_cnpj(cnpj)
    
    @staticmethod
    def ativar_por_cpf(cpf):
        if not is_cpf(cpf):
            raise ValueError("CPF inválido")
        cpf_limpo = only_numbers(cpf)
        usuario = UsuarioModel.buscar_por_cpf(cpf_limpo)
        if not usuario:
            raise ValueError("Usuário não encontrado")
        return UsuarioModel.reativar(usuario['id_usuario'])

    @staticmethod
    def ativar_por_cnpj(cnpj):
        if not is_cnpj(cnpj):
            raise ValueError("CNPJ inválido")
        cnpj_limpo = only_numbers(cnpj)
        usuario = UsuarioModel.buscar_por_cnpj(cnpj_limpo)
        if not usuario:
            raise ValueError("Colaborador não encontrado")
        return UsuarioModel.reativar(usuario['id_usuario'])
#####################################################################################