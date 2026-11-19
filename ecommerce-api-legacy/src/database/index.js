const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');
const config = require('../config');

const db = new sqlite3.Database(config.dbPath);

db.getAsync = promisify(db.get.bind(db));
db.runAsync = function(sql, params) {
    return new Promise((resolve, reject) => {
        db.run(sql, params, function(err) {
            if (err) reject(err);
            else resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
};
db.allAsync = promisify(db.all.bind(db));

function initDb() {
    return new Promise((resolve) => {
        db.serialize(() => {
            db.run("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, pass TEXT)");
            db.run("CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER DEFAULT 1)");
            db.run("CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(course_id) REFERENCES courses(id))");
            db.run("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT, FOREIGN KEY(enrollment_id) REFERENCES enrollments(id))");
            db.run("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)");

            db.run("INSERT OR IGNORE INTO users (id, name, email, pass) VALUES (1, 'Leonan', 'leonan@fullcycle.com.br', '$2a$12$placeholder')");
            db.run("INSERT OR IGNORE INTO courses (id, title, price, active) VALUES (1, 'Clean Architecture', 997.00, 1), (2, 'Docker', 497.00, 1)");
            db.run("INSERT OR IGNORE INTO enrollments (id, user_id, course_id) VALUES (1, 1, 1)");
            db.run("INSERT OR IGNORE INTO payments (id, enrollment_id, amount, status) VALUES (1, 1, 997.00, 'PAID')", [], () => resolve());
        });
    });
}

module.exports = { db, initDb };
