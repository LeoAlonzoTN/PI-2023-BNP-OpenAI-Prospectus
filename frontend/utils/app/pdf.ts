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
import { PDFDocument, PageSizes, StandardFonts, rgb } from 'pdf-lib'

export async function createPdf(data:LatestExportFormat) {
  const pdfDoc = await PDFDocument.create()
  const timesRomanFont = await pdfDoc.embedFont(StandardFonts.TimesRoman)
  const page_size = PageSizes.A4

  var all_conversations = data.history
  var all_folder = data.folders

  var page = pdfDoc.addPage(page_size)
  var { width, height } = page.getSize()
  
  const fontSize = 5
  const base_spacing = 2
  const marge = 5
  const bigmarge = 2*marge

  for (var conv of all_conversations ){
    if (height - base_spacing * fontSize <= 0){
      page = pdfDoc.addPage(page_size)
      var { width, height } = page.getSize()
    }

    page.drawText("Conversation : " + conv.name, {
        x: marge,
        y: height - base_spacing * fontSize,
        size: fontSize,
        lineHeight:fontSize,
        font: timesRomanFont,
        maxWidth: width - 2*marge,
      })
    height = height - base_spacing * fontSize

    for (var message of conv.messages){
        if (height - base_spacing * fontSize <= 0){
          page = pdfDoc.addPage(page_size)
          var { width, height } = page.getSize()
        }

        page.drawText(message.role + " : ", {
            x: bigmarge,
            y: height - base_spacing * fontSize,
            size: fontSize,
            lineHeight:fontSize,
            font: timesRomanFont,
            maxWidth: width - 2*bigmarge,
          })

        height = height - base_spacing * fontSize

        if (height - Math.ceil(message.content.length / (width - 2*bigmarge)) * fontSize - base_spacing * fontSize <= 0){
          page = pdfDoc.addPage(page_size)
          var { width, height } = page.getSize()
        }

        page.drawText(message.content, {
            x: bigmarge,
            y: height - base_spacing * fontSize,
            size: fontSize,
            lineHeight:fontSize,
            font: timesRomanFont,
            maxWidth: width - 2*bigmarge,
          })
        height = height - Math.ceil(message.content.length / (width - 2*bigmarge)) * fontSize - base_spacing * fontSize
    }
  }


  const pdfBytes = await pdfDoc.save()
  return pdfBytes
}


