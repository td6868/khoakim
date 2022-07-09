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
            i = 0
            header_title = ['Mô tả', 'Số lượng', 'Đơn vị', 'Giá', 'Thuế', 'Số tiền', 'Ghi chú']
            for h in header_title:
                sheet.write(row_header, col+i, h)
                i += 1

            for line in so.order_line:
                tax = ''
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
                sheet.write(row_header, col + 6, str(line.note or ''))

class PurchaseOrderReportKhoakimXlsx(models.AbstractModel):
    _name = 'report.khoakim_customize.report_purchaseorder_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, purchaseorders):
        for po in purchaseorders:
            report_name = po.name
            sheet = workbook.add_worksheet(report_name[:31])
            bold = workbook.add_format({'bold': True})
            sheet.write(0, 0, 'Đơn đặt hàng/ 订货单', bold)
            sheet.write(0, 1, po.vend_name or po.name, bold)
            row_header = 2
            col = 0
            header = ['Tên sản phẩm / 产品名称', 'Hãng/ 品牌', 'Màu sắc/ 颜色', 'Đơn giá nhập/ 出厂价格'
                      , 'SL/ 数量', 'Khai hải quan/ 报正关', 'Ghi chú/ 笔记']
            i = 0
            for h1 in header:
                sheet.write(row_header, col + i, h1)
                i += 1
            for line in po.order_line:
                row_header += 1
                if line.declare_ok == 'yes':
                    declare_ok = 'Có (有)'
                else:
                    declare_ok = 'Không (不)'
                vals = [str(line.name), str(line.brand), str(line.color),
                        str(line.price_unit), str(line.product_qty)
                        , str(declare_ok), str(line.note or '')]
                j = 0
                for val in vals:
                    sheet.write(row_header, col+j, val)
                    j += 1

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

