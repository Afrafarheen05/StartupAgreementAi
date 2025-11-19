export function shortText(text, n=160){
  if(!text) return "";
  return text.length > n ? text.slice(0,n) + "…" : text;
}
