import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable'

export function createPDF(items){
    console.log(items)
    const doc = new jsPDF();

    doc.setFontSize(16);
    doc.text('Landed Cost Report', 14, 20);

    const tableData = items.map(item => [
    item.id,
    item.prod_desc,
    item.htsus,
    item.quantity,
    item.prod_value,
    item.weight,
    item.shipping,
    item.insurance,
    item.mrn_duty.toFixed(2),
    item.tax301_duty.toFixed(2),
    item.vat_total.toFixed(2),
    item.landing_cost.toFixed(2),
    ]);

    const tableHeaders = [
    'ID',
    'Description',
    'HTSUS',
    'Qty',
    'Value',
    'Weight',
    'Shipping',
    'Insurance',
    'MRN',
    '301 Tax',
    'VAT',
    'Landed Cost',
    ];

    const totalLandingCost = items.reduce((sum, item) => sum + item.landing_cost, 0);

    const summaryRow = [
    {
        content: 'Total Landing Cost',
        colSpan: 1,
        styles: {
        halign: 'left',
        fontStyle: 'bold',
        fillColor: [220, 220, 220], // light gray background
        textColor: [0, 0, 0],       // black text
        }
    },
    '', '', '', '', '', '', '', '', '',
    {
        content: `$${totalLandingCost.toFixed(2)}`,
        styles: {
        halign: 'left',
        fontStyle: 'bold',
        fillColor: [220, 220, 220],
        textColor: [0, 128, 0] // green total
        }
    }
    ];

    autoTable(doc, {
    startY: 30,
    head: [tableHeaders],
    body: tableData,
    foot: [summaryRow],
    styles: {
        fontSize: 9
    },
    footStyles: {
        fontStyle: 'bold',
        fillColor: [245, 245, 245], // fallback default for other footer cells
        textColor: [50, 50, 50],
    }
    });
    doc.save('landed_cost_report.pdf');
}