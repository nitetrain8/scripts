import re

def column_letter(c):
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s = ""
    c -= 1  # 1-based index, skip if 0-based
    while c >= 26:
        s = abc[c % 26] + s
        c = (c) // 26 - 1
    s = abc[c] + s
    return s


def column_number(s):
    i = 0
    ord_a = 65
    for c in s:
        i *= 26
        i += ord(c) - ord_a + 1
    return i  # 1-based index, -1 for 0 based


def _cell_addr(row, col):
    return column_letter(col) + str(row)


def _range_addr(row1, col1, row2, col2):
    return _cell_addr(row1, col1) + ":" + _cell_addr(row2, col2)
    

_cell_addr_match = re.compile("([A-Za-z]+)([1-9][0-9]*)").match
def _parse_addr(a):
    m = _cell_addr_match(a)
    if m:
        col, row = m.groups()
    else:
        raise ValueError(a)
    return col, row


class BasicTable:
    """ Proxy table, represents an excel table given standard
    but unspecified assumptions about use of an excel spreadsheet
    to store a single table. 
    
    The table proxy itself holds all data & info. Proxy objects
    e.g. Row, Column call back to the table itself for info.
    """
    def __init__(self, ws, origin, columns):
        
        self.ws = ws
        self.cr = ws.Cells.Range
        self.Union = ws.Application.Union
        
        # parse origin into coordinates
        # A2 -> (2, 1)
        # note: (row, col), 1-based index
        c, r = _parse_addr(origin)
        left = column_number(c)
        top = int(r)
        self.top = top
        self.left = left
        
        self._data = []
        self._column_labels = []
        self._column_names = []
        self._column_index = {}
        self._column_count = len(columns)
        
        for i, (name, label) in enumerate(columns):
            if name in self._column_index:
                raise ValueError(f"Duplicate column name: '{name}'")
            self._column_index[name] = i
            self._column_labels.append(label)
            self._column_names.append(name)

    def add_row(self, row):
        self._data.append(row)
        
    # row range/addr

    def row_range(self, i):
        return self.cr(self.row_address(i))
    
    def row_address(self, i):
        row = self.top + i + 1
        right = self.left + self._column_count - 1
        return _range_addr(row, self.left, row, right)

    # cell range/addr
    
    def cell_address(self, name, row):
        return self.column_letter(name) + str(self.top + row + 1)
    
    def cell_address2(self, col, row):
        return _cell_addr(self.top + row + 1, self.left + col)

    def cell_range(self, name, row):
        return self.cr(self.cell_address(name, row))

    def cell_range2(self, col, row):
        return self.cr(self.cell_address2(col, row))

    def header_cell_address(self, name):
        col = self._column_index[name]
        return _cell_addr(self.top, self.left + col)

    def header_cell_range(self, name):
        return self.cr(self.header_cell_address(name))
    
    # column range/addr (data only)

    def column_letter(self, name):
        i = self._column_index[name]
        return self.column_letter2(i)
        
    def column_letter2(self, idx):
        c = self.left + idx
        return column_letter(c)
    
    def column_address(self, name: str):
        idx = self._column_index[name]
        return self.column_address2(idx)
    
    def column_address2(self, idx: int):
        top = self.top + 1
        bot = self.top + len(self._data)
        col = idx + self.left
        return _range_addr(top, col, bot, col)
    
    def column_range(self, name: str):
        return self.cr(self.column_address(name))
    
    def column_range2(self, idx: int):
        return self.cr(self.column_address2(idx))

    # column range/addr(header+data)

    def entire_column_address2(self, idx):
        top = self.top
        bot = self.top + len(self._data)
        col = idx + self.left
        return _range_addr(top, col, bot, col)

    def entire_column_address(self, name):
        idx = self._column_index[name]
        return self.entire_column_address2(idx)

    def entire_column_range(self, name):
        return self.cr(self.entire_column_address(name))

    def entire_column_range2(self, idx):
        return self.cr(self.entire_column_address2(idx))

    def column_index(self, name):
        return self._column_index[name]
    
    # bulk range/addr
    
    def data_address(self):
        top = self.top + 1
        left = self.left
        bot = self.top + len(self._data)
        right = self.left + self._column_count - 1
        return _range_addr(top, left, bot, right)
    
    def data_range(self):
        return self.cr(self.data_address())
    
    def header_address(self):
        right = self.left + self._column_count - 1
        return _range_addr(self.top, self.left, self.top, right)
    
    def header_range(self):
        return self.cr(self.header_address())

    def table_address(self):
        bot = self.top + len(self._data)
        right = self.left + self._column_count - 1
        return _range_addr(self.top, self.left, bot, right)

    def table_range(self):
        return self.cr(self.table_address())

    # misc    
        
    def apply_data(self):
        r = self.data_range()
        r.Value2 = self._data
        
    def iter_column_ranges(self):
        for i, _ in enumerate(self._column_names):
            yield self.column_range2(i)
            
    def iter_column_addresses(self):
        for i, _ in enumerate(self._column_names):
            yield self.column_address2(i)
        
    def apply_header(self):
        r = self.header_range()
        r.Value2 = [self._column_labels]  # unsure if this needs to be wrapped