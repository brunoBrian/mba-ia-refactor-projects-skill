const CourseModel = require('../models/Course');
const EnrollmentModel = require('../models/Enrollment');
const UserModel = require('../models/User');
const { db } = require('../database');

async function financialReport(req, res) {
    try {
        const courses = await CourseModel.findAll();
        const report = [];

        for (const course of courses) {
            const courseData = { course: course.title, revenue: 0, students: [] };
            const enrollments = await EnrollmentModel.findByCourse(course.id);

            for (const enr of enrollments) {
                const user = await UserModel.findById(enr.user_id);
                const payment = await EnrollmentModel.getPayment(enr.id);

                if (payment && payment.status === 'PAID') {
                    courseData.revenue += payment.amount;
                }
                courseData.students.push({
                    student: user ? user.name : 'Unknown',
                    paid: payment ? payment.amount : 0,
                });
            }
            report.push(courseData);
        }

        return res.json(report);
    } catch (err) {
        return res.status(500).json({ error: 'Erro interno' });
    }
}

module.exports = { financialReport };
