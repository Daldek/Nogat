// Applies the stored theme before first paint; "auto" (or nothing) follows the OS.
try {
  var t = localStorage.getItem("nogat-theme");
  if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
} catch (e) {}
