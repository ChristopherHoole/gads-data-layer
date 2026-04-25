/* Fix 1.6 follow-up — PMax CSV upload modal handler.
 * Renders the modal, posts multipart to /v2/api/csv/upload, surfaces
 * a toast. The actual ingestion happens in the watcher process via
 * watchdog's on_created event after the file lands in incoming/. */
(function () {
  const btn      = document.getElementById('mrCsvUploadBtn');
  const overlay  = document.getElementById('mrCsvUploadOverlay');
  if (!btn || !overlay) return;

  const clientSel = document.getElementById('mrCsvUploadClient');
  const fileInput = document.getElementById('mrCsvUploadFile');
  const submitBtn = document.getElementById('mrCsvUploadSubmit');
  const cancelBtn = document.getElementById('mrCsvUploadCancel');

  function toast(msg, kind) {
    // Reuse the morning-review toast if available; otherwise alert().
    const host = document.getElementById('mrToast');
    if (!host) { (kind === 'error' ? alert : console.log)(msg); return; }
    host.textContent = msg;
    host.className = 'st-toast' + (kind === 'error' ? ' st-toast--error' : '');
    host.style.display = 'block';
    clearTimeout(toast._t);
    toast._t = setTimeout(() => { host.style.display = 'none'; }, 6000);
  }

  function open() {
    overlay.style.display = '';
    if (fileInput) fileInput.value = '';
    setTimeout(() => clientSel && clientSel.focus(), 0);
  }
  function close() { overlay.style.display = 'none'; }

  btn.addEventListener('click', open);
  cancelBtn.addEventListener('click', close);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', (e) => {
    if (overlay.style.display === 'none') return;
    if (e.key === 'Escape') close();
  });

  submitBtn.addEventListener('click', async () => {
    const clientId = clientSel && clientSel.value;
    const file     = fileInput && fileInput.files && fileInput.files[0];
    if (!clientId) { toast('Select a client', 'error'); return; }
    if (!file)     { toast('Choose a CSV file', 'error'); return; }
    if (!/\.csv$/i.test(file.name)) {
      toast('Only .csv files are accepted', 'error'); return;
    }

    const fd = new FormData();
    fd.append('client_id', clientId);
    fd.append('file', file);

    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading…';
    try {
      const r = await fetch('/v2/api/csv/upload', {
        method: 'POST',
        credentials: 'same-origin',
        body: fd,
      });
      const data = await r.json().catch(() => ({}));
      if (!r.ok || data.status !== 'ok') {
        toast('Upload failed: ' + (data.message || `HTTP ${r.status}`), 'error');
        return;
      }
      close();
      toast(`Uploaded ${data.saved_as} — ingestion in progress, refresh in ~10s to see result.`);
    } catch (e) {
      toast('Upload failed: ' + e.message, 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Upload';
    }
  });
})();
