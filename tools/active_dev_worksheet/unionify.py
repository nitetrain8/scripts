def group_chunks(thelist, n):
    """Groups items in `thelist` into groups of n.
    Extra items are returned in a shorter list (no
    fillvalue).

    Args:
        thelist (list | tuple): List of items to group
        n (int): Size of each chunk

    Yields:
        list[object]: List of objects.
    """    
    chunks, xtra = divmod(len(thelist), n)
    if xtra:
        chunks += 1
    for i in range(chunks):
        yield thelist[n*i:n*i+n]

def unionify_addresses(addresses, range_obj, U):
    # the range_object can take up to 30 comma separated addresses
    # at a time but no more. To unionify address strings, combine into
    # groups of 30 once, turn into range objects, and then recursively
    # build them into the union
    if not addresses:
        return None
    ranges = [range_obj(','.join(chunk)) for chunk in group_chunks(addresses, 20)]
    if len(ranges) == 1:
        return ranges[0]
    return unionify_ranges(ranges, U)
    
def unionify_ranges(ranges, U):
    if not ranges:
        return None
    chunks = ranges
    while len(chunks) > 30:
        chunks = [U(*chunk) for chunk in group_chunks(chunks, 30)]
    if len(chunks) == 1:
        return chunks[0]
    return U(*chunks)