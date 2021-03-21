export default function downloadTextFile(filename, text, content_type) {
  const element = document.createElement('a');
  element.hidden = true;
  const file = new Blob([text], {type: content_type});
  element.href = URL.createObjectURL(file);
  element.download = filename;
  document.body.appendChild(element);
  element.click();
}
