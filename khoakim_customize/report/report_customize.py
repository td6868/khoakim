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

class SaleOrderReportKhoakimXlsx(models.AbstractModel):
    _name = 'report.khoakim_customize.report_saleorder_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, saleorders):
        for so in saleorders:
            report_name = so.name
            # One sheet by partner
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, so.name, bold)
            row_header = 2
            col = 0
            sheet.write(row_header, col, 'Mô tả')
            sheet.write(row_header, col + 1, 'Số lượng')
            sheet.write(row_header, col + 2, 'Đơn vị')
            sheet.write(row_header, col + 3, 'Giá')
            sheet.write(row_header, col + 4, 'Thuế')
            sheet.write(row_header, col + 5, 'Số tiền')
            sheet.write(row_header, col + 6, 'Ghi chú')

            for line in so.order_line:
                tax = ''
                note = ''
                row_header += 1
                sheet.write(row_header, col, str(line.name))
                sheet.write(row_header, col + 1, str(line.product_uom_qty))
                sheet.write(row_header, col + 2, str(line.product_uom.name))
                sheet.write(row_header, col + 3, str(line.price_unit))
                if line.tax_id:
                    for t in line.tax_id:
                        tax += t.name + ','
                sheet.write(row_header, col + 4, str(tax))
                sheet.write(row_header, col + 5, str(line.price_subtotal))
                if line.note:
                    note = line.note
                sheet.write(row_header, col + 6, str(note))

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

