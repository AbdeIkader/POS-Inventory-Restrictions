# -*- coding: utf-8 -*-
from odoo import models, fields

class PosConfig(models.Model):
    _inherit = "pos.config"

    inventory_restriction_level = fields.Selection(
        selection=[
            ("deny_picking_creation", "Deny Picking Creation"),
            ("deny_validate_picking", "Deny Validate Picking"),
            ("deny_create_cost_layers", "Deny Create Cost Layers"),
        ],
        string="Inventory Restriction Level",
        required=True,
        default="deny_validate_picking",
    )