import { Conversation } from '@/types/chat';
import {
  ExportFormatV1,
  ExportFormatV2,
  ExportFormatV3,
  ExportFormatV4,
  LatestExportFormat,
  SupportedExportFormats,
} from '@/types/export';
import { FolderInterface } from '@/types/folder';
import { Prompt } from '@/types/prompt';
import { PDFDocument, PDFFont, PageSizes, StandardFonts, rgb } from 'pdf-lib'


export async function createPdf(data:LatestExportFormat) {
  var all_conversations = data.history

  const pdfDoc = await PDFDocument.create();
  const page_size = PageSizes.A4
  const font = await pdfDoc.embedFont(StandardFonts.TimesRoman);
  const fontSize = 12;
  let y: number;

  for (const conversation of all_conversations) {
    var page = pdfDoc.addPage(page_size);
    const { width, height } = page.getSize();
    const margin = 50;
    const usableWidth = width - 2 * margin;
    y = height - margin;

    page.drawText(conversation.name, { x: 3*margin, y, font, size:1.5*fontSize, color: rgb(0, 0, 0) });
    y -= font.heightAtSize(1.5*fontSize);

    for (const message of conversation.messages) {
      const senderText =  message.role=="assistant"? "[ChatBot]: " : "[User]: ";
      const fullMessage = `${senderText}${message.content}`;
      const lines = splitTextIntoLines(fullMessage, font, fontSize, usableWidth);

      if (y - lines.length * font.heightAtSize(fontSize) < margin) {
        page = pdfDoc.addPage(page_size);
        y = height - margin;
      }

      lines.forEach((line) => {
        page.drawText(line, { x: margin, y, font, size:fontSize, color: rgb(0, 0, 0) });
        y -= font.heightAtSize(fontSize);
      });

      y -= 10;
    }
  }

  const pdfBytes = await pdfDoc.save()
  return pdfBytes
}

function splitTextIntoLines(text: string, font: PDFFont, fontSize: number, maxWidth: number) {
  const words = text.split(' ');
  const lines = [];
  let currentLine = '';

  for (const word of words) {
    const width = font.widthOfTextAtSize(word, fontSize);

    if (currentLine === '' || font.widthOfTextAtSize(currentLine + ' ' + word, fontSize) <= maxWidth) {
      currentLine += (currentLine === '' ? '' : ' ') + word;
    } else {
      lines.push(currentLine);
      currentLine = word;
    }
  }

  lines.push(currentLine);
  return lines;
}
