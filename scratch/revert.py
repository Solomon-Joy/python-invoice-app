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
        
    old_func = """    def createGSTPDF(self, fileName, data):
        doc = SimpleDocTemplate(fileName, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        company_name = self.COMPANY_NAME
        company_address = self.COMPANY_ADDRESS
        company_phone = self.COMPANY_PHONE
        company_gstin = self.COMPANY_GSTIN
        company_state = self.COMPANY_STATE
        copy_labels = data.get('copyLabels') or self.GST_COPY_LABELS

        hsn = data.get('hsnSac', '').strip() or "19059010"
        unit = data.get('unitName', '').strip() or "Nos"
        place_of_supply = data.get('placeOfSupply', '').strip() or company_state
        vehicle_number = data.get('vehicleNumber', '').strip() or "-"
        vendor_state = data.get('vendorState', '').strip() or place_of_supply
        vendor_contact = data.get('vendorContact', '').strip() or "-"
        vendor_pin = data.get('vendorPin', '').strip() or "-"
        vendor_gstin = data.get('vendorGST', '').strip() or "-"

        subtotal = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_qty = 0
        item_rows = []
        for idx, item in enumerate(data['items'], 1):
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
            ])

        total_tax = data.get('totalTax', total_cgst + total_sgst)
        grand_total = data.get('grossTotal', subtotal + total_tax)
        net_payable = data.get('netPayable', grand_total)
        previous_balance = data.get('previousBalance', 0.0)
        advance_received = data.get('advanceReceived', 0.0)
        round_off = data.get('roundOff', 0.0)
        amount_in_words = self.number_to_words(int(round(net_payable)))

        for copy in range(1, len(copy_labels) + 1):
            copy_index = min(copy - 1, len(copy_labels) - 1)
            invoice_title = Table(
                [[
                    '',
                    Paragraph("<b>TAX INVOICE</b>", styles['Normal']),
                    copy_labels[copy_index],
                ]],
                colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch]
            )
            invoice_title.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (1, 0), (1, 0), 14),
                ('FONTSIZE', (2, 0), (2, 0), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(invoice_title)

            company_block = Table([[
                Paragraph(
                    f"<b>{company_name}</b><br/>{company_address}<br/>Phone: {company_phone}<br/>"
                    f"State: {company_state} &nbsp;&nbsp;&nbsp;&nbsp; GSTIN: {company_gstin}",
                    styles['Normal']
                )
            ]], colWidths=[6.6 * inch])
            company_block.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(company_block)

            customer_and_invoice = Table([[
                Paragraph(
                    f"<b>Bill To:</b><br/>{data['vendorName']}<br/>{data['vendorAddress'].replace(chr(10), '<br/>')}<br/>"
                    f"Contact No: {vendor_contact} &nbsp;&nbsp; State: {vendor_state}<br/>PIN: {vendor_pin}<br/>GSTIN: {vendor_gstin}",
                    styles['Normal']
                ),
                Paragraph(
                    f"<b>Invoice Details:</b><br/>No: {data['invoiceNumber']}<br/>Date: {data['date']}<br/>"
                    f"Place Of Supply: {place_of_supply}<br/><br/><b>Transportation Details:</b><br/>"
                    f"Vehicle Number: {vehicle_number}",
                    styles['Normal']
                )
            ]], colWidths=[3.8 * inch, 2.8 * inch])
            customer_and_invoice.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(customer_and_invoice)

            items_data = [[
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
            ]))
            story.append(items_table)

            tax_summary = Table([
                ['HSN/SAC', f"Taxable Amount({self.PDF_CURRENCY})", 'CGST Rate',
                 f"CGST Amt({self.PDF_CURRENCY})", 'SGST Rate', f"SGST Amt({self.PDF_CURRENCY})",
                 f"Total Tax({self.PDF_CURRENCY})"],
                [hsn, f"{subtotal:.2f}", f"{self.GST_CGST_RATE * 100:.1f}%", f"{total_cgst:.2f}",
                 f"{self.GST_SGST_RATE * 100:.1f}%", f"{total_sgst:.2f}", f"{total_tax:.2f}"],
                ['TOTAL', f"{subtotal:.2f}", '', f"{total_cgst:.2f}", '', f"{total_sgst:.2f}", f"{total_tax:.2f}"],
            ], colWidths=[0.9 * inch, 1.1 * inch, 0.8 * inch, 0.9 * inch, 0.8 * inch, 0.9 * inch, 1.2 * inch])
            tax_summary.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))

            amount_panel = Table([
                ['Sub Total', self.format_pdf_currency(subtotal, space=True)],
                ['Total Tax', self.format_pdf_currency(total_tax, space=True)],
                ['Gross Total', self.format_pdf_currency(grand_total, space=True)],
                ['Previous Balance', self.format_pdf_currency(previous_balance, space=True)],
                ['Advance Received', self.format_pdf_currency(advance_received, space=True)],
                ['Round Off', self.format_pdf_currency(round_off, space=True)],
                ['Net Payable', self.format_pdf_currency(net_payable, space=True)],
                ['Invoice Amount in Words:', f"Rupees {amount_in_words} only"],
                ['Balance', self.format_pdf_currency(net_payable, space=True)],
            ], colWidths=[2.2 * inch, 4.4 * inch])
            amount_panel.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (1, 0), (1, 6), 'RIGHT'),
                ('ALIGN', (1, 7), (1, 7), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(tax_summary)
            story.append(amount_panel)

            terms = Table([[
                Paragraph(
                    "<b>Terms & Conditions:</b><br/>"
                    "Thanks for doing business with us!<br/>"
                    "Please note that goods sold are non-returnable.",
                    styles['Normal']
                )
            ]], colWidths=[6.6 * inch])
            terms.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(terms)

            bank_and_sign = Table([[
                Paragraph(
                    "<b>Bank Details:</b><br/>"
                    "Name: UNION BANK OF INDIA,THRISSUR<br/>"
                    "Account No: 117511010000036<br/>"
                    "IFSC code: UBIN0811751<br/>"
                    "Account holder's name:JOY RAPPAI",
                    styles['Normal']
                ),
                Paragraph(
                    f"<b>For {company_name}:</b><br/><br/><br/>Authorized Signatory",
                    styles['Normal']
                )
            ]], colWidths=[4.2 * inch, 2.4 * inch])
            bank_and_sign.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            story.append(bank_and_sign)

            if copy < len(copy_labels):
                story.append(PageBreak())

        doc.build(story)
"""
    
    new_content = content[:start_idx] + old_func + content[end_idx:]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
if __name__ == "__main__":
    main()
