export const nonStupidDatetimeFormat = (date) => {
  let seconds = date.getSeconds().toString();
  if (seconds.length === 1) {
    seconds = '0' + seconds;
  }
  return `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()} ` +
  `${date.getHours()}:${date.getMinutes()}:${seconds}`;
};
