import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv
from config.config import Config

#importa os blueprints
from back.routes.usuario_routes import usuario_bp
from back.routes.hemocentro_routes import hemocentro_bp
from back.routes.estoque_routes import estoque_bp
from back.routes.campanha_routes import campanha_bp
from back.routes.agendamento_routes import agendamento_bp
from back.routes.historico_routes import historico_bp
from back.routes.horario_routes import horario_bp
from back.routes.preferencia_routes import preferencia_bp
from back.routes.aprovacao_routes import aprovacao_bp
#from back.routes.contato_routes import contato_bp

#carrega variáveis de ambiente
load_dotenv()

#inicializa o flask (configura pastas do front-end)
app = Flask(
    __name__,
    template_folder='front/templates',
    static_folder='front/static',
    static_url_path='/static'
)

#configs
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "chave insegura para desenvolvimento")

#CORS SIMPLES permite todas as origens em desenvolvimento configurar origins específicas em produção
CORS(app)

# registro dos blueprints
app.register_blueprint(usuario_bp, url_prefix="/api")
app.register_blueprint(hemocentro_bp, url_prefix="/api")
app.register_blueprint(estoque_bp, url_prefix="/api")
app.register_blueprint(campanha_bp, url_prefix="/api")
app.register_blueprint(agendamento_bp, url_prefix="/api")
app.register_blueprint(historico_bp, url_prefix="/api")
app.register_blueprint(horario_bp, url_prefix="/api")
app.register_blueprint(preferencia_bp, url_prefix="/api")
app.register_blueprint(aprovacao_bp, url_prefix='/api/aprovacao')
# app.register_blueprint(contato_bp, url_prefix="/api")

# rotas do front-end
@app.route("/")
def homepage():
    try:
        return render_template('index.html')
    except Exception:
        return jsonify({
            "nome": "API Hemocentro",
            "versao": "1.0.0",
            "status": "online",
            "warning": "Template 'index.html' não encontrado"
        }), 200

@app.route("/agendamento")
def agendamento():
    try:
        return render_template('agendamento.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/cadastro")
def cadastro():
    try:
        return render_template('cadastro.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/cadastro_hemocentro")  # NOVA ROTA ADICIONADA
def cadastro_hemocentro():
    try:
        return render_template('cadastro_hemocentro.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/campanha")
def campanha_page():
    try:
        return render_template('campanha.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/contato")
def contato():
    try:
        return render_template('Contato.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/hemocentros")
def hemocentros():
    try:
        return render_template('Hemocentros.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/historia")
def historia():
    try:
        return render_template('Historia.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/login") 
def login():
    try:
        return render_template("login.html")
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/login_doador")
def login_doador():
    try:
        return render_template('login.html')  # Mesmo arquivo de login
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/login_hemocentro")
def login_hemocentro():
    try:
        return render_template('login.html')  # Mesmo arquivo de login
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/noticias")
def noticias():
    try:
        return render_template('Noticias.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/perfil")
def perfil():
    try:
        return render_template('Perfil.html')
    except Exception:
        return jsonify({"success": False, "message": "Página não encontrada"}), 404

@app.route("/api/health")
def health_check():
    # rota da saude kkk
    return jsonify({
        "success": True,
        "status": "healthy"
    }), 200

# tratamentos
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "message": "Rota não encontrada"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "success": False,
        "message": "Erro interno no servidor"
    }), 500

# executando (que funcione meu deussssss)
if __name__ == "__main__":
    print("=" * 50)
    print("API Hemocentro - MVP")
    print(f"Ambiente: {Config.ENVIRONMENT}")
    print(f"Debug: {Config.DEBUG}")
    print(f"Rodando em: {Config.BASE_URL}")
    print("=" * 50)
    
    app.run(
        debug=Config.DEBUG,
        host="0.0.0.0",
        port=5000
    )