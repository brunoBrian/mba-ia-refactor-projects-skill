from flask import request, jsonify
from src.models import produto as produto_model

CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


def listar_produtos():
    produtos = produto_model.get_todos_produtos()
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.get_produto_por_id(id)
    if produto:
        return jsonify({"dados": produto, "sucesso": True}), 200
    return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = request.args.get("preco_min")
    preco_max = request.args.get("preco_max")
    try:
        preco_min = float(preco_min) if preco_min else None
        preco_max = float(preco_max) if preco_max else None
    except ValueError:
        return jsonify({"erro": "Valores de preço inválidos"}), 400

    resultados = produto_model.buscar_produtos(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200


def criar_produto():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if preco is None:
        return jsonify({"erro": "Preço é obrigatório"}), 400
    if estoque is None:
        return jsonify({"erro": "Estoque é obrigatório"}), 400
    if preco < 0:
        return jsonify({"erro": "Preço não pode ser negativo"}), 400
    if estoque < 0:
        return jsonify({"erro": "Estoque não pode ser negativo"}), 400
    if len(nome) < 2 or len(nome) > 200:
        return jsonify({"erro": "Nome deve ter entre 2 e 200 caracteres"}), 400

    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        return jsonify({"erro": f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}"}), 400

    descricao = dados.get("descricao", "")
    id = produto_model.criar_produto(nome, descricao, preco, estoque, categoria)
    return jsonify({"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    produto_existente = produto_model.get_produto_por_id(id)
    if not produto_existente:
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    nome = dados.get("nome", "")
    preco = dados.get("preco")
    estoque = dados.get("estoque")

    if not nome:
        return jsonify({"erro": "Nome é obrigatório"}), 400
    if preco is None:
        return jsonify({"erro": "Preço é obrigatório"}), 400
    if estoque is None:
        return jsonify({"erro": "Estoque é obrigatório"}), 400
    if preco < 0:
        return jsonify({"erro": "Preço não pode ser negativo"}), 400
    if estoque < 0:
        return jsonify({"erro": "Estoque não pode ser negativo"}), 400

    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", "geral")
    produto_model.atualizar_produto(id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    produto = produto_model.get_produto_por_id(id)
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    produto_model.deletar_produto(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
