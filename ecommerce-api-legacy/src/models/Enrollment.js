const { db } = require('../database');

async function create(userId, courseId) {
    return db.runAsync('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
}

async function createPayment(enrollmentId, amount, status) {
    return db.runAsync('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
}

async function logAudit(action) {
    return db.runAsync("INSERT INTO audit_logs (action) VALUES (?)", [action]);
}

async function findByCourse(courseId) {
    return db.allAsync('SELECT * FROM enrollments WHERE course_id = ?', [courseId]);
}

async function getPayment(enrollmentId) {
    return db.getAsync('SELECT amount, status FROM payments WHERE enrollment_id = ?', [enrollmentId]);
}

module.exports = { create, createPayment, logAudit, findByCourse, getPayment };
