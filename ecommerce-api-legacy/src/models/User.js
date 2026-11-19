const { db } = require('../database');

async function findByEmail(email) {
    return db.getAsync('SELECT * FROM users WHERE email = ?', [email]);
}

async function findById(id) {
    return db.getAsync('SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create(name, email, hashedPass) {
    return db.runAsync('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, hashedPass]);
}

async function deleteById(id) {
    await db.runAsync('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [id]);
    await db.runAsync('DELETE FROM enrollments WHERE user_id = ?', [id]);
    return db.runAsync('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, deleteById };
