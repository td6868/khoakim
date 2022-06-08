from odoo import api, models

class SaleOrderReportKhoakim(models.AbstractModel):
    _name = 'report.khoakim_custommize.report_saleorder'
    _description = 'Mẫu in báo giá Khoa Kim'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        if docs:
            return {
                'doc_ids': docs.ids,
                'doc_model': 'sale.order',
                'docs': docs,
            }

class AccountMoveReportKhoakim(models.AbstractModel):
    _name = 'report.khoakim_custommize.report_account_move_khoakim'
    _description = 'Mẫu hoá đơn Khoa Kim'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        if docs:
            return {
                'doc_ids': docs.ids,
                'doc_model': 'account.move',
                'docs': docs,
            }

class StockPickingKhoakim(models.AbstractModel):
    _name = 'report.khoakim_custommize.report_stock_picking_khoakim'
    _description = 'Mẫu phiếu giao hàng Khoa Kim'

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        if docs:
            return {
                'doc_ids': docs.ids,
                'doc_model': 'stock.picking',
                'docs': docs,
            }

class PurchaseOrderKhoakim(models.AbstractModel):
    _name = 'report.khoakim_custommize.report_stock_picking_khoakim'
    _description = 'Mẫu phiếu mua hàng Khoa Kim'

    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)
        if docs:
            return {
                'doc_ids': docs.ids,
                'doc_model': 'purchase.order',
                'docs': docs,
            }