function exportExcel() {
  const params = new URLSearchParams();

  const yearInput = document.querySelector('input[name="year"]');
  const facultyInput = document.querySelector('input[name="faculty"]');
  const typeInput = document.querySelector('input[name="type"]');
  const langSelect = document.querySelector('select[name="lang"]');

  if (yearInput && yearInput.value) params.append('year', yearInput.value);
  if (facultyInput && facultyInput.value) params.append('faculty', facultyInput.value);
  if (typeInput && typeInput.value) params.append('type', typeInput.value);
  if (langSelect && langSelect.value) params.append('lang', langSelect.value);

  window.location.href = '/export/excel?' + params.toString();
}

async function downloadPDF() {
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF();
  const canvases = document.querySelectorAll('canvas');

  for (let i = 0; i < canvases.length; i++) {
    const canvas = canvases[i];

    const scale = 3;
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width * scale;
    tempCanvas.height = canvas.height * scale;

    const ctx = tempCanvas.getContext('2d');

    // Заливаем белым фоном
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

    // Масштабируем и отрисовываем оригинальный канвас
    ctx.scale(scale, scale);
    ctx.drawImage(canvas, 0, 0);

    // Берём изображение из tempCanvas
    const imgData = tempCanvas.toDataURL('image/jpeg', 1.0);
    const imgProps = pdf.getImageProperties(imgData);
    const pdfWidth = pdf.internal.pageSize.getWidth() - 30;
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

    pdf.addImage(imgData, 'JPEG', 15, 20, pdfWidth, pdfHeight);

    if (i < canvases.length - 1) pdf.addPage();
  }

  pdf.save("charts_report.pdf");
}


