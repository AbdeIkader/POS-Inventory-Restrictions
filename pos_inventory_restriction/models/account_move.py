import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model_create_multi
    def create(self, vals_list):
        filtered_vals = []

        for vals in vals_list:
            stock_move_id = vals.get('stock_move_id')
            ref = vals.get('ref', '')

            if stock_move_id or 'Stock' in ref or 'WH/OUT' in ref:
                if stock_move_id:
                    stock_move = self.env['stock.move'].browse(stock_move_id)
                else:
                    stock_move = self.env['stock.move'].search([
                        ('reference', '=', ref)
                    ], limit=1)

                if stock_move and stock_move.picking_id and stock_move.picking_id.pos_session_id:
                    config = stock_move.picking_id.pos_session_id.config_id

                    if config.inventory_restriction_level == 'deny_create_cost_layers':
                        _logger.info(
                            "Inventory restriction: deny_create_cost_layers - "
                            "blocking journal entry creation for stock move %s",
                            stock_move.name
                        )
                        continue

            filtered_vals.append(vals)

        if filtered_vals:
            return super().create(filtered_vals)

        return self.env['account.move']