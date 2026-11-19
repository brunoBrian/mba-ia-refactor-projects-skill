const bcrypt = require('bcryptjs');
const CourseModel = require('../models/Course');
const UserModel = require('../models/User');
const EnrollmentModel = require('../models/Enrollment');

async function checkout(req, res) {
    const { usr, eml, pwd, c_id, card } = req.body;

    if (!usr || !eml || !c_id || !card) {
        return res.status(400).json({ error: 'Bad Request: usr, eml, c_id e card são obrigatórios' });
    }

    try {
        const course = await CourseModel.findActiveById(c_id);
        if (!course) return res.status(404).json({ error: 'Curso não encontrado' });

        // Validação simplificada de cartão (em produção: usar gateway real)
        const paymentStatus = card.startsWith('4') ? 'PAID' : 'DENIED';
        if (paymentStatus === 'DENIED') {
            return res.status(400).json({ error: 'Pagamento recusado' });
        }

        let user = await UserModel.findByEmail(eml);
        if (!user) {
            const hash = await bcrypt.hash(pwd || '123456', 12);
            const result = await UserModel.create(usr, eml, hash);
            user = { id: result.lastID };
        }

        const enr = await EnrollmentModel.create(user.id, c_id);
        await EnrollmentModel.createPayment(enr.lastID, course.price, paymentStatus);
        await EnrollmentModel.logAudit(`Checkout curso ${c_id} por usuário ${user.id}`);

        return res.status(200).json({ msg: 'Sucesso', enrollment_id: enr.lastID });
    } catch (err) {
        return res.status(500).json({ error: 'Erro interno' });
    }
}

module.exports = { checkout };
