function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export function downloadJson(filename: string, payload: unknown) {
  triggerDownload(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }), filename);
}

export function downloadExcelCompatibleFile(filename: string, rows: Array<Record<string, unknown>>) {
  const headers = Array.from(new Set(rows.flatMap((row) => Object.keys(row))));
  const lines = [
    headers.join("\t"),
    ...rows.map((row) => headers.map((header) => String(row[header] ?? "")).join("\t")),
  ];
  triggerDownload(
    new Blob([lines.join("\n")], { type: "application/vnd.ms-excel;charset=utf-8" }),
    filename,
  );
}

export async function exportElementToPng(element: HTMLElement, filename: string) {
  const rect = element.getBoundingClientRect();
  const width = Math.max(Math.ceil(rect.width), 320);
  const height = Math.max(Math.ceil(rect.height), 180);
  const cloned = element.cloneNode(true) as HTMLElement;
  cloned.style.margin = "0";
  cloned.style.width = `${width}px`;
  cloned.style.height = `${height}px`;

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
      <foreignObject width="100%" height="100%">
        <div xmlns="http://www.w3.org/1999/xhtml">${cloned.outerHTML}</div>
      </foreignObject>
    </svg>
  `;
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }));
  try {
    const image = await new Promise<HTMLImageElement>((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = url;
    });
    const canvas = document.createElement("canvas");
    canvas.width = width * 2;
    canvas.height = height * 2;
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas export is not available in this browser.");
    context.scale(2, 2);
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, width, height);
    context.drawImage(image, 0, 0, width, height);
    const pngBlob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, "image/png"));
    if (!pngBlob) throw new Error("Could not generate PNG export.");
    triggerDownload(pngBlob, filename);
  } finally {
    URL.revokeObjectURL(url);
  }
}

export function printElementToPdf(title: string, element: HTMLElement) {
  const popup = window.open("", "_blank", "noopener,noreferrer,width=1280,height=900");
  if (!popup) {
    throw new Error("Pop-up blocked. Allow pop-ups to export this dashboard as PDF.");
  }
  popup.document.write(`
    <html>
      <head>
        <title>${title}</title>
        <style>
          body { font-family: Inter, Arial, sans-serif; background: #ffffff; color: #171717; margin: 24px; }
          * { box-sizing: border-box; }
          .print-shell { max-width: 1280px; margin: 0 auto; }
        </style>
      </head>
      <body>
        <div class="print-shell">${element.outerHTML}</div>
      </body>
    </html>
  `);
  popup.document.close();
  popup.focus();
  popup.print();
  popup.close();
}
