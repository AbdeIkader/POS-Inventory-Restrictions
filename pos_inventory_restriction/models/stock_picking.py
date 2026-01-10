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
        _logger.warning("=" * 80)
        _logger.warning(f"StockPicking.create called with {len(vals_list)} pickings")

        pickings = super().create(vals_list)

        _logger.warning(f"  Created pickings: {pickings.mapped('name')}")

        for picking in pickings:
            _logger.warning(f"  Checking picking {picking.name}, origin: {picking.origin}")

            if picking.origin and not picking.pos_session_id:
                pos_order = self.env['pos.order'].sudo().search([
                    ('name', '=', picking.origin)
                ], limit=1)

                if pos_order and pos_order.session_id:
                    picking.pos_session_id = pos_order.session_id.id
                    _logger.warning(
                        f"  ✓ LINKED picking {picking.name} to session "
                        f"{pos_order.session_id.name} via origin {picking.origin}"
                    )

        for picking in pickings:
            _logger.warning(
                f"    - {picking.name}: pos_session_id = "
                f"{picking.pos_session_id.name if picking.pos_session_id else 'NONE!'}"
            )

        _logger.warning("=" * 80)
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
                        _logger.warning(
                            f"  ✓ LINKED picking {picking.name} to session "
                            f"{pos_order.session_id.name} via write(origin={picking.origin})"
                        )

        return result

    def button_validate(self):
        if self.env.context.get("disable_auto_validate"):
            _logger.info(
                "POS Level 2: auto validation blocked for pickings %s",
                self.mapped("name")
            )
            return True

        return super().button_validate()