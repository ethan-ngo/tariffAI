import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

function createPDF(items) {
  const doc = new jsPDF({ orientation: 'portrait' });
  const margin = 14;
  let y = 36;

  doc.setFontSize(26);
  doc.setFont('times', 'normal');
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
    ['Description', 'prod_desc'],
    ['Country', item => item.origin_country],
    ['HTSUS', 'htsus_code'],
    ['Quantity', 'quantity'],
    ['Value', item => item.productValue != null ? `$${item.productValue.toFixed(2)}` : '-'],
    ['Weight', item => `${item.weight} ${item.weightUnit}`],
    ['Shipping', item => item.shipping != null ? `$${item.shipping.toFixed(2)}` : '-'],
    ['Insurance', item => item.insurance != null ? `$${item.insurance.toFixed(2)}` : '-'],
    ['Base Duty Rate', item => {
      const rate = item?.mrn_rate;

      if (rate === null || rate === undefined || rate === '') return '-';

      const rateStr = rate.toString().toLowerCase();
      return rateStr.includes('/') || rateStr.includes('c') ? rateStr : `${rateStr}%`;
    }],
    ['301 Rate', item => formatRate(item.tax301_rate)],
    ['Reciprocal Rate', item => formatRate(item.reciprocal_total_rate)],
    ['VAT Rate', item => formatRate(item.vat_rate)],
    ['Landed Cost', item => item.landing_cost != null ? `$${item.landing_cost.toFixed(2)}` : '-'],
  ];

  const chunkSize = 3; // max 3 products per table

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
      margin: { left: margin, right: margin },
      styles: {
        fontSize: 12,
        font: 'times',
        fontStyle: 'normal',
        cellPadding: { top: 4, right: 6, bottom: 4, left: 6 },
        valign: 'middle',
        halign: 'center',
        lineColor: [220, 220, 220],
        lineWidth: 0.2,
      },
      headStyles: {
        fillColor: [54, 95, 145],
        textColor: 255,
        fontSize: 13,
        fontStyle: 'bold',
        halign: 'center',
        cellPadding: { top: 6, bottom: 6 },
      },
      bodyStyles: {
        textColor: [30, 30, 30],
        fontSize: 12,
      },
      columnStyles: {
        0: { halign: 'center', fontStyle: 'bold' }, // Label column
        1: { halign: 'center' },
        2: { halign: 'center' },
        3: { halign: 'center' },
        4: { halign: 'center' },
        5: { halign: 'center' },
      },
      alternateRowStyles: {
        fillColor: [245, 245, 245],
      },
      didParseCell: function (data) {
        if (data.section === 'head') {
          data.cell.styles.fillColor = [54, 95, 145];
          data.cell.styles.textColor = 255;
        } else if (data.section === 'body') {
          const isEven = data.row.index % 2 === 0;
          data.cell.styles.fillColor = isEven ? [248, 248, 248] : [255, 255, 255];
        }
      },
    });

    y = doc.lastAutoTable.finalY + 10;

    if (y > doc.internal.pageSize.height - 40) {
      doc.addPage();
      y = margin;
      doc.setFont('times', 'normal');
      doc.setFontSize(12);
      doc.text('Landed Cost Report (continued)', margin, y);
      y += 10;
    }
  }

  // Summary at bottom of last page
  const totalLandingCost = items.reduce((sum, item) => sum + item.landing_cost, 0);

  doc.setFontSize(12);
  doc.setFont(undefined, 'bold');
  doc.text(`Total Landed Cost: $${totalLandingCost.toFixed(2)}`, margin, y);

  doc.save('landed_cost_report.pdf');
}

function create_table_PDF(results) {
  const doc = new jsPDF({ orientation: 'portrait' });
  const margin = 14;
  let y = 36;

  doc.setFontSize(26);
  doc.setFont('times', 'normal');
  doc.text('Country Tariff Rates Comparison', margin, y);
  y += 10;

  const fields = [
    ['HTSUS Code', item => item.htsus_code],
    ['Product Description', item => item.prod_desc],
    ['Quantity', item => item.quantity],
    ['Weight', item => `${item.weight} ${item.weightUnit}`],
    ['Product Value', item => `$${item.productValue.toFixed(2)}`],
    ['Shipping', item => `$${item.shipping.toFixed(2)}`],
    ['Insurance', item => `$${item.insurance.toFixed(2)}`],
    ['Subtotal', item => `$${item.subtotal.toFixed(2)}`],
    ['Base Duty Rate', item => {
      const rate = item?.mrn_rate;
      if (rate === null || rate === undefined || rate === '') return '-';
      const rateStr = rate.toString().toLowerCase();
      return rateStr.includes('/') || rateStr.includes('c') ? rateStr : `${rateStr}%`;
    }],
    ['301 Duty Rate', item => `${item.tax301_rate}%`],
    ['Reciprocal Rate', item => `${item.reciprocal_total_rate}%`],
    ['Total Duty Rates', item => {
      const mrn = item.mrn_rate ?? 0;
      const tax301 = Number(item.tax301_rate ?? 0);
      const reciprocal = Number(item.reciprocal_total_rate ?? 0);
      const isCompoundRate = typeof mrn === 'string' && (mrn.includes('/') || mrn.includes('c'));
      if (!isCompoundRate) {
        const base = Number(mrn ?? 0);
        const total = base + tax301 + reciprocal;
        return `${total.toFixed(2)}%`;
      } else {
        const total = tax301 + reciprocal;
        return `${total.toFixed(2)}% + ${mrn}`;
      }
    }],
    ['VAT Rate', item => `${item.vat_rate}%`],
  ];

  // Split results into chunks of 5
  const chunkSize = 3;
  for (let i = 0; i < results.length; i += chunkSize) {
    const chunk = results.slice(i, i + chunkSize);
    const countryList = chunk.map(r => r.origin_country);
    const headRow = ['Field', ...countryList];

    const bodyRows = fields.map(([label, getter]) => {
      return [label, ...chunk.map(result => {
        try {
          return getter(result) ?? '-';
        } catch {
          return '-';
        }
      })];
    });

    // If not the first chunk, add new page
    if (i > 0) {
      doc.addPage();
      y = 36;
      doc.setFont('times', 'normal');
      doc.setFontSize(12);
      doc.text('Country Tariff Rates Comparison (continued)', margin, y);
      y += 10;
    }

    autoTable(doc, {
      head: [headRow],
      body: bodyRows,
      startY: y,
      margin: { left: margin, right: margin },
      styles: {
        fontSize: 12,
        cellPadding: { top: 4, right: 6, bottom: 4, left: 6 },
        valign: 'middle',
        lineColor: [220, 220, 220],
        lineWidth: 0.2,
        halign: 'center',
        fontStyle: 'normal',
        font: 'times',
      },
      headStyles: {
        fillColor: [54, 95, 145],     // muted blue
        textColor: 255,
        fontSize: 13,
        fontStyle: 'bold',
        halign: 'center',
        cellPadding: { top: 6, bottom: 6 },
      },
      bodyStyles: {
        textColor: [30, 30, 30],
        fontSize: 12,
      },
      alternateRowStyles: {
        fillColor: [245, 245, 245],   // light gray
      },
      columnStyles: {
        0: { halign: 'center', fontStyle: 'bold' }, // Field column
        1: { halign: 'center' },
        2: { halign: 'center' },
        3: { halign: 'center' },
        4: { halign: 'center' },
        5: { halign: 'center' },
      },
      didParseCell: function (data) {
        if (data.section === 'head') {
          data.cell.styles.fillColor = [54, 95, 145];
          data.cell.styles.textColor = 255;
        } else if (data.section === 'body') {
          const isEven = data.row.index % 2 === 0;
          data.cell.styles.fillColor = isEven ? [248, 248, 248] : [255, 255, 255];
        }
      },
    });
  }

  const blob = doc.output('blob');
  const pdfUrl = URL.createObjectURL(blob);
  return pdfUrl;
}


export { createPDF, create_table_PDF };