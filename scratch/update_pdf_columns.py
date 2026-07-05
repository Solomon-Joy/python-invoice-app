import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the item parsing logic
old_parse = """        for idx, item in enumerate(data['items'], 1):
            taxable = item['quantity'] * item['price']
            cgst_amt = taxable * self.GST_CGST_RATE
            sgst_amt = taxable * self.GST_SGST_RATE
            gst_amt = cgst_amt + sgst_amt
            line_total = taxable + gst_amt
            subtotal += taxable
            total_cgst += cgst_amt
            total_sgst += sgst_amt
            total_qty += item['quantity']
            item_rows.append([
                str(idx),
                item['description'],
                hsn,
                str(item['quantity']),
                unit,
                self.format_pdf_currency(item['price']),
                f"{self.format_pdf_currency(gst_amt)} ({(self.GST_CGST_RATE + self.GST_SGST_RATE) * 100:.0f}%)",
                self.format_pdf_currency(line_total),
            ])"""

new_parse = """        for idx, item in enumerate(data['items'], 1):
            qty = item.get('quantity', 1)
            price = item.get('price', 0.0)
            mrp = item.get('mrp', 0.0)
            total = item.get('total', qty * price)
            cgst_pct = item.get('cgst_pct', self.GST_CGST_RATE * 100)
            cgst = item.get('cgst', total * (cgst_pct / 100))
            sgst_pct = item.get('sgst_pct', self.GST_SGST_RATE * 100)
            sgst = item.get('sgst', total * (sgst_pct / 100))
            item_hsn = item.get('hsn', hsn)
            disc = item.get('disc', '')
            taxable = item.get('taxable', '')

            subtotal += total
            total_cgst += cgst
            total_sgst += sgst
            total_qty += qty

            item_rows.append([
                str(idx),
                item['description'],
                item_hsn,
                str(qty),
                self.format_pdf_currency(mrp) if mrp else "",
                self.format_pdf_currency(price),
                self.format_pdf_currency(total),
                str(disc),
                str(taxable),
                f"{cgst_pct}%",
                self.format_pdf_currency(cgst),
                f"{sgst_pct}%",
                self.format_pdf_currency(sgst),
            ])"""

content = content.replace(old_parse, new_parse)


# Replace items_data definition
old_table_def = """            items_data = [[
                '#', 'Item Name', 'HSN/SAC', 'Quantity', 'Unit',
                f"Price/Unit({self.PDF_CURRENCY})", f"GST({self.PDF_CURRENCY})", f"Amount({self.PDF_CURRENCY})"
            ]]
            items_data.extend(item_rows)
            items_data.append([
                '', 'Total', '', str(total_qty), '', '', self.format_pdf_currency(total_tax), self.format_pdf_currency(grand_total)
            ])

            items_table = Table(items_data, colWidths=[
                0.3 * inch, 2.15 * inch, 0.75 * inch, 0.6 * inch,
                0.45 * inch, 0.85 * inch, 0.75 * inch, 0.75 * inch
            ])
            items_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('FONTSIZE', (0, 1), (-1, -1), 7.5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))"""

new_table_def = """            items_data = [[
                '#', 'Desc', 'HSN', 'Qty', 'MRP',
                'Price', 'Total', 'Disc%', 'TaxVal', 'CGST%', 'CGST', 'SGST%', 'SGST'
            ]]
            items_data.extend(item_rows)
            items_data.append([
                '', 'Total', '', str(total_qty), '', '', self.format_pdf_currency(subtotal), '', '', '', self.format_pdf_currency(total_cgst), '', self.format_pdf_currency(total_sgst)
            ])

            items_table = Table(items_data, colWidths=[
                0.2 * inch, 1.4 * inch, 0.55 * inch, 0.3 * inch, 0.4 * inch, 0.45 * inch, 0.5 * inch, 0.3 * inch, 0.4 * inch, 0.35 * inch, 0.55 * inch, 0.35 * inch, 0.55 * inch
            ])
            items_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 6.5), # Smaller font to fit 13 columns
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))"""

content = content.replace(old_table_def, new_table_def)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
