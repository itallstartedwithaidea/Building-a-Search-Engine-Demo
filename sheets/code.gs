/**
 *  Google-Sheet SERP front-end.
 *  Named ranges:
 *    • SearchBar   → B4
 *    • ResultRange → A5:D14  (≥10×4)
 */
function onEdit(e) {
  if (!e) return;                          // skip manual runs
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  const sh   = ss.getActiveSheet();
  const bar  = ss.getRangeByName('SearchBar');
  if (e.range.getA1Notation() !== bar.getA1Notation()) return;

  const api   = PropertiesService.getScriptProperties().getProperty('SEARCH_API');
  const query = e.value.trim();
  if (!query) return;

  const resp  = UrlFetchApp.fetch(api, {
    method:'post', contentType:'application/json',
    payload:JSON.stringify({query, k:10})
  });
  const hits  = JSON.parse(resp.getContentText()).results || [];

  const grid  = ss.getRangeByName('ResultRange');
  grid.clear({contentsOnly:true, formatOnly:false});

  if (!hits.length) { grid.getCell(1,1).setValue('No results'); return; }

  const rows = hits.map(h => [
    h.title,
    h.snippet,
    h.url,
    `=HYPERLINK("${h.url}","↗")`
  ]);
  grid.offset(0,0,rows.length,4).setValues(rows);

  // simple SERP-like styling
  grid.offset(0,0,rows.length,1).setFontColor('#1a0dab').setFontSize(12);
  grid.offset(0,1,rows.length,1).setFontColor('#4d5156').setWrap(true).setFontSize(10);
  grid.offset(0,2,rows.length,1).setFontColor('#006621').setFontSize(9);
  grid.offset(0,3,rows.length,1).setHorizontalAlignment('center');

  ss.getActiveSheet().autoResizeRows(5, rows.length);
  ['A','B','C','D'].forEach(c => sh.autoResizeColumn(sh.getRange(c+'1').getColumn()));

  // hero thumbnail
  const hero = sh.getRange('G5').clearContent();
  if (hits[0]?.thumbnail) hero.setFormula(`=IMAGE("${hits[0].thumbnail}",4)`);
}
