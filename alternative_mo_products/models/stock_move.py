from odoo import models, _
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_alternative_moves(self):
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        for move in self:
            rounding = roundings[move]
            missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            need = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id,
                                                      rounding_method='HALF-UP')
            if float_is_zero(need, precision_rounding=rounding):
                continue
            # Reserve new quants and create move lines accordingly.
            forced_package_id = move.package_level_id.package_id or None
            stock = move._get_available_quantity(move.location_id, package_id=forced_package_id)
            if stock < 0:
                stock = 0
            if stock - need < 0:
                new_moves_vals_list = []
                alternative_needed = abs(stock - need)
                for alternative in move.product_id.alternative_line_ids:
                    product_id = alternative.alternative_product_id
                    alternative_needed = move.product_id.uom_id._compute_quantity(alternative_needed, product_id.uom_id,
                                                                                  rounding_method='HALF-UP')
                    alternative_needed = alternative_needed * alternative.ratio
                    alternative_available = self.env['stock.quant']._get_available_quantity(product_id,
                                                                                            move.location_id,
                                                                                            lot_id=None,
                                                                                            package_id=None,
                                                                                            owner_id=None, strict=False,
                                                                                            allow_negative=False)
                    if alternative_available <= 0:
                        continue
                    if alternative_available <= alternative_needed:
                        alternative_needed -= alternative_available
                        qty = product_id.uom_id._compute_quantity(alternative_available,
                                                                  move.product_id.uom_id,
                                                                  rounding_method='HALF-UP')
                    else:
                        qty = product_id.uom_id._compute_quantity(alternative_needed,
                                                                  move.product_id.uom_id,
                                                                  rounding_method='HALF-UP')
                        alternative_needed = 0
                    new_moves_vals_list.append({
                        'product_id': product_id.id,
                        'qty': qty
                    })

                    if alternative_needed > 0:
                        alternative_needed = product_id.uom_id._compute_quantity(alternative_needed,
                                                                                 move.product_id.uom_id,
                                                                                 rounding_method='HALF-UP')
                        continue
                    break
                move_ids = self.env['stock.move']
                if alternative_needed <= 0:
                    for vals in new_moves_vals_list:
                        move.write({'product_uom_qty': stock})
                        move_vals = self._get_alternative_move_vals(vals, move)
                        move_ids |= self.env['stock.move'].create(move_vals)
                    move_ids._adjust_procure_method()
                    move_ids._action_confirm(merge=False)
                    move_ids._action_assign()

    def _get_alternative_move_vals(self, vals, move):
        product_id = self.env['product.product'].browse(vals['product_id'])
        return {
            'product_id': vals['product_id'],
            'product_uom_qty': vals['qty'],
            'sequence': move.sequence,
            'name': move.name,
            'date': move.date,
            'date_deadline': move.date_deadline,
            'bom_line_id': False,
            'picking_type_id': move.picking_type_id.id,
            'product_uom': product_id.uom_id.id,
            'location_id': move.location_id.id,
            'location_dest_id': move.location_dest_id.id,
            'raw_material_production_id': move.raw_material_production_id.id,
            'company_id': move.company_id.id,
            'operation_id': move.operation_id.id,
            'price_unit': product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': move.origin,
            'state': 'draft',
            'warehouse_id': move.warehouse_id.id,
            'group_id': move.group_id.id,
            'propagate_cancel': move.propagate_cancel,
        }

    def _action_assign(self, force_qty=False):
        # Check if there is enough stock, if not, check if there is any alternative stock (ONLY FOR MRP RAWS)
        moves_to_check_alternatives = self.filtered(lambda m: m.product_id.alternative_line_ids
                                                              and m.state in ['confirmed', 'waiting',
                                                                              'partially_available'])
        moves_to_check_alternatives._prepare_alternative_moves()

        return super(StockMove, self)._action_assign()
