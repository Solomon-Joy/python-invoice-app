import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will replace the newlines inside the single/double quotes with \n if they are broken.
# Actually, it's easier to just overwrite those specific blocks.

items_data_replacement = """            items_data = [[
                'Sl.\\nNo.', 'Description of Goods', 'HSN / Acc\\nCode', 'Qty', 'MRP',
                'Unit\\nPrice', 'Total', 'Disc\\n%', 'Taxable\\nValue', 'CGST\\nRate | Amount', '', 'SGST\\nRate | Amount', ''
            ]]
            
            # Hack for header spanning
            # We want Rate and Amount under CGST, and Rate and Amount under SGST
            # So row 0 is main header, row 1 is sub header
            items_data = [
                ['Sl.\\nNo.', 'Description of Goods', 'HSN / Acc\\nCode', 'Qty', 'MRP', 'Unit\\nPrice', 'Total', 'Disc\\n%', 'Taxable\\nValue', 'CGST', '', 'SGST', ''],
                ['', '', '', '', '', '', '', '', '', 'Rate', 'Amount', 'Rate', 'Amount']
            ]"""

footer_data_replacement = """            # Footer
            footer_data = [
                [f"Amount in Words:\\n{amount_in_words} Only", '', '', f"Total\\nRounded off", f"{net_payable:.2f}"],
                [
                    "Bank Details : Acc. No : 462133853\\nIFSC : IDIB000T054, INDIAN BANK\\nPB NO : 12, SWARAJ ROUND EAST\\nBR. NO : THRISSUR. 275.", 
                    '', '', 
                    f"Invoice Total", f"{net_payable:.2f}"
                ],
                ["Certified that the particulars given above are true and correct", '', '', '', ''],
                ["Remarks if any :", '', "For RINA RICH FOOD & AGENCIES", '', ''],
                ['', '', "(authorised signatory)", '', '']
            ]"""

# Since I know roughly where they are, let's just do a regex replace or string replace.
# Actually, I can just find the start and end of these blocks.

def replace_block(content, start_str, end_str, replacement):
    start = content.find(start_str)
    end = content.find(end_str) + len(end_str)
    if start == -1 or content.find(end_str) == -1:
        print(f"Could not find block: {start_str}")
        return content
    return content[:start] + replacement + content[end:]

start_items = "            # Items\n            items_data = [["
end_items = "            ]\n            items_data.extend(item_rows)"
content = replace_block(content, start_items, end_items, "            # Items\n" + items_data_replacement)

start_footer = "            # Footer\n            footer_data = ["
end_footer = "                ['', '', \"(authorised signatory)\", '', '']\n            ]"
content = replace_block(content, start_footer, end_footer, footer_data_replacement)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
