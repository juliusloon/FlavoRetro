function downloadObject(filename, value) {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: 'application/json' }));
    link.download = filename;link.click();setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}
