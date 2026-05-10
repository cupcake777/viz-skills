# Editing Presentations with python-pptx

## When to Use

Use `python-pptx` when you need to make **surgical text/number changes** or **replace images** in an existing PPTX without restructuring the deck. For major restructuring (adding/removing slides, changing layouts), prefer the unpack/edit XML/pack workflow.

## Setup

```bash
pip install python-pptx Pillow
```

## Key Patterns

### 1. Inspect Before Editing

Always inspect slide structure first to find shape IDs, types, and content:

```python
from pptx import Presentation

prs = Presentation('input.pptx')
for idx, slide in enumerate(prs.slides):
    print(f'=== SLIDE {idx+1} ===')
    for s in slide.shapes:
        stype = str(s.shape_type)
        has_img = 'IMG' if hasattr(s, 'image') else ''
        has_tbl = 'TBL' if s.has_table else ''
        txt = s.text_frame.text[:80] if s.has_text_frame else ''
        print(f'  {s.name} id={s.shape_id} type={stype} {has_img}{has_tbl} text={txt}')
```

For tables specifically:
```python
for s in slide.shapes:
    if s.has_table:
        t = s.table
        for r_idx, row in enumerate(t.rows):
            cells = [row.cells[c_idx].text for c_idx in range(len(t.columns))]
            print(f'  Row {r_idx}: {cells}')
```

### 2. Replace Text in Multi-Run Paragraphs

**⚠️ PITFALL**: PowerPoint paragraphs often split text across multiple `<a:r>` (run) elements with separate formatting. Simply setting `para.text = "new text"` works but destroys all formatting. To replace text while preserving basic formatting:

```python
def replace_in_paragraph(para, old, new):
    """Replace text in a paragraph, keeping first run's formatting."""
    if old not in para.text:
        return False
    new_text = para.text.replace(old, new)
    if para.runs:
        para.runs[0].text = new_text
        for r in para.runs[1:]:
            r.text = ''
    else:
        para.text = new_text
    return True
```

**Key insight**: Concatenate all runs to get full text, then put the entire replacement into `runs[0]` and clear the rest. This preserves the first run's font/color/size while ensuring correct display.

### 3. Replace Images in Place

**⚠️ PITFALL**: `python-pptx` has NO `shape.image.replace()` method. You must:
1. Save the old shape's position/size
2. Remove the old shape's XML element from the spTree
3. Add a new picture at the same position

```python
def replace_picture(slide, shape_id, new_image_path):
    """Replace a picture by shape_id at the same position/size."""
    old_shape = None
    for shape in slide.shapes:
        if shape.shape_id == shape_id and shape.shape_type == 13:  # PICTURE
            old_shape = shape
            break
    if old_shape is None:
        return False
    
    left, top, width, height = old_shape.left, old_shape.top, old_shape.width, old_shape.height
    sp = old_shape._element
    sp.getparent().remove(sp)
    slide.shapes.add_picture(new_image_path, left, top, width, height)
    return True
```

Alternative: find by shape name instead of ID:

```python
for shape in slide.shapes:
    if shape.name == '图片 5' and shape.shape_type == 13:
        # ... same replacement logic
```

### 4. Add New Images

```python
from pptx.util import Emu, Inches

# Position at specific EMU coordinates (from inspection)
slide.shapes.add_picture('path/to/img.png', Emu(860533), Emu(988496), Emu(10470933), Emu(5652052))

# Or use Inches
slide.shapes.add_picture('path/to/img.png', Inches(1), Inches(2), Inches(5), Inches(3))
```

### 5. Add Text Boxes

```python
from pptx.util import Pt

txBox = slide.shapes.add_textbox(Emu(860533), Emu(6800000), Emu(10000000), Emu(500000))
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "Your text here"
p.font.size = Pt(12)
p.font.italic = True
```

### 6. Edit Table Cells

```python
table.rows[1].cells[0].text = "New value"
# Note: this strips all formatting from the cell
# For formatted cells, manipulate runs instead
```

## Common Pitfalls

### Encrypted/Invalid Image Files
**Always verify image files before using them with python-pptx.** Files that appear to be `.png` may actually be encrypted (OpenPGP) or otherwise invalid. Use `file` command to check:

```bash
file /path/to/image.png
# Should output: "PNG image data, ..."
# BAD: "OpenPGP Secret Key" or "data"
```

`python-pptx` will throw `PIL.UnidentifiedImageError` on invalid images, crashing your script.

### Shape Type Constants
```python
MSO_SHAPE_TYPE.PICTURE == 13  # Check with: shape.shape_type == 13
MSO_SHAPE_TYPE.TABLE == 19
MSO_SHAPE_TYPE.TEXT_BOX == 17
MSO_SHAPE_TYPE.PLACEHOLDER == 14
MSO_SHAPE_TYPE.GROUP == 6
```

### Chinese Shape Names
PowerPoint shapes in CJK locales use Chinese names: `图片` (Picture), `文本框` (TextBox), `表格` (Table), `标题` (Title), `组合` (Group). Match by shape_id or shape_type instead of name when possible.

### Performance: Timeout on Large Decks
Inspection scripts on large PPTX files can timeout. Break inspection into per-slide calls or target specific slides by index rather than iterating all slides at once.

## Full Workflow Example

```python
import shutil
from pptx import Presentation
from pptx.util import Emu, Pt

# 1. Copy original before editing
shutil.copy2('original.pptx', 'updated.pptx')
prs = Presentation('updated.pptx')

# 2. Inspect target slides
slide = prs.slides[9]  # 0-indexed

# 3. Replace text in specific shapes
for shape in slide.shapes:
    if shape.has_text_frame and 'old text' in shape.text_frame.text:
        for para in shape.text_frame.paragraphs:
            replace_in_paragraph(para, 'old text', 'new text')

# 4. Replace images
replace_picture(slide, shape_id=6, new_image_path='new_fig.png')

# 5. Add new images
slide.shapes.add_picture('extra_fig.png', Emu(5500000), Emu(6600000), Emu(5000000), Emu(2300000))

# 6. Save
prs.save('updated.pptx')
```

## Copying the Original First

Always `shutil.copy2()` the original PPTX before opening it for editing. This preserves the source and lets you re-run the script without corruption from partial edits.