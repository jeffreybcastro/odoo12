# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class Authorization(models.Model):
    _name = "vitt_fiscal_seq.authorization_code"
    _description = "Code Authorization"
    
    name = fields.Char('Authorization code', help='Authorization code', required=True, size= 37)
    expiration_date = fields.Date('Expiration Date', required=True)
    start_date = fields.Date('Start Date', help='start date', required=True)
    company_id = fields.Many2one('res.company', "Company", required=True)
    #code_type = fields.Many2one('vitt_fiscal_seq.authorization_code_type', string='Tax regime code type', help='tax regime type code', required=True)
    active = fields.Boolean("Actived", default=True)
    fiscal_sequence_regime_ids = fields.One2many('vitt_fiscal_seq.fiscal_sequence_regime', 'authorization_code_id')
    _from_ = fields.Integer(compute='get_from_to')
    _to_ = fields.Integer(compute='get_from_to')
    #doc_type_ = fields.Char(compute='get_from_to',string='Doc. Type')
    doc_type2 = fields.Selection([
        ('out_invoice', 'Customer Invoices'),
        ('out_refund', 'Credit Notes'),
        ('in_refund', 'Debit Notes'),
    ], string='Sequence Type', required=True)




    @api.model
    def create(self, vals):
        res = super(Authorization, self).create(vals)
        _obj = self.env["vitt_fiscal_seq.authorization_code"].search([['active', '=', True] ,['doc_type2', '=', vals.get("doc_type2")]])
        array  = []
        if vals.get("start_date") > vals.get("expiration_date"):
            raise Warning(_('Start date is greater than than expiration date'))
        #Control that only an active regime is allowed
        #if _obj.doc_type2 == self.doc_type2:
        if len(_obj) > 1:
            raise Warning(_('No pueden estar activos dos regimen de %s !' % (self.doc_type2)))
        len_cai = ''
        len_cai = vals.get("name")
        if len(len_cai) <  36 :
            raise Warning(_(len(len_cai)))
        elif len_cai.isupper() == False:
            raise Warning(_('Formato del CAI debe ser en mayuscula!'))                        
        return res

    @api.multi
    def get_action_journal_settings(self):
        ctx = {'company_id': self.company_id.id}
        return {'name': _("Journal Settings and Fiscal Sequences"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'vitt_fiscal_seq.journal_settings',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': ctx}

    @api.multi
    def _update_ir_sequence(self):
        for fiscal_sequence in self.fiscal_sequence_regime_ids:
            if fiscal_sequence.sequence_id:
                sequence_vals = {'expiration_date': self.expiration_date}
                fiscal_sequence.sequence_id.write(sequence_vals)
        return True

    @api.multi
    def write(self, vals):
        res = super(Authorization, self).write(vals)
        res = self._update_ir_sequence()
        return res
    
    @api.multi
    def write(self, vals):
        res = super(Authorization, self).write(vals)
        len_cai = ''
        len_cai = vals.get("name")
        if len(len_cai) <  36 :
            raise Warning(_('Formato del CAI es invalido!'))
        elif len_cai.isupper() == False:
            raise Warning(_('Formato del CAI debe ser en mayuscula!'))       
        return res

    @api.one
    def get_from_to(self):
        #obj = self.env["vitt_fiscal_seq.fiscal_sequence_regime"].search([('authorization_code_id', '=', self.fiscal_sequence_regime_ids.id)])
        for rec in self:
            for obj in rec.fiscal_sequence_regime_ids:
                self._from_ = obj._from
                self._to_ = obj._to
            # obj_sett = self.env["vitt_fiscal_seq.journal_settings"].search([('journal_id', '=', self.fiscal_sequence_regime_ids.journal_id.id)])
            # for config in obj_sett:
            #     self.doc_type_ = config.doc_type.name

    # @api.multi
    # def create(self, vals):
    #     res = super(Authorization, self).create(vals)
    #     for rec in self:
    #         if rec.doc_type2:
    #             for actived_ in rec.active:
    #                 if len(actived_) > 2:
    #                     raise Warning(_('Example'))
    #     return res





class Fiscal_sequence(models.Model):
    _name = "vitt_fiscal_seq.fiscal_sequence_regime"
    _description = "Fiscal Sequence Authorization"
    
    authorization_code_id = fields.Many2one('vitt_fiscal_seq.authorization_code', required=True)
    sequence_id = fields.Many2one('ir.sequence', "Fiscal Number")
    actived = fields.Boolean('Active')
    _from = fields.Integer('From')
    _to = fields.Integer('to')
    user_ids = fields.Many2many("res.users", string="Users", related="sequence_id.user_ids")
    journal_id = fields.Many2one("account.journal", "Journal")

    def build_numbers(self, number):
        res = ''
        prefix = self.sequence_id.prefix
        padding = self.sequence_id.padding
        if padding and prefix and number:
            res = prefix + str(number).zfill(padding)
        return res

    @api.multi
    def _update_ir_sequence(self):
        if self.sequence_id:
            sequence_vals = {'vitt_min_value': self.build_numbers(self._from),
                             'vitt_max_value': self.build_numbers(self._to),
                             }
            self.sequence_id.write(sequence_vals)

    @api.onchange("actived")
    def onchange_actived(self):
        if not self.actived:
            for sequence in self.sequence_id:
                self.sequence_id.write({'active': False})
        if self.actived and not self.sequence_id.active:
            self.sequence_id.write({'active': True})

    @api.multi
    def write(self, vals):
        super(Fiscal_sequence, self).write(vals)
        self._update_ir_sequence()

    @api.multi
    def create(self, vals):
        res = super(Fiscal_sequence, self).create(vals)
        if not vals.get("journal_id"):
            raise Warning(_('Set a journal and a sequence'))
        return res

    # TODO : Verificar que no exista en facturas esta secuencia
    @api.multi
    def unlink(self):
        invoice = self.env["account.invoice"].search([('sequence_ids', '=', self.sequence_id.id)])
        if invoice:
            raise Warning(_('You cannot delete a fiscal regime, you must disable it'))
        return super(Fiscal_sequence, self).unlink()


# class Code_authorization_type(models.Model):
#     _name = "vitt_fiscal_seq.authorization_code_type"
#     _description = "Validation Authorization"

#     name = fields.Char('Name', help='tax regime type', required=True)
#     description = fields.Char('Description', help='tax regime type description', required=True)


#     _sql_constraints = [('value_code_authorization_type_uniq', 'unique (name)', 'Only one authorization type is permitted!')]
