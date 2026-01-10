import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    @api.model_create_multi
    def create(self, vals_list):

        filtered_vals = []
        blocked_count = 0

        for i, vals in enumerate(vals_list):
            _logger.warning(f"SVL {i}: move_id={vals.get('stock_move_id')}, product_id={vals.get('product_id')}")

            move_id = vals.get('stock_move_id')
            should_block = False

            if move_id:
                move = self.env['stock.move'].sudo().browse(move_id)

                _logger.warning(f"Move {move.name}: picking={move.picking_id.name if move.picking_id else 'None'}")

                if move.picking_id:
                    picking = move.picking_id

                    if hasattr(picking, 'pos_session_id') and picking.pos_session_id:
                        session = picking.pos_session_id
                        config = session.config_id

                        _logger.warning(
                            f"Found POS session: {session.name}, "
                            f"config: {config.name}, "
                            f"level: {config.inventory_restriction_level}"
                        )

                        if config.inventory_restriction_level == 'deny_create_cost_layers':
                            should_block = True
                            blocked_count += 1
                            _logger.info(
                                "✓ Inventory restriction: deny_create_cost_layers - "
                                "blocking SVL for move %s (session: %s, product: %s, qty: %s)",
                                move.name,
                                session.name,
                                move.product_id.display_name,
                                vals.get('quantity', 0)
                            )

                    elif picking.origin:
                        _logger.warning(f"Picking origin: {picking.origin}")

                        pos_order = self.env['pos.order'].sudo().search([
                            ('name', '=', picking.origin)
                        ], limit=1)

                        if pos_order:
                            config = pos_order.session_id.config_id

                            _logger.warning(
                                f"Found POS order via origin: {pos_order.name}, "
                                f"session: {pos_order.session_id.name}, "
                                f"level: {config.inventory_restriction_level}"
                            )

                            if config.inventory_restriction_level == 'deny_create_cost_layers':
                                should_block = True
                                blocked_count += 1
                                _logger.info(
                                    "✓ Inventory restriction: deny_create_cost_layers - "
                                    "blocking SVL for move %s (order: %s, product: %s, qty: %s)",
                                    move.name,
                                    pos_order.name,
                                    move.product_id.display_name,
                                    vals.get('quantity', 0)
                                )

            if not should_block:
                _logger.warning(f"SVL {i}: NOT blocked")
                filtered_vals.append(vals)
            else:
                _logger.warning(f"SVL {i}: BLOCKED ✓")

        _logger.warning(f"Final: Blocked {blocked_count}, Allowing {len(filtered_vals)}")
        _logger.warning("=" * 80)

        if filtered_vals:
            return super().create(filtered_vals)

        return self.env['stock.valuation.layer']