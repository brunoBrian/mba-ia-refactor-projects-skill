function errorHandler(err, req, res, next) {
    console.error(`[ERROR] ${err.message}`);
    res.status(500).json({ error: 'Erro interno do servidor' });
}

function notFound(req, res) {
    res.status(404).json({ error: 'Rota não encontrada' });
}

module.exports = { errorHandler, notFound };
