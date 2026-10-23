// ---------- 初始化 ----------
const targetsReady=api('/api/targets').then(rows => {
    for (const row of rows) {
        const zh = TARGET_NAMES_ZH[String(row.name).toLowerCase()];
        const option = text('option', zh ? `${zh} · ${row.name}` : row.name);
        option.value = row.smiles;
        option.dataset.name = String(row.name).toLowerCase();
        $('preset').append(option);
    }
}).catch(error => { $('message').textContent = error.message; });
$('preview').click();
