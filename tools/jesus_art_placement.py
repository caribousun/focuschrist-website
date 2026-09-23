"""Keep source-specific story images beside their explicitly selected paragraph."""
def place_artwork(blocks, keys, positions):
    prose=[b for b in blocks if isinstance(b,str)]
    other=[b for b in blocks if not isinstance(b,str) and 'art' not in b]
    if not any(key in positions for key in keys):
        # Preserve the established default for sections without reviewed overrides.
        merged=[]
        for i in range(max(len(prose),len(keys))):
            if i<len(prose):merged.append(prose[i])
            if i<len(keys):merged.append({'art':keys[i]})
        return merged+other
    groups={}
    for i,key in enumerate(keys):
        after=positions.get(key,min(i+1,len(prose)))
        if type(after) is not int or not 1<=after<=len(prose):
            raise ValueError('Invalid afterParagraph for '+key)
        groups.setdefault(after,[]).append(key)
    merged=[]
    for i,paragraph in enumerate(prose,1):
        merged.append(paragraph)
        merged.extend({'art':key} for key in groups.get(i,[]))
    return merged+other
