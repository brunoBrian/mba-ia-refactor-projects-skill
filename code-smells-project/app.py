from flask import Flask, jsonify
from flask_cors import CORS
from src.config.settings import SECRET_KEY, DEBUG
from src.middlewares.error_handler import register_error_handlers
from src.controllers import produto_ctrl, usuario_ctrl, pedido_ctrl
from database import get_db

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG
CORS(app)

register_error_handlers(app)

# Produtos
app.add_url_rule("/produtos", "listar_produtos", produto_ctrl.listar_produtos, methods=["GET"])
app.add_url_rule("/produtos/busca", "buscar_produtos", produto_ctrl.buscar_produtos, methods=["GET"])
app.add_url_rule("/produtos/<int:id>", "buscar_produto", produto_ctrl.buscar_produto, methods=["GET"])
app.add_url_rule("/produtos", "criar_produto", produto_ctrl.criar_produto, methods=["POST"])
app.add_url_rule("/produtos/<int:id>", "atualizar_produto", produto_ctrl.atualizar_produto, methods=["PUT"])
app.add_url_rule("/produtos/<int:id>", "deletar_produto", produto_ctrl.deletar_produto, methods=["DELETE"])

# Usuários
app.add_url_rule("/usuarios", "listar_usuarios", usuario_ctrl.listar_usuarios, methods=["GET"])
app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", usuario_ctrl.buscar_usuario, methods=["GET"])
app.add_url_rule("/usuarios", "criar_usuario", usuario_ctrl.criar_usuario, methods=["POST"])
app.add_url_rule("/login", "login", usuario_ctrl.login, methods=["POST"])

# Pedidos
app.add_url_rule("/pedidos", "criar_pedido", pedido_ctrl.criar_pedido, methods=["POST"])
app.add_url_rule("/pedidos", "listar_todos_pedidos", pedido_ctrl.listar_todos_pedidos, methods=["GET"])
app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", pedido_ctrl.listar_pedidos_usuario, methods=["GET"])
app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", pedido_ctrl.atualizar_status_pedido, methods=["PUT"])

# Relatórios
app.add_url_rule("/relatorios/vendas", "relatorio_vendas", pedido_ctrl.relatorio_vendas, methods=["GET"])


@app.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "2.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health"
        }
    })


@app.route("/health")
def health_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
            "versao": "2.0.0"
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({"status": "erro"}), 500


if __name__ == "__main__":
    get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
