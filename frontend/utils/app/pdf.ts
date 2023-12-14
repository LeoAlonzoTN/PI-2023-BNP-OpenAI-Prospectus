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
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib'

export async function createPdf(data:LatestExportFormat) {
  const pdfDoc = await PDFDocument.create()
  const timesRomanFont = await pdfDoc.embedFont(StandardFonts.TimesRoman)
  var all_conversations = data.history
  var all_folder = data.folders

  const page = pdfDoc.addPage()
  var { width, height } = page.getSize()
  const fontSize = 5

  for (var conv of all_conversations ){
    page.drawText("Conversation : " + conv.name, {
        x: 5,
        y: height - 4 * fontSize,
        size: fontSize,
        font: timesRomanFont,
      })
    height = height - 4 * fontSize
    for (var message of conv.messages){
        page.drawText(message.role + " : ", {
            x: 5,
            y: height - 4 * fontSize,
            size: fontSize,
            font: timesRomanFont,
          })
        height = height - 4 * fontSize
        page.drawText(message.content , {
            x: 5,
            y: height - 4 * fontSize,
            size: fontSize,
            font: timesRomanFont,
          })
        height = height - 4 * fontSize
    }
  }


  const pdfBytes = await pdfDoc.save()
  return pdfBytes
}


