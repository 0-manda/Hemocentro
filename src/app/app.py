# vai precisar baixar flask, mysql, mysql.connection, 
from flask import Blueprint, request, jsonify, Flask, render_template
from routes.agendamento_routes import agendamento_bp
from routes.autenticacao_routes import auth_bp
from routes.campanha_routes import campanha_bp
from routes.contato_routes import contato_bp
from routes.estoque_routes import estoque_bp
from routes.hemocentro_routes import hemocentro_bp
from routes.historico_routes import historico_bp
from routes.horario_routes import horario_bp
from routes.notificacao_routes import notificacao_bp
from routes.preferencia_routes import preferencia_bp
from routes.usuario_routes import usuario_bp

app = Flask(__name__)

# ===== CONFIGURAÇÕES =====
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "sua_chave_secreta_aqui"  # útil para JWT ou sessions

# ===== REGISTRO DE BLUEPRINTS =====
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(usuario_bp, url_prefix="/usuario")
app.register_blueprint(hemocentro_bp, url_prefix="/hemocentro")
app.register_blueprint(estoque_bp, url_prefix="/estoque")
app.register_blueprint(campanha_bp, url_prefix="/campanha")
app.register_blueprint(agendamento_bp, url_prefix="/agendamento")
app.register_blueprint(historico_bp, url_prefix="/historico")
app.register_blueprint(notificacao_bp, url_prefix="/notificacao")
app.register_blueprint(preferencia_bp, url_prefix="/preferencia")
app.register_blueprint(horario_bp, url_prefix="/horario")
app.register_blueprint(contato_bp, url_prefix="/contato")

# ===== ROTAS GERAIS =====
@app.route("/")
def homepage():
    return render_template('index.html')

@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "message": "API funcionando!"}), 200

# ===== TRATAMENTO DE ERROS GERAIS =====
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Rota não encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"success": False, "message": "Erro interno no servidor"}), 500

if __name__ == "__main__":
    app.run(debug=True)