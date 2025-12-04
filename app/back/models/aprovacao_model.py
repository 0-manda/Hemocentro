from config.config import get_db_manager
from datetime import datetime, timedelta

class AprovacaoModel:
    #Cria um token de aprovação retorna o ID do token criado
    @staticmethod
    def criar_token(tipo, id_entidade, token):
        with get_db_manager() as db:
            sql = """
                INSERT INTO AprovacaoTokens (tipo, id_entidade, token, status, data_criacao)
                VALUES (%s, %s, %s, 'pendente', NOW())
            """
            db.execute(sql, (tipo, id_entidade, token))
            return db.lastrowid
    
    #Busca informações de um token de aprovação retorna info do token ou none se não encontrado
    @staticmethod
    def buscar_por_token(token):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM AprovacaoTokens
                WHERE token = %s
            """
            db.execute(sql, (token,))
            result = db.fetchone()
            return dict(result) if result else None
    
    #Valida se um token existe, está pendente e não venceu (7 dias) retorna info do token ou none
    @staticmethod
    def validar_token(token):
        token_info = AprovacaoModel.buscar_por_token(token)
        if not token_info:
            return None
        if token_info['status'] != 'pendente':
            return None
        data_criacao = token_info['data_criacao']
        if isinstance(data_criacao, str):
            data_criacao = datetime.fromisoformat(data_criacao)
        data_expiracao = data_criacao + timedelta(days=7)
        if datetime.now() > data_expiracao:
            return None
        return token_info
    
    #Marca um token como aprovado retorna True se atualizado
    @staticmethod
    def marcar_como_aprovado(token):
        with get_db_manager() as db:
            sql = """
                UPDATE AprovacaoTokens
                SET status = 'aprovado', data_processamento = NOW()
                WHERE token = %s AND status = 'pendente'
            """
            db.execute(sql, (token,))
            return db.rowcount > 0
    
    #marca um token como rejeitado retorna True se atualizado
    @staticmethod
    def marcar_como_rejeitado(token):
        with get_db_manager() as db:
            sql = """
                UPDATE AprovacaoTokens
                SET status = 'rejeitado', data_processamento = NOW()
                WHERE token = %s AND status = 'pendente'
            """
            db.execute(sql, (token,))
            return db.rowcount > 0
    
    @staticmethod
    def listar_pendentes():
        with get_db_manager() as db:
            sql = """
                SELECT * FROM AprovacaoTokens
                WHERE status = 'pendente'
                ORDER BY data_criacao DESC
            """
            db.execute(sql)
            return db.fetchall()
    
    @staticmethod
    def buscar_por_entidade(tipo, id_entidade):
        with get_db_manager() as db:
            sql = """
                SELECT * FROM AprovacaoTokens
                WHERE tipo = %s AND id_entidade = %s
                ORDER BY data_criacao DESC
            """
            db.execute(sql, (tipo, id_entidade))
            return db.fetchall()
    
    @staticmethod
    def tem_token_pendente(tipo, id_entidade):
        with get_db_manager() as db:
            sql = """
                SELECT COUNT(*) as total FROM AprovacaoTokens
                WHERE tipo = %s AND id_entidade = %s AND status = 'pendente'
            """
            db.execute(sql, (tipo, id_entidade))
            result = db.fetchone()
            return result['total'] > 0 if result else False
    
    @staticmethod
    def limpar_tokens_expirados():
        with get_db_manager() as db:
            sql = """
                DELETE FROM AprovacaoTokens
                WHERE data_criacao < DATE_SUB(NOW(), INTERVAL 30 DAY)
            """
            db.execute(sql)
            return db.rowcount