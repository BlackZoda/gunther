from utils.obsidian_utils import clean_obsidian_links

def parse_markdown_table(md_text):
    """Parses a Markdown table into a list of lists, preserving empty cells."""
    rows = md_text.strip().split("\n")
    if len(rows) < 3:
        return []
    
    # Process header
    header = [clean_obsidian_links(col.strip()) for col in rows[0].strip("|").split("|")]
    if header[0] == "":
        header[0] = " "  # Preserve leading empty cell instead of shifting
    table = [header]
    
    # Process table body
    for row in rows[2:]:

        row_data = [clean_obsidian_links(col.strip()) for col in row.split("|")]

        if row_data[0] == "":
            row_data[0] = " "  # Ensure first column remains correctly positioned

        row_data = row_data[1:-1]

        while len(row_data) < len(header):
            row_data.append("")  # Ensure each row has the same number of columns
        table.append(row_data[:len(header)])  # Truncate excess columns if needed

    return table
