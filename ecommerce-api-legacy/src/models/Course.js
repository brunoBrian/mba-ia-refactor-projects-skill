const { db } = require('../database');

async function findActiveById(id) {
    return db.getAsync('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

async function findAll() {
    return db.allAsync('SELECT * FROM courses', []);
}

module.exports = { findActiveById, findAll };
