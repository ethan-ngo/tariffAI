import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export function createPDF(items) {
  const doc = new jsPDF({ orientation: 'portrait' });
  const margin = 14;
  let y = 36;

  doc.setFontSize(30);
  doc.text('Landed Cost Report', margin, y);
  y += 10;

  function formatRate(rate) {
    if (typeof rate === 'number') {
      return rate === 0 ? '0%' : `${rate}%`;
    }
    if (typeof rate === 'string') {
      if (rate.includes('%')) return rate;
      if (rate.match(/^\d+(\.\d+)?$/)) return `${rate}%`;
      return rate;
    }
    return '-';
  }

  const fields = [
    ['ID', 'id'],
    ['Description', 'prod_desc'],
    ['HTSUS', 'htsus_code'],
    ['Quantity', 'quantity'],
    ['Value', item => item.productValue != null ? `$${item.productValue.toFixed(2)}` : '-'],
    ['Weight', item => `${item.weight} ${item.weightUnit}`],
    ['Shipping', item => item.shipping != null ? `$${item.shipping.toFixed(2)}` : '-'],
    ['Insurance', item => item.insurance != null ? `$${item.insurance.toFixed(2)}` : '-'],
    ['Base Duty Rate', item => formatRate(item.mrn_rate)],
    ['Base Duty', item => item.mrn_duty != null ? `$${item.mrn_duty.toFixed(2)}` : '-'],
    ['301 Rate', item => formatRate(item.tax301_rate)],
    ['301 Duty', item => item.tax301_duty != null ? `$${item.tax301_duty.toFixed(2)}` : '-'],
    ['Reciprocal Rate', item => formatRate(item.reciprocal_total_rate)],
    ['Reciprocal Duty', item => item.reciprocal_duty != null ? `$${item.reciprocal_duty.toFixed(2)}` : '-'],
    ['VAT Rate', item => formatRate(item.vat_rate)],
    ['VAT', item => item.vat_total != null ? `$${item.vat_total.toFixed(2)}` : '-'],
    ['Landed Cost', item => item.landing_cost != null ? `$${item.landing_cost.toFixed(2)}` : '-'],
  ];

  const chunkSize = 2; // max 2 products per table

  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);

    // Build table body for this chunk
    const tableBody = fields.map(([label, accessor]) => {
      const row = [label];
      chunk.forEach(item => {
        if (typeof accessor === 'function') {
          row.push(accessor(item));
        } else {
          row.push(item[accessor] ?? '-');
        }
      });
      return row;
    });

    const headRow = ['Field', ...chunk.map((_, idx) => `Product ${i + idx + 1}`)];

    autoTable(doc, {
      startY: y,
      head: [headRow],
      body: tableBody,
      styles: {
        fontSize: 8,
        cellPadding: 2,
      },
      margin: { left: margin, right: margin },
      didParseCell: function (data) {
        if (data.section === 'body') {
            if (data.row.index % 2 === 0) {
            data.cell.styles.fillColor = [245, 245, 245]; // light gray
            } else {
            data.cell.styles.fillColor = [255, 255, 255]; // white
            }
        }
    }
    });

    y = doc.lastAutoTable.finalY + 10;

    // Add new page if close to bottom
    if (y > doc.internal.pageSize.height - 40) {
      doc.addPage();
      y = margin;
    }
  }

  // Summary at bottom of last page
  const totalLandingCost = items.reduce((sum, item) => sum + item.landing_cost, 0);

  doc.setFontSize(12);
  doc.setFont(undefined, 'bold');
  doc.text(`Total Landed Cost: $${totalLandingCost.toFixed(2)}`, margin, y);

  doc.save('landed_cost_report.pdf');
}
