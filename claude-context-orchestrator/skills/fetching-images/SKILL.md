---
name: Fetching Relevant Images
description: Find, fetch, and legally use images from the web. Covers Wikimedia Commons, free sources, copyright, fair use, and embedding. Use when you need images for any project.
keywords: images, photos, wikimedia, unsplash, pixabay, copyright, fair use, embedding, CC0, public domain
---

# Fetching Relevant Images

## Use Cases

- Images for HTML templates, documents, presentations
- Need proper attribution and legal use
- Finding high-quality free images

## Source Selection

**Need an image?**

- **Personal/Educational (not published)**: Wikimedia Commons (attribution required) or Unsplash/Pexels/Pixabay (CC0, no attribution)
- **Published (blog, website)**: CC0 sources safest, Wikimedia Commons good with attribution
- **Commercial**: Must use CC0 or commercial licenses

## License Types

| License | Attribution? | Commercial? | Modifications? |
|---------|--------------|-------------|----------------|
| CC0 | No | Yes | Yes |
| CC BY | Yes | Yes | Yes |
| CC BY-SA | Yes | Yes | Yes (same license) |
| Public Domain | No | Yes | Yes |

## Free Image Sources

### CC0 (No Attribution Required)

**Pixabay** (pixabay.com) - 5.7M+ images, proprietary license (formerly CC0), no attribution
**Unsplash** (unsplash.com) - 300K+ photos, high-quality, no attribution
**Pexels** (pexels.com) - Photos/videos, clean aesthetic, no attribution
**Others**: Burst (burst.shopify.com), StockSnap (stocksnap.io)

### Attribution Required

**Wikimedia Commons** (commons.wikimedia.org) - 100M+ files, CC BY or CC BY-SA, best for historical/cultural/educational content
**Flickr Commons** (flickr.com/commons) - Public domain from 70+ institutions

## Workflows

### Option 1: Programmatic Script (Easiest)

Use the helper script for automated extraction:

```bash
# Step 1: Search for images
python3 scripts/fetch_wikimedia_image.py "paella valenciana"

# Step 2: Extract URL from File: page (copy URL from WebSearch results)
python3 scripts/fetch_wikimedia_image.py \
  --file-page "https://commons.wikimedia.org/wiki/File:01_Paella_Valenciana_original.jpg" \
  --verify --html --alt "Authentic Valencian paella"
```

**Output:**
```
📸 Image Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Filename:     01_Paella_Valenciana_original.jpg
Direct URL:   https://upload.wikimedia.org/wikipedia/commons/e/ed/01_Paella_Valenciana_original.jpg
License:      CC BY-SA (check file page for exact version)
Attribution:  Photo: Wikimedia Commons, [License]

🔍 Verifying URL...
   ✅ URL verified (HTTP 200, valid image)

📝 HTML Snippet
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<div class="image-container">
    <img src="https://upload.wikimedia.org/..." alt="Authentic Valencian paella">
    <div class="image-caption">
        Authentic Valencian paella (Photo: Wikimedia Commons, CC BY-SA 2.0)
    </div>
</div>
```

**Script location:** `${CLAUDE_PLUGIN_ROOT}/skills/fetching-images/scripts/fetch_wikimedia_image.py`

### Option 2: Manual Workflow (Full Control)

1. **Search**: `site:commons.wikimedia.org [topic] file jpg`
2. **Find File: page**: Navigate to `File:Image_name.jpg`
3. **Extract direct URL**:
   ```bash
   WebFetch("https://commons.wikimedia.org/wiki/File:...",
            "Get the direct https://upload.wikimedia.org URL")
   ```
   - Look for: `https://upload.wikimedia.org/wikipedia/commons/[hash]/[filename]`
4. **Verify URL**:
   ```bash
   curl -I "https://upload.wikimedia.org/wikipedia/commons/7/72/2008_Sagrada_Familia_11.JPG"
   # Should return: HTTP/2 200
   ```
5. **Add attribution**:
   ```html
   <img src="https://upload.wikimedia.org/..." alt="Description">
   <p class="attribution">Photo: [Author] via Wikimedia Commons, [License]</p>
   ```

**Attribution formats**:
- "Photo: Wikimedia Commons, CC BY-SA 4.0"
- "Photo: [Photographer] via Wikimedia Commons, CC BY 2.0"
- "Source: Wikimedia Commons (Public Domain)"

### CC0 Sources (Easiest)

1. **Search**: Visit site or `site:unsplash.com [topic]`
2. **Download**: Click Download or copy image address
3. **Use**:
   ```html
   <img src="https://images.unsplash.com/..." alt="Description">
   <!-- Attribution optional but appreciated -->
   ```

## Fair Use (U.S. Law)

Four-factor test determines fair use:

1. **Purpose**: Educational/nonprofit favored, commercial disfavored, transformative favored
2. **Nature**: Factual works favored, creative less favored
3. **Amount**: Small portions favored, entire work disfavored
4. **Market effect**: No harm favored, substitution disfavored

**Important**: Fair use is case-by-case. Educational doesn't automatically qualify. When in doubt, use licensed images.

## Technical Best Practices

### Never Hotlink

❌ `<img src="https://someones-site.com/their-image.jpg">`
✅ `<img src="./images/my-image.jpg">` or `<img src="https://upload.wikimedia.org/...">`

### Always Verify URLs

```bash
curl -I "[image-url]" | grep -E "(HTTP|content-type)"
# Should see: HTTP/2 200, content-type: image/jpeg
```

### Wikimedia URL Extraction

❌ Don't guess URLs (hash directory is MD5-based, unpredictable)
✅ Extract from File: page using WebFetch

### Responsive Images

```html
<img src="image-800.jpg"
     srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
     sizes="(max-width: 600px) 400px, (max-width: 1000px) 800px, 1200px"
     alt="Description">
```

### Lazy Loading

```html
<img src="image.jpg" loading="lazy" alt="Description">
```

## Common Mistakes

❌ **"I can guess Wikimedia URLs"** → Hash directories are MD5-based and unpredictable. Always extract from File: page.
  - Example: Guessing `/commons/5/50/Image.jpg` when it's actually `/commons/7/72/Image.jpg` = 404 error
  - **Solution:** Use WebFetch or the script to extract the real URL

❌ **"Skip URL verification"** → Even correct-looking URLs can be broken. Always verify with curl.
  - **Solution:** `curl -I [url] | grep HTTP` should show HTTP 200

❌ **"Google Images = free"** → Check license, use Advanced Search → Usage Rights → "Free to use or share"
❌ **"Personal use = no copyright"** → License terms always apply
❌ **"Giving credit = allowed"** → Need proper license, then add attribution
❌ **"Educational = fair use"** → All four factors must be considered
❌ **"No watermark = free"** → Find source and check explicit license

## Lessons from Practice

**From real debugging sessions:**

1. **404 errors from Wikimedia?** → You guessed the URL structure. Extract it properly instead.
   - URLs have hash-based paths: `/commons/[hash]/[filename]`
   - The hash is MD5-based on the filename, but unpredictable without calculation
   - **Fix:** Always use WebFetch to extract from the File: page

2. **Images not showing in browser?** → Verify the URL actually works before embedding.
   - Even if URL looks correct, test with: `curl -I [url]`
   - Check for HTTP 200 and `content-type: image/jpeg`

3. **Which workflow to use?**
   - Quick/single image: Use the script (`--file-page --verify --html`)
   - Multiple images: Manual WebFetch workflow for batch processing
   - Learning/understanding: Manual workflow to see each step

## Code Examples

### HTML with Attribution

```html
<figure>
  <img src="https://upload.wikimedia.org/wikipedia/commons/7/72/2008_Sagrada_Familia_11.JPG"
       alt="Sagrada Familia stained glass window" loading="lazy">
  <figcaption>
    Sagrada Familia, Barcelona
    <br><small>Photo: Wikimedia Commons, CC BY-SA 2.5</small>
  </figcaption>
</figure>
```

### CSS Attribution Styling

```css
.attribution {
  font-size: 0.85rem;
  color: var(--muted);
  font-style: italic;
  margin-top: 0.5rem;
}
```

### JavaScript Image Verification

```javascript
const img = new Image();
img.onload = () => console.log('✅ Image loaded:', img.naturalWidth + 'x' + img.naturalHeight);
img.onerror = () => console.error('❌ Image failed to load');
img.src = 'your-image-url.jpg';
```

## Quick Checklist

- [ ] License identified? (CC0, CC BY, CC BY-SA, Fair Use)
- [ ] Allows intended use? (Personal, published, commercial)
- [ ] Attribution needed? (Prepared to add)
- [ ] URL verified? (`curl -I [url]`)
- [ ] Not hotlinking? (Download or use allowed CDN)
- [ ] Quality sufficient? (Check resolution)
- [ ] Culturally appropriate? (Check context)

## Resources

**Official**:
- U.S. Copyright Office Fair Use: copyright.gov/fair-use/
- Creative Commons Licenses: creativecommons.org/licenses/
- Wikimedia Commons License Guide: commons.wikimedia.org/wiki/Commons:Licensing

**Search Tools**:
- Google Images Advanced → Usage Rights
- Creative Commons Search: search.creativecommons.org/
- Wikimedia Commons Search: commons.wikimedia.org/

## Summary

**Personal/Educational**:
1. Pixabay/Unsplash/Pexels (CC0, easiest)
2. Wikimedia Commons (highest quality, needs attribution)
3. Always verify URLs
4. License terms apply even for personal use

**Published/Commercial**:
1. Use CC0 or commercial licenses only
2. Double-check each image's terms
3. When in doubt, use CC0 or consult lawyer

**Key**: Millions of free, high-quality images exist legally. Use them instead of risking copyright infringement.
