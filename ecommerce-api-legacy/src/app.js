const express = require('express');
const { initDb } = require('./database');
const config = require('./config');
const apiRoutes = require('./routes/api');
const { errorHandler, notFound } = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

app.use('/api', apiRoutes);
app.use(notFound);
app.use(errorHandler);

initDb().then(() => {
    app.listen(config.port, () => {
        console.log(`LMS API rodando na porta ${config.port}`);
    });
});

module.exports = app;
