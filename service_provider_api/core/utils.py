def list_pairs(sequence):
    if not sequence:
        return []
    it = iter(sequence)
    return zip(it, it)
