const router = require('express').Router();
const checkoutCtrl = require('../controllers/checkoutController');
const reportCtrl = require('../controllers/reportController');
const UserModel = require('../models/User');

router.post('/checkout', checkoutCtrl.checkout);
router.get('/admin/financial-report', reportCtrl.financialReport);

router.delete('/users/:id', async (req, res) => {
    try {
        await UserModel.deleteById(req.params.id);
        res.json({ message: 'Usuário e dados relacionados deletados com sucesso' });
    } catch (err) {
        res.status(500).json({ error: 'Erro ao deletar usuário' });
    }
});

module.exports = router;
