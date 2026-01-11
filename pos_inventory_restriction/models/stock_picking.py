import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pos_session_id = fields.Many2one(
        'pos.session',
        string='POS Session',
        help='Link to POS Session if this picking is from POS',
        index=True,
        copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Link picking to POS session IMMEDIATELY after creation"""
        pickings = super().create(vals_list)


        for picking in pickings:
            if picking.origin and not picking.pos_session_id:
                pos_order = self.env['pos.order'].sudo().search([
                    ('name', '=', picking.origin)
                ], limit=1)

                if pos_order and pos_order.session_id:
                    picking.pos_session_id = pos_order.session_id.id
        return pickings

    def write(self, vals):
        """Link picking when origin is set"""
        result = super().write(vals)

        if 'origin' in vals:
            for picking in self:
                if picking.origin and not picking.pos_session_id:
                    pos_order = self.env['pos.order'].sudo().search([
                        ('name', '=', picking.origin)
                    ], limit=1)

                    if pos_order and pos_order.session_id:
                        picking.pos_session_id = pos_order.session_id.id
        return result

    def button_validate(self):
        if self.env.context.get("disable_auto_validate"):
            return True

        return super().button_validate()