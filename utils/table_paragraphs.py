def create_table_paragraphs_descriptors(table):
    """Creates paragraph-style formatted table output, with each cell described by a header."""
    headers = table[0]
    rows = table[1:]
    output = []
    for row in rows:
        entry = "\n".join(f"**{headers[i]}:** {row[i] if i < len(row) else ''}" for i in range(len(headers)))
        output.append(entry)
    return output

def create_table_paragraphs_by_column(table):
    """
    Converts a table (list of rows, where table[0] is the header) into
    paragraphs where each paragraph starts with a header (prefixed with '##')
    followed by an unordered list of all the values in that column.
    
    Example output:
    
    ## Manann
    * Blessing of Battle
    * Blessing of Breath
    
    ## Morr
    * Blessing of Breath
    * Blessing of Courage
    """
    paragraphs = []
    headers = table[0]
    # For each column index in headers:
    for col_index, header in enumerate(headers):
        # Start a paragraph with a header line:
        lines = [f"## {header}"]
        # Iterate over each data row:
        for row in table[1:]:
            # Check if the row has a cell at this column index.
            if col_index < len(row):
                cell = row[col_index]
                # Only include non-empty cells
                if cell.strip():
                    lines.append(f"* {cell.strip()}")
        paragraphs.append("\n".join(lines))
    return paragraphs
