"""Exact owner-authorized withdrawal of three unlicensed legacy reference photographs."""
WITHDRAWN_MASK_PHOTOS = {'assets/page-art/joseph-smith-likeness/hyrum-death-mask.jpg': 'fc5d6713c6c620c92b83355b8c97c18afad5e401', 'assets/page-art/joseph-smith-likeness/joseph-death-mask.jpg': 'e8c099a38cd19c58d1f7c527305c8e8af02c7d8f', 'assets/page-art/joseph-smith-likeness/museum-dibble-masks.jpg': '0260f0bd39d0b3fcb911531507a8f5a65b44ff11'}

def withdrawn_mask_photo(name, baseline_blob, root):
    if name not in WITHDRAWN_MASK_PHOTOS:
        return False
    assert baseline_blob == WITHDRAWN_MASK_PHOTOS[name], 'Withdrawal baseline identity changed: ' + name
    assert not (root / name).exists(), 'Withdrawn photograph returned to public assets: ' + name
    return True
