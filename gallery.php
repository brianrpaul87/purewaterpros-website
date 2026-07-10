<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Our Work — Pure Water Pros</title>
<meta name="description" content="Pure Water Pros — Water treatment experts serving Durham, Peterborough & surrounding area."/>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v=6"></head><body>
<header><div class="container nav"><div class="brand"><a href="/" class="name">Pure Water Pros</a><span class="tag">Durham, Peterborough & Area</span></div>
<nav style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
<a class="btn" href="/well-water-issues.html">Well Water Issues</a>
<a class="btn" href="/city-water-issues.html">City Water Issues</a>
<a class="btn" href="/gallery.php">Our Work</a>
<a class="btn" href="/services/softeners.html">Softeners</a>
<a class="btn" href="/contact.html">Get a quote</a>
</nav></div></header><main>
<div class="container"><h1 class="title">Our Work</h1>
<p class="lead">Check out our recent installs!<code></code></p>



<div class="equip-grid" style="margin-top:14px">
<?php
/**
 * Auto-gallery with on-the-fly image resizing + caching + lightbox.
 * Originals live in /images/gallery/. Resized copies in /images/gallery/_cache/.
 */

$dir = __DIR__ . '/images/gallery';
$url = 'images/gallery';
$cacheDir = $dir . '/_cache';
$cacheUrl = $url . '/_cache';
$ext = ['jpg','jpeg','png','gif','webp'];
$targetWidths = [480, 800, 1200, 1600]; // responsive sizes
$jpegQuality = 78;  // 0–100
$webpQuality = 72;  // 0–100
$preferWebp = function_exists('imagewebp'); // use WebP if GD supports it

// Ensure cache directory exists
if (!is_dir($cacheDir)) { @mkdir($cacheDir, 0755, true); }

function pretty_label($name) {
  $name = pathinfo($name, PATHINFO_FILENAME);
  $name = str_replace(['-', '_'], ' ', $name);
  $name = preg_replace('/\s+/', ' ', $name);
  return ucwords(trim($name));
}

function load_image_resource($path, $ext) {
  switch ($ext) {
    case 'jpg':
    case 'jpeg': return @imagecreatefromjpeg($path);
    case 'png':  return @imagecreatefrompng($path);
    case 'gif':  return @imagecreatefromgif($path);
    case 'webp': return function_exists('imagecreatefromwebp') ? @imagecreatefromwebp($path) : false;
    default:     return false;
  }
}

// Basic EXIF orientation fix for JPEG
function fix_orientation($img, $path, $ext) {
  if (!in_array($ext, ['jpg','jpeg'])) return $img;
  if (!function_exists('exif_read_data')) return $img;
  $exif = @exif_read_data($path);
  if (!isset($exif['Orientation'])) return $img;
  $o = (int)$exif['Orientation'];
  if ($o === 3) { $img = imagerotate($img, 180, 0); }
  elseif ($o === 6) { $img = imagerotate($img, -90, 0); }
  elseif ($o === 8) { $img = imagerotate($img, 90, 0); }
  return $img;
}

function resize_and_cache($srcPath, $dstPath, $maxW, $jpegQ, $webpQ, $preferWebp) {
  $ext = strtolower(pathinfo($srcPath, PATHINFO_EXTENSION));
  $img = load_image_resource($srcPath, $ext);
  if (!$img) return false;
  $img = fix_orientation($img, $srcPath, $ext);
  $w = imagesx($img); $h = imagesy($img);
  if ($w <= $maxW) {
    $newW = $w; $newH = $h;
  } else {
    $scale = $maxW / $w;
    $newW = (int)round($w * $scale);
    $newH = (int)round($h * $scale);
  }
  $dst = imagecreatetruecolor($newW, $newH);
  // preserve transparency for PNG/GIF
  if (in_array($ext, ['png','gif','webp'])) {
    imagealphablending($dst, false);
    imagesavealpha($dst, true);
    $transparent = imagecolorallocatealpha($dst, 0, 0, 0, 127);
    imagefilledrectangle($dst, 0, 0, $newW, $newH, $transparent);
  }
  imagecopyresampled($dst, $img, 0,0,0,0, $newW,$newH, $w,$h);

  $outExt = $preferWebp ? 'webp' : 'jpg';
  $dstPathFinal = preg_replace('/\.\w+$/', '', $dstPath) . "." . $outExt;

  $ok = false;
  if ($preferWebp) {
    $ok = @imagewebp($dst, $dstPathFinal, $webpQ);
  } else {
    $ok = @imagejpeg($dst, $dstPathFinal, $jpegQ); // flatten transparency as needed
  }

  imagedestroy($img);
  imagedestroy($dst);
  return $ok ? $dstPathFinal : false;
}

if (is_dir($dir)) {
  // Collect source files
  $files = array_filter(scandir($dir), function($f) use ($ext,$dir){
    if ($f === '_cache' || $f === '.' || $f === '..') return false;
    $extn = strtolower(pathinfo($f, PATHINFO_EXTENSION));
    return in_array($extn, $ext) && is_file("$dir/$f");
  });
  // newest first
  usort($files, fn($a,$b)=>filemtime("$dir/$b")<=>filemtime("$dir/$a"));

  $index = -1;
  foreach ($files as $f) {
    $index++;
    $src = "$dir/$f";
    $mtime = filemtime($src);
    $label = htmlspecialchars(pretty_label($f), ENT_QUOTES);
    $safe = htmlspecialchars($f, ENT_QUOTES);

    // Build cached variants + srcset
    $displayW = 1200;
    $sources = [];
    foreach ($targetWidths as $w) {
      $cacheBase = $cacheDir . '/' . pathinfo($f, PATHINFO_FILENAME) . '_' . $w;
      $existingWebp = $cacheBase . '.webp';
      $existingJpg  = $cacheBase . '.jpg';
      $candidate = file_exists($existingWebp) ? $existingWebp : (file_exists($existingJpg) ? $existingJpg : null);
      if (!$candidate || filemtime($candidate) < $mtime) {
        $generated = resize_and_cache($src, $cacheBase . '.' . pathinfo($f, PATHINFO_EXTENSION), $w, $jpegQuality, $webpQuality, $preferWebp);
        $candidate = $generated ?: $candidate;
      }
      if ($candidate) {
        $sources[] = [
          'url' => htmlspecialchars($cacheUrl . '/' . basename($candidate), ENT_QUOTES),
          'w'   => $w
        ];
      }
    }

    // Pick best match for main src (closest to displayW) and the largest for "full-size"
    $main = null;
    $full = null;
    $bestDiff = PHP_INT_MAX;
    $maxW = -1;
    foreach ($sources as $s) {
      $diff = abs($s['w'] - $displayW);
      if ($diff < $bestDiff) { $bestDiff = $diff; $main = $s; }
      if ($s['w'] > $maxW) { $maxW = $s['w']; $full = $s; }
    }

    // Build srcset string
    $srcset = implode(', ', array_map(fn($s)=> $s['url'] . ' ' . $s['w'] . 'w', $sources));
    $sizes = '(max-width: 640px) 95vw, (max-width: 1024px) 50vw, 33vw';

    if ($main) {
      $mainUrl = $main['url'];
      $fullUrl = $full ? $full['url'] : ($url . '/' . $safe);
      echo "<figure class='equip' data-index='{$index}'>\n";
      echo "  <a href='{$fullUrl}' class='glink' data-full='{$fullUrl}' data-alt='{$label}' aria-label='Open full size: {$label}'>\n";
      echo "    <img src='{$mainUrl}' srcset='{$srcset}' sizes='{$sizes}' alt='{$label}' loading='lazy' decoding='async'>\n";
      echo "  </a>\n";
      echo "  <figcaption class='cap'>{$label}</figcaption>\n";
      echo "</figure>\n";
    } else {
      // Fallback: original (last resort)
      echo "<figure class='equip' data-index='{$index}'>\n";
      echo "  <a href='{$url}/{$safe}' class='glink' data-full='{$url}/{$safe}' data-alt='{$label}'>\n";
      echo "    <img src='{$url}/{$safe}' alt='{$label}' loading='lazy' decoding='async'>\n";
      echo "  </a>\n";
      echo "  <figcaption class='cap'>{$label}</figcaption>\n";
      echo "</figure>\n";
    }
  }
} else {
  echo "<p>No gallery folder found. Please create <code>/images/gallery/</code>.</p>";
}
?>
</div>

<!-- Lightweight Lightbox with Prev/Next -->
<style>
  .pwplb { position: fixed; inset: 0; display:none; align-items:center; justify-content:center; background: rgba(15,23,42,0.85); z-index: 9999; padding: 20px; }
  .pwplb.open { display:flex; }
  .pwplb img { max-width: 95vw; max-height: 78vh; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,.4); }
  .pwplb .meta { margin-top: 12px; color: #fff; font: 500 14px/1.4 system-ui, -apple-system, Segoe UI, Roboto, Arial; text-align: center; }
  .pwplb .close, .pwplb .nav { position:absolute; background: rgba(255,255,255,.92); border:0; border-radius:999px; padding:10px 14px; cursor:pointer; }
  .pwplb .close { top:14px; right:14px; }
  .pwplb .nav { top:50%; transform: translateY(-50%); }
  .pwplb .nav.prev { left:14px; }
  .pwplb .nav.next { right:14px; }
  @media (max-width: 640px){
    .pwplb .nav { padding:8px 10px; }
  }
</style>
<div class="pwplb" id="pwplb" role="dialog" aria-modal="true" aria-label="Full-size image viewer">
  <button class="close" id="pwplbClose" aria-label="Close">Close ✕</button>
  <button class="nav prev" id="pwplbPrev" aria-label="Previous image">◀</button>
  <div class="inner" style="text-align:center;">
    <img id="pwplbImg" alt="">
    <div class="meta" id="pwplbCap"></div>
  </div>
  <button class="nav next" id="pwplbNext" aria-label="Next image">▶</button>
</div>
<script>
  (function(){
    const lb = document.getElementById('pwplb');
    const img = document.getElementById('pwplbImg');
    const cap = document.getElementById('pwplbCap');
    const btnClose = document.getElementById('pwplbClose');
    const btnPrev = document.getElementById('pwplbPrev');
    const btnNext = document.getElementById('pwplbNext');

    // Collect gallery anchors (order matters)
    const figures = Array.from(document.querySelectorAll('figure.equip'));
    const links = figures.map(f => f.querySelector('a.glink'));

    let idx = -1;

    function show(i){
      if (i < 0 || i >= links.length) return;
      idx = i;
      const a = links[idx];
      img.src = a.dataset.full;
      img.alt = a.dataset.alt || '';
      cap.textContent = a.dataset.alt || '';
      lb.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function close(){
      lb.classList.remove('open');
      img.src = '';
      document.body.style.overflow = '';
    }
    function prev(){ if (idx > 0) show(idx - 1); }
    function next(){ if (idx < links.length - 1) show(idx + 1); }

    document.addEventListener('click', function(e){
      const a = e.target.closest('a.glink');
      if(!a) return;
      e.preventDefault();
      const i = links.indexOf(a);
      show(i);
    });

    btnClose.addEventListener('click', close);
    btnPrev.addEventListener('click', prev);
    btnNext.addEventListener('click', next);

    lb.addEventListener('click', (e)=>{ if(e.target === lb) close(); });

    document.addEventListener('keydown', (e)=>{
      if(!lb.classList.contains('open')) return;
      if(e.key === 'Escape') close();
      if(e.key === 'ArrowLeft') prev();
      if(e.key === 'ArrowRight') next();
    });
  })();
</script>
</main><footer><div class="container foot">
<div><strong>Pure Water Pros</strong> · <a href="mailto:info@purewaterpros.ca">info@purewaterpros.ca</a> · <a href="tel:19052423846">905-242-3846</a></div>
<div>© <span id="year"></span> Pure Water Pros. Serving Durham, Peterborough & Surrounding Area.</div>
</div></footer><script>document.getElementById('year').textContent=new Date().getFullYear();</script></body></html>