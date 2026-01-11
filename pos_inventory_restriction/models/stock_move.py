import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        # LEVEL 2 — block validation
        if self.env.context.get("disable_auto_validate"):
            return self

        return super()._action_done(cancel_backorder=cancel_backorder)

    def _create_out_svl(self, forced_quantity=None):
        if self.env.context.get('disable_svl_creation'):
            return self.env['stock.valuation.layer']

        return super()._create_out_svl(forced_quantity=forced_quantity)

    def _create_in_svl(self, forced_quantity=None):
        if self.env.context.get('disable_svl_creation'):
            return self.env['stock.valuation.layer']

        return super()._create_in_svl(forced_quantity=forced_quantity)

    def _account_entry_move(self, qty, description, svl_id, cost):
        if self.env.context.get('disable_inventory_accounting'):
            return self.env['account.move']

        return super()._account_entry_move(qty, description, svl_id, cost)