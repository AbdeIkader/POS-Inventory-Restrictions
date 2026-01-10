import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = "pos.session"

    def _create_picking_at_end_of_session(self):
        self.ensure_one()
        level = self.config_id.inventory_restriction_level

        # LEVEL 1 — no picking at all
        if level == "deny_picking_creation":
            _logger.info(
                "Inventory restriction: deny_picking_creation - "
                "skipping picking creation for session %s",
                self.name
            )
            return True

        # Build context flags based on level
        ctx = {
            "pos_session_id": self.id,
        }

        # LEVEL 2 — create picking but block auto validation
        if level == "deny_validate_picking":
            ctx["disable_auto_validate"] = True

        # LEVEL 3 — allow validation but block valuation & accounting
        if level == "deny_create_cost_layers":
            ctx.update({
                "disable_svl_creation": True,
                "disable_inventory_accounting": True,
            })

        _logger.warning(
            "Calling super() with context: %s",
            ctx
        )

        res = super(
            PosSession,
            self.with_context(**ctx)
        )._create_picking_at_end_of_session()

        _logger.warning("=" * 80)
        return res

    def _pos_ui_models_to_load(self):
        """Ensure pos_session_id is accessible"""
        result = super()._pos_ui_models_to_load()
        return result

    def _loader_params_stock_picking(self):
        """Add pos_session_id to picking fields"""
        result = super()._loader_params_stock_picking()
        if 'search_params' in result and 'fields' in result['search_params']:
            result['search_params']['fields'].append('pos_session_id')
        return result

    def _get_pos_ui_stock_picking(self, params):
        """Link pickings to session when loading"""
        pickings = super()._get_pos_ui_stock_picking(params)
        for picking in pickings:
            if not picking.pos_session_id and picking.origin and picking.origin.startswith(self.config_id.name):
                picking.pos_session_id = self.id
        return pickings