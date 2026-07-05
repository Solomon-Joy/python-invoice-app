import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update createGSTPDF
old_gst_vars = """        company_name = self.COMPANY_NAME
        company_address = self.COMPANY_ADDRESS
        company_phone = self.COMPANY_PHONE
        company_gstin = self.COMPANY_GSTIN
        company_state = self.COMPANY_STATE
        copy_labels = data.get('copyLabels') or self.GST_COPY_LABELS"""

new_gst_vars = """        company_name = self.db.get_setting('COMPANY_NAME', self.COMPANY_NAME)
        company_address = self.db.get_setting('COMPANY_ADDRESS', self.COMPANY_ADDRESS)
        company_phone = self.db.get_setting('COMPANY_PHONE', self.COMPANY_PHONE)
        company_gstin = self.db.get_setting('COMPANY_GSTIN', self.COMPANY_GSTIN)
        company_state = self.db.get_setting('COMPANY_STATE', self.COMPANY_STATE)
        company_pan = self.db.get_setting('COMPANY_PAN', '')
        company_fssai = self.db.get_setting('COMPANY_FSSAI', '')
        company_logo = self.db.get_setting('COMPANY_LOGO', '')
        copy_labels = data.get('copyLabels') or self.GST_COPY_LABELS"""
content = content.replace(old_gst_vars, new_gst_vars)

old_gst_header = """            company_block = Table([[
                Paragraph(
                    f"<b>{company_name}</b><br/>{company_address}<br/>Phone: {company_phone}<br/>"
                    f"State: {company_state} &nbsp;&nbsp;&nbsp;&nbsp; GSTIN: {company_gstin}",
                    styles['Normal']
                )
            ]], colWidths=[6.6 * inch])"""

new_gst_header = """            header_content = []
            if company_logo:
                try:
                    from reportlab.platypus import Image
                    header_content.append(Image(company_logo, width=1.5*inch, height=0.75*inch))
                except Exception:
                    pass
                    
            header_text = f"<b><font size=12>{company_name}</font></b><br/>{company_address}<br/>Phone: {company_phone}<br/>"
            header_text += f"State: {company_state} &nbsp;&nbsp;&nbsp;&nbsp; GSTIN: {company_gstin}"
            if company_pan:
                header_text += f" &nbsp;&nbsp;&nbsp;&nbsp; PAN: {company_pan}"
            if company_fssai:
                header_text += f"<br/><i>fssai</i>: {company_fssai}"
                
            header_content.append(Paragraph(header_text, styles['Normal']))
            
            company_block = Table([header_content], colWidths=None)"""
content = content.replace(old_gst_header, new_gst_header)

# 2. Update createNormalPDF
old_normal_vars = """        # Company Header - Centered
        company_header = [
            ['RINA RICH FOOD & AGENCIES'],
            ['Aranauttukara, Thrissur, Kerala - 680301'],
            ['Phone: +91-9895314201']
        ]"""

new_normal_vars = """        # Company Header - Centered
        company_name = self.db.get_setting('COMPANY_NAME', self.COMPANY_NAME)
        company_address = self.db.get_setting('COMPANY_ADDRESS', self.COMPANY_ADDRESS)
        company_phone = self.db.get_setting('COMPANY_PHONE', self.COMPANY_PHONE)
        company_logo = self.db.get_setting('COMPANY_LOGO', '')
        
        company_header = []
        if company_logo:
            try:
                from reportlab.platypus import Image
                company_header.append([Image(company_logo, width=1.5*inch, height=0.75*inch)])
            except Exception:
                pass
        company_header.extend([
            [company_name],
            [company_address],
            [f"Phone: {company_phone}"]
        ])"""
content = content.replace(old_normal_vars, new_normal_vars)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
