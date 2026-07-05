import sys

def main():
    file_path = "app.py"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_str = "    def createGSTPDF(self, fileName, data):"
    end_str = "    def format_pdf_currency(self, amount, space=False):"
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find start or end bounds.")
        sys.exit(1)
        
    new_func = """    def createGSTPDF(self, fileName, data):
        doc = SimpleDocTemplate(fileName, pagesize=A4, topMargin=0.2*inch, bottomMargin=0.2*inch, leftMargin=0.3*inch, rightMargin=0.3*inch)
        story = []
        styles = getSampleStyleSheet()
        company_name = self.COMPANY_NAME
        company_address = self.COMPANY_ADDRESS
        company_phone = self.COMPANY_PHONE
        company_gstin = self.COMPANY_GSTIN
        company_pan = "AZOPR2558K"
        company_fssai = "21317199000455"
        company_mob = "8289998398, 9895314201"
        copy_labels = data.get('copyLabels') or self.GST_COPY_LABELS

        subtotal = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        item_rows = []
        for idx, item in enumerate(data['items'], 1):
            qty = item.get('quantity', 0)
            price = item.get('price', 0)
            mrp = item.get('mrp', 0)
            total = item.get('total', qty * price)
            cgst_pct = item.get('cgst_pct', 2.5)
            cgst = item.get('cgst', 0)
            sgst_pct = item.get('sgst_pct', 2.5)
            sgst = item.get('sgst', 0)
            hsn = item.get('hsn', '')
            disc = item.get('disc', '')
            taxable = item.get('taxable', '')
            
            subtotal += total
            total_cgst += cgst
            total_sgst += sgst
            
            item_rows.append([
                str(idx),
                item['description'],
                hsn,
                str(qty),
                f"{mrp:.0f}" if mrp else "",
                f"{price:.0f}" if price else "",
                f"{total:.0f}",
                str(disc),
                str(taxable),
                f"{cgst_pct}%", f"{cgst:.2f}",
                f"{sgst_pct}%", f"{sgst:.2f}",
            ])

        total_tax = data.get('totalTax', total_cgst + total_sgst)
        grand_total = data.get('grossTotal', subtotal + total_tax)
        net_payable = data.get('netPayable', grand_total)
        amount_in_words = self.number_to_words(int(round(net_payable)))

        for copy in range(1, len(copy_labels) + 1):
            copy_index = min(copy - 1, len(copy_labels) - 1)
            
            # Header
            header_table = Table([[
                Paragraph(f"<font size=14><b>{company_name}</b></font><br/>"
                          f"<font size=9>16/49-2, {company_address}</font><br/>"
                          f"<font size=8>GST NO : {company_gstin} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; MOB : {company_mob} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; PAN NO: {company_pan}</font><br/>"
                          f"<font size=8><i>fssai</i> {company_fssai}</font>", styles['Normal'])
            ]], colWidths=[7.6 * inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            # Tax Invoice Banner
            banner_table = Table([
                [f"NO: {data['invoiceNumber']}", Paragraph(f"<b><u>TAX INVOICE</u></b><br/><font size=7>({copy_labels[copy_index]})</font>", styles['Normal']), f"DATE: {data['date']}"]
            ], colWidths=[2.5*inch, 2.6*inch, 2.5*inch])
            banner_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))

            # Bill To
            vendor_table = Table([
                [f"To:  {data['vendorName']}", f"GST NO : {data['vendorGST']}"]
            ], colWidths=[4.8*inch, 2.8*inch])
            vendor_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))

            # Items
            items_data = [[
                'Sl.\nNo.', 'Description of Goods', 'HSN / Acc\nCode', 'Qty', 'MRP',
                'Unit\nPrice', 'Total', 'Disc\n%', 'Taxable\nValue', 'CGST\nRate | Amount', '', 'SGST\nRate | Amount', ''
            ]]
            
            # Hack for header spanning
            # We want Rate and Amount under CGST, and Rate and Amount under SGST
            # So row 0 is main header, row 1 is sub header
            items_data = [
                ['Sl.\nNo.', 'Description of Goods', 'HSN / Acc\nCode', 'Qty', 'MRP', 'Unit\nPrice', 'Total', 'Disc\n%', 'Taxable\nValue', 'CGST', '', 'SGST', ''],
                ['', '', '', '', '', '', '', '', '', 'Rate', 'Amount', 'Rate', 'Amount']
            ]
            items_data.extend(item_rows)
            
            # Add some empty rows to make it look like a bill book
            for _ in range(max(0, 15 - len(item_rows))):
                items_data.append(['', '', '', '', '', '', '', '', '', '', '', '', ''])

            items_data.append([
                '', 'Sub Total', '', '', '', '', f"{subtotal:.0f}", '', '', '', f"{total_cgst:.2f}", '', f"{total_sgst:.2f}"
            ])

            items_table = Table(items_data, colWidths=[
                0.3 * inch, 2.0 * inch, 0.65 * inch, 0.35 * inch, 0.4 * inch,
                0.45 * inch, 0.5 * inch, 0.35 * inch, 0.5 * inch,
                0.4 * inch, 0.65 * inch, 0.4 * inch, 0.65 * inch
            ])
            items_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('SPAN', (0, 0), (0, 1)),
                ('SPAN', (1, 0), (1, 1)),
                ('SPAN', (2, 0), (2, 1)),
                ('SPAN', (3, 0), (3, 1)),
                ('SPAN', (4, 0), (4, 1)),
                ('SPAN', (5, 0), (5, 1)),
                ('SPAN', (6, 0), (6, 1)),
                ('SPAN', (7, 0), (7, 1)),
                ('SPAN', (8, 0), (8, 1)),
                ('SPAN', (9, 0), (10, 0)), # CGST
                ('SPAN', (11, 0), (12, 0)), # SGST
                ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
                ('ALIGN', (1, 2), (1, -2), 'LEFT'), # description
                ('ALIGN', (3, 2), (-1, -1), 'RIGHT'), # numbers
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                # Subtotal row formatting
                ('SPAN', (1, -1), (5, -1)),
                ('ALIGN', (1, -1), (5, -1), 'RIGHT'),
                ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            # Footer
            footer_data = [
                [f"Amount in Words:\n{amount_in_words} Only", '', '', f"Total\nRounded off", f"{net_payable:.2f}"],
                [
                    "Bank Details : Acc. No : 462133853\nIFSC : IDIB000T054, INDIAN BANK\nPB NO : 12, SWARAJ ROUND EAST\nBR. NO : THRISSUR. 275.", 
                    '', '', 
                    f"Invoice Total", f"{net_payable:.2f}"
                ],
                ["Certified that the particulars given above are true and correct", '', '', '', ''],
                ["Remarks if any :", '', "For RINA RICH FOOD & AGENCIES", '', ''],
                ['', '', "(authorised signatory)", '', '']
            ]
            
            footer_table = Table(footer_data, colWidths=[3.0*inch, 2.0*inch, 1.2*inch, 0.75*inch, 0.65*inch])
            footer_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -2), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -2), 0.5, colors.black),
                ('SPAN', (0, 0), (2, 0)), # Amount in words
                ('SPAN', (0, 1), (2, 1)), # Bank Details
                ('SPAN', (3, 0), (3, 0)), # Total Rounded off
                ('SPAN', (3, 1), (3, 1)), # Invoice Total
                ('SPAN', (0, 2), (4, 2)), # Certified
                ('SPAN', (0, 3), (1, 4)), # Remarks
                ('SPAN', (2, 3), (4, 3)), # For Rina Rich
                ('SPAN', (2, 4), (4, 4)), # Signature
                
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (2, 3), (4, 4), 'RIGHT'),
                ('ALIGN', (3, 0), (3, 1), 'CENTER'),
                ('ALIGN', (4, 0), (4, 1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (2, 3), (4, 3), 20), # Space for signature
            ]))

            story.append(header_table)
            story.append(banner_table)
            story.append(vendor_table)
            story.append(items_table)
            story.append(footer_table)

            if copy < len(copy_labels):
                story.append(PageBreak())

        doc.build(story)

"""
    
    new_content = content[:start_idx] + new_func + content[end_idx:]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
if __name__ == "__main__":
    main()
